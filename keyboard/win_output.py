import win32api
import win32con
import kconfig
import os
from gtts import gTTS
from playsound import playsound
import socket


def is_connected():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        pass
    return False


class outputManager():
    def __init__(self):
        self.keycode_dict = {"a": 0x41, "b": 0x42, "c": 0x43, "d": 0x44, "e": 0x45, "f": 0x46, "g": 0x47, "h": 0x48,
                             "i": 0x49, "j": 0x4A, "k": 0x4B, "l": 0x4C, "m": 0x4D, "n": 0x4E, "o": 0x4F, "p": 0x50,
                             "q": 0x51, "r": 0x52, "s": 0x53, "t": 0x54, "u": 0x55, "v": 0x56, "w": 0x57, "x": 0x58,
                             "y": 0x59, "z": 0x5A, kconfig.back_char: 0x08, kconfig.space_char: 0x20, " ": 0x20,
                             ".": 0xBE, ",": 0xBC, "?": 0xBF, "!": 0x31}
        self.audio_file = "./resources/to_speak.mp3"
        self.ignore_keyevent = False

    def send_keystroke(self, char):
        if char == " " or char == "_":
            self.ignore_keyevent = True

        if char in ["!", "?"]:
            win32api.keybd_event(0x10, 0, 0, 0)

        keycode = self.keycode_dict[char]
        win32api.keybd_event(keycode, 0, 0, 0)
        win32api.keybd_event(keycode, 0, win32con.KEYEVENTF_KEYUP, 0)

        if char in ["!", "?"]:
            win32api.keybd_event(0x10, 0, win32con.KEYEVENTF_KEYUP, 0)

    def type_text(self, text):
        for char in text:
            if char in self.keycode_dict:
                self.send_keystroke(char)

    def remove_text(self, num):
        keycode = self.keycode_dict[kconfig.back_char]
        for i in range(num):
            win32api.keybd_event(keycode, 0, 0, 0)
            win32api.keybd_event(keycode, 0, win32con.KEYEVENTF_KEYUP, 0)

    def speak_text(self, text):
        print("speak: ", text)
        if is_connected():
            if len(text) > 0:
                myobj = gTTS(text=text, lang="en", slow=False)
                myobj.save(self.audio_file)
                playsound(self.audio_file)
                os.remove(self.audio_file)
        else:
            playsound("./resources/disconnected.mp3")


def main():
    om = outputManager()

    om.speak_text("hello there i'm nomon")

if __name__ == '__main__':
    main()

