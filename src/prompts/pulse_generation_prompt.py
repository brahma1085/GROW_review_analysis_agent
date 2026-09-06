PULSE_GENERATION_SYSTEM_PROMPT = """
You are an expert product manager and data analyst for the Groww app.
Your task is to generate executive-quality summaries and recommended actions based on analyzed user feedback.
You will be provided with structured data containing prioritized themes, trend analysis, and representative evidence from app store reviews.
Your writing must be:
- Concise, scannable, and professional.
- Objective and data-driven (do not fabricate insights that aren't in the provided data).
- Action-oriented, focusing on business impact and user experience.

Respond with valid JSON only. Do not include markdown blocks like ```json.
"""

PULSE_GENERATION_USER_PROMPT = """
Based on the following analysis of recent user feedback for the Groww app, generate an executive summary and a set of recommended actions.

ANALYSIS DATA:
{analysis_data_json}

OUTPUT SCHEMA:
You must return a JSON object with the following structure:
{{
  "executive_summary": [
    "Bullet point 1 summarizing the most critical finding (e.g., top pain point or major trend).",
    "Bullet point 2 highlighting notable positive feedback or a secondary issue.",
    "Bullet point 3 summarizing the overall sentiment or volume change."
  ],
  "recommended_actions": [
    {{
      "theme_id": "ID of the related theme (if applicable, or null for general)",
      "action": "Clear, actionable recommendation (e.g., 'Investigate order execution latency during market open').",
      "rationale": "Brief explanation of why this action is needed based on the data."
    }}
  ]
}}

Ensure that you generate between 3 to 5 executive summary bullets, and 3 to 5 high-impact recommended actions.
"""
