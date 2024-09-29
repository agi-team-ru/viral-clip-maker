from functools import partial

import logging
import os
from typing import Dict, List
import gradio as gr

from core import DEV_MODE, AbstractPage, Context, Router, UserState, make_public_uri
from routes import upload, configure, preview, processing
from constants import FAVICON_PATH, ICONS_PATH, PUBLIC_ASSETS_DIR, PageName
from utils import read_file

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "WARNING").upper())

logger = logging.getLogger(__name__)

app_title = "Viral Clip Maker"
css = read_file("./assets/style.css")
header_html = read_file("./assets/header.html").format(
    app_title=app_title,
    logo_url=make_public_uri(FAVICON_PATH),
    spinner_url=make_public_uri(f"{ICONS_PATH}/spinner.png"),
)
page_classes = [package.Page for package in [upload, configure, preview, processing]]

gr.set_static_paths(paths=[PUBLIC_ASSETS_DIR])

with gr.Blocks(
    theme=gr.themes.Soft(), css=css, title=app_title, analytics_enabled=False
) as demo:
    gr_current_page = gr.State(value=PageName.UPLOAD)
    # gr_current_page = gr.State(value=PageName.CONFIGURE)
    # gr_current_page = gr.State(value=PageName.PROCESSING)
    # gr_current_page = gr.State(value=PageName.PREVIEW)
    gr_state = gr.State(UserState())

    render_triggers = [gr_current_page.change, demo.load]
    if DEV_MODE:
        gr.HTML("<div class='dev-mode-banner'>Dev Mode Enabled</div>")
        hr_starter = gr.Timer(0.1)
        render_triggers.append(hr_starter.tick)
        hr_starter.tick(lambda: gr.Timer(active=False), outputs=[hr_starter])

    gr.HTML(header_html)

    ctx = Context(gr_current_page=gr_current_page, gr_state=gr_state)
    router = Router(ctx)
    pages: Dict[str, AbstractPage] = {
        str(clazz.name): clazz() for clazz in page_classes
    }
    for page in pages.values():
        page.ctx = ctx
        page.router = router

    @gr.render(inputs=[gr_current_page, gr_state], triggers=render_triggers)
    def route(page_name: str, app_state: UserState):
        pages[str(page_name)].render(app_state)


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        show_api=False,
        favicon_path=FAVICON_PATH,
        # allowed_paths=[PUBLIC_ASSETS_DIR],
    )
