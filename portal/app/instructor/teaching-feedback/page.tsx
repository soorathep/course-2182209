import { chatGPTSignInPath, chatGPTSignOutPath } from "@/app/chatgpt-auth";
import { instructorAccess } from "@/lib/instructor-access";
import { feedbackQuery } from "@/lib/teaching-feedback-policy";
import { readTeachingFeedback } from "@/lib/teaching-feedback-store";
import "../instructor.css";
import "./feedback.css";

export const dynamic = "force-dynamic";
export const revalidate = 0;
export const metadata = { title: "Anonymous teaching feedback", robots: { index: false, follow: false } };
const route = "/instructor/teaching-feedback";

type Props = { searchParams: Promise<{ lesson?: string | string[]; page?: string | string[] }> };

export default async function TeachingFeedbackPage({ searchParams }: Props) {
  const access = await instructorAccess();
  if (!access.allowed) {
    return <div className="teacher-shell"><main id="main-content" className="teacher-login">
      <h1>Anonymous teaching feedback</h1><p>Sign in with the approved instructor account to review feedback.</p>
      {access.user
        ? <a className="teacher-button" href={chatGPTSignOutPath(route)} target="_top">Sign out to switch accounts</a>
        : <a className="teacher-button" href={chatGPTSignInPath(route)} target="_top">Sign in with ChatGPT</a>}
      <a className="teacher-back" href="/">Open student lessons</a>
    </main></div>;
  }
  const { lesson, page } = await searchParams;
  const selection = Array.isArray(lesson) || Array.isArray(page) ? null : feedbackQuery(lesson, page);
  let feedback;
  if (selection) {
    try { feedback = await readTeachingFeedback(selection.lessonNumber, selection.pageNumber); }
    catch { /* Show a retry link without exposing storage details. */ }
  }
  return <div className="teacher-shell"><main id="main-content" className="teacher-main feedback-review">
    <a className="teacher-back" href="/instructor">← Instructor resources</a>
    <div className="teacher-top"><h1>Anonymous teaching feedback</h1>
      <a className="teacher-signout" href={chatGPTSignOutPath("/")} target="_top">Sign out</a></div>
    {!selection ? <p>Choose a valid class and page. <a href={route}>Open Class 1</a></p>
      : !feedback ? <p>Feedback is temporarily unavailable. <a href={`?lesson=${selection.lessonNumber}&page=${selection.pageNumber}`}>Try again</a></p>
      : <>
        <p>Select a class to read its comments. Each submission counts once, including comments submitted without a pace rating.</p>
        <div className="feedback-table-scroll" role="region" aria-label="Pace ratings by class" tabIndex={0}>
          <table><caption>Pace ratings by class</caption>
            <thead><tr>{["Class", "Submissions", "Too slow", "About right", "Too fast"].map(label => <th scope="col" key={label}>{label}</th>)}</tr></thead>
            <tbody>{feedback.classes.map(row => <tr key={row.lessonNumber}>
              <th scope="row"><a href={`?lesson=${row.lessonNumber}#comments`}
                aria-current={feedback.lessonNumber === row.lessonNumber ? "true" : undefined}>Class {row.lessonNumber}</a></th>
              <td>{row.total}</td><td>{row.slow}</td><td>{row.right}</td><td>{row.fast}</td>
            </tr>)}</tbody>
          </table>
        </div>
        <section id="comments" aria-labelledby="feedback-comments">
          <h2 id="feedback-comments">Class {feedback.lessonNumber} comments</h2>
          {feedback.commentCount ? <>
            <p>{feedback.commentCount} written {feedback.commentCount === 1 ? "comment" : "comments"}. Listed alphabetically.</p>
            <ul>{feedback.comments.map((comment, index) => <li key={index}>{comment}</li>)}</ul>
          </> : <p>No written comments for this class yet.</p>}
          {feedback.totalPages > 1 && <nav aria-label="Comment pages">
            {feedback.page > 1 && <a href={`?lesson=${feedback.lessonNumber}&page=${feedback.page - 1}#comments`}>← Previous</a>}
            <span>Page {feedback.page} of {feedback.totalPages}</span>
            {feedback.page < feedback.totalPages && <a href={`?lesson=${feedback.lessonNumber}&page=${feedback.page + 1}#comments`}>Next →</a>}
          </nav>}
        </section>
      </>}
  </main></div>;
}
