from pathlib import Path
from uuid import uuid4

from app.core.config import settings

_EXT_BY_MEDIA = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def ext_for_media(media_type: str) -> str:
    return _EXT_BY_MEDIA.get(media_type.lower(), ".bin")


def save_receipt(image_bytes: bytes, media_type: str) -> str:
    """Simpan foto struk ke direktori receipts, kembalikan path absolut."""
    directory = Path(settings.receipts_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{uuid4().hex}{ext_for_media(media_type)}"
    path.write_bytes(image_bytes)
    return str(path)
