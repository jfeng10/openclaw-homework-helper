import argparse
import json
import logging
import sys
from pathlib import Path

from app.main import run


def configure_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        stream=sys.stderr,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def _load_event(args):
    if args.event_json:
        event = json.loads(args.event_json)
    elif args.event_file:
        with open(args.event_file, "r", encoding="utf-8") as event_file:
            event = json.load(event_file)
    else:
        event = {}

    if args.user:
        event["user"] = args.user
    if args.text:
        event["text"] = args.text
    if args.image:
        event["image_path"] = str(Path(args.image).resolve())

    return event


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Run the OpenClaw homework-helper workflow and print JSON to stdout."
    )
    parser.add_argument("--image", help="Local homework image path to grade.")
    parser.add_argument("--text", default="", help="Optional homework question or caption.")
    parser.add_argument("--user", default="local-cli", help="User or child identifier.")
    parser.add_argument("--event-json", help="Raw OpenClaw/Telegram-style event JSON.")
    parser.add_argument("--event-file", help="Path to a JSON event file.")
    parser.add_argument("--debug", action="store_true", help="Enable verbose workflow logs on stderr.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate event routing without calling Gemini or writing SQLite.",
    )
    args = parser.parse_args(argv)

    configure_logging(args.debug)
    logger = logging.getLogger(__name__)

    try:
        event = _load_event(args)
        logger.info(
            "OpenClaw homework-helper CLI invoked",
            extra={
                "event_keys": sorted(event.keys()),
                "has_image_path": bool(event.get("image_path")),
                "dry_run": args.dry_run,
            },
        )

        if args.dry_run:
            result = {
                "ok": True,
                "dry_run": True,
                "event_keys": sorted(event.keys()),
                "would_invoke": "app.main.run",
                "has_image": bool(event.get("image_path") or event.get("photo") or event.get("image_bytes")),
            }
        else:
            result = run(event)

        print(json.dumps(result, ensure_ascii=False, default=str))
        return 0 if "error" not in result else 1
    except Exception as exc:
        logging.getLogger(__name__).exception("CLI workflow execution failed")
        print(
            json.dumps(
                {
                    "error": str(exc),
                    "metadata": {"workflow": "app.cli.main", "persisted": False},
                },
                ensure_ascii=False,
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
