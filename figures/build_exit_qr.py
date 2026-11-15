"""Generate course 2182209's per-class QR assets and slide-builder input."""
import argparse
import json
import math
from pathlib import Path
import qrcode
import skh_palette as skh

PORTAL = "https://semiconductor-chemistry-2182209.soorathep-k.chatgpt.site"

def build(course, destination, manifest, url_template):
    lessons = json.loads(course.read_text(encoding="utf-8"))
    if [lesson["number"] for lesson in lessons] != list(range(1, 15)):
        raise ValueError("Expected the complete ordered list of 14 lessons.")
    destination.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    skh.use()
    slides = []
    for lesson in lessons:
        n = lesson["number"]
        url = url_template.format(n=n)
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        # At the 4.625-inch size used on the slide the code retains at least 600 dpi.
        qr.box_size = math.ceil(4.625 * 600 / (qr.modules_count + 2 * qr.border))
        image = qr.make_image(fill_color=skh.C["graphite"], back_color="white").get_image()
        image = image.quantize(colors=2)
        name = f"exit-ticket-{n:02d}.png"
        image.save(destination / name, dpi=(600, 600), optimize=True)
        slides.append({"number": n, "title": lesson["title_en"], "question": lesson["exit_question"],
                       "url": url, "png": name})
    manifest.write_text(json.dumps({"colors": {key: skh.C[key] for key in ("graphite", "teal")},
                                    "lessons": slides}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("course", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--url-template", default=PORTAL + "/lessons/{n}#exit-ticket")
    args = parser.parse_args()
    build(args.course, args.destination, args.manifest, args.url_template)
