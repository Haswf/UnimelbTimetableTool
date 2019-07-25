import json
import os

class LoginCredential:
    username = None
    password = None
    filepath = None

    def __init__(self, username=None, password=None, filepath=None):
        self.username = username
        self.password = password
        self.filepath = filepath

    def read_from_input(self):
        self.username = input("What's your UoM username: ")
        self.password = input("Then, what's your password: ")

    def read_from_file(self):
        if self.filepath.exists():
            with open(self.filepath) as f:
                credential = json.load(f)
                self.username = credential['username']
                self.password = credential['password']
                return True
        return False

    def save_to_file(self):
        with open(self.filepath, 'w') as f:
            credential = {
                'username': self.username,
                'password': self.password
            }
            json.dump(credential, f)

    def remove_file(self):
        os.remove(self.filepath)

    def get_credential(self):
        if not self.read_from_file():
            self.read_from_input()
            self.save_to_file()