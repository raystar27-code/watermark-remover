import os
import shutil
import tempfile
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
]

TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"


class GoogleDriveManager:
    def __init__(self):
        self.service = None
        self._authenticate()

    def _authenticate(self):
        creds = None
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(CREDENTIALS_FILE):
                    raise FileNotFoundError(
                        f"'{CREDENTIALS_FILE}' not found. "
                        "Please download it from Google Cloud Console:\n"
                        "1. Go to https://console.cloud.google.com/\n"
                        "2. Create project → Enable Drive API\n"
                        "3. Create OAuth client ID (Desktop app)\n"
                        "4. Download and rename to 'credentials.json'"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())
        self.service = build("drive", "v3", credentials=creds)

    def list_pdfs(self, folder_id=None):
        query = "mimeType='application/pdf'"
        if folder_id:
            query += f" and '{folder_id}' in parents"
        else:
            query += " and 'root' in parents"
        results = (
            self.service.files()
            .list(q=query, pageSize=100, fields="files(id, name)")
            .execute()
        )
        return results.get("files", [])

    def download_file(self, file_id, local_path=None):
        if local_path is None:
            fd, local_path = tempfile.mkstemp(suffix=".pdf")
            os.close(fd)
        request = self.service.files().get_media(fileId=file_id)
        with open(local_path, "wb") as f:
            f.write(request.execute())
        return local_path

    def upload_folder(self, local_folder, parent_folder_id=None):
        folder_name = Path(local_folder).name
        folder_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_folder_id:
            folder_metadata["parents"] = [parent_folder_id]

        try:
            folder = (
                self.service.files()
                .create(body=folder_metadata, fields="id, webViewLink")
                .execute()
            )
            folder_id = folder.get("id")
            web_link = folder.get("webViewLink")

            self._upload_recursive(local_folder, folder_id)
            return folder_id, web_link
        except HttpError as e:
            raise Exception(f"Upload failed: {e}")

    def _upload_recursive(self, local_path, parent_id):
        for item in Path(local_path).iterdir():
            if item.is_file():
                file_metadata = {"name": item.name, "parents": [parent_id]}
                media = MediaFileUpload(str(item))
                self.service.files().create(
                    body=file_metadata, media_body=media, fields="id"
                ).execute()
            elif item.is_dir():
                subfolder_metadata = {
                    "name": item.name,
                    "mimeType": "application/vnd.google-apps.folder",
                    "parents": [parent_id],
                }
                subfolder = (
                    self.service.files()
                    .create(body=subfolder_metadata, fields="id")
                    .execute()
                )
                self._upload_recursive(item, subfolder.get("id"))

    def get_folder_link(self, folder_id):
        return f"https://drive.google.com/drive/folders/{folder_id}"
