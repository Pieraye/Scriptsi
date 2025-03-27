import json
from pprint import pprint

DAT_FILE_PATH = r"C:\Users\Sigit Cutting\Desktop\save.dat"

class Decoder:
    Values = [
        "graphic_detail", "sfx_vol", "defaultScrollProgress", "music_vol",
        "swearFilter", "fullscreen", "pass_update", "tankid_password_chk2",
        "legal_progress", "name", "lastworld", "tankid_checkbox",
        "tankid_name", "tankid_password", "enter", "defaultInventoryHeight",
        "defaultLogHeight", "Client", "meta", "rid", "touch", "rememberZoom",
        "sendSkinColor", "zoomSave", "addJump", "skinColor"
    ]
    
    def __init__(self, path):
        self.pChars = ""
        self.pSize = 0
        self.Positions = []
        self.PositionLength = []
        self.useFilter = True
        self.openFile(path)

    def openFile(self, path):
        try:
            with open(path, 'rb') as file:
                content = file.read()
                self.pSize = len(content)
                self.pChars = content.decode('latin-1', errors='ignore')
                return True
        except Exception as e:
            print(f"Error reading save file: {e}")
            return False

    def DecodeFile(self):
        if not self.pChars or "tankid_password" not in self.pChars:
            return {"Error": "Failed to find tankid_password"}

        extracted_data = {}
        for value in self.Values:
            start = self.pChars.find(value)
            if start != -1:
                extracted_data[value] = self.extractValue(start, value)
        
        return extracted_data

    def extractValue(self, pos, key):
        pos += len(key)
        if key == "tankid_password":
            return ["Hidden for security"]
        elif key in ["name", "lastworld", "rid", "tankid_name"]:
            stringLength = ord(self.pChars[pos])
            return self.pChars[pos + 4: pos + 4 + stringLength]
        elif key in ["fullscreen", "swearFilter", "touch", "addJump"]:
            return "true" if self.pChars[pos] == '\x01' else "false"
        return "unknown"

if __name__ == "__main__":
    decoder = Decoder(DAT_FILE_PATH)
    decoded_content = decoder.DecodeFile()
    
    # Save to JSON file
    with open("decoded_data.json", "w") as f:
        json.dump(decoded_content, f, indent=4)
    
    pprint(decoded_content)
