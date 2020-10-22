import utarfile
import os
import machine

FOLDER_UPDATE = "/update/"
FILE_UPDATE = FOLDER_UPDATE + "update.tar"


def deleteFiles(folder=""):
    """
    delete all files in given folder
    :param folder: folder with files
    """
    for file in os.listdir(folder):
        try:
            os.remove(file)  # try removing as file
        except OSError:
            deleteFiles(file)  # remove files in the directory
            os.rmdir(file)  # remove empty directory


try:
    file_update = utarfile.TarFile(FILE_UPDATE)  # file exists
    for f in file_update : pass  # iterate through tar entire file, exception is thrown if it is invalid
    file_update = utarfile.TarFile(FILE_UPDATE)  # reset file if no exception was thrown

    deleteFiles("/") # delete all current files

    for file in file_update: # unpack all and copy new files onto system
        if file.type == utarfile.DIRTYPE:
            os.mkdir("/" + file.name.rstrip("/"))
        else:
            extracted = file_update.extractfile(file)
            with open("/" + file.name, "wb") as discFile:
                while True:
                    try:
                        chunk = extracted.read(512)
                    except OSError:
                        break
                    if not chunk:
                        break
                    discFile.write(chunk)
    os.remove(FILE_UPDATE)  # delete the update file
    machine.reset() # reset
except Exception:  # do nothing if something went wrong
    pass
