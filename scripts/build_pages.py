"""Build the public course site using Python's standard library, without network access."""

import json
from html import escape
from pathlib import Path
from string import Template
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "pages"
PORTAL = "https://semiconductor-chemistry-2182209.soorathep-k.chatgpt.site"
COURSE = "Chemistry for Semiconductor Engineering"
DRAFT = "teaching/2182209/2027-draft"   # the 2027 classes: the course front page
CLASSIC = "classic/"                      # the earlier lesson site, kept but not linked from the front page
MODULES = [
    ("foundations", "Foundations", 1, 5, "Atoms, bonding, chemical quantities, and solutions"),
    ("materials", "Materials and cells", 6, 8, "From charge carriers in Si to energy storage"),
    ("electrochemistry", "Electrochemistry", 9, 13, "Cell potentials, metal deposition, EDLCs, and stability"),
    ("review", "Integrated review", 14, 14, "Connect the concepts to prepare for the midterm"),
]


def template(name, **values):
    source = (TEMPLATES / name).read_text(encoding="utf-8")
    return Template(source).substitute(values)


def student_lessons():
    lessons = json.loads((ROOT / "content/course-data.json").read_text(encoding="utf-8"))
    if [item["number"] for item in lessons] != list(range(1, 15)):
        raise ValueError("Expected public lessons 1 through 14 in order.")
    return lessons


def layout(body, title, description, prefix, head=""):
    return template("layout.html", content=body, title=escape(title), description=escape(description),
                    root=prefix, head=head, portal=PORTAL)


def lesson_row(item):
    number = item["number"]
    padded = f"{number:02d}"
    title = escape(item["title_en"])
    description = escape(item["objectives"][0])
    link = f"lessons/{number}/"
    worksheet = f"downloads/worksheet-{padded}.pdf"
    return f'''<li class="lesson-row" data-search="{number} {padded} {title} {description}">
      <span class="lesson-number" aria-hidden="true">{padded}</span>
      <div class="lesson-description"><div class="lesson-meta">Class {number} · 90 min</div>
        <h4><a href="{link}">{title}</a></h4><p class="lesson-preview">{description}</p></div>
      <div class="lesson-actions"><a class="lesson-open" href="{link}">Open lesson ↗</a>
        <div><a href="{link}#demo">Demo</a> · <a href="{worksheet}" download aria-label="Download the Class {number} worksheet as a PDF">Worksheet <small>PDF ↓</small></a></div></div>
    </li>'''


def catalog(lessons):
    groups = []
    buttons = ['<button type="button" data-topic="all" aria-pressed="true">All <span>14</span></button>']
    for key, label, first, last, note in MODULES:
        buttons.append(f'<button type="button" data-topic="{key}" aria-pressed="false">{label}</button>')
        numbers = f"{first:02d}–{last:02d}" if first != last else f"{first:02d}"
        rows = "".join(lesson_row(entry) for entry in lessons[first - 1:last])
        groups.append(f'''<section class="lesson-group" data-topic="{key}" aria-labelledby="group-{key}">
          <div class="module-heading"><span class="module-range">{numbers}</span>
            <div><h3 id="group-{key}">{label}</h3><p>{note}</p></div></div>
          <ol class="lesson-list" start="{first}">{rows}</ol></section>''')
    return f'''<div class="catalog-tools" hidden>
      <div class="module-filters" role="group" aria-label="Filter lessons by topic">{"".join(buttons)}</div>
      <label class="search-field"><span class="sr-only">Search lessons</span>
        <input type="search" placeholder="Search, e.g. doping or batteries"></label></div>
      <p class="results-count" aria-live="polite">Showing 14 of 14 classes</p>
      <div class="lesson-groups">{"".join(groups)}</div>
      <div class="empty-state" hidden><h3>No matching lessons</h3><p>Try another topic or keyword, or show all categories.</p>
        <button type="button" class="button button-outline">Show all lessons</button></div>'''


def list_items(values):
    return "".join(f"<li>{escape(value)}</li>" for value in values)


def numbered_items(values, css="", zero_pad=False):
    items = []
    for index, value in enumerate(values, start=1):
        label = f"{index:02d}" if zero_pad else str(index)
        items.append(f'<li><span class="{css}" aria-hidden="true">{label}</span><p>{escape(value)}</p></li>')
    return "".join(items)


def source_link(url):
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError(f"Unexpected source URL: {url!r}")
    label = unquote(parsed.path.rstrip("/").split("/")[-1]).replace("-", " ") or "Reference"
    return (f'<li><a href="{escape(url)}" target="_blank" rel="noopener">{escape(parsed.hostname)} '
            f'<span class="reference-path">{escape(label)}</span> ↗</a></li>')


def adjacent(lessons, index, step):
    target = index + step
    backward = step < 0
    if 0 <= target < len(lessons):
        lesson = lessons[target]
        url = f'../{lesson["number"]}/'
        title = escape(lesson["title_en"])
        direction = "← Previous class" if backward else "Next class →"
    else:
        url, title = "../../#lessons", "All lessons"
        direction = "← Back to" if backward else "Review again →"
    css = "" if backward else "next-lesson"
    return f'<a class="{css}" href="{url}"><small>{direction}</small><strong>{title}</strong></a>'


def lesson_page(lessons, index):
    item = lessons[index]
    number = item["number"]
    padded = f"{number:02d}"
    demo = item["demo"]
    table = item["data_table"]
    cells = "".join("<tr>" + "".join(f"<td>{escape(str(v))}</td>" for v in row) + "</tr>" for row in table["rows"])
    page = template(
        "lesson.html", root="../../", number=number, padded=padded, title=escape(item["title_en"]),
        worksheet=f"../../downloads/worksheet-{padded}.pdf", dataset=f"../../datasets/class_{padded}_teaching_data.csv",
        demo=f"../../demo.html?lesson={number}", demo_title=escape(demo["title"]), steps=list_items(demo["steps"]),
        limitations=escape(demo["limitations"]), objectives=list_items(item["objectives"]),
        prerequisites=escape(item["prerequisites"]), concepts=numbered_items(item["concepts"], zero_pad=True),
        tasks=numbered_items(item["student_tasks"], "activity-number"), rows=cells,
        columns="".join(f'<th scope="col">{escape(str(h))}</th>' for h in table["headers"]),
        caption=escape(table["caption"]), sources="".join(map(source_link, item["source_urls"])),
        question=escape(item["exit_question"]), ticket=f"{PORTAL}/lessons/{number}#exit-ticket",
        feedback=f"{PORTAL}/lessons/{number}#teaching-feedback",
        previous=adjacent(lessons, index, -1), next=adjacent(lessons, index, 1),
    )
    return layout(page, f'Class {number} · {item["title_en"]}', item["objectives"][0], "../../")


def build():
    lessons = student_lessons()
    homepage = template("home.html", root="./", catalog=catalog(lessons))
    outputs = {
        "index.html": layout(homepage, COURSE, "Lessons, simulations, and activities for the first 14 classes.",
                             "./", '<script defer src="./catalog.js"></script>').encode(),
        "course.css": (TEMPLATES / "course.css").read_bytes(),
        "catalog.js": (TEMPLATES / "catalog.js").read_bytes(),
        ".nojekyll": b"",
    }
    assets = ["favicon.svg", "downloads/2182209-exit-ticket-slides.pdf", "downloads/2182209-exit-ticket-slides.pptx", "downloads/Course_Syllabus.docx", "downloads/Student_Workbook_Classes_01_14.docx"]
    for index in range(len(lessons)):
        num = lessons[index]["number"]
        outputs[f"lessons/{num}/index.html"] = lesson_page(lessons, index).encode()
        assets.append(f"qr/exit-ticket-{num:02d}.png")
        assets.extend([f"datasets/class_{num:02d}_teaching_data.csv", f"downloads/worksheet-{num:02d}.pdf"])
    for asset in assets:
        outputs[asset] = (ROOT / "public" / asset).read_bytes()

    # The simulations are self-contained. Only their form link needs the original first-party origin.
    source_demo = (ROOT / "public/demo.html").read_text(encoding="utf-8")
    template_link = 'href="/lessons/${n}#exit-ticket"'
    if source_demo.count(template_link) != 1:
        raise ValueError("Review the simulation's exit-ticket link before rebuilding.")
    outputs["demo.html"] = source_demo.replace(template_link, f'href="{PORTAL}/lessons/${{n}}#exit-ticket"').encode()

    # The earlier site moves under classic/ unchanged (all its links are relative). The front page
    # redirects to the 2027 classes, which are copied byte for byte as built in the course folder.
    outputs = {(name if name == ".nojekyll" else CLASSIC + name): payload for name, payload in outputs.items()}
    outputs["index.html"] = (TEMPLATES / "root-redirect.html").read_bytes()
    for path in sorted((ROOT / DRAFT).rglob("*")):
        if path.is_file():
            outputs[path.relative_to(ROOT).as_posix()] = path.read_bytes()

    destination = ROOT / "_site"
    if destination.is_symlink():
        raise ValueError("_site cannot be a symlink.")
    for old in destination.rglob("*"):
        if old.is_symlink() or (old.is_file() and old.relative_to(destination).as_posix() not in outputs):
            raise ValueError(f"Unexpected file in _site: {old.name}. Build into a clean output directory.")
    for name, payload in outputs.items():
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    print(f"Built {len(lessons)} lessons and {len(outputs)} public files in _site/.")


if __name__ == "__main__":
    build()
