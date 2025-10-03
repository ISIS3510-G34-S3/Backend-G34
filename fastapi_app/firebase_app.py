import os
import glob
from typing import Optional

import firebase_admin
from firebase_admin import credentials


def _find_default_service_account_path() -> Optional[str]:
    """Resolve a service account JSON path from env or firebase/ directory."""
    # 1) Environment variable GOOGLE_APPLICATION_CREDENTIALS
    env_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if env_path and os.path.isfile(env_path):
        return env_path

    # 2) Project-root/firebase/serviceAccountKey.json
    project_root = os.path.dirname(os.path.dirname(__file__))
    explicit_path = os.path.join(project_root, "firebase", "serviceAccountKey.json")
    if os.path.isfile(explicit_path):
        return explicit_path

    # 3) First *.json in project-root/firebase/
    candidates = glob.glob(os.path.join(project_root, "firebase", "*.json"))
    if candidates:
        return candidates[0]

    return None


def initialize_firebase_app() -> firebase_admin.App:
    """Get or initialize the global Firebase Admin app.

    Prefers GOOGLE_APPLICATION_CREDENTIALS; falls back to firebase/*.json.
    """
    try:
        return firebase_admin.get_app()
    except ValueError:
        service_account_path = _find_default_service_account_path()
        if not service_account_path:
            raise RuntimeError(
                "Firebase Admin credentials not found. Set GOOGLE_APPLICATION_CREDENTIALS or place a service account JSON under firebase/."
            )
        cred = credentials.Certificate(service_account_path)
        return firebase_admin.initialize_app(cred)


# Initialize at import so other modules can rely on it.
firebase_app = initialize_firebase_app()


