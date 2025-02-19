import os
import shutil


class TmpFolder:
    PATH = "tmp"

    @staticmethod
    def clear_folder():
        for the_file in os.listdir(TmpFolder.PATH):
            if the_file == ".gitignore":
                continue
            file_path = os.path.join(TmpFolder.PATH, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                else:
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)

    @staticmethod
    def add_file(file_path):
        shutil.copy2(
            file_path, os.path.join(TmpFolder.PATH, os.path.basename(file_path))
        )

    @staticmethod
    def get_file(file_name):
        return os.path.join(TmpFolder.PATH, file_name)

    @staticmethod
    def backup_folder(folder_path):
        shutil.copytree(
            folder_path, os.path.join(TmpFolder.PATH, os.path.basename(folder_path))
        )

    @staticmethod
    def restore_folder(folder_path):
        shutil.rmtree(folder_path)
        shutil.copytree(
            os.path.join(TmpFolder.PATH, os.path.basename(folder_path)), folder_path
        )
