import json
import os
import glob
from pathlib import Path
from typing import List, Optional, Set, Any, Dict
from datetime import datetime
from pydantic import BaseModel

from src.storage.base_store import StorageBackend
from src.models.review import RawReview, NormalizedReview, AnalyzedReview, CollectionMetadata
from src.models.theme import Theme
from src.models.pulse import WeeklyAggregate

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        return super().default(obj)

class JsonFileStore(StorageBackend):
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        dirs = [
            "raw", "normalized", "analysis", "themes",
            "aggregates", "collection", "pulses", "logs"
        ]
        for d in dirs:
            (self.data_dir / d).mkdir(parents=True, exist_ok=True)

    def _get_path(self, category: str, app_id: Optional[str] = None, filename: str = "") -> Path:
        base = self.data_dir / category
        if app_id:
            base = base / app_id
        base.mkdir(parents=True, exist_ok=True)
        return base / filename

    def _atomic_write(self, filepath: Path, data: Any) -> None:
        temp_path = filepath.with_suffix('.tmp')
        with open(temp_path, 'w', encoding='utf-8') as f:
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], BaseModel):
                json.dump([item.model_dump() for item in data], f, cls=CustomJSONEncoder, indent=2)
            elif isinstance(data, BaseModel):
                json.dump(data.model_dump(), f, cls=CustomJSONEncoder, indent=2)
            else:
                json.dump(data, f, cls=CustomJSONEncoder, indent=2)
        
        # Atomic replace (Windows supports this natively with replace in Python 3.3+)
        os.replace(temp_path, filepath)

    def save_raw_reviews(self, reviews: List[RawReview], run_id: str) -> None:
        if not reviews:
            return
        app_id = reviews[0].app_id
        filepath = self._get_path("raw", app_id, f"{run_id}_raw_reviews.json")
        self._atomic_write(filepath, reviews)

    def save_normalized_reviews(self, reviews: List[NormalizedReview], run_id: str) -> None:
        if not reviews:
            return
        app_id = reviews[0].original_review.app_id
        filepath = self._get_path("normalized", app_id, f"{run_id}_normalized.json")
        self._atomic_write(filepath, reviews)

    def save_analysis_results(self, results: List[AnalyzedReview], run_id: str) -> None:
        if not results:
            return
        app_id = results[0].normalized_review.original_review.app_id
        filepath = self._get_path("analysis", app_id, f"{run_id}_analyzed.json")
        self._atomic_write(filepath, results)

    def save_themes(self, themes: List[Theme], run_id: str) -> None:
        # Assuming app_id is passed or handled via orchestration, we can parse run_id or pass app_id.
        # For simplicity, themes are stored without app_id directory if not provided, or we could require it.
        # Let's save them under run_id in the themes directory.
        # Since the interface doesn't have app_id, we'll store at the root of themes.
        filepath = self._get_path("themes", filename=f"{run_id}_themes.json")
        self._atomic_write(filepath, themes)

    def save_weekly_aggregate(self, aggregate: WeeklyAggregate) -> None:
        filepath = self._get_path("aggregates", aggregate.app_id, f"{aggregate.run_id}_aggregate.json")
        self._atomic_write(filepath, aggregate)

    def save_collection_metadata(self, metadata: CollectionMetadata) -> None:
        filepath = self._get_path("collection", metadata.app_id, "collection_state.json")
        self._atomic_write(filepath, metadata)

    def get_previous_aggregate(self, app_id: str, periods_back: int = 1) -> Optional[WeeklyAggregate]:
        agg_dir = self._get_path("aggregates", app_id)
        if not agg_dir.exists():
            return None
        
        # Assuming filename starts with run_id which contains timestamp
        # e.g., run_20260905_080000_aggregate.json
        files = sorted(agg_dir.glob("*_aggregate.json"), reverse=True)
        if len(files) >= periods_back:
            with open(files[periods_back - 1], 'r', encoding='utf-8') as f:
                data = json.load(f)
                return WeeklyAggregate(**data)
        return None

    def get_processed_review_ids(self, app_id: str) -> Set[str]:
        raw_dir = self._get_path("raw", app_id)
        if not raw_dir.exists():
            return set()
            
        processed_ids = set()
        for file in raw_dir.glob("*_raw_reviews.json"):
            with open(file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    for item in data:
                        if "review_id" in item:
                            processed_ids.add(item["review_id"])
                except json.JSONDecodeError:
                    continue
        return processed_ids

    def get_run_history(self, app_id: str, limit: int = 5) -> List[WeeklyAggregate]:
        agg_dir = self._get_path("aggregates", app_id)
        if not agg_dir.exists():
            return []
            
        files = sorted(agg_dir.glob("*_aggregate.json"), reverse=True)
        history = []
        for file in files[:limit]:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                history.append(WeeklyAggregate(**data))
        return history

    def save_error_log(self, error: dict) -> None:
        filepath = self._get_path("logs", filename=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        self._atomic_write(filepath, error)
