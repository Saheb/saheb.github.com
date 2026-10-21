#!/usr/bin/env python3
"""Render CV variants from shared content and explicit page selections."""

import html
import json
import re
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "cv"


def render_bullet(bullet, expanded_details=()):
    text = bullet["html"]
    for key, detail in bullet.get("details", {}).items():
        selected = "expanded_html" if key in expanded_details else "brief_html"
        text = text.replace("{{" + key + "}}", detail[selected])
    return text


def render_entry(ref, content):
    entry = content["entries"][ref["entry"]]
    lines = ["                <article>"]
    heading = entry["heading_html"]
    if ref.get("heading_variant"):
        heading = entry["heading_variants_html"][ref["heading_variant"]]
    lines.extend("                    " + line for line in heading.splitlines())
    if ref.get("show_context"):
        lines.append('                    <p class="entry-links">' + entry["context_html"] + "</p>")
    if entry.get("links_html"):
        lines.append("                    " + entry["links_html"])
    bullets = {bullet["id"]: bullet for bullet in entry["bullets"]}
    lines.append("                    <ul>")
    for bullet_id in ref["bullets"]:
        bullet = bullets[bullet_id]
        text = render_bullet(bullet, ref.get("expanded_details", []))
        lines.append("                        <li>" + text + "</li>")
    lines.extend(["                    </ul>", "                </article>"])
    return "\n".join(lines)


def render_section(section, content, profile):
    section_id = html.escape(section["id"], quote=True)
    css_class = ' class="compact"' if section.get("compact") else ""
    lines = [f'            <section{css_class} aria-labelledby="{section_id}">']
    lines.append(f'                <h2 id="{section_id}">{html.escape(section["title"])}</h2>')
    if section.get("context"):
        lines.append('                <p class="section-context">' + content["contexts"][section["context"]] + "</p>")
    for ref in section.get("entries", []):
        lines.append(render_entry(ref, content))
    if section.get("block"):
        block = content["blocks"][section["block"]]
        if block.get("wrapper"):
            lines.append(f'                <div class="{html.escape(block["wrapper"])}">')
        indent = "                    " if block.get("wrapper") else "                "
        if section["block"] == "skills" and not section.get("production_first"):
            lines.append(indent + profile["ml_skills_html"])
        paragraphs = block["paragraphs_html"]
        if section["block"] == "skills" and profile.get("production_skills_html"):
            paragraphs = [profile["production_skills_html"]]
        lines.extend(indent + p for p in paragraphs)
        if section["block"] == "skills" and section.get("production_first"):
            lines.append(indent + profile["ml_skills_html"])
        if block.get("wrapper"):
            lines.append("                </div>")
    if "project_links" in section:
        links = [content["project_links"][key] for key in section["project_links"]]
        lines.append("                <p>" + " &middot; ".join(links) + "</p>")
    if "project_bullets" in section:
        lines.append("                <ul>")
        for ref in section["project_bullets"]:
            entry = content["entries"][ref["entry"]]
            bullet = next(b for b in entry["bullets"] if b["id"] == ref["bullet"])
            link = content["project_links"][ref["entry"]]
            lines.append("                    <li><strong>" + link + ":</strong> " + render_bullet(bullet) + "</li>")
        lines.append("                </ul>")
    lines.append("            </section>")
    return "\n".join(lines)


def render_profile(profile, content, template, profiles, active, *, index=False):
    pages = []
    page_count = len(profile["pages"])
    for page_index, sections in enumerate(profile["pages"], start=1):
        page = ["        <div class=\"cv-page\">"]
        if page_index == 1:
            page.extend([
                "            <header>",
                f'                <h1>{html.escape(content["name"])}</h1>',
                f'                <p class="focus">{html.escape(profile["focus"])}</p>',
                "                " + content["contact_html"],
                f'                <p class="summary">{html.escape(profile["summary"])}</p>',
                "            </header>",
            ])
        else:
            page.append(f'            <div class="continuation"><strong>{html.escape(content["name"])}</strong><span>{html.escape(profile["focus"])}</span></div>')
        page.extend("\n" + render_section(section, content, profile) for section in sections)
        page.append(f'            <p class="page-number" aria-hidden="true">{page_index} / {page_count}</p>')
        page.append("        </div>")
        pages.append("\n".join(page))
    mode_links = []
    for key, mode in profiles.items():
        current = ' aria-current="page"' if key == active else ""
        mode_links.append(f'            <a href="{html.escape(mode["filename"], quote=True)}"{current}>{html.escape(mode["label"])}</a>')
    filename = "cv.html" if index else profile["filename"]
    return template.substitute(
        TITLE=html.escape(profile["title"]),
        DESCRIPTION=html.escape(profile["description"], quote=True),
        TOOLBAR=html.escape(profile["toolbar"]),
        ROBOTS="index,follow" if index else "noindex",
        CANONICAL_URL="https://saheb.github.io/" + filename,
        MODE_LINKS="\n".join(mode_links),
        BODY_CLASS=html.escape(profile.get("print_class", ""), quote=True),
        PAGES="\n\n".join(pages),
    )


def main():
    content = json.loads((DATA_DIR / "content.json").read_text())
    profiles = json.loads((DATA_DIR / "profiles.json").read_text())
    template = Template((DATA_DIR / "template.html").read_text())
    for profile in profiles.values():
        filename = profile["filename"]
        if not re.fullmatch(r"cv-[a-z-]+\.html", filename):
            raise ValueError(f"Invalid CV output filename: {filename}")
    for key, profile in profiles.items():
        filename = profile["filename"]
        (ROOT / filename).write_text(render_profile(profile, content, template, profiles, key))
        print(f"Built {filename}")
    (ROOT / "cv.html").write_text(render_profile(profiles["mle"], content, template, profiles, "mle", index=True))
    print("Built cv.html")


if __name__ == "__main__":
    main()
