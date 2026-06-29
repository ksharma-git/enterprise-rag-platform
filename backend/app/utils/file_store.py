import shutil
from pathlib import Path

from fastapi import UploadFile

from app.config import UPLOAD_DIR

UPLOAD_DIR.mkdir(exist_ok=True)


def save_uploaded_file(file: UploadFile) -> Path:
    """
    Save an uploaded file to the uploads directory.

    Returns:
        Path: The saved file path.
    """

    safe_filename = Path(file.filename).name
    file_path = UPLOAD_DIR / safe_filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path
