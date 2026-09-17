"""
HRPolicyAI Telemetry, Caching & Cost Tracking Manager.
Provides LRU/TTL caching for identical queries, structured request/response logging,
token counting & cost calculations, and analytics summarization over time.
"""

import os
import json
import time
import uuid
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = OUTPUTS_DIR / "rag_requests.jsonl"
TELEMETRY_LOG_FILE = OUTPUTS_DIR / "rag_telemetry.log"
SUMMARY_JSON_FILE = OUTPUTS_DIR / "telemetry_summary.json"

logger = logging.getLogger("hrpolicyai_telemetry")

# Standard pricing model rates ($ per 1,000,000 tokens)
PRICING_RATES = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    "gpt-4o": {"input": 2.50, "output": 10.00},
}


def estimate_tokens(text: str) -> int:
    """Estimates token count using tiktoken if available, falling back to character approximation."""
    if not text:
        return 0
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        # Standard heuristic: ~4 characters per token in English
        return max(1, len(text.strip()) // 4)


def calculate_cost(prompt_tokens: int, completion_tokens: int, model: str = "gpt-3.5-turbo") -> float:
    """Calculates dollar cost based on model token rates."""
    rates = PRICING_RATES.get(model, PRICING_RATES["gpt-3.5-turbo"])
    input_cost = (prompt_tokens / 1_000_000.0) * rates["input"]
    output_cost = (completion_tokens / 1_000_000.0) * rates["output"]
    return round(input_cost + output_cost, 6)


class QueryCache:
    """In-memory LRU cache with TTL expiration for repeated identical queries."""

    def __init__(self, ttl_seconds: int = 3600, max_size: int = 500):
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._stats = {"hits": 0, "misses": 0}

    def _generate_key(self, query: str, region: str = "Global") -> str:
        normalized = f"{query.strip().lower()}::{region.strip().lower()}"
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def get(self, query: str, region: str = "Global") -> Optional[Tuple[str, List[Dict[str, Any]]]]:
        """Retrieves cached answer & sources if present and not expired."""
        key = self._generate_key(query, region)
        entry = self._cache.get(key)
        now = time.time()

        if entry:
            if now - entry["cached_at"] < self.ttl_seconds:
                entry["hits"] += 1
                entry["last_accessed"] = now
                self._stats["hits"] += 1
                return entry["answer"], entry["sources"]
            else:
                # Expired
                del self._cache[key]

        self._stats["misses"] += 1
        return None

    def set(
        self,
        query: str,
        region: str,
        answer: str,
        sources: List[Dict[str, Any]],
        tokens: Dict[str, int],
        cost: float
    ) -> None:
        """Stores query result in cache."""
        if len(self._cache) >= self.max_size:
            # Evict oldest accessed entry
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k]["last_accessed"])
            del self._cache[oldest_key]

        key = self._generate_key(query, region)
        now = time.time()
        self._cache[key] = {
            "query": query,
            "region": region,
            "answer": answer,
            "sources": sources,
            "cached_at": now,
            "last_accessed": now,
            "hits": 0,
            "tokens": tokens,
            "estimated_cost": cost,
        }

    def clear(self) -> None:
        self._cache.clear()
        self._stats = {"hits": 0, "misses": 0}

    def get_stats(self) -> Dict[str, Any]:
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total * 100.0) if total > 0 else 0.0
        return {
            "cached_entries": len(self._cache),
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "hit_rate_percent": round(hit_rate, 2),
        }


class TelemetryManager:
    """Manages telemetry logging, usage tracking, and aggregation."""

    def __init__(self):
        self.cache = QueryCache(ttl_seconds=3600)
        self.logs: List[Dict[str, Any]] = []
        self._load_existing_logs()

    def _load_existing_logs(self):
        """Loads historical logs from rag_requests.jsonl if present."""
        if LOG_FILE.exists():
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            self.logs.append(json.loads(line))
            except Exception as e:
                logger.warning("Failed to load historical telemetry logs: %s", e)

    def log_request(
        self,
        question: str,
        answer: str,
        sources: List[Dict[str, Any]],
        cache_hit: bool,
        latency_ms: float,
        region: str = "India",
        model: str = "gpt-3.5-turbo",
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Logs a completed request and appends to persistent storage."""
        prompt_tokens = estimate_tokens(question) + 120  # + system prompt estimate
        completion_tokens = estimate_tokens(answer)
        total_tokens = prompt_tokens + completion_tokens

        cost = calculate_cost(prompt_tokens, completion_tokens, model)
        cost_saved = cost if cache_hit else 0.0
        actual_cost = 0.0 if cache_hit else cost

        # Extract compact source descriptors
        sources_summary = [
            {
                "document": s.get("document", "Unknown"),
                "chunk_id": s.get("chunk_id", s.get("document_id", "chk_unknown")),
                "section": s.get("section", "General"),
                "page": s.get("page", 1),
                "score": s.get("score", 0.95),
            }
            for s in sources
        ]

        log_entry = {
            "request_id": f"req_{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "region": region,
            "question": question,
            "answer_preview": answer[:120] + "..." if len(answer) > 120 else answer,
            "sources_count": len(sources),
            "retrieved_sources": sources_summary,
            "cache_hit": cache_hit,
            "latency_ms": round(latency_ms, 2),
            "tokens": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
            },
            "cost": {
                "estimated_cost_usd": actual_cost,
                "cost_saved_usd": cost_saved,
                "model": model,
            },
            "status": "ERROR" if error else "SUCCESS",
            "error": error,
        }

        self.logs.append(log_entry)

        # Append to JSON Lines file
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error("Failed to append to log file: %s", e)

        # Write human-readable telemetry line
        try:
            with open(TELEMETRY_LOG_FILE, "a", encoding="utf-8") as f:
                hit_str = "[CACHE HIT]" if cache_hit else "[CACHE MISS]"
                f.write(
                    f"[{log_entry['timestamp']}] {hit_str} latency={log_entry['latency_ms']}ms "
                    f"tokens={total_tokens} cost=${actual_cost:.6f} "
                    f"query=\"{question}\"\n"
                )
        except Exception as e:
            logger.error("Failed to append to telemetry log: %s", e)

        return log_entry

    def get_summary(self) -> Dict[str, Any]:
        """Calculates aggregated metrics over all recorded requests."""
        total_requests = len(self.logs)
        if total_requests == 0:
            return {
                "total_requests": 0,
                "cache_hits": 0,
                "cache_misses": 0,
                "cache_hit_rate_percent": 0.0,
                "total_tokens": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_cost_usd": 0.0,
                "total_cost_saved_usd": 0.0,
                "average_latency_ms": 0.0,
                "cached_entries": self.cache.get_stats()["cached_entries"],
                "recent_requests": [],
            }

        cache_hits = sum(1 for log in self.logs if log.get("cache_hit", False))
        cache_misses = total_requests - cache_hits
        hit_rate = (cache_hits / total_requests) * 100.0

        total_prompt_tokens = sum(log.get("tokens", {}).get("prompt_tokens", 0) for log in self.logs)
        total_comp_tokens = sum(log.get("tokens", {}).get("completion_tokens", 0) for log in self.logs)
        total_tokens = total_prompt_tokens + total_comp_tokens

        total_cost = sum(log.get("cost", {}).get("estimated_cost_usd", 0.0) for log in self.logs)
        total_saved = sum(log.get("cost", {}).get("cost_saved_usd", 0.0) for log in self.logs)

        latencies = [log.get("latency_ms", 0.0) for log in self.logs]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

        # Region breakdown
        region_counts: Dict[str, int] = {}
        for log in self.logs:
            reg = log.get("region", "Global")
            region_counts[reg] = region_counts.get(reg, 0) + 1

        recent = self.logs[-20:]
        recent.reverse()

        summary = {
            "total_requests": total_requests,
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "cache_hit_rate_percent": round(hit_rate, 2),
            "total_tokens": total_tokens,
            "prompt_tokens": total_prompt_tokens,
            "completion_tokens": total_comp_tokens,
            "total_cost_usd": round(total_cost, 6),
            "total_cost_saved_usd": round(total_saved, 6),
            "average_latency_ms": round(avg_latency, 2),
            "cached_entries": self.cache.get_stats()["cached_entries"],
            "region_distribution": region_counts,
            "recent_requests": recent,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        # Persist summary JSON
        try:
            with open(SUMMARY_JSON_FILE, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
        except Exception as e:
            logger.error("Failed to write telemetry summary JSON: %s", e)

        return summary


# Global singleton instance
telemetry = TelemetryManager()
