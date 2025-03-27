
import os
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

    def ValidateChar(self, t):
        if not self.useFilter:
            return True
        return 0x40 <= ord(t) <= 0x5A or 0x61 <= ord(t) <= 0x7A or 0x30 <= ord(t) <= 0x39 or 0x2B <= ord(t) <= 0x2E

    def ValidateString(self, text):
        return all(self.ValidateChar(c) for c in text)

    def DecodeFile(self):
        if not self.pChars or "tankid_password" not in self.pChars:
            return [("Error", ["An error occurred while searching for tankid_password"])]

        self.Positions.clear()
        self.PositionLength.clear()
        for i, value in enumerate(self.Values):
            start = self.pChars.find(value)
            if start != -1 and value == "tankid_password" and self.pChars[start + len(value)] == '_':
                buf = self.pChars[start + 1:].find(value)
                if buf != -1:
                    start += buf + 1
                else:
                    start = -1
            self.Positions.append(start)

        for i, pos in enumerate(self.Positions):
            if pos != -1:
                PosEndBuffer = len(self.pChars)
                for j, other_pos in enumerate(self.Positions):
                    if other_pos > pos and other_pos < PosEndBuffer:
                        PosEndBuffer = other_pos
                self.PositionLength.append(PosEndBuffer)
            else:
                self.PositionLength.append(0)

        for i, pos in enumerate(self.Positions):
            if pos != -1:
                self.Positions[i] += len(self.Values[i])
                self.PositionLength[i] -= self.Positions[i]

        content = []
        for i, pos in enumerate(self.Positions):
            if pos != -1 and self.pType[i] != 5:
                content.append((self.Values[i], self.ListTrigger(i)))
        return content

    def ListTrigger(self, value):
        if value >= len(self.Values):
            return ["Value pointer overflow"]
        pType = self.pType[value]
        pos = self.Positions[value]
        if pType == 0:
            return ["true"] if self.pChars[pos] == '\x01' else ["false"]
        elif pType == 2:
            stringLength = ord(self.pChars[pos])
            return [self.pChars[pos + 4: pos + 4 + stringLength]]
        elif pType == 4:
            stringLength = ord(self.pChars[pos])
            passwordBuffer = self.pChars[pos + 4: pos + 4 + stringLength]
            return self.decodePassword(passwordBuffer, True)
        else:
            return ["unknown type id!"]
        
    def customIndexOf(self, result, buffer):
        buffer_lower = buffer.lower()
        for i, item in enumerate(result):
            if item.lower() == buffer_lower:
                return i
        return -1

    def decodePassword(self, password, file):
        result = []
        password = password.replace('rid','')

        for offset in range(-128, 128):
            buffer = ""
            for i in range(len(password)):
                cbuffer = (ord(password[i]) + offset - (i if file else 0)) % 255
                if not self.ValidateChar(chr(cbuffer)):
                    break
                buffer += chr(cbuffer)
            if len(buffer) >= len(password):
                if not self.useFilter or self.customIndexOf(result, buffer) == -1:
                    result.append(buffer)
        return result
    
if __name__ == "__main__":
    decoder = Decoder()
    decoded_content = decoder.DecodeFile()
    pprint(decoded_content)
