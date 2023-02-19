import os, random
from internal.logger import new_logger

log = new_logger()

documents = "documents"
photos = "photos"
ignore_files = [".gitkeep"]

assets_path = os.path.join(os.getcwd(), "assets")

photo_formats = ["jpg", "png"]
# doc_formats = ["doc", "odt", "pdf", "docx", ] бред расписывать

def open_directory_and_get_filenames(dir_name):
    files = os.listdir(os.path.join(assets_path, dir_name))
    try:
        files.remove(ignore_files[0]) # TODO
    except Exception as err:
        log.warn(err)
        pass
    return files

def get_file(dir, name):
    try:
        return open(os.path.join(assets_path, dir, name), "rb")
    except Exception as err:
        log.error(err)
        return None



class Asseter:
    typesdoc = ["Документы", "Фотографии"]
    def __init__(self):
        self.documents = self.refresh_documents()
        # self.photos = self.refresh_photos()

    def refresh_documents(self):
        return open_directory_and_get_filenames(documents)
    
    def refresh_photos(self):
        photos_files = open_directory_and_get_filenames(photos)
        pld = []
        for pf in photos_files:
            if pf.split(".")[-1] not in photo_formats:
                continue
            pld.append(pf)
        return pld
    
    def get_rand_photo(self):
        rand_name = random.choice(self.refresh_photos())
        if rand_name in ignore_files:
            return self.get_rand_photo()
        return get_file(photos, rand_name)
        


    def get_doc_by_name(self, name):
        self.refresh_documents()
        return get_file(documents, name)