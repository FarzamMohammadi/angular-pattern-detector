from tkinter import Tk
from tkinter.filedialog import askopenfilename

class FileManager:
    def __init__(self, file_path, logger):
        self.file_path = file_path
        self.logger = logger

    def get_file_path():
        root = Tk()
        root.withdraw()
        file_path = askopenfilename()
        return file_path

    def read_file(self):
        try:
            with open(self.file_path, 'r') as file:
                data = file.read()
            return data
        except FileNotFoundError:
            self.logger.error(f"{self.file_path} not found.")
            return None
            