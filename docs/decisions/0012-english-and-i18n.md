# 0012: English first, translatable from day one

- Status: accepted
- Date: 2026-11-20

## Context

The template assumes a German-speaking Swiss site and German conversation
with the maintainer. Rooterium's audience is the worldwide Armenian diaspora;
the editor lives in Austria. English comes first; Armenian and Russian are
planned later, other languages depending on the audience.

## Decision

- **English everywhere:** conversation with the maintainer, status reports,
  `/start` summaries, docs, code, commit messages, admin labels and website
  content.
- Locale: `LANGUAGE_CODE = "en"`, `LANGUAGES = [("en", "English")]`,
  `TIME_ZONE = "Europe/Vienna"`. The template's Swiss spelling rule no longer
  applies.
- **Translatable from day one:** all user-facing strings use Django i18n
  (`{% translate %}`, `{% blocktranslate %}`, `gettext_lazy`); message files
  live in `locale/`. Wagtail localisation is prepared (models and templates
  do not prevent it) but not enabled in version 1. URL prefixes per language
  (`i18n_patterns`) are introduced together with the first translation, not
  earlier.
- Fonts and layouts must support **Armenian script** (Noto Serif Armenian /
  Noto Sans Armenian, see the brief).

## Consequences

- Adding a language later means translating message files and enabling
  Wagtail localisation, not rewriting templates.
- `og:locale` and `hreflang` tags are added when a second language exists.
- Slightly more ceremony in templates (`{% translate %}` everywhere).
