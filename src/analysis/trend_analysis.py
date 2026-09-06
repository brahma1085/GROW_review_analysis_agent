import json
import structlog
from typing import List, Optional, Dict

from src.models.theme import ThemeResult, TrendResult, TrendSignal, Theme
from src.models.enums import TrendType
from src.models.pulse import WeeklyAggregate
from src.analysis.llm_client import LLMClient
from src.prompts.trend_analysis_prompt import TREND_ANALYSIS_SYSTEM_PROMPT, TREND_ANALYSIS_USER_PROMPT

logger = structlog.get_logger(__name__)

class TrendAnalysisService:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def analyze_trends(self, current: ThemeResult, historical: Optional[WeeklyAggregate]) -> TrendResult:
        logger.info(f"Analyzing trends for {len(current.themes)} themes.")
        
        # Prepare data for LLM
        themes_data = []
        historical_themes_by_name = {}
        
        if historical:
            for pt in historical.themes:
                historical_themes_by_name[pt.theme.name.lower()] = pt.theme

        for theme in current.themes:
            theme_info = {
                "theme_id": theme.id,
                "name": theme.name,
                "description": theme.description,
                "review_percentage": theme.review_percentage
            }
            
            # Determine pre-calculated trend
            trend_type = TrendType.NEW
            volume_change_pct = None
            
            if historical:
                hist_theme = historical_themes_by_name.get(theme.name.lower())
                if hist_theme:
                    volume_change_pct = round(((theme.review_count - hist_theme.review_count) / max(hist_theme.review_count, 1)) * 100, 2)
                    
                    if volume_change_pct > 10.0:
                        trend_type = TrendType.GROWING
                    elif volume_change_pct < -10.0:
                        trend_type = TrendType.DECLINING
                    else:
                        trend_type = TrendType.PERSISTENT
                        
            theme_info["trend_type"] = trend_type.value
            if volume_change_pct is not None:
                theme_info["volume_change_pct"] = volume_change_pct
                
            themes_data.append(theme_info)

        # Call LLM
        prompt = TREND_ANALYSIS_USER_PROMPT.format(themes_data_json=json.dumps(themes_data, indent=2))
        
        try:
            response = self.llm_client.analyze_batch_json(
                prompt=prompt,
                system_prompt=TREND_ANALYSIS_SYSTEM_PROMPT
            )
            llm_trends = response.get("trends", [])
        except Exception as e:
            logger.error(f"Failed to get trend analysis from LLM: {e}")
            llm_trends = []

        # Map LLM response back to TrendSignals
        llm_trend_map = {t["theme_id"]: t for t in llm_trends}
        
        emerging = []
        growing = []
        declining = []
        persistent = []
        new_themes = []
        
        for theme_info, theme_obj in zip(themes_data, current.themes):
            llm_data = llm_trend_map.get(theme_obj.id, {})
            
            signal = TrendSignal(
                theme=theme_obj,
                trend_type=TrendType(theme_info["trend_type"]),
                evidence=llm_data.get("evidence", f"Theme accounted for {theme_info['review_percentage']}% of reviews."),
                interpretation=llm_data.get("interpretation", "No interpretation available."),
                recommendation=llm_data.get("recommendation", "Monitor this area closely."),
                volume_change_pct=theme_info.get("volume_change_pct")
            )
            
            # Categorize
            if signal.trend_type == TrendType.NEW:
                new_themes.append(signal)
            elif signal.trend_type == TrendType.GROWING:
                growing.append(signal)
                if signal.volume_change_pct and signal.volume_change_pct > 30.0:
                    emerging.append(signal)
            elif signal.trend_type == TrendType.DECLINING:
                declining.append(signal)
            elif signal.trend_type == TrendType.PERSISTENT:
                persistent.append(signal)
                
        return TrendResult(
            emerging=emerging,
            growing=growing,
            declining=declining,
            persistent=persistent,
            new_themes=new_themes,
            data_availability_note=None if historical else "No historical data available for comparison. All themes are marked as NEW."
        )
