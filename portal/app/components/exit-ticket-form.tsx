"use client";

import { useCallback, useEffect, useRef, useState, type FormEvent } from "react";
import "./exit-ticket-form.css";

type Fields = { studentName: string; studentId: string; answer: string; uncertainty: string };
type FieldName = keyof Fields;
type Submission = Fields & { id: string; submittedAt: string; updatedAt: string; revision: number };
type LoadState = "loading" | "ready" | "failed";
type Payload = {
  message?: string;
  error?: string;
  fieldErrors?: Partial<Record<FieldName, string>>;
  submission?: Submission | null;
};
const emptyFields: Fields = { studentName: "", studentId: "", answer: "", uncertainty: "" };
const fieldNames: FieldName[] = ["studentName", "studentId", "answer", "uncertainty"];

function fieldsFrom(submission: Submission | null | undefined): Fields {
  return submission ? { studentName: submission.studentName, studentId: submission.studentId, answer: submission.answer, uncertainty: submission.uncertainty } : { ...emptyFields };
}

async function readPayload(response: Response): Promise<Payload> {
  try {
    const value: unknown = await response.json();
    return value && typeof value === "object" && !Array.isArray(value) ? value as Payload : {};
  } catch { return {}; }
}

function savedTime(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : new Intl.DateTimeFormat("en-US", { dateStyle: "medium", timeStyle: "short" }).format(date);
}

export default function ExitTicketForm({ lessonNumber, question }: { lessonNumber: number; question: string }) {
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [fields, setFields] = useState<Fields>({ ...emptyFields });
  const [saved, setSaved] = useState<Submission | null>(null);
  const [message, setMessage] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Partial<Record<FieldName, string>>>({});
  const [submitting, setSubmitting] = useState(false);
  const [conflict, setConflict] = useState(false);
  const [confirmReload, setConfirmReload] = useState(false);
  const [sessionExpired, setSessionExpired] = useState(false);
  const [confirmNewSession, setConfirmNewSession] = useState(false);
  const [recovering, setRecovering] = useState(false);
  const [notice, setNotice] = useState("");
  const [justSaved, setJustSaved] = useState(false);
  const busy = useRef(false);
  const requestRef = useRef<AbortController | null>(null);
  const prefix = `exit-${lessonNumber}`;
  const savedFields = fieldsFrom(saved);
  const dirty = fieldNames.some(key => fields[key] !== savedFields[key]);

  const load = useCallback(async (replaceFields = true) => {
    requestRef.current?.abort();
    const controller = new AbortController();
    requestRef.current = controller;
    setLoadState("loading");
    setMessage("");
    try {
      const options = { credentials: "same-origin" as const, cache: "no-store" as const, signal: controller.signal };
      let response = await fetch(`/api/exit-tickets/${lessonNumber}`, options);
      let payload = await readPayload(response);
      if (controller.signal.aborted) return;
      if (response.status === 401 && payload.error === "session_required") {
        const sessionResponse = await fetch("/api/exit-tickets/session", { ...options, method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
        const sessionPayload = await readPayload(sessionResponse);
        if (!sessionResponse.ok) throw new Error(sessionPayload.message || "We could not start your response. Please try again.");
        response = await fetch(`/api/exit-tickets/${lessonNumber}`, options);
        payload = await readPayload(response);
        if (controller.signal.aborted) return;
        if (response.status === 401) throw new Error("Your browser could not keep the response session. Allow cookies for this course website, then try loading again.");
      }
      if (!response.ok) throw new Error(payload.message || "We could not load your saved response. Please try again.");
      const submission = payload.submission ?? null;
      setSaved(submission);
      if (replaceFields) setFields(fieldsFrom(submission));
      setFieldErrors({});
      setConflict(false);
      setConfirmReload(false);
      setSessionExpired(false);
      setConfirmNewSession(false);
      setNotice("");
      setJustSaved(false);
      setLoadState("ready");
    } catch (error) {
      if (controller.signal.aborted) return;
      setMessage(error instanceof Error ? error.message : "We could not load your response. Please try again.");
      setLoadState("failed");
    }
  }, [lessonNumber]);

  useEffect(() => {
    busy.current = false;
    setFields({ ...emptyFields });
    setSaved(null);
    setSubmitting(false);
    setSessionExpired(false);
    setConfirmNewSession(false);
    setRecovering(false);
    setNotice("");
    setConflict(false);
    setConfirmReload(false);
    setJustSaved(false);
    void load();
    return () => requestRef.current?.abort();
  }, [lessonNumber, load]);

  function changeField(key: FieldName, value: string) {
    setFields(current => ({ ...current, [key]: value }));
    setFieldErrors(current => ({ ...current, [key]: undefined }));
    setJustSaved(false);
    setNotice("");
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy.current || sessionExpired || recovering) return;
    const trimmed = Object.fromEntries(fieldNames.map(key => [key, fields[key].trim()])) as Fields;
    const errors: Partial<Record<FieldName, string>> = {};
    for (const key of fieldNames) if (!trimmed[key]) errors[key] = "Please complete this field.";
    if (trimmed.studentId && !/^[A-Za-z0-9._-]{1,30}$/.test(trimmed.studentId)) errors.studentId = "Use letters, numbers, periods, underscores, or hyphens.";
    if (Object.keys(errors).length) { setFieldErrors(errors); setMessage("Please check the marked fields before submitting."); return; }
    busy.current = true;
    setSubmitting(true);
    setMessage("");
    setFieldErrors({});
    setJustSaved(false);
    const controller = new AbortController();
    requestRef.current = controller;
    try {
      const response = await fetch(`/api/exit-tickets/${lessonNumber}`, {
        method: "POST", credentials: "same-origin", cache: "no-store", signal: controller.signal,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...trimmed, revision: saved?.revision ?? 0 }),
      });
      const payload = await readPayload(response);
      if (controller.signal.aborted) return;
      if (response.status === 401) {
        setSessionExpired(true);
        setConfirmNewSession(false);
        setMessage("Your browser session has expired. Your text is still here. Start a new response to submit it again; earlier responses remain available to your instructor.");
        return;
      }
      if (response.status === 409) {
        setConflict(true);
        setMessage(payload.message || "A newer response is already saved. Your text is still here. Review the saved response before updating it.");
        return;
      }
      if (!response.ok) {
        setFieldErrors(payload.fieldErrors ?? {});
        setMessage(payload.message || "Your response was not saved. Your text is still here. Please try again.");
        return;
      }
      if (!payload.submission) throw new Error("The server did not confirm the saved response. Your text is still here. Please reload your saved response to check before retrying.");
      setSaved(payload.submission);
      setFields(fieldsFrom(payload.submission));
      setConflict(false);
      setConfirmReload(false);
      setJustSaved(true);
    } catch (error) {
      if (controller.signal.aborted) return;
      setMessage(error instanceof Error && error.message.startsWith("The server did not confirm") ? error.message : "The connection was interrupted. Your text is still here. Try submitting again. If it was already saved, you will be asked to reload the saved response.");
    } finally {
      busy.current = false;
      if (!controller.signal.aborted) setSubmitting(false);
    }
  }

  async function startNewResponse() {
    if (busy.current) return;
    busy.current = true;
    setRecovering(true);
    setMessage("");
    const controller = new AbortController();
    requestRef.current = controller;
    const options = { credentials: "same-origin" as const, cache: "no-store" as const, signal: controller.signal };
    try {
      const response = await fetch("/api/exit-tickets/session", { ...options, method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
      const payload = await readPayload(response);
      if (!response.ok) throw new Error(payload.message || "We could not start a new response. Your text is still here. Try again shortly.");
      const check = await fetch(`/api/exit-tickets/${lessonNumber}`, options);
      const current = await readPayload(check);
      if (controller.signal.aborted) return;
      if (!check.ok) throw new Error(check.status === 401 ? "Your browser could not keep the response session. Allow cookies for this course website and try again. Your text is still here." : current.message || "We could not reopen the form. Your text is still here. Please try again.");
      setSaved(current.submission ?? null);
      setSessionExpired(false);
      setConfirmNewSession(false);
      setLoadState("ready");
      if (current.submission) {
        setConflict(true);
        setMessage("A saved response was found in this browser. Your current text is still here. Reload the saved response before updating it.");
      } else {
        setConflict(false);
        setFieldErrors({});
        setNotice("A new response is ready. Your text has been kept. Submit it when you are ready.");
      }
    } catch (error) {
      if (controller.signal.aborted) return;
      setMessage(error instanceof Error ? error.message : "We could not start a new response. Your text is still here. Please try again.");
    } finally {
      busy.current = false;
      if (!controller.signal.aborted) setRecovering(false);
    }
  }

  function errorFor(key: FieldName) {
    return fieldErrors[key] ? <span id={`${prefix}-${key}-error`} className="ticket-field-error">{fieldErrors[key]}</span> : null;
  }

  return <section id="exit-ticket" className="ticket-section" aria-labelledby={`${prefix}-title`}>
    <div className="ticket-heading"><div><p className="eyebrow">LAST 5 MINUTES · CLASS {String(lessonNumber).padStart(2, "0")}</p><h2 id={`${prefix}-title`}>Online exit ticket</h2></div><span className="ticket-individual">Individual response</span></div>
    <p><a className="text-action" href="#teaching-feedback">Give anonymous teaching feedback for this class ↓</a></p>
    <details className="ticket-qr"><summary>Show the class QR code</summary>
      <img src={`/qr/exit-ticket-${String(lessonNumber).padStart(2, "0")}.png`} width="320" height="320" alt={`Class ${lessonNumber} QR code for the exit ticket and feedback`} />
      <a href={`/qr/exit-ticket-${String(lessonNumber).padStart(2, "0")}.png`} download>Download QR image</a>
    </details>
    <p className="ticket-question" id={`${prefix}-question`}>{question}</p>
    <p className="ticket-privacy">No sign-in is required. Your latest response for this class can be reopened in this browser for up to 30 days. On another device, submit a new response. Your instructor can view all submissions.</p>
    <p className="ticket-browser-notice">Use your own browser. Anyone using this browser profile may be able to reopen your saved answers. Your name and student ID are entered by you and are not verified automatically.</p>

    {loadState === "loading" && <div className="ticket-state" role="status">Preparing your exit ticket in this browser…</div>}
    {loadState === "failed" && <div className="ticket-state ticket-error" role="alert"><p>{message}</p><button type="button" className="button button-outline" onClick={() => void load()}>Try loading again</button></div>}

    {(loadState === "ready" || sessionExpired) && <form className="ticket-form" onSubmit={submit} aria-busy={submitting || recovering} aria-label={`Class ${lessonNumber} exit ticket`}>
      <div className="ticket-account"><span>No sign-in required</span>{saved && <span className="ticket-saved-label">Response on file in this browser</span>}</div>
      {saved && <p className="ticket-saved-time">Last saved <time dateTime={saved.updatedAt}>{savedTime(saved.updatedAt)}</time> (your local time).</p>}
      <div className="ticket-name-grid">
        <label className="ticket-field" htmlFor={`${prefix}-studentName`}><span>Full name</span><input id={`${prefix}-studentName`} name="studentName" autoComplete="name" required maxLength={100} value={fields.studentName} onChange={event => changeField("studentName", event.target.value)} disabled={submitting} aria-invalid={Boolean(fieldErrors.studentName)} aria-describedby={fieldErrors.studentName ? `${prefix}-studentName-error` : undefined} />{errorFor("studentName")}</label>
        <label className="ticket-field" htmlFor={`${prefix}-studentId`}><span>Student ID</span><input id={`${prefix}-studentId`} name="studentId" autoComplete="off" spellCheck={false} required maxLength={30} pattern="[A-Za-z0-9._\-]+" value={fields.studentId} onChange={event => changeField("studentId", event.target.value)} disabled={submitting} aria-invalid={Boolean(fieldErrors.studentId)} aria-describedby={`${prefix}-id-help${fieldErrors.studentId ? ` ${prefix}-studentId-error` : ""}`} /><span className="ticket-help" id={`${prefix}-id-help`}>Enter your own student ID exactly as it appears in the course roster.</span>{errorFor("studentId")}</label>
      </div>
      <label className="ticket-field" htmlFor={`${prefix}-answer`}><span>Your answer</span><textarea id={`${prefix}-answer`} name="answer" rows={6} required maxLength={5000} value={fields.answer} onChange={event => changeField("answer", event.target.value)} disabled={submitting} aria-invalid={Boolean(fieldErrors.answer)} aria-describedby={`${prefix}-question ${prefix}-answer-count${fieldErrors.answer ? ` ${prefix}-answer-error` : ""}`} /><span className="ticket-help ticket-count" id={`${prefix}-answer-count`}>{fields.answer.length.toLocaleString("en-US")} / 5,000 characters</span>{errorFor("answer")}</label>
      <label className="ticket-field" htmlFor={`${prefix}-uncertainty`}><span>What is still unclear?</span><span className="ticket-help" id={`${prefix}-uncertainty-help`}>Which topic from this class are you still unsure about? You may answer “None.”</span><textarea id={`${prefix}-uncertainty`} name="uncertainty" rows={3} required maxLength={2000} value={fields.uncertainty} onChange={event => changeField("uncertainty", event.target.value)} disabled={submitting} aria-invalid={Boolean(fieldErrors.uncertainty)} aria-describedby={`${prefix}-uncertainty-help ${prefix}-uncertainty-count${fieldErrors.uncertainty ? ` ${prefix}-uncertainty-error` : ""}`} /><span className="ticket-help ticket-count" id={`${prefix}-uncertainty-count`}>{fields.uncertainty.length.toLocaleString("en-US")} / 2,000 characters</span>{errorFor("uncertainty")}</label>

      {message && <div className="ticket-error" role="alert"><p>{message}</p></div>}
      {sessionExpired && <div className="ticket-conflict">{!confirmNewSession ? <button type="button" className="ticket-text-button" onClick={() => setConfirmNewSession(true)}>Start a new response</button> : <><p>Your current text will be kept, but a new browser response may create another submission for your instructor. Continue?</p><div className="ticket-confirm-actions"><button type="button" className="button button-outline" disabled={recovering} onClick={() => void startNewResponse()}>{recovering ? "Preparing…" : "Continue with my text"}</button><button type="button" className="ticket-text-button" disabled={recovering} onClick={() => setConfirmNewSession(false)}>Cancel</button></div></>}</div>}
      {conflict && <div className="ticket-conflict">{!confirmReload ? <button type="button" className="ticket-text-button" onClick={() => setConfirmReload(true)}>Reload saved response</button> : <><p>Reloading replaces the text currently in this form. Copy anything you want to keep first.</p><div className="ticket-confirm-actions"><button type="button" className="button button-outline" onClick={() => void load()}>Replace with saved response</button><button type="button" className="ticket-text-button" onClick={() => setConfirmReload(false)}>Keep my text</button></div></>}</div>}
      {justSaved && saved && <div className="ticket-success" role="status"><strong>Exit ticket saved.</strong><p>Your instructor can now view your response for Class {lessonNumber}. Any later update will replace this response.</p></div>}
      {notice && <div className="ticket-success" role="status">{notice}</div>}
      <div className="ticket-submit-row"><button type="submit" className="button button-primary" disabled={submitting || recovering || sessionExpired || conflict || (Boolean(saved) && !dirty)}>{submitting ? "Saving…" : saved ? "Update answer" : "Submit exit ticket"}</button><p>{dirty ? "Changes are not saved until you submit." : saved ? "Your saved response is shown above." : "Complete both questions before submitting."}</p></div>
    </form>}
  </section>;
}
