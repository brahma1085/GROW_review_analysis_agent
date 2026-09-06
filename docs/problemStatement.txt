# PROBLEM STATEMENT: Groww Weekly User Feedback Intelligence AI Agent

**Version:** 1.0  
**Target Platform:** Groww mobile application  
**Primary Public Source:** Google Play Store reviews  
**Primary Delivery Surfaces:** Google Docs and Gmail  
**Implementation Target:** Antigravity  

## 1. PROJECT OVERVIEW

Build an intelligent AI agent that converts raw public user feedback for the Groww mobile application into a concise, evidence-backed weekly product feedback pulse.

The agent must collect and aggregate public mobile-store reviews for the Groww app, clean and normalize the feedback, identify recurring themes and emerging issues, summarize what users are saying, preserve representative user voice through selected review excerpts, identify sentiment and priority signals, and generate actionable recommendations for the product/team.

The final weekly pulse must be delivered through familiar Google Workspace surfaces:

1.  A structured Google Doc containing the weekly feedback pulse.
2.  A Gmail draft containing a concise executive summary and a link/reference to the Google Doc, ready for the user to review and send to themselves or their intended recipients.

The system must avoid requiring the user or AI agent to implement OAuth credential management, Google REST API wiring, token handling, or low-level Google API integration directly. These responsibilities should be delegated to an external MCP server hosted on Railway, communicated via Server-Sent Events (SSE).

The project should be designed as a reusable intelligent feedback-analysis agent rather than a one-off script.

## 2. BUSINESS OBJECTIVE

Product teams receive large volumes of user reviews, making it difficult to manually understand:

-   What users care about most.
-   Which problems are recurring.
-   Which issues are becoming more prominent.
-   What users like or appreciate.
-   What users dislike or struggle with.
-   Whether sentiment is improving or deteriorating.
-   What representative users actually said.
-   Which issues may require product, engineering, UX, support, or communication action.

The agent should turn this raw feedback into a weekly pulse that a team member can scan in a few minutes and immediately understand:

**WHAT HAPPENED | WHAT USERS SAID | WHY IT MATTERS | WHAT SHOULD HAPPEN NEXT**

## 3. TARGET APPLICATION

The initial target application is:

**Groww – Stocks, Mutual Fund, IPO**

Google Play Store application:
https://play.google.com/store/apps/details?id=com.nextbillion.groww&hl=en_IN

The architecture must not hard-code the solution so tightly to Groww that it cannot later support another application/store.

## 4. CORE USER JOURNEY

The expected end-to-end workflow is:

1.  Trigger the weekly feedback pulse generation.
2.  Identify the configured Groww Google Play Store application.
3.  Retrieve available public reviews for the configured period/source.
4.  Store or process the raw review data.
5.  Clean, normalize, deduplicate, and validate the reviews.
6.  Analyze each review for:
    -   sentiment
    -   topic/theme
    -   intent/problem type
    -   product area
    -   severity/impact indicators
    -   feature/request/complaint/praise classification
7.  Aggregate reviews into recurring themes.
8.  Detect emerging or increasing themes.
9.  Compare with the previous reporting period when historical data is available.
10. Select representative review excerpts.
11. Generate an evidence-backed weekly pulse.
12. Append/create the formatted pulse in Google Docs.
13. Create a Gmail draft containing the executive summary and Google Doc reference.
14. Report completion, source coverage, processing statistics, and any failures.

## 5. PRIMARY FUNCTIONAL REQUIREMENTS

### 5.1 Review Collection

The agent must be able to collect public Google Play Store reviews associated with the Groww application.

The collector should support:

-   Application/package identifier configuration.
-   Store/source configuration.
-   Reporting date range.
-   Pagination.
-   Configurable maximum review count.
-   Review date.
-   Review text.
-   Star rating.
-   Reviewer/display name when publicly available and appropriate.
-   Review identifier when available.
-   Developer response when available.
-   Review language when detectable.
-   Review version/app version when available.
-   Source URL/reference when available.

Only publicly available review information should be processed.

The solution must not attempt to obtain private user information, private account data, financial account information, passwords, authentication tokens, or other non-public information.

### 5.2 Incremental Collection

The system should support incremental collection so that the same historical reviews are not unnecessarily processed every week.

Maintain sufficient metadata to determine:

-   Last successful collection timestamp.
-   Reporting period.
-   Review identifiers already processed.
-   Source coverage.
-   Collection status.
-   Collection failures.

If the source does not provide a stable review identifier, use a robust deduplication strategy based on available review attributes.

### 5.3 Data Cleaning and Normalization

Before AI analysis, reviews should be normalized.

The pipeline should:

-   Remove exact duplicates.
-   Detect near duplicates where practical.
-   Normalize whitespace.
-   Preserve the original review text.
-   Detect language.
-   Handle emojis and common informal mobile-review language.
-   Preserve important domain terminology.
-   Avoid changing the meaning of the original review.
-   Handle empty or unusable reviews gracefully.

The original review must remain available for evidence/reference.

### 5.4 Review Classification

Each review should be classified into one or more meaningful categories.

Minimum classifications:

-   Praise
-   Complaint
-   Feature request
-   Bug/problem report
-   Question/confusion
-   Performance issue
-   Usability/UX issue
-   Customer support/service issue
-   Pricing/charges issue
-   Trading/investment experience issue
-   Account/KYC/onboarding issue
-   Notification issue
-   Login/authentication issue
-   Mutual fund experience
-   Stock experience
-   IPO experience
-   Other

The taxonomy must be extensible.

### 5.5 Sentiment Analysis

Analyze sentiment at review level.

Minimum sentiment labels:

-   Positive
-   Neutral
-   Negative
-   Mixed

Where useful, generate a confidence score.

Do not treat sentiment as the only indicator of importance. A neutral review may contain a highly important product problem, and a negative review may be an isolated issue.

### 5.6 Theme Extraction

The agent must discover recurring themes rather than relying exclusively on predefined categories.

For each theme, identify:

-   Theme name.
-   Short description.
-   Number of reviews.
-   Percentage of analyzed reviews.
-   Sentiment distribution.
-   Representative evidence.
-   Product area.
-   Severity/impact indicators.
-   Whether it is recurring or emerging.
-   Recommended action.

Examples of possible themes include:

-   App performance/slow loading.
-   Login or OTP problems.
-   KYC/onboarding friction.
-   Customer support responsiveness.
-   Trading execution experience.
-   Portfolio visibility.
-   Mutual fund transaction experience.
-   IPO workflow.
-   Charges/fees/transparency.
-   Notifications.
-   UI/UX changes.
-   Feature requests.

These are examples only. The agent must discover actual themes from the collected feedback.

### 5.7 Emerging Theme Detection

The agent should identify themes that appear to be emerging or changing materially.

When historical data is available, compare the current week with prior weeks.

Potential signals:

-   Increase in review volume.
-   Increase in negative sentiment.
-   Increase in star-rating concentration.
-   New theme appearing for the first time.
-   Significant growth of an existing theme.
-   Sudden concentration of similar complaints.
-   Repeated reports of the same issue.

The system must clearly distinguish:

-   Observed evidence.
-   AI interpretation.
-   Recommendation.

Do not present an inference as a confirmed product defect unless the evidence supports that statement.

### 5.8 Priority Scoring

Assign a priority signal to themes using multiple factors.

Suggested factors:

-   Frequency.
-   Negative sentiment.
-   Severity language.
-   Recency.
-   Growth versus previous period.
-   Breadth across users.
-   Potential user/business impact.

Suggested priority levels:

-   Critical
-   High
-   Medium
-   Low

The scoring logic should be transparent and configurable.

### 5.9 Representative User Voice

The weekly pulse must include carefully selected representative review excerpts.

Selection criteria:

-   Representative of the theme.
-   Clear and understandable.
-   Evidence-based.
-   Recent where appropriate.
-   Avoid excessive repetition.
-   Prefer excerpts that explain the underlying user problem.

Do not fabricate or paraphrase a quote and present it as an exact user quote.

If a review is shortened for display, clearly indicate that it is an excerpt.

Avoid exposing unnecessary personal information from reviewers.

## 6. WEEKLY PULSE OUTPUT

The generated weekly pulse should follow a consistent structure.

Recommended structure:

**TITLE:** Groww Weekly User Feedback Pulse  
**Reporting period:** –

### 6.1. EXECUTIVE SUMMARY

A concise 5–10 bullet summary covering:

-   Overall user sentiment.
-   Most important positive signal.
-   Most important negative signal.
-   Top recurring issue.
-   Most important emerging issue.
-   Important feature requests.
-   Material changes versus previous week.
-   Recommended focus areas.

### 6.2. WEEK AT A GLANCE

Include metrics such as:

-   Reviews analyzed.
-   Average star rating, when available.
-   Positive/neutral/negative/mixed distribution.
-   Number of major themes.
-   Number of emerging themes.
-   Number of high/critical priority themes.

### 6.3. TOP USER THEMES

For each major theme:

-   Theme name.
-   Priority.
-   Review count.
-   Share of reviews.
-   Sentiment.
-   Trend versus previous week.
-   What users are saying.
-   Representative review excerpts.
-   Likely product implication.
-   Recommended next action.

### 6.4. WHAT USERS LOVE

Summarize recurring positive feedback.

Examples may include:

-   Product strengths.
-   Features users appreciate.
-   Ease-of-use wins.
-   Performance improvements.
-   Support experiences.
-   Investment/trading capabilities users value.

Only include findings supported by the reviews.

### 6.5. TOP PAIN POINTS

Summarize the most significant negative experiences.

For each pain point:

-   Problem.
-   Evidence.
-   Frequency.
-   Sentiment.
-   Severity.
-   Trend.
-   Suggested owner/function where inferable.

### 6.6. EMERGING SIGNALS

Highlight newly appearing or rapidly growing themes.

Clearly label whether the signal is:

-   New.
-   Growing.
-   Declining.
-   Persistent.

### 6.7. FEATURE REQUESTS

Aggregate repeated feature requests.

For each:

-   Requested capability.
-   Number of supporting reviews.
-   Representative evidence.
-   Potential user value.
-   Priority signal.

### 6.8. REPRESENTATIVE USER VOICE

Provide a small curated set of review excerpts that capture the week’s most important feedback.

### 6.9. RECOMMENDED ACTIONS

Translate insights into practical actions.

Examples:

-   Investigate a suspected recurring issue.
-   Review UX flow.
-   Validate performance issue.
-   Improve support communication.
-   Evaluate feature request.
-   Monitor an emerging issue.
-   Communicate an existing improvement.

Recommendations must be grounded in evidence and must not claim certainty where evidence is insufficient.

### 6.10. METHODOLOGY AND COVERAGE

Include:

-   Source.
-   Application identifier.
-   Reporting period.
-   Collection timestamp.
-   Number of reviews collected.
-   Number analyzed.
-   Deduplication count.
-   Languages detected.
-   Any collection limitations.
-   Any AI-analysis limitations.
-   Comparison period used.

## 7. GOOGLE DOC REQUIREMENTS

The agent must create or append the weekly pulse to a Google Doc through the configured Google Docs MCP capability.

The document should be professionally formatted.

Recommended formatting:

-   Document title.
-   Reporting period.
-   Executive summary.
-   Metric table.
-   Theme sections.
-   Priority indicators.
-   Evidence/review excerpts.
-   Recommended actions.
-   Methodology.

Use headings, bullets, tables, spacing, and emphasis appropriately.

Do not dump raw JSON or unformatted AI output into the document.

The Google Doc operation should support:

-   Create document when configured.
-   Append a new weekly pulse to an existing document when configured.
-   Preserve previous weekly reports.
-   Add clear weekly separators.
-   Apply proper formatting.
-   Return the document URL/reference when available.

The agent should avoid accidentally overwriting previous reports.

## 8. GMAIL REQUIREMENTS

The agent must create a Gmail draft through the configured Gmail MCP capability.

The email should be concise and executive-friendly.

Suggested structure:

**Subject:** Groww Weekly User Feedback Pulse –

**Body:**
-   One-paragraph executive summary.
-   3–7 most important findings.
-   Top recommended actions.
-   Link/reference to the Google Doc.
-   Coverage/methodology note where useful.

The system should create a DRAFT rather than automatically sending an email unless an explicit send operation is configured and authorized.

The user should be able to review and edit the draft before sending.

## 9. MCP / INTEGRATION REQUIREMENTS

The project must connect to an external MCP server (e.g. hosted on Railway) via an SSE client.

Expected integrations:

1.  Review source/data acquisition capability.
2.  Google Docs MCP.
3.  Gmail MCP.

The AI agent should not contain unnecessary low-level REST integration logic for Gmail or Google Docs.

The MCP layer should abstract:

-   Authentication.
-   OAuth flows.
-   Access tokens.
-   API requests.
-   Request formatting.
-   Response parsing.
-   Service-specific error handling.

The AI agent should interact with integrations through clear, typed tool interfaces.

## 10. SUGGESTED MCP TOOL CONTRACTS

The exact names may be adjusted during implementation.

**Review/data tools:**
-   fetch_reviews
-   get_collection_status
-   get_previous_period_data

**Analysis tools/services:**
-   analyze_reviews
-   cluster_themes
-   compare_periods
-   generate_weekly_pulse

**Google Docs tools:**
-   create_document
-   append_formatted_content
-   get_document_reference

**Gmail tools:**
-   create_draft

The AI agent should choose tools based on the current task rather than hard-code a fixed sequence where unnecessary.

## 11. AGENTIC BEHAVIOR

The solution should behave as an intelligent agent, not simply a sequential ETL script.

The agent should:

-   Understand the reporting objective.
-   Determine which data it needs.
-   Inspect source availability.
-   Select appropriate tools.
-   Analyze evidence.
-   Detect missing information.
-   Validate its own conclusions.
-   Generate a structured output.
-   Deliver the output to the requested surfaces.
-   Explain failures or limitations.

The agent should not blindly produce a report when the input data is incomplete.

## 12. SELF-VALIDATION

Before publishing the weekly pulse, perform validation.

Checks should include:

-   Did review collection succeed?
-   Is the reporting period correct?
-   Are there enough reviews for meaningful analysis?
-   Were duplicates removed?
-   Are theme counts internally consistent?
-   Do percentages approximately reconcile?
-   Are quotes present in the source data?
-   Are recommendations supported by evidence?
-   Are trend claims supported by historical data?
-   Is the Google Doc content complete?
-   Was the Gmail draft successfully created?

If validation fails, the agent should correct the issue where possible or clearly report the limitation.

## 13. SOURCE GROUNDING

Every major insight should be traceable to collected review evidence.

The generated report should avoid hallucinations.

Rules:

-   Never invent reviews.
-   Never invent user quotes.
-   Never invent review counts.
-   Never invent trends.
-   Never claim a feature exists unless supported by source data or configured product knowledge.
-   Clearly separate observed facts from inferred implications.
-   Preserve source references where available.

## 14. ERROR HANDLING

The system must handle:

-   Store/source unavailable.
-   Rate limits.
-   Network failures.
-   Pagination failures.
-   Partial collection.
-   Invalid review data.
-   Duplicate data.
-   AI analysis failure.
-   LLM timeout.
-   Google Docs failure.
-   Gmail failure.
-   Authentication/permission failure through MCP.
-   Malformed MCP responses.

Use retries with sensible limits for transient failures.

Do not silently suppress failures.

If review collection partially succeeds, the report must disclose the limitation.

If Google Docs succeeds but Gmail fails, do not regenerate the analysis unnecessarily. Report the Google Docs success and Gmail failure separately.

If Gmail succeeds but Docs fails, clearly report that the email draft was created without a valid document reference, if applicable.

## 15. DATA STORAGE

The architecture should support persistence of:

-   Raw reviews.
-   Normalized reviews.
-   Review IDs/hashes.
-   Analysis results.
-   Theme assignments.
-   Weekly aggregates.
-   Historical weekly pulses.
-   Collection metadata.
-   Error logs.

Storage implementation should be modular so it can later use a relational database, document database, or other suitable persistence layer.

Do not store credentials in the application database.

## 16. CONFIGURATION

Configuration should be externalized.

At minimum:

-   Application name.
-   Google Play package/application ID.
-   Review source.
-   Reporting period.
-   Maximum reviews.
-   Minimum review count threshold.
-   Theme taxonomy.
-   Priority thresholds.
-   Historical comparison period.
-   Google Docs target document.
-   Gmail recipient(s), where configured.
-   LLM/model configuration.
-   Storage configuration.
-   Logging level.

Use environment variables or a secure configuration mechanism.

Never hard-code credentials or access tokens.

## 17. SECURITY AND PRIVACY

The solution processes public reviews only.

Requirements:

-   Do not collect private Groww user account information.
-   Do not request Groww login credentials.
-   Do not request financial account information.
-   Do not store Google OAuth client secrets in source code.
-   Do not log access tokens.
-   Do not expose credentials in prompts.
-   Minimize personally identifiable information from review content.
-   Avoid unnecessarily reproducing reviewer names.
-   Sanitize logs.

## 18. OBSERVABILITY

Provide structured logging for:

-   Collection start/end.
-   Number of reviews retrieved.
-   Number of duplicates.
-   Number of reviews analyzed.
-   Theme extraction results.
-   Report generation.
-   Google Docs operation.
-   Gmail draft operation.
-   Errors and retries.

Where practical, include a correlation/run ID for each weekly execution.

## 19. REPORTING METRICS

The system should calculate useful metrics such as:

-   Total reviews collected.
-   Total unique reviews.
-   Average star rating.
-   Rating distribution.
-   Sentiment distribution.
-   Theme frequency.
-   Negative-theme frequency.
-   Positive-theme frequency.
-   Week-over-week theme change.
-   New themes.
-   Growing themes.
-   Declining themes.
-   High-priority theme count.

Metric definitions must remain consistent between reporting periods.

## 20. LLM / AI DESIGN

The AI layer should be designed for reliable analytical work.

Recommended pipeline:

`RAW REVIEWS` -> `VALIDATION / CLEANING` -> `DEDUPLICATION` -> `REVIEW-LEVEL CLASSIFICATION` -> `THEME DISCOVERY / CLUSTERING` -> `SENTIMENT + PRIORITY ANALYSIS` -> `WEEK-OVER-WEEK COMPARISON` -> `EVIDENCE SELECTION` -> `WEEKLY PULSE GENERATION` -> `QUALITY VALIDATION` -> `GOOGLE DOC` & `GMAIL DRAFT`

Use structured intermediate representations rather than relying on a single large prompt to perform the entire workflow.

## 21. PROMPTING REQUIREMENTS

Prompts should explicitly instruct the model to:

-   Use only supplied review evidence.
-   Distinguish facts from inference.
-   Avoid hallucination.
-   Preserve user intent.
-   Not fabricate quotes.
-   Not exaggerate isolated feedback.
-   Consider frequency and trend.
-   Highlight uncertainty.
-   Produce concise executive-level writing.

Structured JSON/schema outputs should be preferred for intermediate AI analysis.

## 22. EXTENSIBILITY

Although Groww is the initial target, the system should support future configuration for:

-   Other Google Play applications.
-   Other app stores where legally and technically supported.
-   Different review sources.
-   Different reporting frequencies.
-   Different output templates.
-   Different Google Docs destinations.
-   Different email recipients.
-   Different theme taxonomies.

Groww-specific configuration should be separated from generic agent logic.

## 23. SCHEDULING

The solution should support weekly execution.

Preferred behavior:

-   Run once per week.
-   Determine the previous reporting period automatically.
-   Collect only required incremental/new data where possible.
-   Compare with the previous weekly period.
-   Generate the report.
-   Update the Google Doc.
-   Create the Gmail draft.

The exact scheduling mechanism may be implemented according to the deployment environment.

## 24. FAILURE AND PARTIAL-DATA POLICY

The agent must never hide incomplete coverage.

Examples:

If only 60% of the expected reviews could be collected: “Review collection was partially successful; findings are based on the available 60% coverage.”

If historical data is unavailable: “Week-over-week trend analysis is unavailable because no comparable historical dataset was found.”

If a theme has low sample size: “Low-volume signal; monitor before treating as a broad user trend.”

This transparency is mandatory.

## 25. ACCEPTANCE CRITERIA

The project is considered successful when:

1.  The agent can identify the configured Groww Google Play application.
2.  It can collect public reviews for a specified weekly period.
3.  It can clean and deduplicate the review dataset.
4.  It can analyze sentiment and review categories.
5.  It can discover recurring themes.
6.  It can identify emerging themes when sufficient historical data exists.
7.  It can calculate meaningful aggregate metrics.
8.  It can select evidence-backed representative reviews.
9.  It can generate a concise weekly pulse.
10. It can create/append the pulse to Google Docs through MCP.
11. It can create a Gmail draft through MCP.
12. It does not require the application to directly implement Gmail/Google Docs REST wiring.
13. It does not require credentials to be embedded in source code.
14. It handles partial failures without losing successful work.
15. It clearly reports source limitations.
16. It does not fabricate reviews, metrics, quotes, or trends.
17. The architecture can be reused for another mobile application with configuration changes.
18. The generated Google Doc is readable and professionally formatted.
19. The Gmail draft is concise and suitable for executive review.
20. The complete workflow can be executed repeatedly on a weekly basis.

## 26. NON-FUNCTIONAL REQUIREMENTS

**Performance:**
- Avoid unnecessary repeated processing.
- Support incremental processing.
- Use batching where appropriate.

**Reliability:**
- Retry transient failures.
- Preserve intermediate results where possible.
- Make runs idempotent.

**Maintainability:**
- Separate collection, analysis, persistence, orchestration, and delivery.
- Use clean interfaces.
- Keep configuration externalized.

**Security:**
- No credentials in source code.
- No sensitive information in logs.
- Least-privilege access through integrations.

**Testability:**
- Unit tests for data cleaning.
- Unit tests for aggregation.
- Tests for theme and metric validation.
- Mock MCP integrations.
- End-to-end workflow tests.
- Failure-path tests.

## 27. SUGGESTED PROJECT COMPONENTS

- **Agent Orchestrator**
- **Review Source Adapter**
- **Review Normalizer**
- **Deduplication Service**
- **Review Analysis Service**
- **Theme Discovery Service**
- **Trend Analysis Service**
- **Priority Scoring Service**
- **Evidence/Quote Selection Service**
- **Weekly Pulse Generator**
- **Report Validator**
- **Persistence Layer**
- **Google Docs MCP Client/Adapter**
- **Gmail MCP Client/Adapter**
- **Configuration Manager**
- **Logging/Observability Module**
- **Scheduler**
- **Test Suite**

Exact technology choices may be determined during implementation, but the architecture must preserve these logical responsibilities.

## 28. EXPECTED DELIVERABLES FROM ANTIGRAVITY

Antigravity should produce:

-   Complete source code.
-   Project structure.
-   Configuration templates.
-   Environment-variable documentation.
-   MCP integration configuration/documentation.
-   Data model/schema.
-   AI prompts and structured schemas.
-   Review collection implementation.
-   Analysis pipeline.
-   Weekly report generation.
-   Google Docs integration.
-   Gmail draft integration.
-   Error handling and retry logic.
-   Logging/observability.
-   Unit tests.
-   Integration tests/mocks.
-   End-to-end test.
-   README with setup and execution instructions.
-   Example generated weekly pulse.
-   Example Gmail draft.
-   Instructions for configuring a different mobile application.

## 29. IMPORTANT IMPLEMENTATION PRINCIPLES

- **Evidence over speculation.**
- **User voice over generic summaries.**
- **Trends over isolated anecdotes.**
- **Actionable insights over raw statistics.**
- **Transparent limitations over false certainty.**
- **MCP abstractions over direct Google REST wiring.**
- **Public data only.**
- **Secure credential handling.**
- **Modular architecture.**
- **Reusable agent design.**

## 30. FINAL EXPECTED OUTCOME

The final system should behave like a Product Feedback Intelligence Agent.

Given the Groww mobile application’s public weekly review data, it should autonomously answer:

“What happened in Groww user feedback this week?”

It should then produce a compact, evidence-backed answer covering:

-   What users care about.
-   What users liked.
-   What frustrated users.
-   Which problems are recurring.
-   Which issues are emerging.
-   What users are requesting.
-   What representative users actually said.
-   What changed versus the previous week.
-   What the product team should consider doing next.

Finally, it should deliver that insight into Google Docs and prepare a Gmail draft so the user can review and send it through familiar Google Workspace surfaces.

The system should feel like an intelligent analyst working from public user feedback—not like a raw review scraper or a generic summarization script.
