import unicodedata

from fastapi import HTTPException, UploadFile

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp", "image/gif"]
MAX_IMAGE_SIZE = 10 * 1024 * 1024


def validate_image(file: UploadFile, max_size: int = MAX_IMAGE_SIZE) -> None:
    from loguru import logger

    logger.info(f"=== [validate_image] Starting validation for content_type: {file.content_type}")

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not allowed. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}",
        )

    logger.info("=== [validate_image] Checking file size...")
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    logger.info(f"=== [validate_image] File size: {file_size} bytes")

    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File size {file_size} bytes exceeds maximum allowed size of {max_size} bytes",
        )


def sanitize_filename(filename: str | None) -> str:
    safe_filename = filename or "image"
    safe_filename = (
        unicodedata.normalize("NFKD", safe_filename).encode("ascii", "ignore").decode("ascii")
    )
    safe_filename = "".join(c for c in safe_filename if c.isalnum() or c in "._-")
    return safe_filename or "image"


def generate_image_filename(prefix: str, entity_id: str, filename: str | None) -> str:
    safe_filename = sanitize_filename(filename)
    return f"{prefix}/{entity_id}_{safe_filename}"


def upload_image(
    file: UploadFile,
    prefix: str,
    entity_id: str,
    old_image_url: str | None = None,
    max_size: int = MAX_IMAGE_SIZE,
) -> str:
    from loguru import logger
    from core.storage.client import CloudStorageService

    logger.info(f"=== [upload_image] Received file type: {type(file)}, file: {file}")
    validate_image(file, max_size)
    cloud_storage = CloudStorageService()
    cloud_storage.delete_image(old_image_url)

    filename = generate_image_filename(prefix, entity_id, file.filename)
    content_type = file.content_type or "image/jpeg"
    public_url = cloud_storage.upload_file(file.file, filename, content_type)

    return public_url


def delete_image(image_url: str | None, fallback_prefix: str = None) -> None:
    from core.storage.client import CloudStorageService

    cloud_storage = CloudStorageService()
    cloud_storage.delete_image(image_url, fallback_prefix)


def download_image(file_path: str):
    from core.storage.client import CloudStorageService

    cloud_storage = CloudStorageService()
    return cloud_storage.download_image(file_path)


async def sync_model_image(
    db,
    model_instance,
    file: UploadFile,
    bucket_path: str,
    image_url_field: str = "image_url",
    id_field: str = "id",
    max_size: int = MAX_IMAGE_SIZE,
) -> dict:
    from loguru import logger
    from core.storage.client import CloudStorageService

    logger.info("=== [sync_model_image] Starting, validating image...")
    validate_image(file, max_size)
    logger.info("=== [sync_model_image] Image validated, creating storage client...")
    cloud_storage = CloudStorageService()

    logger.info("=== [sync_model_image] Deleting old image...")
    old_image_url = getattr(model_instance, image_url_field, None)
    cloud_storage.delete_image(old_image_url)

    logger.info("=== [sync_model_image] Generating filename...")
    entity_id = str(getattr(model_instance, id_field))
    filename = generate_image_filename(bucket_path, entity_id, file.filename)
    content_type = file.content_type or "image/jpeg"

    logger.info(f"=== [sync_model_image] Uploading file: {filename}, content_type: {content_type}")
    new_image_url = cloud_storage.upload_file(file.file, filename, content_type)
    logger.info(f"=== [sync_model_image] Upload complete, URL: {new_image_url}")

    logger.info("=== [sync_model_image] Updating model...")
    setattr(model_instance, image_url_field, new_image_url)
    db.add(model_instance)
    await db.commit()
    await db.refresh(model_instance)
    logger.info("=== [sync_model_image] Database updated")

    return {
        "message": f"{type(model_instance).__name__} image uploaded successfully",
        "image_url": new_image_url,
        "model": model_instance,
    }
