import utarfile
import os
import machine

FOLDER_UPDATE = "/update/"
FILE_UPDATE = FOLDER_UPDATE + "update.tar"

try:
    file_update = utarfile.TarFile(FILE_UPDATE)  # file exists
    for f in file_update : pass  # iterate through tar entire file, exception is thrown if it is invalid
    file_update = utarfile.TarFile(FILE_UPDATE)  # reset file if no exception was thrown

    for file in file_update: # unpack all and copy new files onto system
        if file.type == utarfile.DIRTYPE:
            try:
                os.mkdir("/" + file.name.rstrip("/"))
            except Exception: # ignore exception if folder exists
                pass
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

