import { parseLessonNumber } from "./exit-ticket-policy.mjs";

export const PACES = ["Too slow", "About right", "Too fast"] as const;
export const COMMENT_LIMIT = 1000;
export const COMMENTS_PER_PAGE = 25;
export type FeedbackPace = typeof PACES[number] | "";
export type FeedbackInput = { pace: FeedbackPace; comment: string };

export function validateFeedback(body: unknown): { data: FeedbackInput } | { message: string } {
  if (!body || typeof body !== "object" || Array.isArray(body)) {
    return { message: "Send a JSON object with a pace choice or a comment." };
  }
  const fields = body as Record<string, unknown>;
  if (Object.keys(fields).some(key => key !== "pace" && key !== "comment")) {
    return { message: "Send only the pace choice and comment." };
  }
  const { pace = "", comment = "" } = fields;
  if (pace !== "" && !PACES.some(value => value === pace)) {
    return { message: "Choose one of the listed pace options." };
  }
  if (typeof comment !== "string" || comment.length > COMMENT_LIMIT ||
      /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(comment)) {
    return { message: "Enter a comment of up to 1,000 characters." };
  }
  const trimmed = comment.trim();
  if (!pace && !trimmed) {
    return { message: "Choose a pace or write a comment before submitting." };
  }
  return { data: { pace: pace as FeedbackPace, comment: trimmed } };
}

export function feedbackQuery(lesson = "1", page = "1") {
  const lessonNumber = parseLessonNumber(lesson);
  const pageNumber = /^[1-9]\d{0,6}$/.test(page) ? Number(page) : 0;
  if (lessonNumber === null || !pageNumber) return null;
  return { lessonNumber, pageNumber };
}
