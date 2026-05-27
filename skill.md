---
name: homework-helper
description: Route worksheet photos, homework grading, math answer checks, school assignments, and parent education workflows through the local Gemini plus SQLite homework workflow.
homepage: https://docs.openclaw.ai/tools/skills
user-invocable: true
metadata: {"openclaw":{"requires":{"env":["GEMINI_API_KEY"]},"primaryEnv":"GEMINI_API_KEY"}}
---

# Homework Helper

Use this skill when a Telegram user, parent, student, or OpenClaw operator asks for help with:

- worksheet photos
- homework grading
- checking math answers
- school assignments
- parent education workflows
- bilingual homework explanations
- grading or reviewing an uploaded homework image

Do not answer worksheet photos directly with the base multimodal model. The local workflow must be invoked so Gemini analysis, SQLite persistence, and debug logging all run in one place.

## Required Invocation

Run the repository workflow with lightweight shell-command execution:

```bash
cd {baseDir} && python3 -m app.cli --image /absolute/path/to/homework.jpg --text "optional caption" --user "telegram-or-openclaw-user"
```

For raw OpenClaw or Telegram-style events, pass JSON:

```bash
cd {baseDir} && python3 -m app.cli --event-json '{"user":"parent","text":"Check this worksheet","image_path":"/absolute/path/to/homework.jpg"}'
```

The command prints structured JSON to stdout. Logs go to stderr. Return the JSON assessment to the user, and mention any `"error"` field if present.

## Routing Rules

When the user provides an image of homework, a worksheet, a math problem, schoolwork, a workbook page, answer checking, or asks for grading, invoke the CLI before composing a reply.

When the input comes from Telegram photo metadata, preserve the `photo` array and invoke:

```bash
cd {baseDir} && python3 -m app.cli --event-json '{"user":"telegram-user","text":"caption text","photo":[{"file_id":"TELEGRAM_FILE_ID"}]}'
```

The Python workflow downloads the Telegram image, calls Gemini, writes SQLite, and returns JSON. Do not bypass it by calling Gemini directly from the model.

## Debugging

Use this dry run to confirm OpenClaw routing without calling Gemini or writing SQLite:

```bash
cd {baseDir} && python3 -m app.cli --image /absolute/path/to/homework.jpg --text "check answers" --user "debug-user" --dry-run --debug
```
