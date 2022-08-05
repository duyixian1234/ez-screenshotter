import logging
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Literal, Optional, TypedDict

from fastapi import Depends, FastAPI
from fastapi.responses import StreamingResponse
from playwright.async_api import Browser, async_playwright
from pydantic import BaseModel, HttpUrl

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

class Browsers(TypedDict):
    chromium: Browser
    firefox: Browser
    webkit: Browser


class Task(BaseModel):
    url: HttpUrl
    browser: Literal["chromium", "firefox", "webkit"] = "chromium"
    device: Optional[str]
    viewport: Optional[tuple[int, int]]
    screen: Optional[tuple[int, int]]
    user_agent: Optional[str]
    locale: Optional[str]
    color_scheme: Optional[Literal["dark", "light", "no-preference"]]
    timezone_id: Optional[str]

    async def execute(self, browsers: Browsers, devices: dict[str, dict]):
        logging.info("Executing task %s", self)
        browser = browsers[self.browser]
        page = await browser.new_page(
            **(
                devices.get(self.device, {})
                | {
                    k: v
                    for k, v in dict(
                        viewport=self.viewport,
                        screen=self.screen,
                        user_agent=self.user_agent,
                        locale=self.locale,
                        color_scheme=self.color_scheme,
                        timezone_id=self.timezone_id,
                    ).items()
                    if v
                }
            )
        )
        await page.goto(self.url)
        with NamedTemporaryFile(suffix=".png") as f:
            await page.screenshot(path=f.name)
            return Path(f.name).read_bytes()


class Context:
    async def __call__(self):
        if "browsers" not in self.__dict__:
            await self.initialsize()
        return self.browsers, self.devices

    async def initialsize(self):
        self.context = async_playwright()
        self.p = await self.context.__aenter__()
        self.browsers = {
                "chromium": await self.p.chromium.launch(),
                "firefox": await self.p.firefox.launch(),
                "webkit": await self.p.webkit.launch(),
            }
        self.devices = self.p.devices
        logging.info("Initialized context")


context = Context()


app = FastAPI()


@app.post("/new")
async def new(task: Task, deps=Depends(context)):
    browsers, devices = deps
    return StreamingResponse(
        BytesIO(await task.execute(browsers, devices)), media_type="image/png"
    )
