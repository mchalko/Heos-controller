import sys
import os
import shutil
import htmlmin
from bs4 import BeautifulSoup 
from csscompressor import compress
import rjsmin


if __name__ == '__main__':
	src = "src/"
	dest = "build/"
	try:
		shutil.rmtree(dest)
		os.remove("heos_controller.tar")
	except Exception:
		pass
	shutil.copytree(src, dest)
	for file in os.listdir(dest):
		name = dest+file
		if file[0] == ".":
			if os.path.isdir(name):
				shutil.rmtree(name)
			else:
				os.remove(name)
	
	for path, subdirs, files in os.walk(dest):
	    
		for name in files:
			fullname = os.path.join(path, name)
			if fullname[0] == ".":
				continue
			print("processing file :", fullname)
			filename, file_extension = os.path.splitext(name)
			if file_extension == ".py":
				os.system("pyminifier "+fullname+" | sed -e '/^[ \t]*#/d' > " +fullname+"min")
				os.remove(fullname)
				os.rename(fullname+"min", fullname)
			elif file_extension == ".html":
				with open(fullname, "r") as htmlf:
					data = htmlf.read()
					soup = BeautifulSoup(data,"lxml")
					for scr in soup.findAll('script'):
						scr.string.replace_with(rjsmin.jsmin(scr.string))
					for stl in soup.findAll('style'):
						stl.string.replace_with (compress(stl.string))
					data = str(soup)
					datamin = htmlmin.minify(data, remove_empty_space=True)
				with open(fullname, "w") as htmlf:
					htmlf.write(datamin)
				
	os.system('cd '+dest+'& tar -cvf ../heos_controller.tar *')
				
