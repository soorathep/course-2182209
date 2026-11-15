# 2182209 Chemistry for Semiconductor Engineering

This repository contains the English public materials for the 14 classes before the midterm. Students can use the [course portal](https://semiconductor-chemistry-2182209.soorathep-k.chatgpt.site/#lessons) for lessons, demos, worksheets and online exit tickets. The [instructor area](https://semiconductor-chemistry-2182209.soorathep-k.chatgpt.site/instructor) requires an authorized login.

## Public course files

Edit the public lesson content in `content/course-data.json`. The `public/` directory contains the standalone simulation, 14 worksheet PDFs, 14 teaching datasets, the syllabus and the student workbook. The initial import used the approved student files from course portal source revision `50873dfea9cf6d33b80884e1238abaaf5a71a242`, with the 32 public assets checked against its SHA-256 manifest. The static templates and catalog controls are in `pages/`.

The exit-ticket link in each lesson opens that class on the course portal. Students submit their name, student ID and answer there. Editing uses the original portal's browser cookie. The protected instructor guide, answer keys and response review also use the portal. For a change to an exit-ticket question, coordinate the displayed prompt and the hosted form's question together. Leave the existing responses and question snapshots intact.

## Build and publish

Use Python 3.10 or newer. The build uses the standard library and no network access. Run from the repository root on a lab Mac:

```sh
"$HOME/.venvs/research/bin/python" scripts/build_pages.py
"$HOME/.venvs/research/bin/python" tools/check_pages.py _site
"$HOME/.venvs/research/bin/python" -m http.server 8000 --bind 127.0.0.1 --directory _site
```

Publish course changes to [soorathep/course-2182209](https://github.com/soorathep/course-2182209). GitHub Actions builds and validates pull requests and pushes to `main`. When the repository has Pages enabled with **GitHub Actions** as its source, the workflow deploys the verified `_site/` directory. After enabling Pages, use **Actions → Test and publish course pages → Run workflow** on `main`. The expected project URL is `https://soorathep.github.io/course-2182209/`. Verify the deployment and public URL before sharing that address with students.

See [ARCHIVING.md](ARCHIVING.md) for annual Zenodo preparation, credits, rights, privacy checks, SHA-256 and verified version-specific DOI links.
