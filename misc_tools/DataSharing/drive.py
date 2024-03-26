import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import os
from google.oauth2.credentials import Credentials


def upload(filepath):

    SCOPES = ["https://www.googleapis.com/auth/drive"]
    dir_path = os.path.dirname(os.path.realpath(__file__)) + '/'
    # creds, _ = google.auth.default()
    if os.path.exists(dir_path + "token.json"):
        creds = Credentials.from_authorized_user_file(dir_path + "token.json", SCOPES)
    try:
        # create drive api client
        service = build("drive", "v3", credentials=creds)

        file_metadata = {"name": filepath}
        media = MediaFileUpload(file_metadata["name"], mimetype=None)
        # pylint: disable=maybe-no-member
        file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
        )
        print(f'File ID: {file.get("id")}')

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None

    return file.get("id")

def trash(file_id):
  
    SCOPES = ["https://www.googleapis.com/auth/drive"]
    dir_path = os.path.dirname(os.path.realpath(__file__)) + '/'
    # creds, _ = google.auth.default()
    if os.path.exists(dir_path + "token.json"):
        creds = Credentials.from_authorized_user_file(dir_path + "token.json", SCOPES)
    try:
        # create drive api client
        service = build("drive", "v3", credentials=creds)
        body_value = {'trashed': True}
        service.files().update(fileId=file_id, body=body_value).execute()
        print('File moved to trash.')

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None
    
    return 


if __name__ == "__main__":
    upload()
