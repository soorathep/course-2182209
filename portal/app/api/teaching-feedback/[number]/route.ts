import { privateJson } from "@/lib/instructor-access";
import { discardSubmissionBody, parseLessonNumber, readSubmissionJson, SubmissionBodyError, validateSubmissionRequest } from "@/lib/exit-ticket-policy.mjs";
import { validateFeedback } from "@/lib/teaching-feedback-policy";
import { saveTeachingFeedback } from "@/lib/teaching-feedback-store";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export async function POST(request: Request, { params }: { params: Promise<{ number: string }> }) {
  const lessonNumber = parseLessonNumber((await params).number);
  const requestError = validateSubmissionRequest(request);
  if (lessonNumber === null || requestError) {
    await discardSubmissionBody(request);
    if (lessonNumber === null) return privateJson({ error: "lesson_not_found", message: "Choose a class from 1 to 14." }, 404);
    if (requestError) return privateJson({ error: requestError.error, message: requestError.message }, requestError.status);
  }

  let input: unknown;
  try {
    input = await readSubmissionJson(request);
  } catch (error) {
    if (error instanceof SubmissionBodyError) return privateJson({ error: error.code, message: error.message }, error.status);
    return privateJson({ error: "invalid_json", message: "Your feedback could not be read." }, 400);
  }
  const result = validateFeedback(input);
  if ("message" in result) return privateJson({ error: "invalid_feedback", message: result.message }, 400);

  try {
    await saveTeachingFeedback(lessonNumber, result.data);
    return privateJson({ saved: true }, 201);
  } catch {
    return privateJson({ error: "storage_unavailable", message: "Feedback could not be saved. Keep your comment and try again." }, 503);
  }
}
