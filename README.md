# GROWW Review Analysis Agent

A sophisticated, AI-powered agent designed to automatically collect, process, and analyze Google Play Store reviews for the GROWW app (or any target application). The agent leverages LLMs for sentiment analysis, categorization, theme discovery, and generates structured "Weekly Pulse" reports that are automatically delivered via Google Docs and Gmail using the Model Context Protocol (MCP).

## Overview

The GROWW Review Analysis Agent performs the following tasks:
1. **Collection**: Scrapes recent reviews from the Google Play Store using incremental fetching.
2. **Processing**: Normalizes text, detects language, and removes near-duplicates.
3. **AI Analysis**: Uses an LLM to perform zero-shot classification, extract sentiment, and identify product-specific categories.
4. **Theme & Trend Discovery**: Groups reviews into actionable themes, compares them with historical data to identify emerging issues, and calculates priority scores.
5. **Report Generation**: Structures a comprehensive markdown report.
6. **Delivery**: Connects to Google Docs and Gmail via MCP to distribute the findings to stakeholders.

## Prerequisites

- Python 3.10+
- An OpenAI API Key (or compatible LLM provider)
- An MCP Server configured for Google Drive/Docs and Gmail (e.g., standard MCP Google integrations)
- Windows environment (instructions assume Windows paths and Python execution)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd GROW_review_analysis_agent
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The agent uses a two-file configuration approach:

### 1. `config/config.yaml`
This is the primary configuration file that controls agent behavior, collection settings, prompt engineering, and MCP endpoints. **The `mcp_server_url` and `mcp_api_key` MUST be configured in this file, not in `.env`.**

Example `config.yaml` highlights:
```yaml
app:
  package_id: "com.nextbillion.groww"
  name: "GROWW"

collection:
  days_to_fetch: 7
  max_reviews: 1000

mcp:
  # The URL of your local or remote MCP server for Google integrations
  server_url: "http://localhost:8000"
  api_key: "your_mcp_api_key_here"
```
*(See the provided `config/config.yaml` for all options).*

### 2. `.env`
This file stores sensitive credentials primarily for the LLM. 
Copy the provided example to create your own:
```bash
cp .env.example .env
```
Ensure your `.env` contains:
```env
OPENAI_API_KEY=your_openai_api_key
```

## Running the Agent

You can run the agent manually or set it up on a scheduler (like Windows Task Scheduler or cron).

**Manual Execution:**
```bash
# Ensure virtual environment is active
.\.venv\Scripts\activate

# Run the main pipeline
python main.py
```

**Custom Configuration:**
```bash
python main.py --config config/custom_config.yaml
```

## Output and History

- **Local Storage**: Raw and processed data, as well as generated markdown pulses, are stored in `data/reviews/`, `data/processed/`, and `data/pulses/`.
- **Historical Trends**: Historical aggregates are automatically stored in `data/history/` to support trend analysis week-over-week.
- **Delivery**: Upon successful execution, the final report will be available in Google Docs and a draft summary will be created in your Gmail account. The console output will include the Google Doc URL.

## How to Configure for a Different App

The agent is highly modular and can be retargeted to any app on the Google Play Store with zero code changes:

1. **Update `config.yaml`**:
   Change the `package_id` and `name` under the `app` section.
   ```yaml
   app:
     package_id: "com.spotify.music"
     name: "Spotify"
   ```
2. **Customize Category Taxonomy (Optional)**:
   Modify the classification prompts or threshold weights in `config.yaml` to better suit the new app's domain (e.g., changing financial categories to music categories).
3. **Adjust Priority Weights (Optional)**:
   Tune the `thresholds` in `config.yaml` based on the new app's expected review volume.
4. **Run the agent**:
   The agent will automatically create new storage directories for the new app data.

## Troubleshooting

- **MCP Connection Failures**: Ensure the MCP server is running at the configured `mcp_server_url` and the `mcp_api_key` matches. Check `logs/` for detailed HTTP errors.
- **LLM Rate Limits**: If processing fails due to quota limits, consider reducing `collection.max_reviews` in `config.yaml`.
- **Pydantic Validation Errors**: Ensure the LLM is responding in strict JSON as prompted. The agent has fallback validation, but overly complex inputs may require prompt tuning in `config.yaml`.

## Testing

The project includes a comprehensive test suite covering unit tests and end-to-end integration paths.
```bash
python -m pytest tests
```
