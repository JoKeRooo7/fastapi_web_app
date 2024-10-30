import asyncio
from PIL import Image
from settings import settings


async def add_watermark(image_path:str) -> None:
    asyncio
    base = await asyncio.to_thread(Image.open, image_path)
    watermark = await asyncio.to_thread(Image.open, settings.watermark_path)
    # 20% от основного изображения
    max_watermark_width = base.width * 0.2
    max_watermark_height = base.height * 0.2
    watermark.thumbnail((max_watermark_width, max_watermark_height), Image.LANCZOS)
    # Отступы 10 пикселей
    x = base.width - watermark.width - 10
    y = base.height - watermark.height - 10
    watermarked = Image.new("RGBA", base.size)
    watermarked.paste(base, (0, 0))
    watermarked.paste(watermark, (x, y), watermark)
    watermarked = watermarked.convert("RGB")
    await asyncio.to_thread(watermarked.save, image_path, "JPEG")

