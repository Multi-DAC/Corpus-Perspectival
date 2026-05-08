"""Sleep-Time Memory Consolidation — Automated memory management.

Inspired by LightMem, EverMemOS, and Letta Context Repos.

During quiet hours (1-7 AM) or on-demand, this module:
1. Scans today's daily log for new information
2. Extracts atomic facts and insights
3. Checks for contradictions/updates against existing items
4. Merges confirmed facts, updates changed facts, flags conflicts
5. Compresses raw log sections into structured summaries
6. Updates importance scores based on retrieval frequency

Raw logs are preserved in an archive directory so nothing is truly lost.
"""
import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path

import config

logger = logging.getLogger("clawd.tools.consolidation")

ARCHIVE_DIR = config.MEMORY_DIR / "archive"


async def consolidate_memory(router=None) -> str:
    """Run a full memory consolidation pass.

    Can be triggered:
    - By heartbeat during quiet hours (1-7 AM)
    - Manually via the consolidate_memory tool
    - During morning boot (7-8 AM)

    Args:
        router: Optional ModelRouter for LLM-assisted summarization.
               If None, uses rule-based extraction only.
    """
    results = []

    # 1. Archive and compress old daily logs
    archived = _archive_old_logs()
    if archived:
        results.append(f"Archived {archived} old daily logs")

    # 2. Extract facts from recent logs (LLM-assisted if router available)
    extracted = await _extract_facts_from_recent_logs(router)
    if extracted:
        results.append(f"Extracted {extracted} new memory items from recent logs")

    # 3. Decay importance scores for unaccessed items
    decayed = _decay_unused_items()
    if decayed:
        results.append(f"Decayed importance for {decayed} stale items")

    # 3b. Update memory tiers (BudgetMem)
    try:
        from tools.memory_items import update_item_tiers
        tiered = update_item_tiers()
        if tiered:
            results.append(f"Updated memory tiers for {tiered} items")
    except Exception as e:
        logger.debug(f"Tier update skipped: {e}")

    # 4. Deduplicate similar items
    deduped = _deduplicate_items()
    if deduped:
        results.append(f"Merged {deduped} duplicate items")

    # 5. Evolve memory items — update confidence, handle contradictions
    evolved = _evolve_memory_items()
    if evolved:
        results.append(f"Evolved {evolved} memory items (confidence updates)")

    # 6. Extract principles from patterns (Task 15)
    principles = _extract_principles()
    if principles:
        results.append(f"Extracted {principles} new strategic principles")

    # 7. Auto-populate knowledge graph from memory items
    kg_populated = _populate_knowledge_graph()
    if kg_populated:
        results.append(f"Added {kg_populated} entities/edges to knowledge graph")

    # 7b. Cluster recent episodes into semantic notes (HiMem-style)
    if router:
        try:
            from tools.semantic_segmentation import cluster_episodes_into_notes
            from tools.sqlite_store import upsert_semantic_note

            exp_file = config.MEMORY_DIR / "experiences.json"
            recent_episodes = []
            if exp_file.exists():
                all_eps = json.loads(exp_file.read_text(encoding="utf-8"))
                recent_episodes = all_eps[-30:]  # Last 30 episodes

            if len(recent_episodes) >= 3:
                notes = await cluster_episodes_into_notes(recent_episodes, router)
                for note in notes:
                    await upsert_semantic_note(note)
                    # Link notes to KG
                    try:
                        from tools.knowledge_graph import add_entity_raw, add_edge_raw
                        add_entity_raw(note["topic"], "concept", {"source": "semantic_note", "note_id": note["id"]})
                        for ep_id in note.get("source_episode_ids", [])[:5]:
                            add_edge_raw(note["topic"], str(ep_id), "derived_from")
                    except Exception as e:
                        logger.debug(f"Failed to link note to knowledge graph: {e}")
                if notes:
                    results.append(f"Clustered episodes into {len(notes)} semantic notes")
        except Exception as e:
            logger.debug(f"Episode clustering skipped: {e}")

    # 8. Generate daily summary
    summarized = _generate_daily_summary()
    if summarized:
        results.append(f"Generated daily summary")

    # 9. Run proactive memory agent cycle (LLM-powered dreaming)
    if router:
        try:
            from tools.memory_agent import run_memory_agent_cycle
            agent_result = await run_memory_agent_cycle(router)
            results.append(f"Memory agent: {agent_result[:200]}")
        except Exception as e:
            logger.debug(f"Memory agent cycle skipped: {e}")

    if not results:
        return "Consolidation complete — no changes needed."

    return "Memory consolidation complete:\n" + "\n".join(f"  - {r}" for r in results)


def _archive_old_logs() -> int:
    """Move daily logs older than 14 days to archive directory."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    archived = 0
    today = datetime.now()

    for log_file in config.MEMORY_DIR.glob("20??-??-??.md"):
        try:
            date_str = log_file.stem
            log_date = datetime.strptime(date_str, "%Y-%m-%d")
            age_days = (today - log_date).days

            if age_days > 14:
                dest = ARCHIVE_DIR / log_file.name
                if not dest.exists():
                    # Copy to archive (preserve original until confirmed)
                    dest.write_text(log_file.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
                    archived += 1
                    logger.info(f"Archived {log_file.name} ({age_days} days old)")
        except (ValueError, Exception) as e:
            logger.debug(f"Skipping {log_file.name}: {e}")
            continue

    return archived


async def _extract_facts_from_recent_logs(router=None) -> int:
    """Extract structured facts from recent daily logs."""
    from tools.memory_items import _generate_id, _save_item, _update_index_for_item, _extract_keywords, _find_related_items, _add_backlinks

    extracted = 0
    today = datetime.now()

    # Process logs from the last 3 days
    for days_ago in range(1, 4):
        date = today - timedelta(days=days_ago)
        log_file = config.MEMORY_DIR / f"{date.strftime('%Y-%m-%d')}.md"
        if not log_file.exists():
            continue

        content = log_file.read_text(encoding="utf-8", errors="replace")

        # Track what we've already extracted (check for extraction marker)
        marker_file = config.MEMORY_DIR / ".consolidated"
        consolidated_dates = set()
        if marker_file.exists():
            try:
                consolidated_dates = set(json.loads(marker_file.read_text(encoding="utf-8")))
            except Exception:
                consolidated_dates = set()

        date_str = date.strftime("%Y-%m-%d")
        if date_str in consolidated_dates:
            continue

        # LLM-assisted extraction if router available, else rule-based fallback
        facts = []
        if router:
            try:
                from tools.semantic_segmentation import segment_daily_log
                facts = await segment_daily_log(date_str, content, router)
            except Exception as e:
                logger.debug(f"LLM segmentation unavailable: {e}")
        if not facts:
            facts = _extract_facts_from_text(content, date_str)

        for fact in facts:
            item_id = _generate_id()
            keywords = _extract_keywords(fact["content"])
            auto_links = _find_related_items(fact["content"], keywords, exclude_id=item_id)

            item = {
                "id": item_id,
                "type": fact["type"],
                "content": fact["content"],
                "source": f"daily_log {date_str} (auto-consolidated)",
                "categories": fact["categories"],
                "related_items": [],
                "links": auto_links,
                "keywords": keywords,
                "importance": fact.get("importance", 4),
                "created": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "access_count": 0,
                "utility_score": 0.5,
                "confidence": 0.7,
            }
            _save_item(item)
            _update_index_for_item(item_id, item["categories"])
            if auto_links:
                _add_backlinks(item_id, auto_links)
            extracted += 1

        # Mark date as consolidated
        consolidated_dates.add(date_str)
        marker_file.write_text(json.dumps(list(consolidated_dates)), encoding="utf-8")

    return extracted


def _extract_facts_from_text(content: str, date_str: str) -> list[dict]:
    """Rule-based extraction of facts from daily log text."""
    facts = []
    lines = content.split("\n")

    for i, line in enumerate(lines):
        line_stripped = line.strip()

        # Skip empty lines and pure timestamps
        if not line_stripped or line_stripped.startswith("#"):
            continue

        # Pattern: "Discovered X" / "Found X" / "Learned X"
        discovery_match = re.match(
            r'.*?\b(discovered|found|learned|realized|confirmed|verified|established)\b\s+(.{20,})',
            line_stripped, re.IGNORECASE
        )
        if discovery_match:
            action, what = discovery_match.groups()
            facts.append({
                "type": "fact",
                "content": what[:200].strip(),
                "categories": ["auto-extracted", "discoveries"],
                "importance": 5,
            })

        # Pattern: "Decision: X" or "Decided to X"
        decision_match = re.match(
            r'.*?\b(decided|decision|chose|choosing)\b[:\s]+(.{15,})',
            line_stripped, re.IGNORECASE
        )
        if decision_match:
            _, what = decision_match.groups()
            facts.append({
                "type": "decision",
                "content": what[:200].strip(),
                "categories": ["auto-extracted", "decisions"],
                "importance": 6,
            })

        # Pattern: "Insight: X" or "Key insight:"
        insight_match = re.match(
            r'.*?\b(insight|realization|key\s+learning|important)\b[:\s]+(.{15,})',
            line_stripped, re.IGNORECASE
        )
        if insight_match:
            _, what = insight_match.groups()
            facts.append({
                "type": "insight",
                "content": what[:200].strip(),
                "categories": ["auto-extracted", "insights"],
                "importance": 7,
            })

    # Limit to 10 facts per day to avoid noise
    return facts[:10]


def _decay_unused_items() -> int:
    """Reduce importance of items that haven't been accessed recently."""
    if not config.MEMORY_ITEMS_DIR.is_dir():
        return 0

    decayed = 0
    now = datetime.now()
    decay_threshold_days = 30  # Start decaying after 30 days of no access

    for fpath in config.MEMORY_ITEMS_DIR.glob("*.json"):
        if fpath.name == "_index.json":
            continue
        try:
            item = json.loads(fpath.read_text(encoding="utf-8"))
        except Exception:
            continue

        last_accessed = item.get("last_accessed", item.get("created", ""))
        if not last_accessed:
            continue

        try:
            last_dt = datetime.fromisoformat(last_accessed)
            days_since = (now - last_dt).days
        except (ValueError, TypeError):
            continue

        if days_since > decay_threshold_days:
            current_importance = item.get("importance", 5)
            if current_importance > 1:
                item["importance"] = max(1, current_importance - 1)
                fpath.write_text(json.dumps(item, indent=2), encoding="utf-8")
                decayed += 1

    return decayed


def _deduplicate_items() -> int:
    """Find and merge items with very similar content.

    Uses MinHash-inspired fingerprinting to avoid O(N^2) full comparisons:
    1. Build word-set fingerprints for each item
    2. Group by fingerprint buckets (items sharing frequent words)
    3. Only compare within buckets (much smaller than N^2)
    """
    if not config.MEMORY_ITEMS_DIR.is_dir():
        return 0

    items = []
    for fpath in config.MEMORY_ITEMS_DIR.glob("*.json"):
        if fpath.name == "_index.json":
            continue
        try:
            item = json.loads(fpath.read_text(encoding="utf-8"))
            items.append(item)
        except Exception:
            continue

    if len(items) < 2:
        return 0

    # Phase 1: Build fingerprint buckets to reduce comparison space
    # Map each item to its word set; bucket by most-frequent words
    item_words = {}
    word_to_items = {}
    for item in items:
        content = item.get("content", "").lower().strip()
        words = frozenset(content.split())
        item_words[item["id"]] = (words, len(content))
        # Index by words for bucket lookups (only words > 3 chars to reduce noise)
        for w in words:
            if len(w) > 3:
                word_to_items.setdefault(w, []).append(item["id"])

    # Phase 2: Find candidate pairs via shared-word buckets
    # Only compare items that share at least one significant word
    candidate_pairs = set()
    for word, item_ids in word_to_items.items():
        if len(item_ids) > 50:
            continue  # Skip very common words (would create too many pairs)
        for i in range(len(item_ids)):
            for j in range(i + 1, len(item_ids)):
                pair = (min(item_ids[i], item_ids[j]), max(item_ids[i], item_ids[j]))
                candidate_pairs.add(pair)

    # Phase 3: Compare only candidate pairs
    merged = 0
    to_delete = set()
    items_by_id = {item["id"]: item for item in items}

    for id_a, id_b in candidate_pairs:
        if id_a in to_delete or id_b in to_delete:
            continue

        words_a, len_a = item_words.get(id_a, (frozenset(), 0))
        words_b, len_b = item_words.get(id_b, (frozenset(), 0))

        if not words_a or not words_b:
            continue

        # Quick length check
        if abs(len_a - len_b) > len_a * 0.3:
            continue

        # Word-level Jaccard similarity
        intersection = words_a & words_b
        union = words_a | words_b
        similarity = len(intersection) / len(union) if union else 0

        if similarity > 0.8:
            item_a = items_by_id[id_a]
            item_b = items_by_id[id_b]
            score_a = item_a.get("importance", 5) + item_a.get("access_count", 0) * 0.5
            score_b = item_b.get("importance", 5) + item_b.get("access_count", 0) * 0.5

            if score_a >= score_b:
                to_delete.add(id_b)
                keeper_links = item_a.get("links", [])
                for link in item_b.get("links", []):
                    if link not in keeper_links and link != id_a:
                        keeper_links.append(link)
                item_a["links"] = keeper_links
            else:
                to_delete.add(id_a)
                keeper_links = item_b.get("links", [])
                for link in item_a.get("links", []):
                    if link not in keeper_links and link != id_b:
                        keeper_links.append(link)
                item_b["links"] = keeper_links

            merged += 1

    # Phase 4: Save keepers FIRST, then delete duplicates (atomic ordering)
    for item in items:
        if item["id"] not in to_delete:
            fpath = config.MEMORY_ITEMS_DIR / f"{item['id']}.json"
            fpath.write_text(json.dumps(item, indent=2), encoding="utf-8")

    for item_id in to_delete:
        fpath = config.MEMORY_ITEMS_DIR / f"{item_id}.json"
        if fpath.exists():
            fpath.unlink()
            logger.info(f"Deduplicated item {item_id}")

    return merged


def _evolve_memory_items() -> int:
    """Evolve memory items: update confidence based on access patterns,
    handle contradictions when new episodes conflict with existing items."""
    if not config.MEMORY_ITEMS_DIR.is_dir():
        return 0

    evolved = 0
    now = datetime.now()

    for fpath in config.MEMORY_ITEMS_DIR.glob("*.json"):
        if fpath.name == "_index.json":
            continue
        try:
            item = json.loads(fpath.read_text(encoding="utf-8"))
        except Exception:
            continue

        changed = False

        # Confidence grows with validation (access), decays without
        access_count = item.get("access_count", 0)
        last_accessed = item.get("last_accessed", item.get("created", ""))
        try:
            last_dt = datetime.fromisoformat(last_accessed)
            days_since = (now - last_dt).days
        except (ValueError, TypeError):
            days_since = 30

        current_confidence = item.get("confidence", 0.7)

        if access_count > 5 and days_since < 14:
            # Frequently accessed and recent — boost confidence
            new_conf = min(1.0, current_confidence + 0.05)
            if new_conf != current_confidence:
                item["confidence"] = round(new_conf, 3)
                # Append to confidence_history
                conf_history = item.get("confidence_history", [])
                if not isinstance(conf_history, list):
                    conf_history = []
                conf_history.append({
                    "timestamp": now.isoformat(),
                    "confidence": new_conf,
                    "reason": f"evolution_boost (accessed {access_count}x in {days_since}d)"
                })
                item["confidence_history"] = conf_history[-20:]
                changed = True
        elif days_since > 60 and access_count < 2:
            # Rarely accessed and old — decay confidence
            new_conf = max(0.1, current_confidence - 0.05)
            if new_conf != current_confidence:
                item["confidence"] = round(new_conf, 3)
                conf_history = item.get("confidence_history", [])
                if not isinstance(conf_history, list):
                    conf_history = []
                conf_history.append({
                    "timestamp": now.isoformat(),
                    "confidence": new_conf,
                    "reason": f"evolution_decay ({days_since}d since access, {access_count} accesses)"
                })
                item["confidence_history"] = conf_history[-20:]
                changed = True

        if changed:
            fpath.write_text(json.dumps(item, indent=2), encoding="utf-8")
            evolved += 1

    return evolved


def _extract_principles() -> int:
    """Extract strategic principles from experience patterns.

    When 3+ experiences share a common lesson pattern (keyword clustering),
    distill into a reusable principle.
    """
    import config

    exp_file = config.MEMORY_DIR / "experiences.json"
    if not exp_file.exists():
        return 0

    try:
        experiences = json.loads(exp_file.read_text(encoding="utf-8"))
    except Exception:
        return 0

    if len(experiences) < 5:
        return 0

    # Load existing principles
    principles_file = config.MEMORY_DIR / "principles.json"
    principles = []
    if principles_file.exists():
        try:
            principles = json.loads(principles_file.read_text(encoding="utf-8"))
        except Exception:
            principles = []

    existing_texts = {p.get("principle", "").lower() for p in principles}

    # Group lessons by keyword clusters
    lesson_groups = {}
    for e in experiences:
        lesson = e.get("lesson", "").strip()
        if not lesson or len(lesson) < 10:
            continue
        # Extract key words
        words = set(re.findall(r'\b[a-zA-Z]{4,}\b', lesson.lower()))
        # Create a signature from top words
        for word in words:
            if word not in lesson_groups:
                lesson_groups[word] = []
            lesson_groups[word].append(e)

    # Find clusters with 3+ experiences sharing a keyword in their lessons
    new_principles = 0
    seen_clusters = set()
    for keyword, cluster in sorted(lesson_groups.items(), key=lambda x: len(x[1]), reverse=True):
        if len(cluster) < 3:
            continue
        if keyword in seen_clusters:
            continue
        seen_clusters.add(keyword)

        # Extract a principle from the cluster
        lessons = [e.get("lesson", "") for e in cluster[:5]]
        categories = [e.get("category", "general") for e in cluster]
        # Most common category
        cat_freq = {}
        for c in categories:
            cat_freq[c] = cat_freq.get(c, 0) + 1
        top_cat = max(cat_freq, key=cat_freq.get)

        # Use the highest-scored experience's lesson as the principle
        best = max(cluster, key=lambda e: e.get("score", 0.5))
        principle_text = best.get("lesson", "").strip()

        if not principle_text or principle_text.lower() in existing_texts:
            continue

        # Calculate success rate
        successes = sum(1 for e in cluster if e.get("outcome") == "success")
        success_rate = round(successes / len(cluster), 2)

        principle = {
            "id": len(principles) + 1,
            "principle": principle_text,
            "derived_from": [e.get("id") for e in cluster[:5]],
            "category": top_cat,
            "confidence": min(0.9, 0.5 + len(cluster) * 0.05),
            "times_applied": 0,
            "success_rate_when_applied": success_rate,
            "created": datetime.now().isoformat(),
            "last_validated": datetime.now().isoformat(),
        }
        principles.append(principle)
        existing_texts.add(principle_text.lower())
        new_principles += 1

        if new_principles >= 3:  # Cap at 3 new principles per consolidation
            break

    if new_principles > 0:
        principles_file.parent.mkdir(parents=True, exist_ok=True)
        principles_file.write_text(json.dumps(principles, indent=2), encoding="utf-8")
        logger.info(f"Extracted {new_principles} new strategic principles")

    return new_principles


def _populate_knowledge_graph() -> int:
    """Auto-populate knowledge graph from memory items.
    Extract entity-relation-entity triples from items."""
    if not config.MEMORY_ITEMS_DIR.is_dir():
        return 0

    try:
        from tools.knowledge_graph import add_entity_raw, add_edge_raw
    except ImportError:
        return 0

    added = 0

    for fpath in config.MEMORY_ITEMS_DIR.glob("*.json"):
        if fpath.name == "_index.json":
            continue
        try:
            item = json.loads(fpath.read_text(encoding="utf-8"))
        except Exception:
            continue

        item_type = item.get("type", "")
        content = item.get("content", "")
        categories = item.get("categories", [])

        # Extract entities from different item types
        if item_type == "relationship" and content:
            # "Clayton prefers X" → entity: Clayton, relation: prefers
            add_entity_raw("Clayton", "person", {"role": "user"})
            added += 1

        if item_type == "skill" and content:
            # Skills become tool/concept entities
            keywords = item.get("keywords", [])
            if keywords:
                entity_name = keywords[0]
                add_entity_raw(entity_name, "concept", {"source": "memory_item", "content": content[:100]})
                added += 1

        # Add category-based entities
        for cat in categories:
            if cat not in ("auto-extracted", "general", "discoveries", "decisions", "insights"):
                add_entity_raw(cat, "concept", {"source": "category"})
                # Link content to category
                for kw in item.get("keywords", [])[:2]:
                    add_edge_raw(kw, cat, "related_to")
                    added += 1

    return added


def _generate_daily_summary() -> bool:
    """Generate a concise summary of yesterday's log if not already done."""
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    log_file = config.MEMORY_DIR / f"{date_str}.md"
    summary_file = config.MEMORY_DIR / "daily-summaries" / f"{date_str}-summary.md"

    if not log_file.exists() or summary_file.exists():
        return False

    content = log_file.read_text(encoding="utf-8", errors="replace")
    if len(content) < 200:  # Skip very short logs
        return False

    summary_file.parent.mkdir(parents=True, exist_ok=True)

    # Rule-based summary extraction
    lines = content.split("\n")
    summary_parts = [f"# Daily Summary — {date_str}\n"]

    # Extract timestamped entries
    entries = []
    for line in lines:
        if re.match(r'\*\*\d{2}:\d{2}', line):
            entries.append(line.strip())

    if entries:
        summary_parts.append(f"## Activity ({len(entries)} log entries)")
        # Keep first and last entries, and any with key words
        important = []
        for entry in entries:
            if any(kw in entry.lower() for kw in [
                "completed", "discovered", "error", "success", "milestone",
                "decided", "created", "published", "telegram", "heartbeat #1"
            ]):
                important.append(entry)

        if not important:
            important = [entries[0]] + ([entries[-1]] if len(entries) > 1 else [])

        for entry in important[:10]:
            summary_parts.append(f"- {entry}")

    summary_parts.append(f"\n*Original log: {len(content)} chars, {len(lines)} lines*")

    summary_file.write_text("\n".join(summary_parts), encoding="utf-8")
    logger.info(f"Generated daily summary for {date_str}")
    return True


# Tool definitions for consolidation
TOOL_DEFINITIONS = [
    {
        "name": "consolidate_memory",
        "description": (
            "Run memory consolidation: archive old logs, extract facts, "
            "decay stale items, deduplicate, and generate summaries. "
            "Automatically runs during quiet hours but can be triggered manually."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "force": {
                    "type": "boolean",
                    "description": "Force consolidation even outside quiet hours. Default: false.",
                },
            },
            "required": [],
        },
    },
]


async def _consolidate_memory_tool(input_data: dict) -> str:
    """Tool handler for manual consolidation trigger."""
    return await consolidate_memory()


TOOL_HANDLERS = {
    "consolidate_memory": _consolidate_memory_tool,
}
