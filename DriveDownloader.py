from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io, os

API_KEY = 'AIzaSyD4E-EnfS8h0AlNlvKWzgBsRYqm0Sx32Mw'

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
        fh = io.FileIO(filename, 'wb')
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Downloaded {int(status.progress() * 100)}%")

    def download_from_drive(self):
        folder_id = "1Qm1u0i9Ck1nLsTR7EExIQSDPbSC3Ltsn"
        newest_file = self._list_files_in_folder(folder_id)
        if newest_file:
            self._download_file(newest_file['id'], newest_file['name'])
            return os.path.abspath(newest_file['name'])