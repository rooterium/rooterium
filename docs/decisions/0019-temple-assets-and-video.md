# 0019: Temple imagery: AI assets, originals and video delivery

- Status: accepted
- Date: 2026-11-26

## Context

The temple design (ADR 0017) is carried by AI-generated images and videos
from the editor's design package (Higgsfield: Soul Cinema for stills,
Kling 3.0 for video): 18 PNGs of 2048 px and three 720p clips, about 69 MB
of originals, linked on a third-party CDN that may expire. The site needs
web versions of them, the editor must be able to replace them, videos need
HTTP range requests (Safari will not play MP4 without them), and nothing
may be loaded from third parties (ADR 0013).

`docs/PROJECT_BRIEF.md`, section 6 says that AI images are "for atmosphere
only" and that "Armenian symbols and script are never AI-generated". The
temple images show khachkars, eternity signs and costumes as part of the
scenery, so the rule needs a precise reading.

## Decision

1. **AI imagery is atmosphere** (temple brief, section 3): portal,
   chapel, hall headers, transitions, category covers. It never
   illustrates or explains a real object, symbol, place or person inside
   an article; articles keep real, credited photos. The rule "Armenian
   symbols are never AI-generated" is read as: **no AI image is ever the
   depiction a visitor learns a symbol from**. A khachkar in a hall header
   is scenery; the article about khachkars shows a real photo. Armenian
   script is never AI-generated.
2. **Credit and disclosure**: AI images are stored with credit "AI
   illustration (Higgsfield, Soul Cinema)" (videos: "AI video (Higgsfield,
   Kling 3.0)") and licence "Rooterium, see Higgsfield terms". They are not
   captioned on the full-screen temple screens; the About page (editor)
   and `design/README.md` say that the temple imagery is AI-generated. Mood
   board 1 of the package (other people's photos and film stills) is never
   used on the site.
3. **Originals are not committed.** `design/temple/manifest.json`
   (committed) lists every approved asset: key, title, intended use,
   generator, source URL, size and SHA-256. Originals go to
   `design/temple/originals/` (git-ignored);
   `design/temple/build_temple_assets.py fetch` downloads missing ones and
   checks them against the manifest. A copy of the originals belongs in
   the shared storage of issue #12, since the CDN links may expire.
4. **Web versions are generated**, never edited by hand:
   `build_temple_assets.py build` writes to `design/temple/web/`
   (git-ignored):
   - images: WebP, quality 80, 1920 px and 960 px wide (never upscaled;
     the 3:4 images are 1536 px at most);
   - videos: H.264 High, 1280×720, no audio track, `+faststart`,
     **CRF 22 with `-tune grain`** (the brief suggested about CRF 26; that
     visibly smoothed the film grain the design depends on, and CRF 22
     still stays under the 3 MB per clip budget: 0.4, 2.2 and 1.4 MB);
     plus a poster (first frame) and a last-frame still per video, as WebP;
   - the film-grain texture: a 256 px seamless tile of generated noise
     (fixed seed, no AI), written to `core/static/core/img/grain.png` and
     committed like the favicons.
5. **Images are Wagtail images** (`images.CustomImage`), so the editor can
   replace them in the admin.
6. **Videos are Wagtail documents**: `mp4` is added to
   `WAGTAILDOCS_EXTENSIONS` and `WAGTAILDOCS_SERVE_METHOD = "direct"`, so
   document URLs point at `/media/documents/…`, which Caddy serves from
   the media volume with range requests and caching (`deploy/Caddyfile`);
   in development `core.dev_media` does the same (ADR 0015). The CSP needs
   no change (`default-src 'self'` covers `media-src`).
7. **Loading into a database**: a management command
   `load_temple_assets <folder>` creates or updates the images, documents
   and page fields from the web folder, with the same production safety
   flag as `load_example_content` (`--allow-production`). On the server the
   folder is first copied with `scp`. Nothing large goes into the Docker
   image.
8. **Rights** (A15): the images and videos are assumed usable on the
   public site under the editor's Higgsfield plan. The editor confirms this
   before the site is announced (#58).

## Consequences

- The design assets can be rebuilt and verified from the manifest as long
  as the CDN links work; after that, only from the shared copy.
- Direct serving means Wagtail's per-collection privacy for documents does
  not apply: every uploaded document (PDFs too) is public by its URL. That
  is acceptable because the site has no private documents; if it ever
  needs some, this decision is revisited.
- Videos and images live in the media volume and its backups (ADR 0008),
  about 8 MB of web versions for the current set.
- New hall images and descent videos for the other sections are added the
  same way: manifest entry, `fetch --record`, `build`, `load_temple_assets`
  or an upload in the admin.
