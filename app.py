from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
from dotenv import load_dotenv


# Carregar variáveis de ambiente do arquivo .env
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TARGET_FOLDER_ID = os.getenv("TARGET_FOLDER_ID")


def generate_tokens(client_id, client_secret):
    """
    Generate access token and refresh token using OAuth 2.0 authorization flow.

    Args:
        client_id (str): OAuth 2.0 client ID.
        client_secret (str): OAuth 2.0 client secret.

    Returns:
        tuple: Tuple containing access token and refresh token.
    """
    flow = InstalledAppFlow.from_client_config(
        client_config = {
            "web": {
                "client_id"     : client_id,
                "client_secret" : client_secret,
                "redirect_uris" : ["urn:ietf:wg:oauth:2.0:oob"],
                "auth_uri"      : "https://accounts.google.com/o/oauth2/auth",
                "token_uri"     : "https://accounts.google.com/o/oauth2/token",
            }
        },
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    flow.run_local_server(port=0)
    return flow.credentials.token, flow.credentials.refresh_token


def authenticate_with_token(token):
    """
    Authenticate user with API token.

    Args:
        token (dict): Token dictionary containing access token, refresh token, etc.

    Returns:
        google.oauth2.credentials.Credentials: Authenticated credentials object.
    """
    creds = Credentials.from_authorized_user_info(token)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
    return creds


def upload_file_to_drive(file_path, token, folder_id):
    """
    Upload a file to Google Drive.

    Args:
        file_path (str): Path to the file to be uploaded.
        token (dict): Token dictionary containing access token, refresh token, etc.
        folder_id (str): ID of the folder to upload the file into.
    """
    creds = authenticate_with_token(token)
    service = build("drive", "v3", credentials=creds)
    file_name = os.path.basename(file_path)
    file_metadata = {
        "name"      : file_name,
        "parents"   : [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(
        body        = file_metadata,
        media_body  = media,
        fields      = "id"
    ).execute()
    return file.get("id")


def upload_file_to_drive_as_google_sheet(file_path, token, folder_id):
    """
    Upload an Excel file (xlsx) to Google Drive and convert it to Google Sheets format.

    Args:
        file_path (str): Path to the Excel file to be uploaded.
        token (dict): Token dictionary containing access token, refresh token, etc.
        folder_id (str): ID of the folder to upload the file into.

    Returns:
        str: The ID of the uploaded file in Google Drive.
    """
    creds = authenticate_with_token(token)
    service = build("drive", "v3", credentials=creds)
    file_name = os.path.basename(file_path)
    # File metadata with MIME type for Google Sheets
    file_metadata = {
        "name"      : file_name,
        "mimeType"  : "application/vnd.google-apps.spreadsheet",  # Convert to Google Sheets format
        "parents"   : [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", resumable=True)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()
    return file.get("id")


def get_token_auth(client_id, client_secret):
    access_token, refresh_token = generate_tokens(CLIENT_ID, CLIENT_SECRET)
    token_auth = {
        "token"         : access_token,
        "refresh_token" : refresh_token,
        "token_uri"     : "https://oauth2.googleapis.com/token",
        "client_id"     : client_id,
        "client_secret" : client_secret,
        "scopes"        : ["https://www.googleapis.com/auth/drive"]
    }
    return token_auth
