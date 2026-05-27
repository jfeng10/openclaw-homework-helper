import json
import logging

from app.db import get_all_logs
from app.gemini_client import get_client

logger = logging.getLogger(__name__)


def generate_weekly_report():
    logger.info("Generating weekly homework report")
    logs = get_all_logs()

    if not logs:
        logger.info("No homework logs available for weekly report")
        return {
            "summary": "No data this week.",
            "actions": []
        }

    summary_input = []
    for child, question, answer_json, timestamp in logs:
        summary_input.append({
            "child": child,
            "question": question,
            "answer": json.loads(answer_json),
            "time": timestamp
        })

    prompt = f"""
You are an educational analyst.

Analyze weekly homework data:

{summary_input}

Return JSON ONLY:
{{
  "weak_topics": [],
  "common_mistakes": [],
  "progress_summary": "",
  "recommended_practice": []
}}
"""

    client = get_client()
    logger.info("Calling Gemini for weekly homework report", extra={"log_count": len(logs)})
    response = client.models.generate_content(
        model="gemini-3.1-pro-preview",
        contents=prompt
    )

    return response.text

def weekly_report_task(event=None):
    """
    OpenClaw scheduled task entry point
    """
    return generate_weekly_report()
