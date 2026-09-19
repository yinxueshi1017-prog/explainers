# Deploying this site

Four static files, no build step. Any static host works. The two options below are free
and neither needs a card.

## Option A — Cloudflare Pages (recommended, no git required)

1. Sign in at dash.cloudflare.com → **Workers & Pages** → **Create** → **Pages** →
   **Upload assets**.
2. Drag this `site/` folder in. Name the project (e.g. `explainers`).
3. It publishes to `<project>.pages.dev` in about a minute.

Why this one: drag-and-drop, no repo, no toolchain, and a custom domain is one field
later if you want one.

## Option B — GitHub Pages

```bash
cd site
git init && git add -A && git commit -m "Interactive explainers"
gh repo create <name> --public --source=. --push
```

Then in the repo: **Settings → Pages → Source: deploy from branch → main / (root)**.
Publishes to `<user>.github.io/<name>`.

## A custom domain, later

Not needed to launch. `*.pages.dev` is fine for a first send. When it earns one, point
the domain at the host in that host's dashboard — DNS is the only step.

---

## What has to stay true

- **No build step.** Files are served exactly as they are. Do not add a bundler.
- **`hydrogen-embrittlement.html` makes zero network requests.** Verified: the only
  request when loading it is the document itself. If a future edit adds a font, a CDN
  script, or an analytics tag, the claim printed on the page becomes false — either
  remove the request or remove the claim.
- **Relative links only.** The pages link to each other by filename. Do not reintroduce
  absolute `claude.ai/code/artifact/...` URLs — those point at old builds, including one
  that still contains the torque mark.
- **`water-hammer.html` runs its own physics checks on load** and warns to the console if
  they fail. `#dev` prints them on the page; `#reduce` forces the reduced-motion path.
  If a future edit breaks the model, the page will tell you — check the console after
  changing it.
- **Every page carries its own "what is not verified" section.** The index says each page
  does. Keep that true: if you add a piece, it needs one before it goes up.
- **Every page carries a contact.** The whole revenue path is someone reading a piece and
  emailing you; a page without a way to reply is a dead end.
- **The site is pinned dark.** No page follows `prefers-color-scheme` any more. The
  hydrogen piece is a dark instrument panel by brief and does not invert, so the pages
  around it must not either. Each page keeps a light palette under `@media print`, because
  print dialogs drop CSS backgrounds and would otherwise leave pale ink on white paper.
  If you add a page: dark by default, light for print, no OS-preference branch.

## Fonts

`the-bolt-that-was-fine.html` used to pull IBM Plex from `fonts.googleapis.com` — three
external requests on a page that argues for making none. The five faces the page actually
sets are now embedded as base64 woff2 (latin subsets): Sans Condensed 600/700, Sans 400,
Mono 400/500. The page costs ~88 KB more and asks nothing of a third party.

IBM Plex is (c) 2017 IBM Corp under the SIL Open Font License 1.1. `LICENSE-IBM-Plex.txt`
ships beside the pages because the OFL requires the licence to travel with the fonts —
**do not delete it.**

If you ever add a weight to that page, embed the matching face too. A weight with no face
is silently faux-bolded by the browser, which looks wrong at headline sizes and gives no
error.

## No external requests anywhere

Verified on the live origin: every page loads zero off-origin resources. If you add
anything that fetches — a font, a script, an analytics tag, an embedded video — either
remove it or remove the claim from the pages, because the claim is printed on them.
