# OpenClaw Homework Helper

Help K12 parents check homework from Telegram photos, generate bilingual Gemini assessments, and persist results to SQLite.

## Current Architecture

- `skills/homework-helper/SKILL.md` is the modern OpenClaw workspace skill.
- `SKILL.md` at the repository root keeps the repo installable as a standalone skill source.
- `app/cli.py` is the single shell-command entrypoint OpenClaw should invoke.
- `app/main.py::run(event)` is the main executable workflow.
- `app/telegram_handler.py` receives Telegram text/photos and calls the same workflow.
- `app/gemini_client.py` preserves Gemini integration.
- `app/db.py` owns SQLite initialization, writes, and reads.

## Routing Flow

1. OpenClaw loads workspace skills from `skills/<skill-name>/SKILL.md`.
2. Homework-related image intent semantically matches `homework-helper`.
3. Skill instructions tell OpenClaw to run `python3 -m app.cli`, not answer directly with the base multimodal model.
4. `app.cli` normalizes arguments or event JSON and invokes `app.main.run(event)`.
5. `app.main.run` loads local image bytes or downloads Telegram photo bytes.
6. Gemini analyzes the homework.
7. SQLite writes the result to `homework.db`.
8. Structured JSON is printed to stdout for OpenClaw or Telegram to reply with.

## Environment

Required:

```bash
export GEMINI_API_KEY="..."
```

Required for Telegram photo downloads:

```bash
export TELEGRAM_BOT_TOKEN="..."
```

Optional:

```bash
export LOG_LEVEL=DEBUG
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Local CLI Test Commands

Dry run routing without Gemini or SQLite:

```bash
python3 -m app.cli --image /absolute/path/to/homework.jpg --text "check this worksheet" --user "debug-parent" --dry-run --debug
```

Grade a local image:

```bash
python3 -m app.cli --image /absolute/path/to/homework.jpg --text "Please grade this homework" --user "debug-parent" --debug
```

Simulate an OpenClaw event:

```bash
python3 -m app.cli --event-json '{"user":"parent","text":"check answers","image_path":"/absolute/path/to/homework.jpg"}' --debug
```

Simulate Telegram photo metadata:

```bash
python3 -m app.cli --event-json '{"user":"telegram-user","text":"worksheet photo","photo":[{"file_id":"TELEGRAM_FILE_ID"}]}' --debug
```

## Example OpenClaw Invocation

From the workspace skill:

```bash
cd skills/homework-helper/../.. && python3 -m app.cli --image /absolute/path/to/homework.jpg --text "check this worksheet" --user "openclaw-user"
```

From the repository root:

```bash
python3 -m app.cli --image /absolute/path/to/homework.jpg --text "check this worksheet" --user "openclaw-user"
```

## Expected Logs

Logs are emitted to stderr so stdout remains structured JSON.

Expected successful path:

```text
INFO app.cli OpenClaw homework-helper CLI invoked
INFO app.main Homework workflow invoked
INFO app.db Initializing SQLite schema
INFO app.main Local homework image loaded
INFO app.gemini_client Calling Gemini for homework assessment
INFO app.db Writing homework assessment to SQLite
INFO app.db Homework assessment stored
INFO app.main Homework workflow completed
```

Expected Telegram photo path:

```text
INFO app.telegram_handler Telegram image message received
INFO app.main Telegram image receipt normalized
INFO app.telegram_utils Requesting Telegram file metadata
INFO app.telegram_utils Downloading Telegram image bytes
INFO app.telegram_utils Telegram image downloaded
```

Failures include stack traces with:

```text
ERROR app.gemini_client Gemini client initialization failed: GEMINI_API_KEY not set
ERROR app.db SQLite write failed
ERROR app.main Homework workflow failed
```

## Migration Notes

- Replaced legacy lowercase `skill.md` with modern `SKILL.md` files that use YAML frontmatter.
- Added `skills/homework-helper/SKILL.md` because OpenClaw workspace discovery checks `<workspace>/skills`.
- Removed deprecated Python plugin entrypoint assumptions. The skill now uses shell-command execution via `python3 -m app.cli`.
- SQLite path handling now uses `Path(__file__).resolve().parent.parent / "homework.db"` for deterministic storage.
- Existing `homework_logs` schema is preserved.
- Gemini and Telegram integration code remain in place, with logging and shared workflow invocation added.

## Why SQLite Writes May Have Failed Before

- The previous skill was lowercase `skill.md` at the repository root, so modern OpenClaw workspace loading could miss it.
- If OpenClaw answered with the base multimodal model, `app.main.run` was bypassed entirely and no SQLite write occurred.
- `app/main.py` initialized SQLite at import time, which made failures harder to attribute.
- Results were stored with `str(answer_json)`, which is not valid JSON for weekly report parsing.
- `weekly_report.py` referenced `get_all_logs` and `client` in ways that could fail at runtime.
