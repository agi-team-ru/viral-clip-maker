import logging
import gradio as gr

from core import AbstractPage, ResultVideo, Subtitles, TimecodedText, UserState
from constants import PageName
from common import convert_words_sentences

logger = logging.getLogger(__name__)


class Page(AbstractPage):
    name = PageName.PREVIEW

    def render(self, state: UserState):
        # state.result = result
        if not state.result:
            gr.Markdown("*No source video provided*")
            return

        for result_video in state.result:
            with gr.Row():
                with gr.Column():
                    if result_video.path:
                        gr.Video(
                            # label=f"Viral Score: {int(result_video.score*100+0.5)}%",
                            show_label=False,
                            value=result_video.path,
                            interactive=True,
                            show_download_button=True,
                            show_share_button=False,
                        )
                    else:
                        gr.Markdown("*No video*")
                with gr.Column():

                    sentences = convert_words_sentences(result_video.subtitles.words)

                    full_text = "\n\n".join(
                        [sentence.text for sentence in sentences[0:10]]
                    ).replace("  ", " ")
                    gr.Markdown(
                        f"""
## Почему мы выбрали этот фрагмент?

{result_video.explanation}
""",
                    )

                    if result_video.hashtags:
                        hashtags = " ".join(
                            [f"#{hashtag}" for hashtag in result_video.hashtags]
                        )
                        gr.Markdown(
                            f"""
## Хештеги

{hashtags}
""",
                        )

                    gr.Markdown(f"""## Транскрипция""")

                    gr.Markdown(
                        full_text,
                        sanitize_html=True,
                        elem_classes="scrollable-block",
                    )


# samples_dir = "/app/src/.tmp"
# subtitle_file = samples_dir + "/sample1.json"
# import json
# from utils import read_file
# subtitles_json = json.loads(read_file(subtitle_file))
# source_words = [
#     TimecodedText(text=word["text"], start=float(word["start"]), end=float(word["end"]))
#     for word in subtitles_json
# ]
# subtitles = Subtitles()
# subtitles.words = source_words
# result = [
#     ResultVideo(
#         path="",
#         subtitles=subtitles,
#         explanation="This is explaination " * 10,
#         score=1.2,
#         hashtags=["helloworld", "foobar"] * 5,
#     )
# ] * 4
