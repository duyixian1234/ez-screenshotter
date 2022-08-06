import logging
from typing import TypedDict

from playwright.async_api import Browser, Playwright, async_playwright


class Browsers(TypedDict):
    chromium: Browser
    firefox: Browser
    webkit: Browser


class Context:
    async def __call__(self) -> tuple[Browsers, Playwright]:
        return self.browsers, self.playwright

    async def initialsize(self) -> None:
        self.context = async_playwright()
        self.playwright = await self.context.__aenter__()
        self.browsers: Browsers = {
            "chromium": await self.playwright.chromium.launch(),
            "firefox": await self.playwright.firefox.launch(),
            "webkit": await self.playwright.webkit.launch(),
        }
        logging.info("Initialized context")

    async def clear(self) -> None:
        await self.context.__aexit__()
