import json
from typing import Any, Optional

from firebase_admin import credentials
from google.oauth2.service_account import Credentials


# Custom credentials that use json string for the firebase initialization
# Taken from: https://github.com/xtrinch/fcm-django/issues/212
# Exact instructions for generating the JSON at
# https://firebase.google.com/docs/admin/setup#initialize_the_sdk_in_non-google_environments
# The primary difference is that the json is taken from the environment variable
class CustomFirebaseCredentials(credentials.ApplicationDefault):
    def __init__(self, service_account_json: str):
        self.service_account_json = service_account_json
        super().__init__()

    _g_credential: Optional[Any]

    def _load_credential(self):
        if not self._g_credential:
            json_creds = json.loads(self.service_account_json)
            self._project_id = json_creds["project_id"]
            self._g_credential = Credentials.from_service_account_info(json_creds, scopes=credentials._scopes)
