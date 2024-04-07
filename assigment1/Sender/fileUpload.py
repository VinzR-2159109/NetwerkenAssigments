import requests

class FileUploader:
    def __init__(self, file_path):
        self.file_path = file_path

    def upload(self):
        try:
            url = 'https://file.io/'
            files = {'file': open(self.file_path, 'rb')}
            response = requests.post(url, files=files)
            
            if response.status_code == 200:
                data = response.json()
                file_url = data.get('key')
                return file_url, None
            else:
                return None, f"Upload failed. Status code: {response.status_code}"
        except Exception as e:
            return None, f"An error occurred: {str(e)}"
