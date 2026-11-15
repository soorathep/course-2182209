"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import "./teaching-feedback-form.css";

type Status = "ready" | "sending" | "received" | "unconfirmed";
const paceOptions = ["Too slow", "About right", "Too fast"] as const;
const unconfirmedMessage = "We could not confirm delivery. Your entries are still here. Sending again could create a second response.";

export default function TeachingFeedbackForm({ lessonNumber }: { lessonNumber: number }) {
  const [pace, setPace] = useState("");
  const [comment, setComment] = useState("");
  const [status, setStatus] = useState<Status>("ready");
  const [error, setError] = useState("");
  const [interactive, setInteractive] = useState(false);
  const activeRequest = useRef<AbortController | null>(null);
  const paceControl = useRef<HTMLSelectElement>(null);
  const prefix = `feedback-${lessonNumber}`;

  useEffect(() => {
    setInteractive(true);
    return () => activeRequest.current?.abort();
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (activeRequest.current || status === "received" || !interactive) return;

    const cleanComment = comment.trim();
    if (!pace && !cleanComment) {
      setError("Choose a pace or write a comment before sending.");
      paceControl.current?.focus();
      return;
    }

    const request = new AbortController();
    activeRequest.current = request;
    setStatus("sending");
    setError("");
    try {
      const response = await fetch(`/api/teaching-feedback/${lessonNumber}`, {
        method: "POST",
        credentials: "omit",
        referrerPolicy: "no-referrer",
        redirect: "error",
        cache: "no-store",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pace, comment: cleanComment }),
        signal: request.signal,
      });
      const payload: unknown = await response.json().catch(() => null);
      const result = payload && typeof payload === "object" && !Array.isArray(payload)
        ? payload as Record<string, unknown>
        : null;
      if (request.signal.aborted) return;

      if (response.status === 201 && result?.saved === true) {
        setStatus("received");
        setPace("");
        setComment("");
      } else if (response.status >= 400 && response.status < 500) {
        setStatus("ready");
        setError(typeof result?.message === "string" ? result.message : "Your feedback was not accepted. Check your entries and try again.");
      } else {
        setStatus("unconfirmed");
        setError(unconfirmedMessage);
      }
    } catch {
      if (!request.signal.aborted) {
        setStatus("unconfirmed");
        setError(unconfirmedMessage);
      }
    } finally {
      activeRequest.current = null;
    }
  }

  return (
    <section id="teaching-feedback" className="teaching-feedback" aria-labelledby={`${prefix}-title`}>
      <h2 id={`${prefix}-title`}>Anonymous teaching feedback</h2>
      <p className="feedback-intro">How did Class {lessonNumber} work for you? Your instructor receives the class number and the feedback you enter here. Please leave out identifying details.</p>
      <p className="feedback-status" role="status">
        {status === "received" && "Thank you. Your anonymous teaching feedback was received."}
      </p>
      {status !== "received" && (
        <form onSubmit={submit} autoComplete="off" aria-label={`Anonymous teaching feedback for Class ${lessonNumber}`} aria-busy={status === "sending"}>
          <p id={`${prefix}-instructions`} className="feedback-instructions">Choose a pace, leave a comment, or do both.</p>
          <fieldset disabled={status === "sending"} aria-describedby={`${prefix}-instructions`}>
            <legend className="sr-only">Class feedback</legend>
            <label htmlFor={`${prefix}-pace`}>Pace of this class</label>
            <select id={`${prefix}-pace`} ref={paceControl} value={pace} onChange={event => setPace(event.target.value)}>
              <option value="">Select a pace (optional)</option>
              {paceOptions.map(option => <option key={option} value={option}>{option}</option>)}
            </select>
            <label htmlFor={`${prefix}-comment`}>What helped you learn, or what would you change?</label>
            <textarea id={`${prefix}-comment`} value={comment} onChange={event => setComment(event.target.value)}
              rows={3} maxLength={1000} aria-describedby={`${prefix}-limit`} />
            <small id={`${prefix}-limit`}>Optional, up to 1,000 characters.</small>
          </fieldset>
          {error && <p className="feedback-error" role="alert">{error}</p>}
          <button className="button button-primary" type="submit" disabled={!interactive || status === "sending"}>
            {status === "sending" ? "Sending…" : status === "unconfirmed" ? "Send feedback again" : "Send anonymous feedback"}
          </button>
          <noscript><p>Enable JavaScript to submit teaching feedback.</p></noscript>
        </form>
      )}
    </section>
  );
}
