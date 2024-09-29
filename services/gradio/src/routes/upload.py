import logging
import gradio as gr
import os

from core import AbstractPage, UserState
from constants import PageName

logger = logging.getLogger(__name__)


def after_upload(video: str, state: UserState, data: gr.EventData):
    print("data", data.__dict__)
    state.src_video = video
    if video:
        state.video_name = os.path.basename(video)
    logger.info(f"Video {video} uploaded")
    return state


class Page(AbstractPage):
    name = PageName.UPLOAD

    def render(self, state: UserState):
        url_input = gr.Textbox(
            placeholder="Ссылка на видео (Yandex Disk, Google Drive, YouTube)",
            show_label=False,
            max_lines=1,
        )

        @url_input.change(trigger_mode="once")
        def not_working():
            raise gr.Error("Загрузка по ссылке в данный момент недоступна")

        video_input = gr.Video(show_label=False)

        upload_btn = gr.Button("Загрузить", variant="primary")

        evt = upload_btn.click(
            fn=after_upload,
            inputs=[video_input, self.ctx.gr_state],
            outputs=[self.ctx.gr_state],
        )

        self.router.attach_go(evt.then, PageName.CONFIGURE)

        # EventListenerCallable
        # b.click(on_click, inputs=self.ctx.gr_page_name, outputs=self.ctx.gr_page_name)
