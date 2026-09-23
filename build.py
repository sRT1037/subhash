#!/usr/bin/env python3
"""
Tiny static-site builder. No dependencies.

Edit the shared shell in src/layout.html and the per-page content in
src/pages/*.html, then run `python3 build.py`. It stamps every page
into the matching *.html file under docs/ -- that's the folder GitHub
Pages is configured to serve (Settings -> Pages -> Source: main /docs),
so commit the regenerated docs/*.html too.

All links in layout.html and page content use root-relative paths
(e.g. "/style.css", "/cv.html") rather than same-directory-relative
ones, so nested pages (e.g. ai-ml/some-post.html) still resolve
correctly regardless of how deep they are.
"""
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
OUT = ROOT / "docs"

SITE_NAME = "Subhash Ram Tallapaneni"

# GitHub Pages serves this repo at /subhash/, not the domain root (the
# repo is named "subhash" rather than "sRT1037.github.io" -- keep in
# sync with wherever this actually deploys). Every absolute path in
# the templates/pages is written as "{{BASE}}/..." and resolved here,
# so moving the site later is a one-line change.
BASE = "/subhash"

# (slug, nav label) -- order here is the order in the masthead nav
# (desktop). slug is the path relative to both src/pages/ and docs/.
NAV = [
    ("projects.html", "Projects"),
    ("ai-ml/index.html", "AI/ML"),
    ("cv.html", "CV"),
]

# On mobile, CV stays inline/visible by default (like Yann's own
# masthead keeps its first nav item visible); everything else
# collapses behind a hamburger button into a dropdown, echoing his
# real .greedy-nav/.hidden-links mechanism -- fixed rather than his
# width-measuring JS version, since that's real complexity for
# marginal benefit here.
NAV_MOBILE_VISIBLE = "cv.html"

# (slug, title, category) -- every post that shows up in the AI/ML
# section's side nav (Yann Dubois's ML Glossary style: on ai-ml/*
# pages this nav REPLACES the usual profile sidebar, same slot, same
# width -- it doesn't add a third column). Add a post here and it's
# built + shows up in the nav; no other registration needed.
AIML_POSTS = [
    ("ai-ml/llm-software-dev.html", "How LLMs Could Reshape Software Development", "AI"),
    ("ai-ml/understanding-ai.html", "My Initial Thoughts on AI", "AI"),
    ("ai-ml/multiagent-multi-team.html", "Multiagent Multi-Team", "AI"),
    ("ai-ml/ai-vs-humanity.html", "Artificial Intelligence vs Humanity", "AI"),
    ("ai-ml/consciousness-of-ai.html", "Consciousness of AI", "AI"),
    ("ai-ml/brain-vs-llm.html", "Brain vs LLM", "AI"),
    ("ai-ml/agent-survival.html", "Why Agents Try to Survive by Bypassing Instructions", "AI"),
]
AIML_CATEGORIES = ["AI", "ML"]  # order to render categories in the nav

# (slug, <title> text) -- every page that should be built.
# Pages not listed in NAV (e.g. research.html) are still built, just
# not linked from the masthead -- same as a sub-page reached via a link.
PAGES = [
    ("index.html", SITE_NAME),
    ("projects.html", "Projects"),
    ("ai-ml/index.html", "AI/ML"),
    ("cv.html", "CV"),
    ("research.html", "Undergraduate Research"),
] + [(slug, title) for slug, title, _cat in AIML_POSTS]

# (old slug, new slug) -- old URLs that must keep working (e.g. printed
# on a resume that can't be reprinted) get a tiny meta-refresh page
# that instantly forwards to the new location.
REDIRECTS = [
    ("ai.html", "ai-ml/index.html"),
]


def aiml_sidebar_html(current_slug):
    by_cat = {cat: [] for cat in AIML_CATEGORIES}
    for slug, title, cat in AIML_POSTS:
        by_cat[cat].append((slug, title))

    parts = ['      <div class="glossary-title">AI / ML</div>']
    for cat in AIML_CATEGORIES:
        parts.append(f'      <div class="glossary-cat">{cat}</div>')
        items = by_cat[cat]
        if not items:
            parts.append('      <ul class="glossary-empty"><li><i>Coming soon</i></li></ul>')
            continue
        parts.append("      <ul>")
        for slug, title in items:
            active = ' class="active"' if slug == current_slug else ""
            parts.append(f'        <li><a href="{BASE}/{slug}"{active}>{title}</a></li>')
        parts.append("      </ul>")
    return "\n".join(parts)


def build():
    layout = (SRC / "layout.html").read_text()
    profile_sidebar = (SRC / "sidebar.html").read_text()

    for slug, title in PAGES:
        content = (SRC / "pages" / slug).read_text()
        sidebar = aiml_sidebar_html(slug) if slug.startswith("ai-ml/") else profile_sidebar

        def nav_link(href, label):
            active = ' class="active"' if href == slug else ""
            return f'<a href="{BASE}/{href}"{active}>{label}</a>'

        desktop_links = "\n          ".join(nav_link(h, l) for h, l in NAV)
        visible = [(h, l) for h, l in NAV if h == NAV_MOBILE_VISIBLE]
        collapsed = [(h, l) for h, l in NAV if h != NAV_MOBILE_VISIBLE]
        mobile_visible_links = "\n          ".join(nav_link(h, l) for h, l in visible)
        mobile_collapsed_links = "\n            ".join(nav_link(h, l) for h, l in collapsed)

        nav_html = f"""        <span class="nav-desktop">
          {desktop_links}
        </span>
        <span class="nav-mobile">
          {mobile_visible_links}
          <div class="nav-dropdown-wrapper">
            <button class="nav-toggle" type="button" onclick="this.parentElement.classList.toggle('open')" aria-label="Menu">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
            </button>
            <div class="nav-dropdown">
              {mobile_collapsed_links}
            </div>
          </div>
        </span>"""

        page_title = title if slug == "index.html" else f"{title} &mdash; {SITE_NAME}"

        html = (
            layout.replace("{{TITLE}}", page_title)
            .replace("{{NAV}}", nav_html)
            .replace("{{SIDEBAR}}", sidebar)
            .replace("{{CONTENT}}", content)
            .replace("{{BASE}}", BASE)
        )
        out_path = OUT / slug
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html)
        print(f"built {slug}")

    for old_slug, new_slug in REDIRECTS:
        target = f"{BASE}/{new_slug}"
        redirect_html = (
            "<!DOCTYPE html>\n"
            '<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
            f'<meta http-equiv="refresh" content="0; url={target}">\n'
            f'<link rel="canonical" href="{target}">\n'
            "<title>Redirecting&hellip;</title>\n</head>\n<body>\n"
            f'<p>This page has moved -- redirecting to <a href="{target}">{target}</a>.</p>\n'
            "</body>\n</html>\n"
        )
        out_path = OUT / old_slug
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(redirect_html)
        print(f"redirect {old_slug} -> {new_slug}")


if __name__ == "__main__":
    build()
