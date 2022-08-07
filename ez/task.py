import logging
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Literal, Optional

from PIL import Image, ImageDraw, ImageFont
from playwright.async_api import Playwright, ViewportSize
from pydantic import BaseModel, HttpUrl

from ez.config import get_settings
from ez.context import Browsers


class Task(BaseModel):
    browser: Literal["chromium", "firefox", "webkit"] = "chromium"
    color_scheme: Optional[Literal["dark", "light", "no-preference"]]
    device: str = ""
    locale: Optional[str] = None
    screen: Optional[ViewportSize]
    timezone_id: Optional[str]
    url: HttpUrl
    user_agent: Optional[str] = None
    viewport: Optional[ViewportSize]

    async def execute(self, browsers: Browsers, playwright: Playwright) -> bytes:
        logging.info("Executing task %s", self)
        image = await self.screenshot(browsers, playwright)
        return self.add_watermark(image) if get_settings().watermark else image

    async def screenshot(self, browsers: Browsers, playwright: Playwright) -> bytes:
        browser = browsers[self.browser]
        kwargs = self.get_config(playwright)

        page = await browser.new_page(**kwargs)
        await page.goto(self.url, timeout=10000)
        with NamedTemporaryFile(suffix=".png") as f:
            f.close()
            await page.screenshot(path=f.name)
            return Path(f.name).read_bytes()

    def get_config(self, playwright: Playwright) -> dict[str, Any]:
        custom_kwargs = dict(
            viewport=self.viewport,
            screen=self.screen,
            user_agent=self.user_agent,
            locale=self.locale,
            color_scheme=self.color_scheme,
            timezone_id=self.timezone_id,
        )

        filtered = {k: v for k, v in custom_kwargs.items() if v}

        device = playwright.devices.get(self.device, {})

        return device | filtered

    def add_watermark(self, image: bytes) -> bytes:
        watermark_image = Image.open(BytesIO(image))
        _, y = watermark_image.size
        draw = ImageDraw.Draw(watermark_image)
        font = ImageFont.truetype("arial.ttf", size=50)
        draw.text((10, y - 100), "Powered By EZ Screenshot", (200, 200, 200), font=font)
        temp = BytesIO()
        watermark_image.save(temp, format="PNG")
        temp.seek(0)
        return temp.read()
