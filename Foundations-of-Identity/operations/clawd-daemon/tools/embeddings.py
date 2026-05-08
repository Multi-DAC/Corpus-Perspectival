"""
Semantic Embedding Index — Vector search for memory files.

Uses BAAI/bge-m3 (1024-dim, 63.0 MTEB, 100+ languages) for embeddings.
Falls back to all-MiniLM-L6-v2 (384-dim) if BGE-M3 fails to load.
Stores index in memory/.search_index/ as .npz + .json.
Supports incremental rebuilds based on file content hashes.
"""
import asyncio
import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Optional

import numpy as np

import config

logger = logging.getLogger("clawd.tools.embeddings")

# Lock to prevent concurrent index builds from corrupting the index
_build_lock = asyncio.Lock()

INDEX_DIR = config.MEMORY_DIR / ".search_index"
EMBEDDINGS_FILE = INDEX_DIR / "embeddings.npz"
METADATA_FILE = INDEX_DIR / "metadata.json"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 128

# Model configuration — BGE-M3 primary, MiniLM fallback
PRIMARY_MODEL = "BAAI/bge-m3"
PRIMARY_DIM = 1024
FALLBACK_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
FALLBACK_DIM = 384


class EmbeddingIndex:
    """Semantic search index using sentence-transformers."""

    def __init__(self):
        self._model = None
        self._model_dim: int = PRIMARY_DIM
        self._embeddings: Optional[np.ndarray] = None
        self._metadata: list[dict] = []  # [{file, chunk_text, chunk_idx, file_hash}]
        self._file_hashes: dict[str, str] = {}  # path -> content_hash
        self._ready = False

    def _load_model(self):
        """Lazy-load the sentence-transformer model. Tries BGE-M3 first, falls back to MiniLM."""
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
            try:
                self._model = SentenceTransformer(PRIMARY_MODEL)
                self._model_dim = PRIMARY_DIM
                logger.info(f"Loaded {PRIMARY_MODEL} ({PRIMARY_DIM}-dim)")
            except Exception as e:
                logger.warning(f"Failed to load {PRIMARY_MODEL}: {e}. Falling back to {FALLBACK_MODEL}")
                self._model = SentenceTransformer(FALLBACK_MODEL)
                self._model_dim = FALLBACK_DIM
                logger.info(f"Loaded {FALLBACK_MODEL} ({FALLBACK_DIM}-dim)")
        except ImportError:
            logger.warning(
                "sentence-transformers not installed. "
                "Semantic search disabled. "
                "Install with: pip install sentence-transformers"
            )
            raise

    def _content_hash(self, content: str) -> str:
        """Compute hash of file content for incremental updates."""
        return hashlib.md5(content.encode("utf-8", errors="replace")).hexdigest()[:12]

    def _chunk_text(self, text: str) -> list[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + CHUNK_SIZE
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk.strip())
            start += CHUNK_SIZE - CHUNK_OVERLAP
        return chunks

    def _get_indexable_files(self) -> list[Path]:
        """Get all files that should be indexed."""
        files = []

        # Identity files in CLAWD_HOME
        for md_file in config.CLAWD_HOME.glob("*.md"):
            files.append(md_file)

        # Memory directory
        if config.MEMORY_DIR.is_dir():
            for md_file in config.MEMORY_DIR.glob("*.md"):
                files.append(md_file)
            convos_dir = config.MEMORY_DIR / "conversations"
            if convos_dir.is_dir():
                files.extend(convos_dir.glob("*.md"))
            summaries_dir = config.MEMORY_DIR / "weekly-summaries"
            if summaries_dir.is_dir():
                files.extend(summaries_dir.glob("*.md"))
            daily_summaries_dir = config.MEMORY_DIR / "daily-summaries"
            if daily_summaries_dir.is_dir():
                files.extend(daily_summaries_dir.glob("*.md"))

        # Project files
        if config.PROJECTS_DIR.is_dir():
            for md_file in config.PROJECTS_DIR.glob("**/*.md"):
                files.append(md_file)

        # Memory items (structured JSON items, excluding index)
        if config.MEMORY_ITEMS_DIR.is_dir():
            for json_file in config.MEMORY_ITEMS_DIR.glob("*.json"):
                if json_file.name != "_index.json":
                    files.append(json_file)

        return files

    def _load_index(self) -> bool:
        """Load existing index from disk. Forces rebuild if embedding dimensions changed."""
        if not EMBEDDINGS_FILE.exists() or not METADATA_FILE.exists():
            return False
        try:
            data = np.load(str(EMBEDDINGS_FILE))
            embeddings = data["embeddings"]
            # Check dimension compatibility — force rebuild if model changed
            if embeddings.ndim == 2 and embeddings.shape[1] != self._model_dim:
                logger.warning(
                    f"Index dimension mismatch: {embeddings.shape[1]} vs {self._model_dim}. "
                    f"Forcing full rebuild."
                )
                return False
            self._embeddings = embeddings
            meta = json.loads(METADATA_FILE.read_text(encoding="utf-8"))
            self._metadata = meta.get("chunks", [])
            self._file_hashes = meta.get("file_hashes", {})
            logger.info(
                f"Loaded search index: {len(self._metadata)} chunks, "
                f"{len(self._file_hashes)} files"
            )
            return True
        except Exception as e:
            logger.warning(f"Failed to load search index: {e}")
            return False

    def _save_index(self):
        """Save index to disk."""
        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        try:
            if self._embeddings is not None:
                np.savez_compressed(str(EMBEDDINGS_FILE), embeddings=self._embeddings)
            meta = {
                "chunks": self._metadata,
                "file_hashes": self._file_hashes,
                "updated": time.time(),
            }
            METADATA_FILE.write_text(json.dumps(meta), encoding="utf-8")
            logger.info(f"Saved search index: {len(self._metadata)} chunks")
        except Exception as e:
            logger.error(f"Failed to save search index: {e}")

    async def build(self, force: bool = False):
        """Build or incrementally update the search index.

        Runs in a thread pool to avoid blocking the event loop.
        Skips if another build is already in progress.
        """
        if _build_lock.locked():
            logger.info("Embedding index build skipped — another build already in progress")
            return
        async with _build_lock:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: self._build_sync(force))

    def _build_sync(self, force: bool = False):
        """Synchronous index build."""
        try:
            self._load_model()
        except ImportError:
            return

        start = time.time()

        # Load existing index
        if not force:
            self._load_index()

        files = self._get_indexable_files()
        new_chunks = []
        new_metadata = []
        files_updated = 0

        # Keep chunks from unchanged files
        kept_metadata = []
        kept_indices = []

        if not force and self._metadata:
            for i, meta in enumerate(self._metadata):
                fpath = meta.get("file", "")
                old_hash = self._file_hashes.get(fpath, "")
                # Check if file still exists and hasn't changed
                p = Path(fpath) if Path(fpath).is_absolute() else config.CLAWD_HOME / fpath
                if p.exists():
                    try:
                        content = p.read_text(encoding="utf-8", errors="replace")
                        current_hash = self._content_hash(content)
                        if current_hash == old_hash:
                            kept_metadata.append(meta)
                            kept_indices.append(i)
                            continue
                    except Exception as e:
                        logger.debug(f"Failed to read file for hash comparison, re-indexing: {e}")

        # Index new/changed files
        for fpath in files:
            try:
                rel = str(fpath.relative_to(config.CLAWD_HOME))
            except ValueError:
                rel = str(fpath)

            try:
                content = fpath.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            current_hash = self._content_hash(content)
            old_hash = self._file_hashes.get(rel, "")

            if not force and current_hash == old_hash:
                continue

            # File is new or changed — re-chunk and embed
            chunks = self._chunk_text(content)
            for idx, chunk in enumerate(chunks):
                new_chunks.append(chunk)
                new_metadata.append({
                    "file": rel,
                    "chunk_text": chunk,
                    "chunk_idx": idx,
                    "file_hash": current_hash,
                })

            self._file_hashes[rel] = current_hash
            files_updated += 1

        if not new_chunks and not force:
            if not self._ready and self._embeddings is not None:
                self._ready = True
                logger.info(f"Search index ready (no changes, {len(self._metadata)} chunks)")
            return

        # Embed new chunks
        if new_chunks:
            logger.info(f"Embedding {len(new_chunks)} new chunks from {files_updated} files...")
            new_embeddings = self._model.encode(
                new_chunks,
                show_progress_bar=False,
                batch_size=64,
            )
        else:
            new_embeddings = np.array([]).reshape(0, self._model_dim)

        # Combine kept + new
        if kept_indices and self._embeddings is not None:
            kept_embeddings = self._embeddings[kept_indices]
            if new_embeddings.size > 0:
                self._embeddings = np.vstack([kept_embeddings, new_embeddings])
            else:
                self._embeddings = kept_embeddings
            self._metadata = kept_metadata + new_metadata
        else:
            self._embeddings = new_embeddings if new_embeddings.size > 0 else None
            self._metadata = new_metadata

        # Save to disk
        self._save_index()
        self._ready = True

        elapsed = time.time() - start
        logger.info(
            f"Search index built in {elapsed:.1f}s: "
            f"{len(self._metadata)} chunks, {files_updated} files updated"
        )

    def index_file(self, filepath: Path):
        """Re-index a single file (called after memory_update)."""
        if not self._ready or self._model is None:
            return

        try:
            rel = str(filepath.relative_to(config.CLAWD_HOME))
        except ValueError:
            rel = str(filepath)

        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return

        current_hash = self._content_hash(content)
        if current_hash == self._file_hashes.get(rel):
            return  # No change

        # Remove old chunks for this file
        if self._metadata and self._embeddings is not None:
            keep_indices = [
                i for i, m in enumerate(self._metadata)
                if m.get("file") != rel
            ]
            if keep_indices:
                self._embeddings = self._embeddings[keep_indices]
                self._metadata = [self._metadata[i] for i in keep_indices]
            else:
                self._embeddings = np.array([]).reshape(0, self._model_dim)
                self._metadata = []

        # Add new chunks
        chunks = self._chunk_text(content)
        if chunks:
            new_embeddings = self._model.encode(chunks, show_progress_bar=False)
            new_metadata = [
                {"file": rel, "chunk_text": c, "chunk_idx": i, "file_hash": current_hash}
                for i, c in enumerate(chunks)
            ]

            if self._embeddings is not None and self._embeddings.size > 0:
                self._embeddings = np.vstack([self._embeddings, new_embeddings])
            else:
                self._embeddings = new_embeddings
            self._metadata.extend(new_metadata)

        self._file_hashes[rel] = current_hash
        self._save_index()

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, str, float]]:
        """Search the index for semantically similar content.

        Returns list of (filepath, chunk_text, score) tuples.
        """
        if not self._ready or self._model is None or self._embeddings is None:
            return []

        if len(self._embeddings) == 0:
            return []

        # Encode query
        query_embedding = self._model.encode([query], show_progress_bar=False)

        # Cosine similarity
        norms = np.linalg.norm(self._embeddings, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        normalized = self._embeddings / norms

        query_norm = np.linalg.norm(query_embedding)
        if query_norm == 0:
            return []
        query_normalized = query_embedding / query_norm

        similarities = np.dot(normalized, query_normalized.T).flatten()

        # Top-K
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score < 0.1:  # Skip very low similarity
                continue
            meta = self._metadata[idx]
            results.append((meta["file"], meta["chunk_text"], score))

        return results

    @property
    def is_ready(self) -> bool:
        return self._ready

    @property
    def chunk_count(self) -> int:
        return len(self._metadata)
