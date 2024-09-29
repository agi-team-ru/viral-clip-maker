from enum import StrEnum


class PageName(StrEnum):
    UPLOAD = "UPLOAD"
    CONFIGURE = "CONFIGURE"
    PREVIEW = "PREVIEW"
    PROCESSING = "PROCESSING"


ASSETS_DIR = "./assets"
PUBLIC_ASSETS_DIR = ASSETS_DIR + "/public"
FAVICON_PATH = PUBLIC_ASSETS_DIR + "/favicon.png"
ICONS_PATH = PUBLIC_ASSETS_DIR + "/icons"
FONTS_DIR = ASSETS_DIR + "/fonts"
