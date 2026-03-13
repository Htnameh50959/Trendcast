import os
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore

_app = None

def get_firebase_app():
    global _app
    if _app is None:
        sa_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
        if not sa_json:
            raise RuntimeError("FIREBASE_SERVICE_ACCOUNT environment variable is not set")
        sa_dict = json.loads(sa_json)
        cred = credentials.Certificate(sa_dict)
        _app = firebase_admin.initialize_app(cred)
    return _app

def get_db():
    get_firebase_app()
    return firestore.client()

def verify_token(token: str) -> str:
    get_firebase_app()
    decoded = auth.verify_id_token(token)
    return decoded["uid"]
