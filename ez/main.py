import logging
from io import BytesIO

from fastapi import Depends, FastAPI
from fastapi.responses import StreamingResponse

from ez.context import Browsers, Context, Playwright
from ez.task import Task

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

context = Context()

app = FastAPI(on_startup=(context.initialsize,), on_shutdown=(context.clear,))


@app.post("/new")
async def new_screenshot(
    task: Task, deps: tuple[Browsers, Playwright] = Depends(context)
) -> StreamingResponse:
    browsers, playwright = deps
    return StreamingResponse(
        BytesIO(await task.execute(browsers, playwright)), media_type="image/png"
    )
