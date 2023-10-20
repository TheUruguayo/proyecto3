from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io, os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("DRIVE-API_KEY")

class DriveDownloader:
    def __init__(self):
        self.service = self.get_drive_service()

    def get_drive_service(self):
        return build('drive', 'v3', developerKey=API_KEY)

    def _list_files_in_folder(self, folder_id):
        query = f"'{folder_id}' in parents"
        results = self.service.files().list(q=query, orderBy='modifiedTime desc', pageSize=1, fields="files(id, name, modifiedTime)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
            return None
        else:
            newest_file = items[0]
            print(f"Newest file is: {newest_file['name']} (ID: {newest_file['id']}, Modified: {newest_file['modifiedTime']})")
            return newest_file

    def _download_file(self, file_id, filename):
        request = self.service.files().get_media(fileId=file_id)
        print(f"download file path: {filename}")
        fh = io.FileIO(filename, 'wb')
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Downloaded {int(status.progress() * 100)}%")

    def download_from_drive(self, folder_path):
        folder_id = os.getenv("DRIVE-FOLDER_ID")
        app_path = os.getenv("APP-PATH")
        newest_file = self._list_files_in_folder(folder_id)

        if newest_file:
            file_name = newest_file['name']
            download_path = os.path.join(f"{app_path}/models", file_name)
            print(f"Download Path: {download_path} - Folder Path: {folder_path}")

            if download_path == folder_path:
                print("Elimino el archivo existente de mismo nombre")
                os.remove(download_path)

            self._download_file(newest_file['id'], download_path)

            return os.path.abspath(download_path)
