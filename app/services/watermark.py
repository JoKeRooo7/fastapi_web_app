import io
import os
import uuid
import asyncio
from PIL import Image
from fastapi import UploadFile
from settings import settings


class AvatarError(Exception):
    pass


class AvatarHandler:
    async def save_avatar_file(self, user_avatar_file: UploadFile):
        await self._validate_avatar(user_avatar_file)
        file_extension = user_avatar_file.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        avatar_path = os.path.join(settings.AVATARS_PATH, unique_filename)
        image = await asyncio.to_thread(Image.open, user_avatar_file.file)
        watermarked = await self._add_watermark(image)
        await asyncio.to_thread(watermarked.save, avatar_path, "JPEG")
        user_avatar_file.file.close()
        return avatar_path

    async def _add_watermark(self, image: str) -> None:
        watermark = await asyncio.to_thread(
            Image.open, settings.WATERMARK_PATH)
        # 20% от основного изображения
        max_watermark_width = image.width * 0.2
        max_watermark_height = image.height * 0.2
        watermark.thumbnail(
            (max_watermark_width, max_watermark_height), Image.LANCZOS)
        # Отступы 10 пикселей
        x = image.width - watermark.width - 10
        y = image.height - watermark.height - 10
        watermarked = Image.new("RGBA", image.size)
        watermarked.paste(image, (0, 0))
        watermarked.paste(watermark, (x, y), watermark)
        return watermarked.convert("RGB")

    async def _validate_avatar(self, avatar):
        if (not (avatar.filename.endswith('.jpeg') or
                 avatar.filename.endswith('.jpg') or
                 avatar.filename.endswith('.png'))):
            raise AvatarError("Неверный формат")
        contents = await avatar.read()
        if not contents:
            raise AvatarError("Файл пуст или открыт в другом потоке")
        try:
            avatar.file.seek(0)
            image = Image.open(io.BytesIO(contents))
            image.verify()
        except Exception as e:
            raise AvatarError("Некорректное изображение")

    async def delete_avatar(self, avatar_path: str) -> None:
        if os.path.exists(avatar_path):
            os.remove(avatar_path)
