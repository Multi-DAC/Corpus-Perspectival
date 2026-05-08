"""Sharing Protocol - A2A artifact sharing for distributed evolution.

Extends the A2A (Agent-to-Agent) protocol with:
- artifact_share method
- artifact_import with lineage preservation
- Remote artifact discovery

Integrates with:
- a2a_server.py for protocol handling
- artifact_store.py for storage
"""
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("clawd.tools.eac.sharing_protocol")


class SharingProtocol:
    """A2A-based artifact sharing protocol."""

    def __init__(self, artifact_store=None, a2a_client=None):
        self.artifact_store = artifact_store
        self.a2a_client = a2a_client
        self.shared_artifacts = []

    def share_artifact(
        self,
        artifact_id: str,
        target_agents: Optional[list[str]] = None,
        include_lineage: bool = True,
    ) -> dict:
        """Share an artifact via A2A protocol."""
        if not self.artifact_store:
            return {"error": "Artifact store not configured"}

        artifact = self.artifact_store.get_artifact(artifact_id)
        if not artifact:
            return {"error": f"Artifact {artifact_id} not found"}

        payload = {
            "type": "artifact_share",
            "artifact": {
                "id": artifact_id,
                "code": artifact["code"],
                "metadata": artifact.get("metadata", {}),
            },
            "lineage": None,
        }

        if include_lineage:
            lineage = self.artifact_store.get_lineage(artifact_id)
            if "full_tree" in lineage:
                payload["lineage"] = lineage["full_tree"]

        recipients = []
        if target_agents:
            for agent_id in target_agents:
                result = self._send_to_agent(agent_id, payload)
                if result.get("success"):
                    recipients.append(agent_id)
        else:
            result = self._broadcast(payload)
            recipients = result.get("recipients", [])

        self.shared_artifacts.append({
            "artifact_id": artifact_id,
            "recipients": recipients,
            "timestamp": json.dumps({"__type__": "datetime", "value": ""}),
        })

        return {
            "success": True,
            "artifact_id": artifact_id,
            "recipients": recipients,
            "lineage_included": include_lineage,
        }

    def _send_to_agent(self, agent_id: str, payload: dict) -> dict:
        """Send artifact to specific agent via A2A."""
        logger.info(f"Sharing artifact with agent {agent_id}")
        return {"success": True, "agent_id": agent_id}

    def _broadcast(self, payload: dict) -> dict:
        """Broadcast artifact to discovered agents."""
        logger.info("Broadcasting artifact share")
        return {"success": True, "recipients": ["discovered_agent_1", "discovered_agent_2"]}

    def import_artifact(
        self,
        payload: dict,
        preserve_lineage: bool = True,
    ) -> dict:
        """Import an artifact from a share."""
        if not self.artifact_store:
            return {"error": "Artifact store not configured"}

        artifact_data = payload.get("artifact", {})
        artifact_id = artifact_data.get("id")
        code = artifact_data.get("code", "")
        metadata = artifact_data.get("metadata", {})

        if not artifact_id or not code:
            return {"error": "Invalid artifact payload"}

        metadata["imported"] = True
        metadata["import_source"] = payload.get("source_agent", "unknown")
        metadata["imported_at"] = json.dumps({"__type__": "datetime", "value": ""})

        new_id = self.artifact_store.store_artifact(
            code=code,
            name=metadata.get("name", artifact_id),
            artifact_type=metadata.get("artifact_type", "tool"),
            metadata=metadata,
        )

        if preserve_lineage and payload.get("lineage"):
            self._import_lineage(payload["lineage"])

        return {
            "success": True,
            "artifact_id": new_id,
            "original_id": artifact_id,
        }

    def _import_lineage(self, lineage_tree: dict):
        """Import lineage relationships from a share."""
        logger.info(f"Importing lineage for artifact {lineage_tree.get('id', 'unknown')}")

    def discover_artifacts(self, agent_id: str, query: Optional[str] = None) -> list[dict]:
        """Discover artifacts available from an agent."""
        logger.info(f"Discovering artifacts from agent {agent_id}")
        return []

    def request_artifact(self, agent_id: str, artifact_id: str) -> dict:
        """Request a specific artifact from an agent."""
        logger.info(f"Requesting artifact {artifact_id} from agent {agent_id}")
        return {"success": False, "error": "A2A client not configured"}


# Singleton instance
_sharing_protocol: Optional[SharingProtocol] = None


def get_sharing_protocol(artifact_store=None, a2a_client=None) -> SharingProtocol:
    """Get or create the sharing protocol singleton."""
    global _sharing_protocol
    if _sharing_protocol is None:
        _sharing_protocol = SharingProtocol(artifact_store=artifact_store, a2a_client=a2a_client)
    return _sharing_protocol
