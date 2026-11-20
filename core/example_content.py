"""Example content for the test phase: real photos and checked facts.

Loaded by `python manage.py load_example_content`. It shows what the site
will look like with real content; the editor reviews, rewrites or deletes
every entry before the site is announced (issue #14).

Rules followed here (brief, section 6; CLAUDE.md):
- Photos only from Wikimedia Commons with a free licence (CC BY or
  CC BY-SA); author, licence and source page are stored with each image
  and shown under it. The command checks the licence again on download.
- Facts only as stated in the listed sources (Wikipedia, UNESCO); where
  the sources disagree, the text says so. No invented quotes, no book
  excerpts, no Armenian script.
- Events are real, recurring dates; projects are real organisations,
  described only with what their own site or Wikipedia states.
"""

import datetime
from decimal import Decimal

from core.themes import Theme
from projects.models import ProjectKind

# --- Images --------------------------------------------------------------
# key: (Commons file name, licence, author as named on Commons, alt text).
# The loader checks the licence again when it downloads from Commons.

IMAGES = {
    "garni": (
        "Templo de Garni, Armenia, 2016-10-02, DD 03.jpg",
        "CC BY-SA 4.0",
        "Diego Delso",
        "The Garni Temple, a Greco-Roman temple with Ionic columns on a high "
        "stone platform, under a blue sky",
    ),
    "geghard": (
        "Monasterio de Geghard, Armenia, 2016-10-02, DD 63.jpg",
        "CC BY-SA 4.0",
        "Diego Delso",
        "Geghard Monastery seen from above, its stone church and buildings "
        "set against the cliffs of a green valley",
    ),
    "geghard-valley": (
        "Geghard Monastery, Armenia.jpg",
        "CC BY 4.0",
        "Vyacheslav Argenberg",
        "Geghard Monastery among trees at the foot of rocky slopes in the "
        "upper Azat valley",
    ),
    "ararat": (
        "Mount Ararat and Khor Virap, Ararat Plain, Armenia.jpg",
        "CC BY 4.0",
        "Vyacheslav Argenberg",
        "The snow-capped Mount Ararat rising above green fields, with the "
        "Khor Virap monastery on a hill on the right",
    ),
    "khachkar": (
        "Khachkar Byurakan1.jpg",
        "CC BY-SA 4.0",
        "Armenak Margarian",
        "A tall carved cross-stone set into a wall of red stone blocks next "
        "to a doorway",
    ),
    "noratus": (
        "2014 Prowincja Gegharkunik, Cmentarz Noratus (19).jpg",
        "CC BY-SA 4.0",
        "Marcin Konsek",
        "Two old cross-stones covered in orange lichen lying in the grass of "
        "the Noratus cemetery",
    ),
    "eternity-sign": (
        "Armenian eternity sign, Noravank.jpg",
        "CC BY-SA 4.0",
        "Yerevantsi",
        "A round, swirling eternity sign carved in light stone on a wall at "
        "Noravank monastery",
    ),
    "duduk-ensemble": (
        "05 Duduk rehearsal in Horovel ensemble, Yerevan, Armenia.jpg",
        "CC BY-SA 4.0",
        "Volare42",
        "Black-and-white photo of four musicians playing the duduk together "
        "at a rehearsal",
    ),
    "duduk-garni": (
        "Duduk player Garni (5211685832).jpg",
        "CC BY-SA 2.0",
        "Shaun Dunphy",
        "A man playing the duduk, standing against a stone wall",
    ),
    "gasparyan": (
        "Djivan Gasparyan 2009 (cropped).jpg",
        "CC BY 3.0",
        "Sebmarouani",
        "Djivan Gasparyan, an elderly man with white hair, playing the duduk on stage",
    ),
    "sevanavank": (
        "Armenia. Lake Sevan. Sevanavank P8230612 2350.jpg",
        "CC BY-SA 4.0",
        "Alexxx1979",
        "Sevanavank monastery on a dry, grassy hill above the blue water of Lake Sevan",
    ),
}

# --- Places --------------------------------------------------------------
# Coordinates from the Wikipedia articles listed in the stories' sources.

PLACES = [
    {
        "name": "Mount Ararat",
        "theme": Theme.SYMBOLS,
        "latitude": Decimal("39.701900"),
        "longitude": Decimal("44.298300"),
        "short_description": "The principal national symbol of Armenia, "
        "5,137 m high and visible from Yerevan. Today it lies in Turkey.",
    },
    {
        "name": "Khor Virap",
        "theme": Theme.HISTORY,
        "latitude": Decimal("39.878333"),
        "longitude": Decimal("44.576111"),
        "short_description": "The monastery above the pit where, by "
        "tradition, Gregory the Illuminator was imprisoned for 13 years.",
    },
    {
        "name": "Garni Temple",
        "theme": Theme.HISTORY,
        "latitude": Decimal("40.112421"),
        "longitude": Decimal("44.730277"),
        "short_description": "A colonnaded temple in the Ionic order above the "
        "Azat gorge, the best-known symbol of pre-Christian Armenia.",
    },
    {
        "name": "Geghard Monastery",
        "theme": Theme.MYTHS,
        "latitude": Decimal("40.140425"),
        "longitude": Decimal("44.818511"),
        "short_description": "A monastery partly carved out of the mountain, "
        "named after the holy spear once kept here. UNESCO World Heritage.",
    },
    {
        "name": "Noravank",
        "theme": Theme.SYMBOLS,
        "latitude": Decimal("39.684061"),
        "longitude": Decimal("45.232872"),
        "short_description": "A 13th-century monastery in a gorge of red "
        "cliffs, known for its two-storey church and its stone carvings.",
    },
    {
        "name": "Noratus Cemetery",
        "theme": Theme.TRADITIONS,
        "latitude": Decimal("40.373889"),
        "longitude": Decimal("45.181111"),
        "short_description": "The largest surviving field of medieval "
        "cross-stones (khachkars), near the shore of Lake Sevan.",
    },
    {
        "name": "Sevanavank",
        "theme": Theme.HISTORY,
        "latitude": Decimal("40.563917"),
        "longitude": Decimal("45.010808"),
        "short_description": "A monastery on a former island in Lake Sevan; "
        "it became a peninsula when the lake level fell by about 20 m.",
    },
    {
        "name": "Gyumri",
        "theme": Theme.TRADITIONS,
        "latitude": Decimal("40.789444"),
        "longitude": Decimal("43.847500"),
        "short_description": "Armenia's second-largest city, long known as a "
        "cultural hub; badly damaged in the 1988 Spitak earthquake.",
    },
]

# Names of the earlier placeholder places that this content replaces.
RENAMED_PLACES = {"Lake Sevan": "Sevanavank"}

THEME_INTROS = {
    Theme.HISTORY: "Kingdoms, temples and monasteries: how Armenia's past "
    "shaped the places you can still visit today.",
    Theme.TRADITIONS: "Crafts, feasts and customs that families carried "
    "from village to village and across the world.",
    Theme.MYTHS: "Legends and holy relics: the stories Armenians have told "
    "about their land for centuries.",
    Theme.SYMBOLS: "Ararat, the eternity sign and other signs that carry "
    "Armenian identity.",
    Theme.MUSIC: "From the duduk to sacred song: the sounds of Armenia.",
}

# --- Stories -------------------------------------------------------------
# Body blocks: ("paragraph", html), ("heading", text), ("image", key, caption).

WIKI = "https://en.wikipedia.org/wiki/"

STORIES = [
    {
        "title": "The monastery of the spear",
        "theme": Theme.MYTHS,
        "days_ago": 2,
        "hero": "geghard",
        "teaser": "Half church, half cave: Geghard is carved into the "
        "mountain, and its name comes from a spear that, by legend, "
        "wounded Jesus.",
        "places": ["Geghard Monastery", "Garni Temple"],
        "body": [
            (
                "paragraph",
                "<p>At the end of a road along the Azat river, the cliffs "
                "close in and a monastery appears that seems to grow out of "
                "the rock. Some of Geghard's churches are built of stone "
                "blocks; others are not built at all, but dug out of the "
                "mountain itself.</p>",
            ),
            ("heading", "A sacred spring in a cave"),
            (
                "paragraph",
                "<p>According to tradition, the monastery was founded in the "
                "4th century by Gregory the Illuminator, at a sacred spring "
                "inside a cave. That is why it was first called "
                "<em>Ayrivank</em>, “the Monastery of the Cave”. "
                "Its main chapel was built much later, in 1215.</p>",
            ),
            ("image", "geghard-valley", "Geghard in the upper Azat valley."),
            ("heading", "The spear"),
            (
                "paragraph",
                "<p>The name used today, Geghard or Geghardavank, means "
                "“the Monastery of the Spear”. It refers to the "
                "spear that, by legend, wounded Jesus at the Crucifixion and "
                "was brought to Armenia by the Apostle Jude, called Thaddeus "
                "here. The relic was kept at the monastery among many others; "
                "today it is shown in the treasury of Etchmiadzin.</p>",
            ),
            ("heading", "Visiting today"),
            (
                "paragraph",
                "<p>The monastery and the towering cliffs of the Azat gorge "
                "around it are listed together as a UNESCO World Heritage "
                "Site. Geghard is often visited on the same day as the Garni "
                "Temple, a short drive down the valley.</p>",
            ),
        ],
        "sources": [
            ("Geghard", WIKI + "Geghard", "Wikipedia"),
            (
                "Monastery of Geghard and the Upper Azat Valley",
                "https://whc.unesco.org/en/list/960",
                "UNESCO World Heritage Centre",
            ),
        ],
    },
    {
        "title": "The duduk, voice of apricot wood",
        "theme": Theme.MUSIC,
        "days_ago": 12,
        "hero": "duduk-ensemble",
        "teaser": "A small wooden pipe with a very large reed: why the sound "
        "of the duduk moves people far beyond Armenia.",
        "places": [],
        "body": [
            (
                "paragraph",
                "<p>If you have heard one Armenian instrument, it was "
                "probably the duduk. Its warm, slightly husky sound has "
                "found its way into film soundtracks, but its home is the "
                "music of Armenia.</p>",
            ),
            ("heading", "Made of apricot wood"),
            (
                "paragraph",
                "<p>The duduk is a double-reed woodwind instrument made of "
                "apricot wood. Its Armenian name <em>tsiranapogh</em> means "
                "“apricot-made wind instrument”. Compared with "
                "other double-reed instruments such as the oboe, its reed is "
                "very large for its size, and its sound is closer to the "
                "English horn.</p>",
            ),
            ("image", "duduk-garni", "A duduk player at Garni."),
            ("heading", "Always in pairs"),
            (
                "paragraph",
                "<p>The duduk is commonly played in pairs: one musician "
                "plays the melody while the second holds a steady drone, the "
                "<em>dum</em>. Together the two instruments sound richer than "
                "either alone. Related instruments are found throughout the "
                "Caucasus, the Balkans and the Middle East.</p>",
            ),
            ("heading", "The master of the duduk"),
            (
                "paragraph",
                "<p>Djivan Gasparyan (1928–2021) is known as the "
                "“Master of the duduk”. He was named People's "
                "Artist of the Armenian SSR in 1978 and was nominated for a "
                "Grammy Award in 2006.</p>",
            ),
            ("image", "gasparyan", "Djivan Gasparyan on stage in 2009."),
            (
                "paragraph",
                "<p>In 2005 UNESCO proclaimed the Armenian duduk and its "
                "music a Masterpiece of the Oral and Intangible Heritage of "
                "Humanity; it was inscribed on the Representative List in "
                "2008.</p>",
            ),
        ],
        "sources": [
            ("Duduk", WIKI + "Duduk", "Wikipedia"),
            (
                "Duduk and its music",
                "https://ich.unesco.org/en/RL/duduk-and-its-music-00092",
                "UNESCO Intangible Cultural Heritage",
            ),
            ("Djivan Gasparyan", WIKI + "Djivan_Gasparyan", "Wikipedia"),
        ],
    },
    {
        "title": "The eternity sign",
        "theme": Theme.SYMBOLS,
        "days_ago": 22,
        "hero": "eternity-sign",
        "teaser": "A wheel of curved rays that seems to turn: one of the "
        "oldest Armenian symbols, carved in stone and worn as jewellery.",
        "places": ["Noravank"],
        "body": [
            (
                "paragraph",
                "<p>Look closely at old Armenian churches and cross-stones, "
                "and you will often find it: a round sign of curved rays "
                "that all turn in the same direction, as if the stone were "
                "spinning.</p>",
            ),
            ("heading", "The sun cross"),
            (
                "paragraph",
                "<p>It is called the Armenian eternity sign, or "
                "<em>arevakhach</em>, “sun cross”. It is an "
                "ancient Armenian national symbol and a sign of Armenian "
                "identity, and one of the most common symbols in Armenian "
                "architecture.</p>",
            ),
            ("heading", "Carved in stone"),
            (
                "paragraph",
                "<p>The sign is carved on khachkars, the Armenian "
                "cross-stones, and on the walls of churches. The example "
                "in the photo is at Noravank, a 13th-century monastery in a "
                "gorge of brick-red cliffs near Yeghegnadzor.</p>",
            ),
            ("image", "khachkar", "A cross-stone set into a wall in Byurakan."),
            (
                "paragraph",
                "<p>Today the eternity sign also appears on jewellery, in "
                "logos and on monuments – a small symbol that many "
                "Armenians abroad carry with them.</p>",
            ),
        ],
        "sources": [
            ("Armenian eternity sign", WIKI + "Armenian_eternity_sign", "Wikipedia"),
            ("Noravank", WIKI + "Noravank", "Wikipedia"),
        ],
    },
    {
        "title": "A temple older than Christianity in Armenia",
        "theme": Theme.HISTORY,
        "days_ago": 32,
        "hero": "garni",
        "teaser": "Garni is the only largely preserved Hellenistic building "
        "in the former Soviet Union – and still a puzzle for "
        "historians.",
        "places": ["Garni Temple"],
        "body": [
            (
                "paragraph",
                "<p>About 30 km east of Yerevan, on the edge of the Azat "
                "gorge, stands a building that looks as if it had been "
                "carried here from Greece or Rome: a temple with Ionic "
                "columns on a high stone platform.</p>",
            ),
            ("heading", "Temple or tomb?"),
            (
                "paragraph",
                "<p>Garni is conventionally identified as a pagan temple to "
                "the sun god Mihr, built by King Tiridates I in the first "
                "century AD. A competing hypothesis sees it as a tomb from "
                "the second century. Either way, it is the best-known "
                "structure of pre-Christian Armenia and is considered an "
                "eastern outpost of the Greco-Roman world.</p>",
            ),
            ("heading", "Fallen and rebuilt"),
            (
                "paragraph",
                "<p>The temple collapsed in an earthquake in 1679, but many "
                "of its stones stayed on the site. After excavations in the "
                "20th century it was reconstructed between 1969 and 1975, "
                "putting the original pieces back in place.</p>",
            ),
            (
                "paragraph",
                "<p>Today Garni is one of the most visited places in Armenia, "
                "and the central shrine of Armenian neopaganism.</p>",
            ),
        ],
        "sources": [("Garni Temple", WIKI + "Garni_Temple", "Wikipedia")],
    },
    {
        "title": "Khachkars, crosses carved in stone",
        "theme": Theme.TRADITIONS,
        "days_ago": 42,
        "hero": "noratus",
        "teaser": "Memorial stones with a cross and endless ornaments: the "
        "khachkar is the signature of medieval Armenian art.",
        "places": ["Noratus Cemetery"],
        "body": [
            (
                "paragraph",
                "<p>A khachkar is a carved stele bearing a cross. The word "
                "combines <em>khach</em>, “cross”, and "
                "<em>kar</em>, “stone”. Around the cross the "
                "carvers added rosettes, interlace and plant motifs.</p>",
            ),
            ("image", "khachkar", "A khachkar in a church wall in Byurakan."),
            ("heading", "The largest field of cross-stones"),
            (
                "paragraph",
                "<p>The cemetery of Noratus, near Gavar and Lake Sevan, has "
                "the largest cluster of khachkars in Armenia. It is the "
                "largest surviving cemetery of its kind since the "
                "cross-stones of Old Julfa in Nakhichevan were destroyed.</p>",
            ),
            (
                "image",
                "sevanavank",
                "Lake Sevan, on whose western shore Noratus lies.",
            ),
            ("heading", "A living craft"),
            (
                "paragraph",
                "<p>Since 2010 the art of the khachkars, their symbolism and "
                "craftsmanship have been on UNESCO's list of Intangible "
                "Cultural Heritage – not only the old stones, but the "
                "skill of carving new ones.</p>",
            ),
        ],
        "sources": [
            ("Khachkar", WIKI + "Khachkar", "Wikipedia"),
            ("Noratus Cemetery", WIKI + "Noratus_Cemetery", "Wikipedia"),
            (
                "Armenian cross-stones art. Symbolism and craftsmanship of Khachkars",
                "https://ich.unesco.org/en/RL/armenian-cross-stones-art-"
                "symbolism-and-craftsmanship-of-khachkars-00434",
                "UNESCO Intangible Cultural Heritage",
            ),
        ],
    },
    {
        "title": "Ararat, the mountain on the horizon",
        "theme": Theme.SYMBOLS,
        "days_ago": 52,
        "hero": "ararat",
        "teaser": "Seen from Yerevan, out of reach across the border: why a "
        "mountain in Turkey is the principal symbol of Armenia.",
        "places": ["Mount Ararat", "Khor Virap"],
        "body": [
            (
                "paragraph",
                "<p>On a clear day, Mount Ararat fills the southern horizon "
                "of Yerevan. Greater Ararat rises to 5,137 m, Little Ararat "
                "to 3,896 m – a dormant volcano with two cones, about "
                "35 km wide at its base.</p>",
            ),
            ("heading", "A sacred mountain"),
            (
                "paragraph",
                "<p>Although it lies outside the borders of modern Armenia, "
                "in easternmost Turkey, the mountain is the principal "
                "national symbol of Armenia and has been considered sacred "
                "by Armenians. It is depicted on the coat of arms of Armenia, "
                "together with Noah's Ark. Armenians also call it "
                "<em>Masis</em>.</p>",
            ),
            ("heading", "The view from Khor Virap"),
            (
                "paragraph",
                "<p>The classic view of Ararat is from Khor Virap, a "
                "monastery on the Ararat Plain near the border. By "
                "tradition, Gregory the Illuminator was imprisoned here for "
                "13 years by King Tiridates III; he later became the king's "
                "religious mentor, and in 301 Armenia became the first "
                "country to declare itself Christian.</p>",
            ),
            (
                "paragraph",
                "<p>The first recorded ascent of the summit was made in 1829 "
                "by Friedrich Parrot, Khachatur Abovian and four others.</p>",
            ),
        ],
        "sources": [
            ("Mount Ararat", WIKI + "Mount_Ararat", "Wikipedia"),
            ("Khor Virap", WIKI + "Khor_Virap", "Wikipedia"),
        ],
    },
]

# --- Events and projects -------------------------------------------------
# Real, recurring dates; coordinates of the main place where it is held.

YEREVAN = (Decimal("40.181100"), Decimal("44.513600"))

EVENTS = [
    {
        "title": "Armenian Christmas",
        "start_date": datetime.date(2027, 1, 6),
        "city": "Yerevan",
        "country": "Armenia",
        "link": WIKI + "Christmas_in_Armenia",
        "coords": YEREVAN,
    },
    {
        "title": "Trndez – jumping over the fire",
        "start_date": datetime.date(2027, 2, 13),
        "city": "Yerevan",
        "country": "Armenia",
        "link": WIKI + "Trndez",
        "coords": None,
    },
    {
        "title": "Genocide Remembrance Day at Tsitsernakaberd",
        "start_date": datetime.date(2027, 4, 24),
        "city": "Yerevan",
        "country": "Armenia",
        "link": WIKI + "Tsitsernakaberd",
        "coords": (Decimal("40.185600"), Decimal("44.490600")),
    },
    {
        # 98 days after Easter (28 March 2027).
        "title": "Vardavar – the water festival",
        "start_date": datetime.date(2027, 7, 4),
        "city": "Yerevan",
        "country": "Armenia",
        "link": WIKI + "Vardavar",
        "coords": None,
    },
]

PROJECTS = [
    {
        "name": "TUMO Center for Creative Technologies",
        "kind": ProjectKind.INITIATIVE,
        "city": "Yerevan",
        "country": "Armenia",
        "link": "https://tumo.org/",
        "short_description": "Free after-school programme where teenagers "
        "learn design, programming, film and music.",
    },
    {
        "name": "Armenia Tree Project",
        "kind": ProjectKind.INITIATIVE,
        "city": "Yerevan",
        "country": "Armenia",
        "link": "https://www.armeniatree.org/",
        "short_description": "Non-profit founded in 1994 that has planted "
        "more than 8 million trees in communities across Armenia.",
    },
    {
        "name": "Picsart",
        "kind": ProjectKind.STARTUP,
        "city": "Yerevan",
        "country": "Armenia",
        "link": "https://picsart.com/",
        "short_description": "Photo and video editing platform that started "
        "in Armenia and is used by millions worldwide.",
    },
    {
        "name": "Komitas Museum-Institute",
        "kind": ProjectKind.MUSIC,
        "city": "Yerevan",
        "country": "Armenia",
        "link": "https://www.komitasmuseum.am/",
        "short_description": "Museum and research institute dedicated to "
        "Komitas, founder of the Armenian national school of music.",
    },
]

ABOUT_BODY = (
    "<p>Rooterium collects and connects Armenian history, traditions, myths, "
    "symbols and music – for Armenians all over the world, above all in "
    "the diaspora, and for anyone curious about their roots.</p>"
    "<h2>How it works</h2>"
    "<p>Every place on the map leads to a story. A new story is published "
    "about every ten days, with its sources listed at the end. Photos are "
    "credited with their author and licence.</p>"
    "<h2>Who is behind it</h2>"
    "<p>[The editor introduces themselves here.]</p>"
    "<h2>Contact</h2>"
    "<p>[How to get in touch.]</p>"
)
