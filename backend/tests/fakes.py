import io

from botocore.exceptions import ClientError


def client_error(code: str, operation: str) -> ClientError:
    return ClientError({"Error": {"Code": code, "Message": code}}, operation)


class FakeS3Client:
    """In-memory stand-in for a boto3 S3 client. No network, no credentials."""

    def __init__(self):
        self.objects: dict[tuple[str, str], dict] = {}
        self.fail_put = False
        self.fail_get = False
        self.fail_delete = False
        self.fail_head = False
        self.fail_presign = False

    def put_object(self, **kwargs):
        if self.fail_put:
            raise client_error("AccessDenied", "PutObject")
        self.objects[(kwargs["Bucket"], kwargs["Key"])] = kwargs
        return {}

    def get_object(self, Bucket, Key):
        if self.fail_get:
            raise client_error("AccessDenied", "GetObject")
        obj = self.objects.get((Bucket, Key))
        if obj is None:
            raise client_error("NoSuchKey", "GetObject")
        body = obj["Body"]
        return {
            "Body": io.BytesIO(body),
            "ContentType": obj.get("ContentType"),
            "ContentLength": len(body),
            "ETag": '"fake-etag"',
        }

    def delete_object(self, Bucket, Key):
        if self.fail_delete:
            raise client_error("AccessDenied", "DeleteObject")
        self.objects.pop((Bucket, Key), None)
        return {}

    def head_bucket(self, Bucket):
        if self.fail_head:
            raise client_error("403", "HeadBucket")
        return {}

    def generate_presigned_url(self, ClientMethod, Params=None, ExpiresIn=3600):
        if self.fail_presign:
            raise client_error("InternalError", "Presign")
        return (
            f"https://{Params['Bucket']}.s3.eu-north-1.amazonaws.com/{Params['Key']}"
            f"?X-Amz-Expires={ExpiresIn}&X-Amz-Signature=fake"
        )