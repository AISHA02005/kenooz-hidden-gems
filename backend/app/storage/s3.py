import logging

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import BotoCoreError, ClientError
from flask import Response, redirect
from werkzeug.datastructures import FileStorage

from app.storage.base import (
    ImageStorage,
    StorageError,
    StorageNotFoundError,
    content_type_for,
    generate_image_key,
    is_safe_image_key,
)

logger = logging.getLogger(__name__)

_NOT_FOUND_CODES = {"NoSuchKey", "404", "NotFound"}


def _error_code(exc: ClientError) -> str:
    return str(exc.response.get("Error", {}).get("Code", ""))


class S3Storage(ImageStorage):
    """
    Stores images as PRIVATE objects in Amazon S3.

    Credentials come from the standard boto3 provider chain (the EC2 IAM Role
    in production). No keys are read from application config.
    """

    name = "s3"

    def __init__(
        self,
        bucket: str,
        region: str,
        prefix: str = "places/",
        delivery: str = "proxy",
        presigned_expiry: int = 900,
        server_side_encryption: str | None = None,
        client=None,
    ):
        if not bucket:
            raise ValueError("S3_BUCKET_NAME is required for the S3 storage backend.")
        if delivery not in ("proxy", "presigned"):
            raise ValueError("IMAGE_DELIVERY must be 'proxy' or 'presigned'.")
        self.bucket = bucket
        self.region = region
        cleaned = (prefix or "").strip().strip("/")
        self.prefix = f"{cleaned}/" if cleaned else ""
        self.delivery = delivery
        self.presigned_expiry = presigned_expiry
        self.server_side_encryption = server_side_encryption
        self._client = client  # injectable for tests

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client(
                "s3",
                region_name=self.region,
                config=BotoConfig(
                    signature_version="s3v4",
                    retries={"max_attempts": 3, "mode": "standard"},
                    connect_timeout=5,
                    read_timeout=15,
                ),
            )
        return self._client

    def _object_key(self, image_key: str) -> str:
        return f"{self.prefix}{image_key}"

    def save(self, file: FileStorage) -> str:
        key = generate_image_key(file.filename)
        params = {
            "Bucket": self.bucket,
            "Key": self._object_key(key),
            "Body": file.read(),  # already validated <= 5 MB
            "ContentType": content_type_for(key),
        }
        if self.server_side_encryption:
            params["ServerSideEncryption"] = self.server_side_encryption
        try:
            self.client.put_object(**params)
        except (BotoCoreError, ClientError) as exc:
            logger.error("S3 upload failed for %s: %s", params["Key"], exc)
            raise StorageError("Failed to upload image to S3.") from exc
        return key

    def delete(self, image_key: str) -> bool:
        if not is_safe_image_key(image_key):
            return False
        try:
            self.client.delete_object(Bucket=self.bucket, Key=self._object_key(image_key))
            return True
        except (BotoCoreError, ClientError) as exc:
            logger.error("S3 delete failed for %s: %s", self._object_key(image_key), exc)
            return False

    def _presign(self, image_key: str) -> str:
        try:
            return self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": self._object_key(image_key)},
                ExpiresIn=self.presigned_expiry,
            )
        except (BotoCoreError, ClientError) as exc:
            raise StorageError("Failed to generate presigned URL.") from exc

    def serve(self, image_key: str):
        if not is_safe_image_key(image_key):
            raise StorageNotFoundError(image_key)

        if self.delivery == "presigned":
            return redirect(self._presign(image_key), code=302)

        try:
            obj = self.client.get_object(Bucket=self.bucket, Key=self._object_key(image_key))
            data = obj["Body"].read()
        except ClientError as exc:
            if _error_code(exc) in _NOT_FOUND_CODES:
                raise StorageNotFoundError(image_key) from exc
            logger.error("S3 read failed for %s: %s", self._object_key(image_key), exc)
            raise StorageError("Failed to read image from S3.") from exc
        except BotoCoreError as exc:
            logger.error("S3 read failed for %s: %s", self._object_key(image_key), exc)
            raise StorageError("Failed to read image from S3.") from exc

        content_type = obj.get("ContentType") or ""
        if not content_type.startswith("image/"):
            content_type = content_type_for(image_key)
        headers = {"Cache-Control": "public, max-age=86400"}
        if obj.get("ETag"):
            headers["ETag"] = obj["ETag"]
        return Response(data, mimetype=content_type, headers=headers)

    def url_for(self, image_key: str) -> str:
        if self.delivery == "presigned":
            try:
                return self._presign(image_key)
            except StorageError:
                logger.warning("Presign failed for %s; using /uploads URL", image_key)
        return f"/uploads/{image_key}"

    def check(self) -> None:
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except (BotoCoreError, ClientError) as exc:
            raise StorageError("S3 bucket is not reachable.") from exc