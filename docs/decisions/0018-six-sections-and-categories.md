# 0018: Six sections and category pages

- Status: accepted
- Date: 2026-11-26

## Context

ADR 0014 fixed five themes (History, Traditions, Myths, Symbols, Music) as
a code list, one `ThemeIndexPage` per theme with stories directly below it.
The editor's design package
(`docs/handoff/design-package-2026-11-22.md`) has **six sections**, each a hall with a root symbol: Music (duduk), Symbols
(arevakhach), History (Ararat, fortress), Artifacts (griffin), Key people
(figure with a hidden face), Religion (from paganism to Christianity,
sacred fire). The Symbols section is split into eight categories, and the
package asks for content that can be extended without code changes:
"adding a symbol = adding a record; adding a category = a record with its
own cover", for all six sections.

## Decision

1. **The six sections**, in this order: `music` (Music), `symbols`
   (Symbols), `history` (History), `artifacts` (Artifacts), `people` (Key
   people), `religion` (Religion). They stay a fixed list in code
   (`core.themes.Theme`), as in ADR 0014: the sections are the temple's
   architecture, each with its own hall image and video, not something the
   editor adds casually. Traditions and Myths are dropped as sections
   (A2).
2. **Naming**: everything the editor and visitors see says **"section"**
   (admin labels, help texts, page type name, templates). The internal
   names `Theme`, `ThemeIndexPage` and the `theme` fields **stay**:
   renaming a Wagtail page model and its database fields means content
   type changes and a larger migration for no visible gain. Docstrings say
   "theme = section". A rename can follow later in its own PR.
3. **Section page** (`ThemeIndexPage`) gets optional fields: root symbol
   (short text), motto (one line), hall image, descent video (a Wagtail
   document, ADR 0019), cover image for the chapel list. Allowed children:
   category pages and stories.
4. **Category page** (new page type, child of a section page): title,
   intro, optional cover image; its order in the section is the page
   tree order. Children: stories. Generic for all six sections. The eight
   Symbols categories from the package (Eternity and the sun, Tree of
   life, Cross and khachkar, Pomegranate and grapes, Beasts and mythical
   creatures, Ararat, Letters, Knots and ornaments) are created by the
   seed and example-content commands, with the package's "what it covers"
   line as intro.
5. **Stories** (shown to visitors as "articles") may sit under a section
   page or a category page. A story's section is the **nearest
   `ThemeIndexPage` above it** in the tree; ADR 0014's "the theme is where
   the story sits" still holds. Symbol pages are ordinary stories (A13);
   there is no separate symbol model.
6. **Places** keep their `theme` field with the six new values.
7. **Data migration**: Myths → Religion, Traditions → History for every
   stored value (theme pages and places). The example content is then
   re-sorted explicitly as listed in `docs/TEMPLE_BRIEF.md`, section 5
   (e.g. "The eternity sign" → Symbols / Eternity and the sun), and
   `seed_demo` / `load_example_content` produce the same structure on a
   fresh database.

## Consequences

- Supersedes ADR 0014, points 3 and 4 (page tree and theme list); the rest
  of ADR 0014 stays valid.
- New categories and articles are pure content work in the admin; a new
  section is still a code change plus hall assets, which matches the
  design.
- Internal code says "theme" where the admin says "section"; the
  docstrings and `docs/data-model.md` keep the mapping visible.
- The map's theme filters change with the list (six sections instead of
  five themes).
