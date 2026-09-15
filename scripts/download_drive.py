"""
VINLUX Media Engine
Google Drive downloader.

Reads GOOGLE_CREDENTIALS from GitHub Actions secret and downloads
VINLUX_MEDIA folders for processing.
"""

import os
import json
from pathlib import Path
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def get_drive_service():
    credentials_json = os.environ.get("GOOGLE_CREDENTIALS")
    if not credentials_json:
        raise RuntimeError("GOOGLE_CREDENTIALS secret not found")

    info = json.loads(credentials_json)
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


def download_folder(folder_name, output="input"):
    service = get_drive_service()

    result = service.files().list(
        q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
        fields="files(id,name)"
    ).execute()

    folders = result.get("files", [])
    if not folders:
        raise RuntimeError(f"Folder not found: {folder_name}")

    folder_id = folders[0]["id"]
    Path(output, folder_name).mkdir(parents=True, exist_ok=True)

    files = service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id,name)"
    ).execute().get("files", [])

    for file in files:
        request = service.files().get_media(fileId=file["id"])
        path = Path(output, folder_name, file["name"])

        with io.FileIO(path, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

    print(f"Downloaded {len(files)} files from {folder_name}")


if __name__ == "__main__":
    import sys
    download_folder(sys.argv[1])
