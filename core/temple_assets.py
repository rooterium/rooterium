"""Which temple asset goes where (ADR 0019, temple brief A11).

File names are those written by `design/temple/build_temple_assets.py
build` into `design/temple/web/`; `load_temple_assets <folder>` reads them
from that folder (or a copy of it on the server). The mapping lives in the
app, not in `design/`, because `design/` is not part of the Docker image.
"""

from core.themes import Theme

COLLECTION = "Temple"
LICENCE = "Rooterium, see Higgsfield terms"
CREDIT_STILL = "AI illustration (Higgsfield, Soul Cinema)"
CREDIT_VIDEO = "AI video (Higgsfield, Kling 3.0)"

# key: (file, title, alt text, credit). Alt texts describe what the AI
# image shows; the editor may refine them in the admin.
IMAGES = {
    "portal": (
        "img01-1920.webp",
        "Temple: portal",
        "An arched stone portal carved into a misty cliff, with a bare "
        "branch and a dried pomegranate in the foreground",
        CREDIT_STILL,
    ),
    # The last frame of the entrance video, so the chapel holds the exact
    # frame the video ends on.
    "chapel": (
        "vid-entrance-last.webp",
        "Temple: chapel",
        "A dark rock-cut chapel: a manuscript and a split pomegranate on a "
        "stone lectern, a woman in Armenian folk dress hiding her face, a "
        "shaft of light from the dome",
        CREDIT_VIDEO,
    ),
    "hall-music": (
        "img05-1920.webp",
        "Temple: Music hall",
        "An old duduk and a kamancha on a faded red carpet beside a candle, "
        "an old man seen from behind in the dark",
        CREDIT_STILL,
    ),
    "hall-symbols": (
        "hall-symbols-1920.webp",
        "Temple: Symbols hall",
        "A carved cross-stone standing alone in the dark, lit by a faint "
        "shaft of light from above",
        CREDIT_STILL,
    ),
    "hall-history": (
        "img08-1920.webp",
        "Temple: History hall",
        "Mount Ararat in the haze, seen through the broken window of a "
        "ruined fortress, with a rusted sword and a clay vessel on the ledge",
        CREDIT_STILL,
    ),
    "hall-artifacts": (
        "img09-1920.webp",
        "Temple: Artifacts hall",
        "Old objects crowded on the shelves of a dark storeroom, caught by "
        "a camera flash",
        CREDIT_STILL,
    ),
    "hall-people": (
        "img10-1920.webp",
        "Temple: Key people hall",
        "Figures in old Armenian clothing standing in a row, each face "
        "hidden behind a book, a pomegranate, a hand, a candle or a mirror",
        CREDIT_STILL,
    ),
    "hall-religion": (
        "img11-1920.webp",
        "Temple: Religion hall",
        "A double exposure: a sacred fire on a stone altar and the dark "
        "interior of a stone church with a cross-stone",
        CREDIT_STILL,
    ),
}

# key: (file, title)
VIDEOS = {
    "portal": ("vid-portal-loop.mp4", "Temple: portal loop"),
    "entrance": ("vid-entrance.mp4", "Temple: entrance"),
    "descent-symbols": ("vid-descent-symbols.mp4", "Temple: descent into Symbols"),
}

# Home page field: ("image" | "video", key)
HOME_FIELDS = {
    "portal_poster": ("image", "portal"),
    "portal_video": ("video", "portal"),
    "entrance_video": ("video", "entrance"),
    "chapel_image": ("image", "chapel"),
}

# Section: {section page field: (kind, key)}
SECTION_FIELDS = {
    Theme.MUSIC: {"hall_image": ("image", "hall-music")},
    Theme.SYMBOLS: {
        "hall_image": ("image", "hall-symbols"),
        "descent_video": ("video", "descent-symbols"),
    },
    Theme.HISTORY: {"hall_image": ("image", "hall-history")},
    Theme.ARTIFACTS: {"hall_image": ("image", "hall-artifacts")},
    Theme.PEOPLE: {"hall_image": ("image", "hall-people")},
    Theme.RELIGION: {"hall_image": ("image", "hall-religion")},
}
