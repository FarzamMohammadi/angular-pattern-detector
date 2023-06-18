from logger import Logger
from file_manager import FileManager

if __name__ == '__main__':
    logger = Logger("file_manager")
    file_path = FileManager.get_file_path()
    file_manager = FileManager(file_path, logger)
    data = file_manager.read_file()
    print(data)