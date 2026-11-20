# 0013: Privacy by default

- Status: accepted
- Date: 2026-11-20

## Context

Most visitors are expected from the EU (GDPR); the editor is in Austria.
Every request a page makes to a third party (fonts, video, analytics, map
tiles) transfers the visitor's IP address and usually needs consent and a
cookie banner. We want neither the legal risk nor the banner.

## Decision

- **No third-party requests from the browser by default.** Fonts, scripts,
  styles and map tiles are served from our own server.
- **Fonts self-hosted** as woff2 (no Google Fonts CDN); licences noted in
  `design/README.md` or next to the font files.
- **YouTube** only via `youtube-nocookie.com`, and only after the visitor
  clicks a placeholder that says the video is loaded from YouTube (two-click
  embed). The placeholder shows a locally stored thumbnail or a neutral
  graphic, not one hot-linked from YouTube.
- **No analytics** in version 1.
- **No third-party scripts without an ADR.**
- Newsletter: explicit consent text and double opt-in; consent and
  confirmation timestamps are stored.
- Submitter email addresses (events, projects) are never shown publicly.

## Consequences

- No cookie banner needed in version 1 (only the session/CSRF cookies that
  are strictly necessary).
- Slightly more work: fonts, scripts and tiles have to be vendored and kept
  up to date by us.
- A Content-Security-Policy that only allows our own origin (plus
  `youtube-nocookie.com` frames) becomes possible and should be added with
  the design foundation.
- Without analytics, success (brief: people refer to Rooterium) has to be
  judged by other means for now.
