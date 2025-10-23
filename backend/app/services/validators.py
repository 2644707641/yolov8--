from pathlib import Path

from fastapi import HTTPException, status, UploadFile


def validate_extension(filename: str, allowed_extensions: set[str], message: str) -> None:
    suffix = Path(filename).suffix.lower()
    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


def save_upload_file(
    upload: UploadFile,
    destination: Path,
    *,
    max_size: int,
) -> int:
    """
    将 UploadFile 保存到目标路径，并限制文件大小。
    返回写入的字节数。
    """
    total = 0
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("wb") as buffer:
        while True:
            chunk = upload.file.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > max_size:
                buffer.close()
                destination.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"文件大小超出限制（最大 {max_size // 1024 // 1024} MB）",
                )
            buffer.write(chunk)

    upload.file.close()
    return total

