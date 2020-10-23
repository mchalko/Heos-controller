import os
import sys
import subprocess
import re

def run():
	if not len(sys.argv) in range(4,6):
		print("""Usage : python upload.py COMPORT BAUDRATE DIRECTORY [keepRegex]
	COMPORT - port of the device
	BAUDRATE - communication speed
	DIRECTORY - derectory to upload
	deleteRegex - files on device that match this regex are not deleted""")
		return
	
	useRegex = False
	if len(sys.argv)==5:
		useRegex = True
		regex = re.compile(sys.argv[4])
	
	directory = sys.argv[3]
	command = "ampy --port {} --baud {} ".format(sys.argv[1], sys.argv[2])

	if not os.path.isdir(directory):
		print("invalid directory")
		return
	print("removing existing files ...")
	ufiles = subprocess.run(command + 'ls', stdout=subprocess.PIPE)
	ufiles = ufiles.stdout.decode().split("\r\n")

	for file in ufiles:
		if not file.strip():
			continue
		if useRegex:
			if re.match(regex, file):
				print("keeping " + file)
				continue
		print("removing " + file)
		result = subprocess.run(command + 'rm ' + file, stderr=subprocess.PIPE)
		if result.stderr.decode().strip():
			result = subprocess.run(command + 'rmdir ' + file, stdout=subprocess.PIPE)
		
	print("uploading files ...")
	files = os.listdir(directory)
	for file in files:
		if file[0] == ".":
			continue
		file = directory + "/" + file
		print("uploading " + file)
		subprocess.run(command + 'put ' + file)
	print("finished")

if __name__ == "__main__":
	run()
	
		
