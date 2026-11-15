// Build a native, editable slide for each lesson from build_exit_qr.py's manifest.
import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const [manifestPath, images, output] = process.argv.slice(2);
if (!output) throw new Error("Usage: node build_exit_slides.mjs manifest.json qr-directory output.pptx");
const { colors, lessons } = JSON.parse(await fs.readFile(manifestPath, "utf8"));
const deck = Presentation.create({ slideSize: { width: 1280, height: 720 } });
const noLine = { style: "solid", fill: "none", width: 0 };

function text(slide, name, value, pos, size, { bold = false, color = colors.graphite, url } = {}) {
  const shape = slide.shapes.add({ name, geometry: "textbox", position: pos,
                                   fill: "none", line: noLine });
  shape.text = value;
  shape.text.style = { typeface: "Arial", fontSize: size, bold, color,
                       wrap: "square", autoFit: "none", verticalAlignment: "top", insets: 0 };
  if (url) {
    shape.text.get(value).link = { uri: url, isExternal: true };
    shape.text.get(value).color = color;
    shape.hyperlink = { uri: url, isExternal: true };
  }
  return shape;
}
function box(left, top, width, height) { return { left, top, width, height }; }
for (const lesson of lessons) {
  const slide = deck.slides.add();
  slide.background.fill = "#FFFFFF";
  const label = "Class " + String(lesson.number).padStart(2, "0");
  text(slide, "course-class", "2182209   /   " + label + "   /   5 minutes", box(70, 55, 1180, 42), 26,
       { color: colors.teal, bold: true });
  text(slide, "slide-title", "Exit ticket and feedback", box(66, 113, 1150, 90), 67, { bold: true });
  text(slide, "class-title", lesson.title, box(70, 255, 650, 74), 29, { color: colors.teal, bold: true });
  text(slide, "question", lesson.question, box(70, 342, 650, 228), 39);
  text(slide, "link", "Open the " + label + " response page", box(70, 614, 680, 50), 28,
       { color: colors.teal, bold: true, url: lesson.url });
  slide.images.add({ blob: await fs.readFile(path.join(images, lesson.png)), contentType: "image/png",
    alt: "QR code for the " + label + " exit ticket and feedback page", hyperlink: { uri: lesson.url, isExternal: true },
    position: box(778, 210, 444, 444), fit: "contain" });
  slide.speakerNotes.text = "Project this slide during the final five minutes of " + label + ".\n" + lesson.url;
}
await fs.mkdir(path.dirname(output), { recursive: true });
await (await PresentationFile.exportPptx(deck)).save(output);
