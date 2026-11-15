import { instructorAccess, privateJson } from "@/lib/instructor-access";
import { feedbackQuery } from "@/lib/teaching-feedback-policy";
import { readTeachingFeedback } from "@/lib/teaching-feedback-store";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export async function GET(request: Request) {
  const access = await instructorAccess();
  if (!access.allowed) return privateJson({ error: "instructor_required", message: "Sign in with the approved instructor account." }, access.status);
  const params = new URL(request.url).searchParams;
  const selected = feedbackQuery(params.get("lesson") ?? undefined, params.get("page") ?? undefined);
  if (!selected) return privateJson({ error: "invalid_query", message: "Choose a valid class and page." }, 400);
  try {
    return privateJson(await readTeachingFeedback(selected.lessonNumber, selected.pageNumber));
  } catch {
    return privateJson({ error: "storage_unavailable", message: "Teaching feedback is temporarily unavailable." }, 503);
  }
}
