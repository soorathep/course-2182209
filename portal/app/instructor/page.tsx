import { instructorAccess } from "@/lib/instructor-access";
import { chatGPTSignInPath, chatGPTSignOutPath } from "@/app/chatgpt-auth";
import "./instructor.css";

export const dynamic = "force-dynamic";
export const revalidate = 0;
export const metadata = { title: "Instructor resources | Chemistry for Semiconductor Engineering", robots: { index: false, follow: false } };

export default async function InstructorPage() {
  const access = await instructorAccess();
  if (!access.allowed) return <div className="teacher-shell"><main id="main-content" className="teacher-login">
    <p className="teacher-eyebrow">INSTRUCTOR RESOURCES</p><h1>Instructor resources</h1>
    <p>Teaching guidance, activity answers, and exit-ticket criteria for all 14 classes.</p>
    {access.user ? <><div className="teacher-notice"><strong>This account does not have instructor access</strong><p>You are signed in as {access.user.email} If you use multiple accounts, sign out and choose the account approved by the course administrator.</p></div><a className="teacher-button" href={chatGPTSignOutPath("/instructor")} target="_top">Sign out to switch accounts</a></> : <><p className="teacher-muted">Sign in with the ChatGPT account approved for instructor access.</p><a className="teacher-button" href={chatGPTSignInPath("/instructor")} target="_top">Sign in with ChatGPT <span aria-hidden="true">↗</span></a></>}
    <a className="teacher-back" href="/">Open student lessons</a>
  </main></div>;
  const { default: lessons } = await import("@/private/lessons");
  return <div className="teacher-shell"><main id="main-content" className="teacher-main">
    <div className="teacher-top"><div><p className="teacher-eyebrow">INSTRUCTOR RESOURCES · CLASSES 01–14</p><h1>Instructor guide and answers</h1><p>Instructor account: {access.user?.email}</p></div><a href={chatGPTSignOutPath("/")} target="_top" className="teacher-signout">Sign out</a></div>
    <div className="teacher-download"><div><h2>Exit-ticket responses</h2><p>Read student answers for all 14 classes, filter by class or student, and download responses as a CSV file.</p></div><a className="teacher-button" href="/instructor/exit-tickets">View student responses →</a></div>
    <div className="teacher-download"><div><h2>Anonymous teaching feedback</h2><p>Review pace ratings and comments by class.</p></div><a className="teacher-button" href="/instructor/teaching-feedback">View teaching feedback →</a></div>
    <div className="teacher-download"><div><h2>End-of-class QR slides</h2><p>One slide per class. Download the editable deck or project the PDF.</p></div><div><a className="teacher-button" href="/downloads/2182209-exit-ticket-slides.pptx" download>PowerPoint ↓</a> <a className="teacher-button" href="/downloads/2182209-exit-ticket-slides.pdf" download>PDF ↓</a></div></div>
    <div className="teacher-download"><div><h2>Complete instructor guide</h2><p>Class plans, core content, demo procedures, answers, and assessment guidance · Word document</p></div><a className="teacher-button" href="/api/instructor/download">Download instructor guide ↓</a></div>
    <p className="teacher-guide">Choose a class to view teaching notes and answers. Exit-ticket criteria diagnose understanding without adding a new course assessment weighting.</p>
    <div className="teacher-lessons">{lessons.map(lesson => <details className="teacher-lesson" key={lesson.number}>
      <summary><span className="teacher-number">{String(lesson.number).padStart(2,"0")}</span><span>{lesson.title_en}</span><span className="teacher-expand" aria-hidden="true">+</span></summary>
      <div className="teacher-content"><a href={`/lessons/${lesson.number}`} className="teacher-back">Open student lessons ↗</a>
        <h3>Slide outline</h3><ol>{lesson.slide_outline.map((text,i)=><li key={i}>{text}</li>)}</ol>
        <h3>Worked example</h3><p className="teacher-question">{lesson.worked_example.prompt}</p><p>{lesson.worked_example.solution}</p>
        <h3>Demo preparation</h3><ul>{lesson.demo.setup.map((text,i)=><li key={i}>{text}</li>)}</ul>
        <h3>Expected observations</h3><ul>{lesson.demo.expected.map((text,i)=><li key={i}>{text}</li>)}</ul>
        <h3>Activity answers</h3>{lesson.student_tasks.map((task,i)=><section className="teacher-answer" key={i}><h4>{i+1}. {task.prompt}</h4><p>{task.answer}</p></section>)}
        <h3>Misconceptions to address</h3><p className="teacher-question">{lesson.misconception.claim}</p><p>{lesson.misconception.correction}</p>
        <h3>Online exit ticket</h3><p className="teacher-question">{lesson.exit.question}</p><p>{lesson.exit.answer}</p><p className="teacher-rubric">{lesson.exit.rubric}</p>
      </div></details>)}</div>
  </main></div>;
}
