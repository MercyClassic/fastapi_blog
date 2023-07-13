import uuid
from io import BytesIO
from fastapi import UploadFile, HTTPException
from starlette import status
from PIL import Image
from src.config import MEDIA_ROOT


def check_for_type(content_type: str) -> bool:
    possible_content_types = ('image/jpeg', 'image/png')
    if content_type in possible_content_types:
        return True
    return False


async def upload_image(image: UploadFile):
    if not check_for_type(image.content_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid image type'
        )
    path = f'{MEDIA_ROOT}/{uuid.uuid4()}.jpg'
    img = Image.open(BytesIO(await image.read()))
    img.thumbnail((2000, 1000))
    img.save(path)
    return path
