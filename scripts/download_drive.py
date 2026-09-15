"""
VINLUX Media Engine — Google Drive downloader.

Reads GOOGLE_CREDENTIALS, TEXTURE_SLUG and GOOGLE_DRIVE_ROOT_NAME
from GitHub Actions environment variables.
"""

import io
import json
import os
import shutil
from pathlib import Path

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
FOLDER_MIME = "application/vnd.google-apps.folder"

# GitHub slug -> expected folder name in Google Drive.
DRIVE_FOLDER_NAMES = {
    "mat-serebro-temnoe": "мат серебро темное",
    "mat-goluboy": "мат голубой",
    "mat-zhelty": "мат желтый",
    "mat-cherny": "мат черный",
    "mat-bely": "мат белый",
    "mat-krasny": "мат красный",
    "mat-siniy": "мат синий",
}


def get_drive_service():
    credentials_json = os.environ.get("GOOGLE_CREDENTIALS", "").strip()
    if not credentials_json:
        raise RuntimeError("GOOGLE_CREDENTIALS secret not found")

    info = json.loads(credentials_json)
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


def escape_query(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def find_folder(service, name: str, parent_id: str | None = None):
    query = [
        f"name='{escape_query(name)}'",
        f"mimeType='{FOLDER_MIME}'",
        "trashed=false",
    ]
    if parent_id:
        query.append(f"'{parent_id}' in parents")

    response = service.files().list(
        q=" and ".join(query),
        fields="files(id,name)",
        pageSize=100,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()

    folders = response.get("files", [])
    if not folders:
        raise RuntimeError(f"Google Drive folder not found: {name}")
    return folders[0]


def list_children(service, folder_id: str):
    result = []
    page_token = None
    while True:
        response = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="nextPageToken,files(id,name,mimeType,size)",
            pageSize=1000,
            pageToken=page_token,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        result.extend(response.get("files", []))
        page_token = response.get("nextPageToken")
        if not page_token:
            return result


def download_file(service, file_id: str, destination: Path):
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = service.files().get_media(fileId=file_id)
    with io.FileIO(destination, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()


def download_texture(texture_slug: str, root_name: str = "VINLUX_MEDIA"):
    service = get_drive_service()

    root = find_folder(service, root_name)
    drive_name = DRIVE_FOLDER_NAMES.get(texture_slug, texture_slug)

    try:
        texture = find_folder(service, drive_name, root["id"])
    except RuntimeError:
        # Allows a Drive folder to be named directly with the Latin slug.
        texture = find_folder(service, texture_slug, root["id"])

    destination = Path("input") / texture_slug
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)

    files = [f for f in list_children(service, texture["id"]) if f["mimeType"] != FOLDER_MIME]
    if not files:
        raise RuntimeError(f"No files found in Google Drive folder: {texture['name']}")

    for item in files:
        download_file(service, item["id"], destination / item["name"])
        print(f"Downloaded: {item['name']} ({item.get('size', '?')} bytes)")

    print(f"Downloaded {len(files)} files from '{texture['name']}' to '{destination}'")


if __name__ == "__main__":
    slug = os.environ.get("TEXTURE_SLUG", "").strip()
    root = os.environ.get("GOOGLE_DRIVE_ROOT_NAME", "VINLUX_MEDIA").strip()
    if not slug:
        raise RuntimeError("TEXTURE_SLUG is empty")
    download_texture(slug, root)
