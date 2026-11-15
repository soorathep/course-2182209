CREATE TABLE `teaching_feedback` (
	`lesson_number` integer NOT NULL,
	`pace` text NOT NULL,
	`comment` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `teaching_feedback_lesson_idx` ON `teaching_feedback` (`lesson_number`);