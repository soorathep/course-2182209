"""Check the staged GitHub Pages artifact offline, including its project URL prefix."""

import argparse
import csv
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from xml.etree import ElementTree
from zipfile import ZipFile

BASE = "https://soorathep.github.io/course-2182209/"
PORTAL = "https://semiconductor-chemistry-2182209.soorathep-k.chatgpt.site"
CLASSES = range(1, 15)
DOCS = ("downloads/Course_Syllabus.docx", "downloads/Student_Workbook_Classes_01_14.docx")


def workbook(number):
    return f"downloads/worksheet-{number:02}.pdf"


def dataset(number):
    return f"datasets/class_{number:02}_teaching_data.csv"


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Page(HTMLParser):
    """Collect destinations, fragment targets and displayed column labels."""
    def __init__(self, filename, address):
        super().__init__()
        self.links = set()
        self.targets = set()
        self.headers = []
        self.cell = None
        self.address = address
        self.feed(filename.read_text(encoding="utf-8"))
        self.close()

    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        if tag == "th":
            self.cell = []
        for key in ("id", "name") if tag == "a" else ("id",):
            if fields.get(key):
                self.targets.add(fields[key])
        for key in ("href", "src", "poster", "action"):
            if key in fields and fields[key] is not None:
                self.links.add((tag, key, urljoin(self.address, fields[key])))

    def handle_data(self, text):
        if self.cell is not None:
            self.cell.append(text)

    def handle_endtag(self, tag):
        if tag == "th" and self.cell is not None:
            self.headers.append("".join(self.cell).strip())
            self.cell = None


def public_files(root):
    expected = {".nojekyll", "index.html", "course.css", "catalog.js", "favicon.svg", "demo.html", *DOCS}
    for n in CLASSES:
        expected.update((f"lessons/{n}/index.html", workbook(n), dataset(n)))
    require(root.is_dir() and not root.is_symlink(), f"Invalid output directory: {root}")
    actual = set()
    for path in root.rglob("*"):
        require(not path.is_symlink(), f"Output contains symlink: {path}")
        if path.is_file():
            actual.add(path.relative_to(root).as_posix())
    require(expected == actual,
            f"Public inventory mismatch. Missing: {sorted(expected-actual)}; unexpected: {sorted(actual-expected)}")
    return actual


def resolve_links(pages, files):
    origin = urlsplit(BASE)
    for filename, page in pages.items():
        for tag, _, url in page.links:
            parts = urlsplit(url)
            if parts.scheme == "data" and tag in ("img", "source"):
                continue
            if parts.scheme in ("mailto", "tel") and tag == "a":
                continue
            require(parts.scheme in ("http", "https") and parts.netloc, f"{filename}: invalid link {url[:160]}")
            if parts.hostname != origin.hostname:
                continue
            require(parts.netloc == origin.netloc and parts.scheme == origin.scheme and parts.path.startswith(origin.path),
                    f"{filename}: link escapes course Pages prefix: {url}")
            relative = unquote(parts.path[len(origin.path):])
            if not relative or relative.endswith("/"):
                relative += "index.html"
            require(relative in files, f"{filename}: missing file for {url}")
            fragment = unquote(parts.fragment)
            if fragment and relative in pages:
                require(fragment in pages[relative].targets, f"{filename}: missing #{fragment} in {relative}")


def check_downloads(root, page, n):
    pdf = (root / workbook(n)).read_bytes()
    require(pdf.startswith(b"%PDF-") and pdf.rstrip().endswith(b"%%EOF"), f"Class {n}: damaged PDF")
    with (root / dataset(n)).open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.reader(stream, strict=True))
    require(len(rows) >= 2 and rows[0] == page.headers and bool(page.headers),
            f"Class {n}: CSV does not match displayed column headers or has no data")
    require(all(len(row) == len(rows[0]) for row in rows), f"Class {n}: uneven CSV columns")


def check_docs(root):
    for name in DOCS:
        with ZipFile(root / name) as doc:
            require(doc.testzip() is None, f"{name}: corrupt ZIP entry")
            types = ElementTree.fromstring(doc.read("[Content_Types].xml"))
            require(any(item.get("PartName") == "/word/document.xml" and
                        item.get("ContentType") == "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"
                        for item in types), f"{name}: not a Word document")
            document = ElementTree.fromstring(doc.read("word/document.xml"))
            require(document.tag == "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}document",
                    f"{name}: invalid Word document")


def check(root):
    files = public_files(root)
    pages = {}
    for name in sorted(files):
        if name.endswith(".html"):
            address = BASE + name.removesuffix("index.html")
            pages[name] = Page(root / name, address)
    resolve_links(pages, files)
    home = pages["index.html"]
    for name in DOCS:
        require(("a", "href", BASE + name) in home.links, f"Home: missing download {name}")
    for n in CLASSES:
        path = f"lessons/{n}/"
        require(("a", "href", BASE + path) in home.links, f"Class {n}: missing home link")
        page = pages[path + "index.html"]
        demo = f"{BASE}demo.html?lesson={n}"
        required_links = {
            ("a", "href", BASE + workbook(n)),
            ("a", "href", BASE + dataset(n)),
            ("a", "href", demo),
            ("iframe", "src", demo + "&embed=1"),
            ("a", "href", f"{PORTAL}/lessons/{n}#exit-ticket"),
            ("a", "href", f"{PORTAL}/instructor"),
        }
        require(required_links <= page.links, f"Class {n}: missing links {sorted(required_links-page.links)}")
        require("exit-ticket" in page.targets, f"Class {n}: missing exit-ticket section")
        check_downloads(root, page, n)
    require(("a", "href", f"{PORTAL}/instructor") in home.links, "Home: missing protected instructor link")
    demo_source = (root / "demo.html").read_text(encoding="utf-8")
    require(f'{PORTAL}/lessons/${{n}}#exit-ticket' in demo_source, "Demo: missing live exit-ticket destination")
    check_docs(root)
    print(f"Passed: {len(files)} approved public files, 14 lessons, demos, downloads, form links and internal anchors.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Generated Pages directory, usually _site")
    check(parser.parse_args().output)
