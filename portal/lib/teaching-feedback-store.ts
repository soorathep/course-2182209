import "server-only";
import { and, asc, count, eq, ne } from "drizzle-orm";
import { getDb } from "@/db";
import { teachingFeedback } from "@/db/schema";
import { COMMENTS_PER_PAGE, type FeedbackInput } from "./teaching-feedback-policy";

export async function saveTeachingFeedback(lessonNumber: number, input: FeedbackInput) {
  await getDb().insert(teachingFeedback).values({ lessonNumber, pace: input.pace, comment: input.comment });
}

export async function readTeachingFeedback(lessonNumber: number, requestedPage: number) {
  const db = getDb();
  const { pace, comment } = teachingFeedback;
  const classComments = and(eq(teachingFeedback.lessonNumber, lessonNumber), ne(comment, ""));
  const [paceRows, [commentCount]] = await Promise.all([
    db.select({ lessonNumber: teachingFeedback.lessonNumber, pace, total: count() })
      .from(teachingFeedback).groupBy(teachingFeedback.lessonNumber, pace),
    db.select({ total: count() }).from(teachingFeedback).where(classComments),
  ]);
  const classes = Array.from({ length: 14 }, (_, i) => ({
    lessonNumber: i + 1, total: 0, slow: 0, right: 0, fast: 0,
  }));
  for (const row of paceRows) {
    const summary = classes[row.lessonNumber - 1];
    if (!summary) continue;
    summary.total += row.total;
    if (row.pace === "Too slow") summary.slow += row.total;
    if (row.pace === "About right") summary.right += row.total;
    if (row.pace === "Too fast") summary.fast += row.total;
  }
  const totalPages = Math.max(1, Math.ceil(commentCount.total / COMMENTS_PER_PAGE));
  const page = Math.min(requestedPage, totalPages);
  // Alphabetical order keeps the instructor view independent of arrival order.
  const rows = await db.select({ comment }).from(teachingFeedback).where(classComments)
    .orderBy(asc(comment)).limit(COMMENTS_PER_PAGE).offset((page - 1) * COMMENTS_PER_PAGE);
  return { classes, lessonNumber, page, totalPages, commentCount: commentCount.total, comments: rows.map(row => row.comment) };
}
