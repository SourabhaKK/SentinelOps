"""
Session Persistence Layer

Manages investigation state across reconnections.
Allows investigation to resume mid-run after forced disconnect.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import os


@dataclass
class InvestigationState:
    """Complete state of an ongoing investigation."""
    incident_id: str
    session_id: str
    state: str  # STARTED, TRIAGE_COMPLETE, INVESTIGATION_IN_PROGRESS, INVESTIGATION_COMPLETE, REMEDIATION_PROPOSED
    triage_output: Optional[Dict[str, Any]] = None
    investigation_output: Optional[Dict[str, Any]] = None
    remediation_output: Optional[Dict[str, Any]] = None
    last_checkpoint: Optional[str] = None
    timestamp: str = None
    disconnections: int = 0
    reconnections: int = 0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class SessionPersistence:
    """Persist and recover investigation state."""

    def __init__(self, storage_dir: str = "./sessions"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def _get_session_path(self, session_id: str, incident_id: str) -> str:
        """Get path for session state file."""
        return os.path.join(self.storage_dir, f"{session_id}_{incident_id}.json")

    def save_state(self, state: InvestigationState) -> str:
        """
        Save investigation state to disk.

        Returns: Path to saved state file
        """
        path = self._get_session_path(state.session_id, state.incident_id)

        state_dict = asdict(state)
        state_dict["timestamp"] = state.timestamp

        with open(path, "w") as f:
            json.dump(state_dict, f, indent=2, default=str)

        print(f"[Persistence] Saved state: {path}")
        return path

    def load_state(self, session_id: str, incident_id: str) -> Optional[InvestigationState]:
        """
        Load investigation state from disk.

        Returns: InvestigationState if exists, else None
        """
        path = self._get_session_path(session_id, incident_id)

        if not os.path.exists(path):
            print(f"[Persistence] No saved state: {path}")
            return None

        with open(path, "r") as f:
            state_dict = json.load(f)

        try:
            state = InvestigationState(**state_dict)
            print(f"[Persistence] Loaded state: {path}")
            return state
        except Exception as e:
            print(f"[Persistence] Error loading state: {e}")
            return None

    def checkpoint(self, state: InvestigationState, checkpoint_name: str):
        """
        Save a named checkpoint within an investigation.

        Useful for testing reconnection at specific points.
        """
        state.last_checkpoint = checkpoint_name
        state.timestamp = datetime.now().isoformat()
        return self.save_state(state)

    def list_sessions(self) -> List[Dict[str, str]]:
        """List all saved investigation sessions."""
        sessions = []
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.storage_dir, filename)
                with open(path, "r") as f:
                    data = json.load(f)
                    sessions.append({
                        "file": filename,
                        "session_id": data.get("session_id"),
                        "incident_id": data.get("incident_id"),
                        "state": data.get("state"),
                        "last_checkpoint": data.get("last_checkpoint"),
                        "timestamp": data.get("timestamp"),
                    })
        return sessions

    def clear_session(self, session_id: str, incident_id: str):
        """Delete a session's state file."""
        path = self._get_session_path(session_id, incident_id)
        if os.path.exists(path):
            os.remove(path)
            print(f"[Persistence] Cleared session: {path}")


class InvestigationWithPersistence:
    """Investigation wrapper that handles persistence."""

    def __init__(self, session_id: str, incident_id: str, persistence: SessionPersistence = None):
        self.session_id = session_id
        self.incident_id = incident_id
        self.persistence = persistence or SessionPersistence()
        self.state: Optional[InvestigationState] = None

        # Try to load existing state
        loaded = self.persistence.load_state(session_id, incident_id)
        if loaded:
            self.state = loaded
            self.state.reconnections += 1
        else:
            self.state = InvestigationState(
                incident_id=incident_id,
                session_id=session_id,
                state="STARTED",
            )

    def triage_complete(self, triage_output: Dict[str, Any]):
        """Mark triage complete and save state."""
        self.state.triage_output = triage_output
        self.state.state = "TRIAGE_COMPLETE"
        self.persistence.checkpoint(self.state, "triage_complete")

    def investigation_in_progress(self, partial_output: Optional[Dict[str, Any]] = None):
        """Mark investigation as in-progress and save state."""
        self.state.state = "INVESTIGATION_IN_PROGRESS"
        if partial_output:
            self.state.investigation_output = partial_output
        self.persistence.checkpoint(self.state, "investigation_in_progress")

    def investigation_complete(self, investigation_output: Dict[str, Any]):
        """Mark investigation complete and save state."""
        self.state.investigation_output = investigation_output
        self.state.state = "INVESTIGATION_COMPLETE"
        self.persistence.checkpoint(self.state, "investigation_complete")

    def remediation_proposed(self, remediation_output: Dict[str, Any]):
        """Mark remediation proposed and save state."""
        self.state.remediation_output = remediation_output
        self.state.state = "REMEDIATION_PROPOSED"
        self.persistence.checkpoint(self.state, "remediation_proposed")

    def simulate_disconnect(self):
        """Simulate network disconnect during investigation."""
        self.state.disconnections += 1
        self.persistence.save_state(self.state)
        print(f"\n[Persistence] Simulated disconnect #{self.state.disconnections}")
        print(f"             Current state saved: {self.state.state}")

    def resume_after_disconnect(self) -> bool:
        """Resume investigation after simulated disconnect."""
        print(f"\n[Persistence] Resuming after disconnect...")
        print(f"             Previous state: {self.state.state}")
        print(f"             Last checkpoint: {self.state.last_checkpoint}")
        print(f"             Disconnections: {self.state.disconnections}")
        print(f"             Reconnections: {self.state.reconnections}")
        return True

    def get_investigation_context(self) -> Dict[str, Any]:
        """Get complete investigation context (for resumption)."""
        return {
            "incident_id": self.incident_id,
            "session_id": self.session_id,
            "state": self.state.state,
            "triage": self.state.triage_output,
            "investigation": self.state.investigation_output,
            "remediation": self.state.remediation_output,
            "disconnections": self.state.disconnections,
            "reconnections": self.state.reconnections,
            "last_checkpoint": self.state.last_checkpoint,
        }


def test_session_persistence():
    """Test session persistence with simulated disconnect/reconnect."""
    print("\n" + "="*70)
    print("SESSION PERSISTENCE TEST")
    print("="*70)

    persistence = SessionPersistence()
    session_id = f"test-session-{int(datetime.now().timestamp())}"
    incident_id = "bad-deploy-001"

    print(f"\n[Test] Starting new investigation")
    inv = InvestigationWithPersistence(session_id, incident_id, persistence)

    # Phase 1: Triage
    print(f"\n[Test] Phase 1: Triage")
    triage_data = {
        "severity": "CRITICAL",
        "incident_type": "BAD_DEPLOY",
        "confidence": "HIGH",
    }
    inv.triage_complete(triage_data)
    print(f"       State: {inv.state.state}")

    # Phase 2: Investigation starts
    print(f"\n[Test] Phase 2: Investigation starting")
    inv.investigation_in_progress()
    print(f"       State: {inv.state.state}")

    # Simulate disconnect mid-investigation
    print(f"\n[Test] SIMULATED DISCONNECT")
    inv.simulate_disconnect()

    # Simulate reconnection
    print(f"\n[Test] SIMULATED RECONNECTION")
    inv2 = InvestigationWithPersistence(session_id, incident_id, persistence)
    inv2.resume_after_disconnect()

    # Continue investigation
    print(f"\n[Test] Phase 2: Investigation continuing (post-reconnect)")
    investigation_data = {
        "root_cause": "Unauthorized model deployed",
        "candidates": ["bad_commit", "version_mismatch"],
        "findings": "Commit c104edc contains unauthorized model",
    }
    inv2.investigation_complete(investigation_data)
    print(f"       State: {inv2.state.state}")

    # Phase 3: Remediation
    print(f"\n[Test] Phase 3: Remediation")
    remediation_data = {
        "action": "disable_endpoint",
        "reasoning": "Unauthorized model detected; prevent cascading failures",
        "confidence": "HIGH",
    }
    inv2.remediation_proposed(remediation_data)
    print(f"       State: {inv2.state.state}")

    # Print final context
    print(f"\n[Test] Final Investigation Context:")
    context = inv2.get_investigation_context()
    print(json.dumps(context, indent=2, default=str))

    # List all sessions
    print(f"\n[Test] All saved sessions:")
    for session in persistence.list_sessions():
        print(f"       {session['session_id']} / {session['incident_id']}: {session['state']}")

    # Cleanup
    persistence.clear_session(session_id, incident_id)
    print(f"\n[Test] Cleared session for cleanup")

    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)


if __name__ == "__main__":
    test_session_persistence()
