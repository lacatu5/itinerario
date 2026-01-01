import mimetypes
import os

from google.cloud import storage
from loguru import logger

from core.config import config


class CloudStorageService:
    def __init__(self):
        self.bucket_name = config.CLOUD_STORAGE_BUCKET
        self.client = self._create_client()
        self.bucket = self.client.bucket(self.bucket_name)
        self._ensure_bucket_exists()

    def _create_client(self) -> storage.Client:
        if config.is_local:
            emulator_host = config.STORAGE_EMULATOR_HOST
            if not emulator_host.startswith("http://") and not emulator_host.startswith("https://"):
                emulator_host = f"http://{emulator_host}"
            os.environ["STORAGE_EMULATOR_HOST"] = emulator_host
            return storage.Client(project=config.GOOGLE_CLOUD_PROJECT, credentials=None)
        return storage.Client(project=config.GOOGLE_CLOUD_PROJECT)

    def _ensure_bucket_exists(self) -> None:
        try:
            if not self.bucket.exists():
                logger.info(f"Creating bucket: {self.bucket_name}")
                self.client.create_bucket(self.bucket_name)
                logger.info(f"Bucket {self.bucket_name} created successfully")
        except Exception as e:
            logger.warning(
                f"Failed to ensure bucket exists: {e}. Bucket creation will be attempted on first upload."
            )

    def upload_file(self, file_data, filename: str, content_type: str = None) -> str:
        if content_type is None:
            content_type, _ = mimetypes.guess_type(filename)
            if content_type is None:
                content_type = "application/octet-stream"

        blob = self.bucket.blob(filename)

        blob.metadata = {
            "contentType": content_type,
            "cacheControl": "public, max-age=3600",
        }

        if hasattr(file_data, "read"):
            file_content = file_data.read()
            blob.upload_from_string(file_content, content_type=content_type)
        else:
            blob.upload_from_file(file_data, content_type=content_type, num_retries=3)
        blob.make_public()

        public_url = blob.public_url
        if config.is_local:
            public_url = public_url.replace("storage-emulator:4443", "localhost:4443")

        return public_url

    def download_image(self, file_path: str) -> tuple[bytes, str, str | None]:
        try:
            blob = self.bucket.blob(file_path)

            if not blob.exists():
                raise FileNotFoundError(f"File {file_path} not found")

            content = blob.download_as_bytes()
            content_type = blob.content_type or "application/octet-stream"
            cache_control = blob.cache_control

            return content, content_type, cache_control

        except Exception as e:
            raise e

    def extract_filename_from_url(self, url: str) -> str:
        if "storage.googleapis.com" in url:
            return url.split("/")[-1].split("?")[0]
        else:
            return url

    def delete_image(self, image_url: str | None, fallback_prefix: str = None) -> None:
        if image_url:
            try:
                filename = self.extract_filename_from_url(image_url)
                blob = self.bucket.blob(filename)
                blob.delete()
            except Exception:
                pass
