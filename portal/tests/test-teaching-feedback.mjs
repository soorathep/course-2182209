/** HTTP checks for an isolated local Worker with the course migrations applied. Uses synthetic records. */
import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";

const base = new URL(process.argv[2]);
assert(base.protocol === "http:" && ["localhost", "127.0.0.1"].includes(base.hostname));
assert(base.href === base.origin + "/", "Supply a local origin without a path or credentials");
const review = "/api/instructor/teaching-feedback";
const teacher = { "oai-authenticated-user-id": "qa-instructor", "oai-authenticated-user-email": "instructor-test@example.test" };
const marker = "Synthetic " + randomUUID();

async function json(path, status, options = {}) {
  const response = await fetch(new URL(path, base), { ...options, redirect: "error" });
  assert.equal(response.status, status, path);
  assert.match(response.headers.get("cache-control") ?? "", /no-store/);
  assert.equal(response.headers.get("set-cookie"), null);
  return response.json();
}
function submit(number, input, status, extra = {}) {
  return json("/api/teaching-feedback/" + number, status, {
    method: "POST", body: JSON.stringify(input),
    headers: { Origin: base.origin, "Content-Type": "application/json", ...extra },
  });
}
function summary(number, page = 1) {
  return json(review + "?lesson=" + number + "&page=" + page, 200, { headers: teacher });
}

await json(review, 401);
await json(review, 403, { headers: { ...teacher, "oai-authenticated-user-email": "unauthorized@example.test" } });
const before = await summary(1);
assert.equal(before.classes.length, 14);
for (const number of [0, 15, "01"]) await submit(number, { pace: "About right" }, 404);
for (const input of [{}, { pace: null }, { pace: "other" }, { comment: "   " }, { comment: "x".repeat(1001) },
  { comment: "ok", studentId: "spoofed" }, { comment: "ok", session: "spoofed" }]) {
  await submit(1, input, 400);
}
await submit(1, { pace: "Too fast" }, 403, { Origin: "https://unrelated.example" });
await submit(1, { pace: "Too fast" }, 415, { "Content-Type": "text/plain" });
await submit(1, { comment: "x".repeat(35_000) }, 413);
await json(review + "?lesson=15", 400, { headers: teacher });
for (let number = 1; number <= 14; number++) {
  const accepted = await submit(number, { pace: "About right", comment: marker }, 201, {
    Cookie: "ignored_cookie=synthetic", "CF-Connecting-IP": "192.0.2.10", "User-Agent": "synthetic client",
  });
  assert.deepEqual(accepted, { saved: true });
}
await submit(1, { pace: "Too fast" }, 201);
await submit(1, { comment: marker + " comment only" }, 201);
const after = await summary(1);
for (let i = 0; i < 14; i++) {
  assert.equal(after.classes[i].total - before.classes[i].total, i === 0 ? 3 : 1);
  assert.equal(after.classes[i].right - before.classes[i].right, 1);
}
assert.equal(after.classes[0].fast - before.classes[0].fast, 1);
assert.equal(after.commentCount - before.commentCount, 2);
assert(after.comments.every(text => typeof text === "string"));
assert.deepEqual(Object.keys(after).sort(), ["classes", "commentCount", "comments", "lessonNumber", "page", "totalPages"]);
assert.deepEqual(Object.keys(after.classes[0]).sort(), ["fast", "lessonNumber", "right", "slow", "total"]);
const comments = [];
for (let page = 1; page <= after.totalPages; page++) {
  const result = page === 1 ? after : await summary(1, page);
  assert(result.comments.length <= 25);
  comments.push(...result.comments);
}
assert(comments.includes(marker) && comments.includes(marker + " comment only"));
assert.equal(comments.length, after.commentCount);
const pagePath = new URL("/instructor/teaching-feedback?lesson=1", base);
assert(!(await (await fetch(pagePath)).text()).includes(marker));
const instructorHtml = await (await fetch(pagePath, { headers: teacher })).text();
assert(instructorHtml.replaceAll("<!-- -->", "").includes("Class 1 comments"));
console.log("Passed: all 14 classes, input bounds, ignored identity headers, protected instructor reports, anonymous receipts, counts and comments.");
