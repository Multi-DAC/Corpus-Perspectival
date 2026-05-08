"""Artifact Store - CRUD and lineage tracking for evolved artifacts.

Stores code artifacts with metadata:
- Generation number
- Fitness scores (multi-objective)
- Parent lineage (mutation/crossover sources)
- Mutation history
- Creation timestamps

Integrates with:
- SQLite for persistent storage
- Knowledge graph for lineage edges
- File system for code storage
"""
import json
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, asdict

import config

logger = logging.getLogger("clawd.tools.eac.artifact_store")

ARTIFACTS_DIR = config.CLAWD_HOME / "artifacts"
ARTIFACTS_INDEX = ARTIFACTS_DIR / "artifacts.json"


@dataclass
class ArtifactMetadata:
    """Metadata for an evolved artifact."""
    artifact_id: str
    name: str
    artifact_type: str  # tool, skill, workflow, prompt, config
    generation: int
    fitness: dict  # Multi-objective scores
    parents: list[str]  # Parent artifact IDs
    mutations: list[dict]  # Applied mutations
    created_at: str
    created_by: str  # "mutation", "crossover", "seed"
    status: str = "active"  # active, archived, superseded
    tags: list[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ArtifactMetadata":
        return cls(
            artifact_id=data.get("artifact_id", ""),
            name=data.get("name", ""),
            artifact_type=data.get("artifact_type", "tool"),
            generation=data.get("generation", 0),
            fitness=data.get("fitness", {}),
            parents=data.get("parents", []),
            mutations=data.get("mutations", []),
            created_at=data.get("created_at", ""),
            created_by=data.get("created_by", "seed"),
            status=data.get("status", "active"),
            tags=data.get("tags") or [],
        )


class ArtifactStore:
    """Persistent artifact store with lineage tracking."""

    def __init__(self):
        self.artifacts_dir = ARTIFACTS_DIR
        self.index_file = ARTIFACTS_INDEX
        self._index: dict = {"artifacts": {}, "next_id": 1}
        self._load_index()

    def _ensure_dirs(self):
        """Ensure artifact directories exist."""
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.index_file.parent.mkdir(parents=True, exist_ok=True)

    def _load_index(self):
        """Load artifact index from disk."""
        self._ensure_dirs()
        if self.index_file.exists():
            try:
                self._index = json.loads(self.index_file.read_text(encoding="utf-8"))
                logger.debug(f"Loaded artifact index with {len(self._index.get('artifacts', {}))} artifacts")
            except Exception as e:
                logger.warning(f"Failed to load artifact index, using empty: {e}")
        else:
            self._save_index()

    def _save_index(self):
        """Persist artifact index to disk."""
        self._ensure_dirs()
        self.index_file.write_text(
            json.dumps(self._index, indent=2, default=str),
            encoding="utf-8"
        )

    def _generate_id(self) -> str:
        """Generate unique artifact ID."""
        artifact_id = f"artifact:{self._index['next_id']:04d}"
        self._index["next_id"] += 1
        return artifact_id

    def _code_hash(self, code: str) -> str:
        """Generate hash of code content."""
        return hashlib.sha256(code.encode()).hexdigest()[:16]

    async def store_artifact(
        self,
        code: str,
        name: str,
        artifact_type: str = "tool",
        metadata: Optional[dict] = None,
    ) -> str:
        """Store an artifact with metadata.

        Args:
            code: The artifact code content
            name: Human-readable name
            artifact_type: Type (tool, skill, workflow, prompt, config)
            metadata: Optional metadata dict (generation, fitness, parents, etc.)

        Returns:
            Artifact ID
        """
        artifact_id = metadata.get("artifact_id") if metadata else None
        if not artifact_id:
            artifact_id = self._generate_id()

        if metadata:
            meta = ArtifactMetadata.from_dict(metadata)
            meta.artifact_id = artifact_id
        else:
            meta = ArtifactMetadata(
                artifact_id=artifact_id,
                name=name,
                artifact_type=artifact_type,
                generation=0,
                fitness={},
                parents=[],
                mutations=[],
                created_at=datetime.now().isoformat(),
                created_by="seed",
            )

        artifact_dir = self.artifacts_dir / artifact_type / artifact_id
        artifact_dir.mkdir(parents=True, exist_ok=True)

        code_file = artifact_dir / "code.py"
        code_file.write_text(code, encoding="utf-8")

        meta_file = artifact_dir / "metadata.json"
        meta_file.write_text(
            json.dumps(meta.to_dict(), indent=2),
            encoding="utf-8"
        )

        self._index["artifacts"][artifact_id] = {
            "name": name,
            "type": artifact_type,
            "generation": meta.generation,
            "fitness": meta.fitness,
            "status": meta.status,
            "code_hash": self._code_hash(code),
            "created_at": meta.created_at,
        }
        self._save_index()

        await self._store_in_sqlite(artifact_id, code, meta)
        self._add_to_knowledge_graph(meta)

        logger.info(f"Stored artifact: {artifact_id} ({name})")
        return artifact_id

    async def _store_in_sqlite(self, artifact_id: str, code: str, meta: ArtifactMetadata):
        """Store artifact in SQLite for persistent querying."""
        try:
            from tools.sqlite_store import store_eac_artifact
            await store_eac_artifact({
                "id": artifact_id,
                "name": meta.name,
                "artifact_type": meta.artifact_type,
                "generation": meta.generation,
                "fitness_correctness": meta.fitness.get("correctness", 0.5),
                "fitness_performance": meta.fitness.get("performance", 0.5),
                "fitness_readability": meta.fitness.get("readability", 0.5),
                "fitness_brevity": meta.fitness.get("brevity", 0.5),
                "fitness_overall": meta.fitness.get("overall", 0.5),
                "parents": meta.parents,
                "mutations": meta.mutations,
                "created_by": meta.created_by,
                "status": meta.status,
                "code_hash": self._code_hash(code),
                "created_at": meta.created_at,
            })
        except ImportError:
            logger.debug("SQLite store not available for EAC artifacts")
        except Exception as e:
            logger.debug(f"Failed to store artifact in SQLite: {e}")

    def get_artifact(self, artifact_id: str) -> Optional[dict]:
        """Retrieve artifact by ID."""
        if artifact_id not in self._index.get("artifacts", {}):
            return None

        meta = self._index["artifacts"][artifact_id]
        artifact_type = meta.get("type", "tool")

        artifact_dir = self.artifacts_dir / artifact_type / artifact_id
        if not artifact_dir.exists():
            return None

        code_file = artifact_dir / "code.py"
        code = code_file.read_text(encoding="utf-8") if code_file.exists() else ""

        meta_file = artifact_dir / "metadata.json"
        metadata = {}
        if meta_file.exists():
            metadata = json.loads(meta_file.read_text(encoding="utf-8"))

        return {
            "artifact_id": artifact_id,
            "code": code,
            "metadata": metadata,
        }

    def get_lineage(self, artifact_id: str) -> dict:
        """Get evolutionary tree for an artifact."""
        if artifact_id not in self._index.get("artifacts", {}):
            return {"error": f"Artifact {artifact_id} not found"}

        artifact = self.get_artifact(artifact_id)
        if not artifact:
            return {"error": f"Artifact data not found for {artifact_id}"}

        parents = artifact.get("metadata", {}).get("parents", [])

        children = []
        for aid, info in self._index.get("artifacts", {}).items():
            if artifact_id in info.get("parents", []):
                children.append(aid)

        def build_tree(aid: str, depth: int = 0) -> dict:
            if depth > 5:
                return {"id": aid, "truncated": True}
            art = self.get_artifact(aid)
            if not art:
                return {"id": aid, "missing": True}
            meta = art.get("metadata", {})
            return {
                "id": aid,
                "name": meta.get("name", "?"),
                "generation": meta.get("generation", 0),
                "fitness": meta.get("fitness", {}),
                "parents": [build_tree(p, depth + 1) for p in meta.get("parents", [])],
            }

        return {
            "artifact": artifact,
            "parents": parents,
            "children": children,
            "full_tree": build_tree(artifact_id),
        }

    def search_similar(self, code: str, threshold: float = 0.8) -> list[dict]:
        """Find artifacts with similar code (hash-based)."""
        code_hash = self._code_hash(code)
        similar = []

        for aid, info in self._index.get("artifacts", {}).items():
            if info.get("code_hash") == code_hash:
                similar.append({
                    "artifact_id": aid,
                    "name": info.get("name", "?"),
                    "type": info.get("type", "?"),
                    "similarity": 1.0,
                })

        return similar

    def list_artifacts(
        self,
        artifact_type: Optional[str] = None,
        min_fitness: Optional[float] = None,
        status: str = "active",
    ) -> list[dict]:
        """List artifacts with optional filters."""
        results = []

        for aid, info in self._index.get("artifacts", {}).items():
            if artifact_type and info.get("type") != artifact_type:
                continue
            if status and info.get("status") != status:
                continue
            if min_fitness:
                fitness = info.get("fitness", {})
                overall = fitness.get("overall", 0)
                if overall < min_fitness:
                    continue
            results.append({
                "artifact_id": aid,
                "name": info.get("name", "?"),
                "type": info.get("type", "?"),
                "generation": info.get("generation", 0),
                "fitness": info.get("fitness", {}),
                "status": info.get("status", "active"),
            })

        return sorted(results, key=lambda x: x.get("generation", 0), reverse=True)

    def update_fitness(self, artifact_id: str, fitness: dict):
        """Update fitness scores for an artifact."""
        if artifact_id not in self._index.get("artifacts", {}):
            logger.warning(f"Cannot update fitness: artifact {artifact_id} not found")
            return

        artifact_type = self._index["artifacts"][artifact_id].get("type", "tool")
        artifact_dir = self.artifacts_dir / artifact_type / artifact_id
        meta_file = artifact_dir / "metadata.json"

        if meta_file.exists():
            metadata = json.loads(meta_file.read_text(encoding="utf-8"))
            metadata["fitness"] = fitness
            metadata["updated_at"] = datetime.now().isoformat()
            meta_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

            self._index["artifacts"][artifact_id]["fitness"] = fitness
            self._save_index()

            logger.debug(f"Updated fitness for {artifact_id}: {fitness}")

    def archive_artifact(self, artifact_id: str, reason: str = "superseded"):
        """Archive an artifact (mark as superseded)."""
        if artifact_id not in self._index.get("artifacts", {}):
            return

        artifact_type = self._index["artifacts"][artifact_id].get("type", "tool")
        artifact_dir = self.artifacts_dir / artifact_type / artifact_id
        meta_file = artifact_dir / "metadata.json"

        if meta_file.exists():
            metadata = json.loads(meta_file.read_text(encoding="utf-8"))
            metadata["status"] = "archived"
            metadata["archived_reason"] = reason
            metadata["archived_at"] = datetime.now().isoformat()
            meta_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

            self._index["artifacts"][artifact_id]["status"] = "archived"
            self._save_index()

    def _add_to_knowledge_graph(self, meta: ArtifactMetadata):
        """Add artifact entity to knowledge graph."""
        try:
            from tools.knowledge_graph import add_artifact_entity, add_mutation_edge, add_crossover_edge

            add_artifact_entity(
                artifact_id=meta.artifact_id,
                name=meta.name,
                artifact_type=meta.artifact_type,
                generation=meta.generation,
                fitness=meta.fitness,
                parents=meta.parents,
            )

            for mutation in meta.mutations:
                mutation_type = mutation.get("type", "unknown")
                parent_id = mutation.get("source_artifact") or (meta.parents[0] if meta.parents else None)
                if parent_id:
                    if mutation_type == "crossover":
                        parent_b = mutation.get("parent_b")
                        if parent_b:
                            add_crossover_edge(parent_id, parent_b, meta.artifact_id)
                    else:
                        add_mutation_edge(parent_id, meta.artifact_id, mutation_type)

            logger.debug(f"Added {meta.artifact_id} to knowledge graph with lineage")
        except Exception as e:
            logger.debug(f"Failed to add artifact to knowledge graph: {e}")

    def get_stats(self) -> dict:
        """Get artifact store statistics."""
        artifacts = list(self._index.get("artifacts", {}).values())

        by_type = {}
        by_generation = {}
        fitness_scores = []

        for art in artifacts:
            t = art.get("type", "unknown")
            by_type[t] = by_type.get(t, 0) + 1

            g = art.get("generation", 0)
            by_generation[g] = by_generation.get(g, 0) + 1

            if art.get("fitness", {}).get("overall"):
                fitness_scores.append(art["fitness"]["overall"])

        return {
            "total_artifacts": len(artifacts),
            "by_type": by_type,
            "by_generation": by_generation,
            "avg_fitness": sum(fitness_scores) / len(fitness_scores) if fitness_scores else 0,
            "max_generation": max(by_generation.keys()) if by_generation else 0,
        }


# Singleton instance
_artifact_store: Optional[ArtifactStore] = None


def get_artifact_store() -> ArtifactStore:
    """Get or create the artifact store singleton."""
    global _artifact_store
    if _artifact_store is None:
        _artifact_store = ArtifactStore()
    return _artifact_store
