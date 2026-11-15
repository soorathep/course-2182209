import { notFound } from "next/navigation";
import TeachingFeedbackForm from "@/app/components/teaching-feedback-form";
import ExitTicketForm from "@/app/components/exit-ticket-form";
import lessons from "@/content/course-data.json";
import type { Metadata } from "next";

type Props = { params: Promise<{ number: string }> };
function findLesson(value: string) { return /^([1-9]|1[0-4])$/.test(value) ? lessons.find(l => l.number === Number(value)) : undefined; }
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { number } = await params;
  const lesson = findLesson(number);
  return { title: lesson ? `Class ${lesson.number} ${lesson.title_en}` : "Lesson not found" };
}
export default async function LessonPage({ params }: Props) {
  const { number } = await params;
  const lesson = findLesson(number);
  if (!lesson) notFound();
  const padded = String(lesson.number).padStart(2, "0");
  return (
    <main id="main-content" className="lesson-page shell">
      <nav className="breadcrumbs" aria-label="Breadcrumb"><a href="/#lessons">All lessons</a><span aria-hidden="true">/</span><span>Class {padded}</span></nav>
      <header className="lesson-hero">
        <div><p className="eyebrow">LESSON {padded} OF 14 <span>·</span> 90 min</p><h1>{lesson.title_en}</h1></div>
        <div className="lesson-downloads"><a className="button button-primary" href={`/downloads/worksheet-${padded}.pdf`} download>Download worksheet <span className="file-type">PDF ↓</span></a><a href={`/datasets/class_${padded}_teaching_data.csv`} download>Download CSV data <span aria-hidden="true">↓</span></a></div>
      </header>
      <nav className="lesson-section-nav" aria-label="Lesson sections"><a href="#overview">Objectives</a><a href="#concepts">Concepts</a><a href="#demo">Simulation & demo</a><a href="#activities">Activities</a><a href="#exit-ticket">Exit ticket</a><a href="#teaching-feedback">Teaching feedback</a></nav>
      <section id="overview" className="lesson-overview" aria-labelledby="overview-title"><div><p className="eyebrow">BEFORE YOU BEGIN</p><h2 id="overview-title">By the end of this class</h2><ul className="objectives">{lesson.objectives.map((item, i) => <li key={i}>{item}</li>)}</ul></div><aside className="prerequisites"><h3>What you need to know</h3><p>{lesson.prerequisites}</p><p className="muted">Read the question and predict the result before opening the demo. Then use the data to test your reasoning.</p></aside></section>
      <section id="concepts" className="lesson-content-section" aria-labelledby="concepts-title"><div className="section-heading compact"><div><p className="eyebrow">CORE IDEAS</p><h2 id="concepts-title">Core concepts</h2></div><span className="section-counter">01</span></div><ol className="concept-list">{lesson.concepts.map((item, i) => <li key={i}><span aria-hidden="true">{String(i + 1).padStart(2, "0")}</span><p>{item}</p></li>)}</ol></section>
      <section id="demo" className="lesson-content-section" aria-labelledby="demo-title"><div className="section-heading compact"><div><p className="eyebrow">PREDICT · EXPLORE · EXPLAIN</p><h2 id="demo-title">Simulation & demo</h2></div><a className="text-action" href={`/demo.html?lesson=${lesson.number}`} target="_blank" rel="noreferrer">Open in a new window <span aria-hidden="true">↗</span></a></div><h3 className="demo-name">{lesson.demo.title}</h3><p className="demo-intro">Change one variable at a time. Record what happens and compare it with your prediction.</p><iframe className="demo-frame" src={`/demo.html?lesson=${lesson.number}&embed=1`} title={`Simulation Class ${lesson.number}: ${lesson.title_en}`} loading="lazy" allow="fullscreen" /><details className="demo-directions"><summary>Exploration steps and model limitations</summary><ol>{lesson.demo.steps.map((step, i) => <li key={i}>{step}</li>)}</ol><p><strong>Model limitations</strong> {lesson.demo.limitations}</p></details></section>
      <section id="activities" className="lesson-content-section" aria-labelledby="activities-title"><div className="section-heading compact"><div><p className="eyebrow">WORK WITH THE EVIDENCE</p><h2 id="activities-title">Activities and data</h2></div><span className="section-counter">03</span></div><p className="activity-intro">Complete the worksheet activities. Show your reasoning, units, and assumptions.</p><ol className="activity-list">{lesson.student_tasks.map((task, i) => <li key={i}><span className="activity-number">{i + 1}</span><p>{task}</p></li>)}</ol><div className="data-heading"><h3>Activity data</h3><a href={`/datasets/class_${padded}_teaching_data.csv`} download>Download CSV ↓</a></div><div className="table-scroll" role="region" aria-label="Activity data table. Scroll horizontally to read all columns." tabIndex={0}><table><thead><tr>{lesson.data_table.headers.map((h, i) => <th key={i} scope="col">{h}</th>)}</tr></thead><tbody>{lesson.data_table.rows.map((row, i) => <tr key={i}>{row.map((value, j) => <td key={j}>{String(value)}</td>)}</tr>)}</tbody></table></div><p className="data-caption">{lesson.data_table.caption}</p></section>
      <ExitTicketForm lessonNumber={lesson.number} question={lesson.exit_question} />
      <TeachingFeedbackForm key={lesson.number} lessonNumber={lesson.number} />
      <section className="references-section" aria-labelledby="references-title"><h2 id="references-title">Further reading</h2><ul>{lesson.source_urls.map((url, i) => <li key={i}><a href={url} target="_blank" rel="noreferrer">{new URL(url).hostname.replace(/^www\./, "")} <span className="reference-path">{decodeURIComponent(new URL(url).pathname.split("/").filter(Boolean).slice(-1)[0] || "Reference").replace(/-/g, " ")}</span><span aria-hidden="true">↗</span></a></li>)}</ul></section>
      <nav className="lesson-pagination" aria-label="Previous and next lessons">{lesson.number > 1 ? <a href={`/lessons/${lesson.number - 1}`}><small>← Previous class</small><strong>{lessons[lesson.number - 2].title_en}</strong></a> : <a href="/#lessons"><small>← Back to</small><strong>All lessons</strong></a>}{lesson.number < 14 ? <a className="next-lesson" href={`/lessons/${lesson.number + 1}`}><small>Next class →</small><strong>{lessons[lesson.number].title_en}</strong></a> : <a className="next-lesson" href="/#lessons"><small>Review again →</small><strong>Browse all lessons</strong></a>}</nav>
    </main>
  );
}
