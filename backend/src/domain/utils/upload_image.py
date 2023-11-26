import uuid
from io import BytesIO

from fastapi import HTTPException, UploadFile
from PIL import Image
from starlette import status

from main.config import get_settings


def check_for_type(content_type: str) -> bool:
    return content_type in ('image/jpeg', 'image/png')


async def upload_image(image: UploadFile):
    if not check_for_type(image.content_type):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Invalid image type',
        )
    path = f'{get_settings().MEDIA_ROOT}/{uuid.uuid4()}.jpg'
    img = Image.open(BytesIO(await image.read()))
    img.thumbnail((2000, 1000))
    img.save(path)
    return path
