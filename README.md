# subhashram.dev source

Personal site, served via GitHub Pages (Settings -> Pages -> Source:
`main` / `/docs`). Plain static HTML/CSS, no build dependencies beyond
Python 3 (stdlib only).

## Structure

```
src/
  layout.html          shared shell: <head>, masthead nav, sidebar, footer
  pages/*.html          per-page content only (what goes inside <main>)
build.py                 stamps src/ into docs/*.html
docs/                     generated -- this is what GitHub Pages serves
  *.html                  do not hand-edit, these come from src/
  style.css
  assets/
    profile.jpg
    logos/*.png           institution/company logos used on the CV page
    writeups/*.pdf         long-form write-ups linked from ai.html
```

## Editing

1. Edit the shared header/sidebar/footer in `src/layout.html`, or a
   page's content in `src/pages/<name>.html`.
2. To add a page: create `src/pages/<name>.html`, add it to `PAGES` (and
   `NAV` if it should show up in the masthead) in `build.py`.
3. Run:
   ```
   python3 build.py
   ```
4. Commit both the `src/` changes and the regenerated `docs/*.html` files
   -- `docs/` is what's actually deployed.
