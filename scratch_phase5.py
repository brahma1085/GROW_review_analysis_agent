import json
import os
import sys
from datetime import datetime

# Adjust path so we can import src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.review import AnalyzedReview
from src.analysis.llm_client import LLMClient
from src.analysis.theme_discovery import ThemeDiscoveryService
from src.analysis.trend_analysis import TrendAnalysisService
from src.analysis.priority_scoring import PriorityScoringService
from src.analysis.evidence_selection import EvidenceSelectionService

def load_analyzed_reviews(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return [AnalyzedReview(**r) for r in data]

def main():
    import dotenv
    dotenv.load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("Error: GROQ_API_KEY not set.")
        return
        
    llm_client = LLMClient(api_key=api_key, model_name="openai/gpt-oss-120b")
    
    # Use standard groq model
    llm_client.model_name = "openai/gpt-oss-120b"
    
    analyzed_file = "data/analysis/com.nextbillion.groww/run_20260905_181940_analyzed.json"
    
    if not os.path.exists(analyzed_file):
        print(f"Error: Could not find analyzed reviews file {analyzed_file}")
        return
        
    print(f"Loading analyzed reviews from {analyzed_file}")
    reviews = load_analyzed_reviews(analyzed_file)
    print(f"Loaded {len(reviews)} analyzed reviews.")
    
    # 1. Theme Discovery
    theme_discovery = ThemeDiscoveryService(llm_client=llm_client, max_reviews_per_chunk=30)
    print("\n--- Discovering Themes ---")
    theme_result = theme_discovery.discover_themes(reviews)
    print(f"Discovered {len(theme_result.themes)} themes. ({theme_result.unthemed_count} unthemed reviews)")
    for t in theme_result.themes:
        print(f" - {t.name}: {t.review_count} reviews ({t.review_percentage}%) - Sev: {t.severity}")
        
    # 2. Trend Analysis (First Run Scenario)
    trend_service = TrendAnalysisService(llm_client=llm_client)
    print("\n--- Analyzing Trends (First Run) ---")
    trend_result = trend_service.analyze_trends(current=theme_result, historical=None)
    print(f"Trend Analysis complete. All themes marked as NEW: {len(trend_result.new_themes)}")
    
    # 3. Priority Scoring
    priority_service = PriorityScoringService()
    print("\n--- Scoring Priorities ---")
    prioritized_themes = priority_service.score_themes(theme_result=theme_result, trend_result=trend_result)
    for pt in prioritized_themes:
        print(f" - {pt.theme.name}: Score {pt.score} ({pt.priority.value.upper()}) -> {pt.rationale}")
        
    # 4. Evidence Selection
    evidence_service = EvidenceSelectionService()
    print("\n--- Selecting Evidence ---")
    evidence_result = evidence_service.select_evidence(
        prioritized_themes=prioritized_themes, 
        all_reviews=reviews, 
        max_per_theme=2, 
        max_overall=3
    )
    
    for theme_id, excerpts in evidence_result.theme_evidence.items():
        theme_name = next(pt.theme.name for pt in prioritized_themes if pt.theme.id == theme_id)
        print(f"\nEvidence for {theme_name}:")
        for exc in excerpts:
            try:
                print(f"   > {exc.displayed_text} (Rating: {exc.star_rating})")
            except UnicodeEncodeError:
                print(f"   > [Unicode text omitted] (Rating: {exc.star_rating})")
            
    # Save results for manual inspection
    out_file = "data/phase5_output.json"
    
    output_data = {
        "themes": [pt.model_dump() for pt in prioritized_themes],
        "trends": {
            "emerging": [ts.model_dump() for ts in trend_result.emerging],
            "growing": [ts.model_dump() for ts in trend_result.growing],
            "declining": [ts.model_dump() for ts in trend_result.declining],
            "persistent": [ts.model_dump() for ts in trend_result.persistent],
            "new_themes": [ts.model_dump() for ts in trend_result.new_themes],
        },
        "evidence": evidence_result.model_dump()
    }
    
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, default=str)
        
    print(f"\nSaved Phase 5 output to {out_file}")

if __name__ == "__main__":
    main()
