"""Build index.html from site.json and the markdown case studies in projects/.

Usage:  python build.py
Needs:  pip install markdown
"""
import html
import json
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
site = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
md = markdown.Markdown(extensions=["tables"])


def render(text: str) -> str:
    md.reset()
    out = md.convert(text)
    return out.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")


def project_html(p: dict) -> str:
    text = (ROOT / p["file"]).read_text(encoding="utf-8")
    lines = text.splitlines()
    title = lines[0].lstrip("# ").strip()
    body = "\n".join(lines[1:])

    # Split on level-2 headings; the first chunk is the opening summary.
    parts = re.split(r"(?m)^## ", body)
    out = [render(parts[0])]
    for chunk in parts[1:]:
        heading, _, rest = chunk.partition("\n")
        inner = f"<h3>{html.escape(heading.strip())}</h3>\n{render(rest)}"
        if heading.strip().lower().startswith("what this can't show"):
            out.append(f'<aside class="limits">{inner}</aside>')
        else:
            out.append(f"<section>{inner}</section>")

    meta = (
        "<dl class=\"meta\">"
        f"<dt>Data</dt><dd>{html.escape(p['data'])}</dd>"
        f"<dt>Methods</dt><dd>{html.escape(p['methods'])}</dd>"
        f"<dt>Tools</dt><dd>{html.escape(p['tools'])}</dd>"
        "</dl>"
    )
    return (
        f'<article id="{p["slug"]}" class="project">'
        f"<h2>{html.escape(title)}</h2>{meta}{''.join(out)}</article>"
    )


def glance_rows() -> str:
    rows = []
    for p in site["projects"]:
        rows.append(
            "<tr>"
            f'<th scope="row"><a href="#{p["slug"]}">{html.escape(p["nav"])}</a></th>'
            f"<td>{html.escape(p['question'])}</td>"
            f"<td>{html.escape(p['result'])}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def header_links() -> str:
    links = []
    if site.get("github"):
        links.append(f'<a href="{html.escape(site["github"])}">GitHub</a>')
    if site.get("linkedin"):
        links.append(f'<a href="{html.escape(site["linkedin"])}">LinkedIn</a>')
    return "".join(links)


nav = "".join(
    f'<li><a href="#{p["slug"]}">{html.escape(p["nav"])}</a></li>' for p in site["projects"]
)
articles = "\n".join(project_html(p) for p in site["projects"])
name = html.escape(site["name"])

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name}: analytics portfolio</title>
<meta name="description" content="{html.escape(site['description'])}">
<link rel="icon" href="data:,">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@400;600;700;800&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;1,7..72,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to the projects</a>
<header class="bar">
  <div class="bar-inner">
    <span class="who">{name}</span>
    <span class="links">{header_links()}</span>
  </div>
</header>
<div class="layout">
  <nav class="side" aria-label="Projects">
    <ul>{nav}</ul>
  </nav>
  <main id="main">
    <section class="hero">
      <h1>{html.escape(site['title'])}.</h1>
      <p class="intro">{html.escape(site['intro'])}</p>
      <div class="table-wrap">
        <table class="glance">
          <thead><tr><th scope="col">Project</th><th scope="col">Question</th><th scope="col">Result</th></tr></thead>
          <tbody>
{glance_rows()}
          </tbody>
        </table>
      </div>
    </section>
{articles}
    <footer>
      <p>Every project has its write-up in <code>projects/</code> and the scripts that re-check its numbers in <code>scripts/</code>. Charts come from the original analysis notebooks.</p>
    </footer>
  </main>
</div>
</body>
</html>
"""
(ROOT / "index.html").write_text(page, encoding="utf-8")
print("Wrote index.html with", len(site["projects"]), "projects")
