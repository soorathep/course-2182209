import { index, integer, sqliteTable, text, uniqueIndex } from "drizzle-orm/sqlite-core";

export const exitTicketSessions = sqliteTable("exit_ticket_sessions", {
  id: text("id").primaryKey(),
  tokenHash: text("token_hash").notNull(),
  createdAt: text("created_at").notNull(),
  expiresAt: text("expires_at").notNull(),
}, table => [uniqueIndex("exit_ticket_sessions_token_unique").on(table.tokenHash)]);

export const exitTickets = sqliteTable("exit_tickets", {
  id: text("id").primaryKey(),
  ownerSessionId: text("user_id").notNull(),
  studentName: text("student_name").notNull(),
  studentId: text("student_id").notNull(),
  lessonNumber: integer("lesson_number").notNull(),
  question: text("question").notNull(),
  answer: text("answer").notNull(),
  uncertainty: text("uncertainty").notNull(),
  createdAt: text("created_at").notNull(),
  updatedAt: text("updated_at").notNull(),
  revision: integer("revision").notNull().default(1),
}, table => [
  uniqueIndex("exit_tickets_user_lesson_unique").on(table.ownerSessionId, table.lessonNumber),
  index("exit_tickets_lesson_updated_idx").on(table.lessonNumber, table.updatedAt),
]);

export const teachingFeedback = sqliteTable("teaching_feedback", {
  lessonNumber: integer("lesson_number").notNull(),
  pace: text("pace").notNull(),
  comment: text("comment").notNull(),
}, table => [index("teaching_feedback_lesson_idx").on(table.lessonNumber)]);
