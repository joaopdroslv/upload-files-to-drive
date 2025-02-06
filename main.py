from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
from typing import Dict, Tuple


def generate_tokens(client_id: str, client_secret: str) -> Tuple[str, str]:
    """
    Generate access token and refresh token using OAuth 2.0 authorization flow.

    This function initiates an OAuth 2.0 authorization flow, allowing the user to 
    authenticate and authorize access to their Google Drive account. It retrieves 
    both the access token and refresh token necessary for making authenticated API calls.

    Args:
        client_id (str): OAuth 2.0 client ID provided by Google Cloud Console.
        client_secret (str): OAuth 2.0 client secret provided by Google Cloud Console.

    Returns:
        tuple: Tuple containing access token (str) and refresh token (str).
    """
    # Create an OAuth 2.0 flow instance
    flow = InstalledAppFlow.from_client_config(
        client_config={
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://accounts.google.com/o/oauth2/token",
            }
        },
        scopes=["https://www.googleapis.com/auth/drive"]  # Scope for Google Drive API
    )
    
    # Start the local server and obtain user authorization
    flow.run_local_server(port=0)
    
    # Return the access and refresh tokens
    return flow.credentials.token, flow.credentials.refresh_token


def authenticate_with_token(token: Dict[str, str]) -> Credentials:
    """
    Authenticate user with API token.

    This function takes a token dictionary and creates an authenticated credentials object.
    If the access token is expired, it attempts to refresh it using the refresh token.

    Args:
        token (dict): Token dictionary containing access token, refresh token, etc.

    Returns:
        google.oauth2.credentials.Credentials: Authenticated credentials object.
    """
    # Create credentials from the provided token dictionary
    creds = Credentials.from_authorized_user_info(token)
    
    # Check if credentials are valid
    if not creds.valid:
        # If expired and refresh token is available, refresh the credentials
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
    
    return creds


def upload_file_to_drive(file_path: str, token: Dict[str, str], folder_id: str) -> str:
    """
    Upload a file to Google Drive.

    This function uploads a specified file to a specified folder in Google Drive.
    It authenticates the user using the provided token, prepares the file for upload,
    and interacts with the Google Drive API to upload the file.

    Args:
        file_path (str): Path to the file to be uploaded.
        token (dict): Token dictionary containing access token, refresh token, etc.
        folder_id (str): ID of the folder to upload the file into.

    Returns:
        str: The ID of the uploaded file in Google Drive.
    """
    # Authenticate and get valid credentials
    creds = authenticate_with_token(token)
    
    # Build the Google Drive API service
    service = build("drive", "v3", credentials=creds)
    
    # Extract the file name from the file path
    file_name = os.path.basename(file_path)
    
    # Prepare the metadata for the file to be uploaded
    file_metadata = {
        "name": file_name,  # The name of the file in Google Drive
        "parents": [folder_id]  # The ID of the folder to upload the file into
    }
    
    # Create a MediaFileUpload object to handle the file upload
    media = MediaFileUpload(file_path, resumable=True)
    
    # Create the file in Google Drive
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"  # Request the ID of the uploaded file
    ).execute()
    
    # Return the ID of the uploaded file
    return file.get("id")


def upload_file_to_drive_as_google_sheet(file_path: str, token: Dict[str, str], folder_id: str) -> str:
    """
    Upload an Excel file (xlsx) to Google Drive and convert it to Google Sheets format.

    This function takes an Excel file and uploads it to Google Drive, converting it
    to Google Sheets format in the specified folder. It authenticates the user using
    the provided token.

    Args:
        file_path (str): Path to the Excel file to be uploaded.
        token (dict): Token dictionary containing access token, refresh token, etc.
        folder_id (str): ID of the folder to upload the file into.

    Returns:
        str: The ID of the uploaded file in Google Drive.
    """
    # Authenticate and get valid credentials
    creds = authenticate_with_token(token)
    
    # Build the Google Drive API service
    service = build("drive", "v3", credentials=creds)
    
    # Extract the file name from the file path
    file_name = os.path.basename(file_path)
    
    # Prepare the metadata for the file with MIME type for Google Sheets
    file_metadata = {
        "name": file_name,  # The name of the file in Google Drive
        "mimeType": "application/vnd.google-apps.spreadsheet",  # MIME type for Google Sheets
        "parents": [folder_id]  # The ID of the folder to upload the file into
    }
    
    # Create a MediaFileUpload object for the Excel file
    media = MediaFileUpload(file_path, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", resumable=True)
    
    # Create the file in Google Drive, converting it to Google Sheets
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"  # Request the ID of the uploaded file
    ).execute()
    
    # Return the ID of the uploaded file
    return file.get("id")


def get_token_auth(client_id: str, client_secret: str) -> Dict[str, str]:
    """
    Get authentication tokens for Google Drive API.

    This function generates access and refresh tokens by calling the 
    `generate_tokens` function. It creates a token dictionary that is used 
    for subsequent API calls.

    Args:
        client_id (str): OAuth 2.0 client ID provided by Google Cloud Console.
        client_secret (str): OAuth 2.0 client secret provided by Google Cloud Console.

    Returns:
        dict: Dictionary containing the access token, refresh token, token URI,
              client ID, client secret, and scopes.
    """
    # Generate access and refresh tokens
    access_token, refresh_token = generate_tokens(client_id, client_secret)
    
    # Create a token dictionary for later use
    token_auth = {
        "token": access_token,  # Access token for API calls
        "refresh_token": refresh_token,  # Refresh token to obtain new access tokens
        "token_uri": "https://oauth2.googleapis.com/token",  # Token URI for refreshing tokens
        "client_id": client_id,  # Client ID
        "client_secret": client_secret,  # Client secret
        "scopes": ["https://www.googleapis.com/auth/drive"]  # Scopes for Google Drive API
    }
    
    return token_auth
