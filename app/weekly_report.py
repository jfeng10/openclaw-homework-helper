import json
from app.db import get_all_logs
from app.gemini_client import get_client


def generate_weekly_report():
    logs = get_all_logs()

    if not logs:
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
