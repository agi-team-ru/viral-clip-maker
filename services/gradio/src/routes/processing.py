import logging
from typing import List, Optional
import gradio as gr
from time import sleep

from core import AbstractPage, Processor, UserState, ProcessingState
from constants import PageName
from processors import (
    annotator,
    editor,
    cropper,
    estimator,
    speech_recognizer,
    scene_recognizer,
    validator,
    subtitler,
    hashtagger,
    music,
)
from components import create_spinner

logger = logging.getLogger(__name__)


class Page(AbstractPage):
    name = PageName.PROCESSING

    def render(self, state: UserState):
        # NOTE: do not define globally to avoid unexpected caching on dev hot-reload
        processors_pipe = [
            ("Распознание речи", speech_recognizer.process),
            # ("Распознание сцен", scene_recognizer.process),
            ("Валидация", validator.process),
            ("Аннотация", annotator.process),
            ("Нарезка клипов", editor.process),
            ("Кадрирование", cropper.process),
            ("Наложение субтитров", subtitler.process),
            ("Подбор хештегов", hashtagger.process),
            # ("Наложение музыки", music.process),
            ("Оценка", estimator.process),
        ]

        create_spinner()
        # gr.Markdown("## Processings")
        gr_step_idx = gr.State(0)
        checkboxes = []
        errors: List[Optional[str]] = []
        checkbox_labels: List[str] = []
        num_steps = len(processors_pipe)
        processor_funcs: List[Processor] = []
        for title, processor_fn in processors_pipe:
            checkbox_labels.append(title)
            step_checkbox = gr.Checkbox(False, label=title, interactive=False)
            checkboxes.append(step_checkbox)
            errors.append(None)
            processor_funcs.append(processor_fn)

        cancel_btn = gr.Button("Отмена", variant="stop")
        self.router.attach_go(cancel_btn.click, PageName.CONFIGURE)

        step_timer = gr.Timer(0.1, active=True)
        next_page_timer = gr.Timer(0.1, active=False)

        processing_state = ProcessingState()
        processing_state.source_video_path = state.src_video
        if state.user_preferences:
            processing_state.user_preferences = state.user_preferences
        else:
            logger.error("UserPreferences are not defined")

        def on_timer(step_idx):
            nonlocal processing_state
            done = step_idx >= num_steps
            if not done:
                logger.info(f"Step '{processors_pipe[step_idx][0]}': started")
                try:
                    processing_state = processor_funcs[step_idx](processing_state)
                except Exception as ex:
                    errors[step_idx] = str(ex)
                logger.info(f"Step '{processors_pipe[step_idx][0]}': done")
                # print("progress_state", progress_state)
                sleep(0.1)
            checkbox_values = []
            for i in range(num_steps):
                label = checkbox_labels[i]
                value = i < step_idx
                if errors[i]:
                    label += f": произошла ошибка ({errors[i]})"
                elif value:
                    label += ": готово"

                checkbox_values.append(gr.Checkbox(value=value, label=label))

            has_errors = any(errors)

            return [
                gr.Timer(active=not done and not has_errors),
                gr.Timer(active=done and not has_errors),
                step_idx + 1,
            ] + checkbox_values

        step_timer.tick(
            on_timer,
            inputs=[gr_step_idx],
            outputs=[step_timer, next_page_timer, gr_step_idx] + checkboxes,
        )

        def on_next_page(user_state: UserState):
            if not processing_state.result:
                logger.warning("No result provided")
            else:
                user_state.result = processing_state.result
            return [gr.Timer(active=False), user_state]

        next_page_timer.tick(
            on_next_page,
            inputs=[self.ctx.gr_state],
            outputs=[next_page_timer, self.ctx.gr_state],
        )

        self.router.attach_go(next_page_timer.tick, PageName.PREVIEW)
