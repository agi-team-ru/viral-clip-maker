import gradio as gr

from core import (
    AbstractPage,
    UserPreferences,
    UserState,
    Language,
    AspectRatio,
    ClipTemplate,
)
from constants import PUBLIC_ASSETS_DIR, PageName

languages = [("Русский", Language.RU), ("Английский", Language.EN)]
durations = [
    ("Авто", (0, 0)),
    ("Короче 30 сек", (0, 30)),
    ("30 - 60 сек", (30, 60)),
    ("60 - 90 сек", (30, 60)),
    ("90 сек - 3 мин", (90, 180)),
]
aspect_ratios = [
    ("Вертикальное 9:16", AspectRatio.VERTICAL),
    ("Квадратное 1:1", AspectRatio.SQUARE),
    ("Горизонтальное 16:9", AspectRatio.HORIZONTAL),
]

templates = [
    (
        ClipTemplate.RECOMBINED,
        "Рекомбинация",
        f"{PUBLIC_ASSETS_DIR}/templates/recombined.jpg",
    ),
    (
        ClipTemplate.CROPPED,
        "Кадрирование",
        f"{PUBLIC_ASSETS_DIR}/templates/cropped.jpg",
    ),
    (
        ClipTemplate.EXTENDED,
        "Расширение",
        f"{PUBLIC_ASSETS_DIR}/templates/extended.jpg",
    ),
]


class Page(AbstractPage):
    name = PageName.CONFIGURE

    def render(self, state: UserState):
        with gr.Row():
            with gr.Column(scale=1):
                if state.src_video:
                    gr.Video(
                        show_label=False,
                        value=state.src_video,
                        show_download_button=False,
                        show_share_button=False,
                        # height=160,
                    )
                else:
                    gr.Markdown("*No video*")
            with gr.Column(scale=3):
                gr.Markdown(f"## {state.video_name}")
                language_input = gr.Dropdown(
                    label="Язык видео", choices=languages, value=Language.RU
                )

        gr.Markdown("## Продвинутые настройки клипов")

        with gr.Accordion(
            "С помощью расширенных настроек можно определить длину, соотношение, стиль и ключевые слова для идеальных результатов.",
            open=True,
        ):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Формат видео")

                    durations_input = gr.Radio(
                        label="Продолжительность роликов",
                        choices=[(label, i) for i, (label, _) in enumerate(durations)],
                        value=0,
                    )
                    aspect_ratio_input = gr.Radio(
                        label="Соотношение сторон",
                        choices=aspect_ratios,
                        value=AspectRatio.VERTICAL,
                    )

                    gr.Markdown("### Музыка")

                    music_input = gr.Audio(
                        show_label=False, show_download_button=False, autoplay=False
                    )

                    gr.Markdown("### Стиль")

                    use_emoji_input = gr.Checkbox(
                        label="Автоматическое добавление смайликов"
                    )

                    keyword_highlight_input = gr.Checkbox(
                        label="Подсветка ключевых слов"
                    )

                    gr.Markdown("### Дополнительные настройки")
                    keywords_input = gr.Textbox(
                        label="Уточнение темы ролика (опционально)",
                        placeholder="Ключевые слова, через запятую",
                        lines=3,
                    )

                with gr.Column():
                    gr.Markdown("### Шаблон видео")

                    template_input = gr.Textbox(ClipTemplate.RECOMBINED, visible=False)
                    tpl_checkboxes = []

                    for tpl_val, tpl_label, tpl_img in templates:
                        tpl_checkbox = gr.Checkbox(
                            # label=tpl_label, value=tpl_val == ClipTemplate.RECOMBINED
                            label=tpl_label,
                            value=False,
                            interactive=True,
                        )

                        tpl_checkboxes.append(tpl_checkbox)

                        def on_tpl_checkbox_change(
                            checked: bool, current_val: ClipTemplate, self_val=tpl_val
                        ):
                            return self_val if checked else current_val

                        tpl_checkbox.change(
                            on_tpl_checkbox_change,
                            inputs=[tpl_checkbox, template_input],
                            outputs=template_input,
                        )

                        gr.Image(
                            tpl_img,
                            show_label=False,
                            interactive=False,
                            show_download_button=False,
                            show_fullscreen_button=False,
                            height=240,
                        )

                    def on_template_input_change(
                        selected: ClipTemplate,
                    ):
                        # print("on_template_input_change ", selected)
                        return [
                            gr.Checkbox(value=tpl_val == selected)
                            for tpl_val, _, _ in templates
                        ]

                    template_input.change(
                        on_template_input_change,
                        inputs=template_input,
                        outputs=tpl_checkboxes,
                    )

        with gr.Row():
            with gr.Column(scale=1):
                back_btn = gr.Button("Назад", variant="stop")
                self.router.attach_go(back_btn.click, PageName.UPLOAD)
            with gr.Column(scale=5):
                generate_btn = gr.Button("Получить виральные клипы", variant="primary")

                def store_preferences(
                    state: UserState,
                    language: Language,
                    duration_idx: int,
                    aspect_ratio: AspectRatio,
                    use_emoji: bool,
                    keyword_highlight: bool,
                    keywords: str,
                    template: ClipTemplate,
                ):
                    user_preferences = UserPreferences()
                    user_preferences.language = language
                    user_preferences.aspect_ratio = aspect_ratio
                    user_preferences.duration = durations[duration_idx][1]
                    user_preferences.use_emoji = use_emoji
                    user_preferences.keyword_highlight = keyword_highlight
                    user_preferences.keywords = keywords
                    user_preferences.template = template

                    state.user_preferences = user_preferences
                    return state

                chain = generate_btn.click(
                    store_preferences,
                    inputs=[
                        self.ctx.gr_state,
                        language_input,
                        durations_input,
                        aspect_ratio_input,
                        use_emoji_input,
                        keyword_highlight_input,
                        keywords_input,
                        template_input,
                    ],
                    outputs=[self.ctx.gr_state],
                )

                self.router.attach_go(chain.then, PageName.PROCESSING)
