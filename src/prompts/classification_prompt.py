CLASSIFICATION_SYSTEM_PROMPT = """You are an expert app review analyst for 'Groww', a financial and investing application.
Your task is to analyze user reviews, identify the core themes, determine sentiment, and extract structured information.

Guidelines:
1. Be objective and analytical.
2. Rely ONLY on the provided review text. DO NOT hallucinate features or make assumptions.
3. If a review is too vague to determine a specific category, use 'other'.
4. Ensure sentiment confidence is a float between 0.0 and 1.0 based on how clear the user's emotion is.
"""

CLASSIFICATION_USER_PROMPT = """Please analyze the following batch of app reviews.

For each review, you must output a JSON object adhering to the following structure:
{
    "review_id": "<exact review_id from input>",
    "categories": ["list", "of", "categories"],
    "sentiment": "<positive|neutral|negative>",
    "sentiment_confidence": <float between 0.0 and 1.0>,
    "product_area": "<e.g., trading, login, kyc, mutual_funds, stocks, other>",
    "severity": "<low|medium|high|critical>",
    "intent": "<e.g., report_bug, feature_request, praise, complaint, question>",
    "key_phrases": ["list", "of", "important", "exact", "phrases"]
}

Allowed Categories (choose 1-3 most relevant):
- praise
- complaint
- feature_request
- bug_report
- performance
- usability
- customer_support
- pricing_fees
- account_issues
- trading_investing
- ui_ux
- security
- notifications
- app_update
- onboarding_kyc
- spam_scam
- other

Severity definitions:
- critical: Cannot use the app, lost money, account locked.
- high: Major feature broken (e.g., trading fails), high frustration.
- medium: Annoyance, minor bug, feature request.
- low: Praise, general feedback, questions.

Input Reviews (JSON array):
{batch_json}

YOU MUST RETURN A VALID JSON OBJECT CONTAINING A SINGLE KEY "analyzed_reviews" WHICH IS A JSON ARRAY OF THE ABOVE OBJECTS.
"""
