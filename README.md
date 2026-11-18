# 2182209 Chemistry for Semiconductor Engineering

**2027 offering (Classes 1 to 14, January to February 2027).** The front page redirects to `teaching/2182209/2027-draft/`, which holds each class's narrated slides, lab page, Python module and the anonymous Exit Ticket and feedback form (`exit.html?s=N`). These files are built in `2027/sessions/` in the course folder on the instructor's Mac and copied here unchanged; `scripts/build_pages.py` copies them into `_site/` byte for byte. Lab credit is the answer file each student uploads to myCourseVille. Folder names are fixed once their QR codes exist.

**Earlier lesson site.** The material described below is still built, unchanged, under `classic/` and is not linked from the 2027 front page, except for the practice worksheet PDFs. Its portal Exit Tickets are not used for the 2027 classes; existing portal responses are left intact.


This repository contains the English public materials for the 14 classes before the midterm. Students can use the [course portal](https://semiconductor-chemistry-2182209.soorathep-k.chatgpt.site/#lessons) for lessons, demos, worksheets and online exit tickets. The [instructor area](https://semiconductor-chemistry-2182209.soorathep-k.chatgpt.site/instructor) requires an authorized login.

## Public course files

Edit the public lesson content in `content/course-data.json`. The `public/` directory contains the standalone simulation, 14 worksheet PDFs, 14 teaching datasets, the syllabus and the student workbook. The initial import used the approved student files from course portal source revision `50873dfea9cf6d33b80884e1238abaaf5a71a242`, with the 32 public assets checked against its SHA-256 manifest. The static templates and catalog controls are in `pages/`.

The exit-ticket link in each lesson opens that class on the course portal. Students submit their name, student ID and answer there. Editing uses the original portal's browser cookie. The protected instructor guide, answer keys and response review also use the portal. For a change to an exit-ticket question, coordinate the displayed prompt and the hosted form's question together. Leave the existing responses and question snapshots intact.

## End-of-class QR codes

Each slide contains the class question, a clickable link and the same QR code for everyone in that class. Replace or append the matching slide in the last five minutes of each lesson. Download the [editable PowerPoint](public/downloads/2182209-exit-ticket-slides.pptx), [projection PDF](public/downloads/2182209-exit-ticket-slides.pdf) or [14 individual QR images in one ZIP](classroom/2182209-exit-ticket-qr.zip).

The QR code opens the named exit ticket, with a link at the top to a separate anonymous teaching-feedback form. The feedback form accepts pace and/or a comment. Its request omits browser credentials and its table records only the class number, pace and comment. The [instructor feedback page](https://semiconductor-chemistry-2182209.soorathep-k.chatgpt.site/instructor/teaching-feedback) shows class totals and comments in alphabetical order.

The QR assets are generated from the class prompts in `content/course-data.json` using `figures/build_exit_qr.py`. The same generated manifest and PNG files are inputs to `scripts/build_exit_slides.mjs` for the editable deck.

The reviewed portal source changes are in `portal/`, outside the Pages artifact. They apply to the authenticated Sites project at baseline `50873dfea9cf6d33b80884e1238abaaf5a71a242`. The QR images and slide downloads are shared from `public/`. Apply these changes alongside the existing portal migrations, then build and test with the Sites workflow.

## Build and publish

Use Python 3.10 or newer. The build uses the standard library and no network access. Run from the repository root on a lab Mac:

```sh
"$HOME/.venvs/research/bin/python" scripts/build_pages.py
"$HOME/.venvs/research/bin/python" tools/check_pages.py _site
"$HOME/.venvs/research/bin/python" -m http.server 8000 --bind 127.0.0.1 --directory _site
```

Publish course changes to [soorathep/course-2182209](https://github.com/soorathep/course-2182209). GitHub Actions builds and validates pull requests and pushes to `main`. When the repository has Pages enabled with **GitHub Actions** as its source, the workflow deploys the verified `_site/` directory. After enabling Pages, use **Actions → Test and publish course pages → Run workflow** on `main`. The expected project URL is `https://soorathep.github.io/course-2182209/`. Verify the deployment and public URL before sharing that address with students.

See [ARCHIVING.md](ARCHIVING.md) for the owner’s manual Zenodo preparation, credits, rights, privacy checks, SHA-256 and verified version-specific DOI links.
