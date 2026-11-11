import io
import os
import re

import pytest
from werkzeug.datastructures import FileStorage

from app.storage.base import (
    StorageError,
    StorageNotFoundError,
    generate_image_key,
    is_safe_image_key,
)
from app.storage.local import LocalStorage
from app.storage.s3 import S3Storage
from tests.fakes import FakeS3Client

BUCKET = "kenooz11-gems-2026"


def make_file(data: bytes, name: str = "photo.png") -> FileStorage:
    return FileStorage(stream=io.BytesIO(data), filename=name)


def make_s3(client, **kwargs) -> S3Storage:
    return S3Storage(bucket=BUCKET, region="eu-north-1", client=client, **kwargs)


# ---------------------------------------------------------------- key helpers
def test_generate_image_key_is_unique_and_safe():
    k1 = generate_image_key("../../My Photo.PNG")
    k2 = generate_image_key("../../My Photo.PNG")
    assert k1 != k2
    assert re.fullmatch(r"[0-9a-f]{32}\.png", k1)
    assert is_safe_image_key(k1)


def test_generate_image_key_keeps_jpg_extension():
    assert generate_image_key("holiday.JPG").endswith(".jpg")


@pytest.mark.parametrize(
    "key", ["../x.png", "a/b.png", "", ".hidden", "a\\b.png", "x" * 300]
)
def test_unsafe_image_keys_rejected(key):
    assert is_safe_image_key(key) is False


# -------------------------------------------------------------- local storage
def test_local_storage_roundtrip(app, client, sample_image_bytes):
    storage = LocalStorage()
    key = storage.save(make_file(sample_image_bytes))

    assert os.path.isfile(os.path.join(app.config["UPLOAD_FOLDER"], key))
    assert storage.url_for(key) == f"/uploads/{key}"

    # Close the response so the streamed file handle is released before the
    # delete below (Windows cannot delete a file that is still open).
    with client.get(storage.url_for(key)) as response:
        assert response.status_code == 200
        assert response.data == sample_image_bytes

    assert storage.delete(key) is True
    assert not os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], key))
    assert storage.delete(key) is True  # deleting a missing file is not an error


def test_local_storage_delete_rejects_unsafe_key(app):
    assert LocalStorage().delete("../outside.png") is False


def test_local_storage_serve_missing_raises_not_found(app):
    with pytest.raises(StorageNotFoundError):
        LocalStorage().serve("missing.png")


def test_local_storage_write_failure_raises_storage_error(app, sample_image_bytes):
    class BrokenFile(FileStorage):
        def save(self, *args, **kwargs):
            raise OSError("disk full")

    broken = BrokenFile(stream=io.BytesIO(sample_image_bytes), filename="a.png")
    with pytest.raises(StorageError):
        LocalStorage().save(broken)


def test_local_storage_check_ok(app):
    LocalStorage().check()


# ----------------------------------------------------------------- S3 storage
def test_s3_save_uploads_private_object(app, sample_image_bytes):
    fake = FakeS3Client()
    key = make_s3(fake).save(make_file(sample_image_bytes, "a.png"))

    obj = fake.objects[(BUCKET, f"places/{key}")]
    assert obj["Body"] == sample_image_bytes
    assert obj["ContentType"] == "image/png"
    assert "ACL" not in obj  # objects stay private
    assert "ServerSideEncryption" not in obj


def test_s3_save_jpeg_content_type(app, sample_jpeg_bytes):
    fake = FakeS3Client()
    key = make_s3(fake).save(make_file(sample_jpeg_bytes, "a.jpg"))
    assert fake.objects[(BUCKET, f"places/{key}")]["ContentType"] == "image/jpeg"


def test_s3_optional_server_side_encryption(app, sample_image_bytes):
    fake = FakeS3Client()
    key = make_s3(fake, server_side_encryption="AES256").save(make_file(sample_image_bytes))
    assert fake.objects[(BUCKET, f"places/{key}")]["ServerSideEncryption"] == "AES256"


def test_s3_prefix_normalisation(app, sample_image_bytes):
    fake = FakeS3Client()
    key = make_s3(fake, prefix="/custom/").save(make_file(sample_image_bytes))
    assert (BUCKET, f"custom/{key}") in fake.objects

    fake2 = FakeS3Client()
    key2 = make_s3(fake2, prefix="").save(make_file(sample_image_bytes))
    assert (BUCKET, key2) in fake2.objects


def test_s3_save_failure_raises_storage_error(app, sample_image_bytes):
    fake = FakeS3Client()
    fake.fail_put = True
    with pytest.raises(StorageError):
        make_s3(fake).save(make_file(sample_image_bytes))
    assert fake.objects == {}


def test_s3_delete_and_delete_failure(app, sample_image_bytes):
    fake = FakeS3Client()
    storage = make_s3(fake)
    key = storage.save(make_file(sample_image_bytes))
    assert storage.delete(key) is True
    assert fake.objects == {}

    key = storage.save(make_file(sample_image_bytes))
    fake.fail_delete = True
    assert storage.delete(key) is False  # never raises
    assert storage.delete("../bad.png") is False


def test_s3_proxy_url_is_stable_relative_path(app):
    assert make_s3(FakeS3Client()).url_for("abc.png") == "/uploads/abc.png"


def test_s3_presigned_url_and_fallback(app):
    fake = FakeS3Client()
    storage = make_s3(fake, delivery="presigned", presigned_expiry=600)
    url = storage.url_for("abc.png")
    assert url.startswith(f"https://{BUCKET}.s3.eu-north-1.amazonaws.com/places/abc.png")
    assert "X-Amz-Expires=600" in url

    fake.fail_presign = True
    assert storage.url_for("abc.png") == "/uploads/abc.png"


def test_s3_serve_streams_private_object(app, sample_image_bytes):
    storage = make_s3(FakeS3Client())
    key = storage.save(make_file(sample_image_bytes))
    response = storage.serve(key)
    assert response.status_code == 200
    assert response.mimetype == "image/png"
    assert response.get_data() == sample_image_bytes
    assert "max-age" in response.headers["Cache-Control"]


def test_s3_serve_missing_raises_not_found(app):
    with pytest.raises(StorageNotFoundError):
        make_s3(FakeS3Client()).serve("missing.png")


def test_s3_serve_other_errors_are_storage_errors(app):
    fake = FakeS3Client()
    fake.fail_get = True
    with pytest.raises(StorageError) as exc_info:
        make_s3(fake).serve("abc.png")
    assert not isinstance(exc_info.value, StorageNotFoundError)


def test_s3_serve_presigned_redirects(app):
    response = make_s3(FakeS3Client(), delivery="presigned").serve("abc.png")
    assert response.status_code == 302
    assert "places/abc.png" in response.headers["Location"]


def test_s3_serve_rejects_unsafe_key(app):
    with pytest.raises(StorageNotFoundError):
        make_s3(FakeS3Client()).serve("../secret")


def test_s3_requires_bucket_and_valid_delivery():
    with pytest.raises(ValueError):
        S3Storage(bucket="", region="eu-north-1", client=FakeS3Client())
    with pytest.raises(ValueError):
        make_s3(FakeS3Client(), delivery="public")


def test_s3_check(app):
    fake = FakeS3Client()
    make_s3(fake).check()
    fake.fail_head = True
    with pytest.raises(StorageError):
        make_s3(fake).check()