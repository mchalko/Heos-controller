""" Strip comments and docstrings from a file.
"""

import sys, token, tokenize
import os
import shutil
import htmlmin
from bs4 import BeautifulSoup 
from csscompressor import compress
import rjsmin
def do_file(fname):
    """ Run on just one file.
    """
    source = open(fname)
    mod = open(fname+"_", "w")

    prev_toktype = token.INDENT
    first_line = None
    last_lineno = -1
    last_col = 0

    tokgen = tokenize.generate_tokens(source.readline)
    for toktype, ttext, (slineno, scol), (elineno, ecol), ltext in tokgen:
        if 0:   # Change to if 1 to see the tokens fly by.
            print("%10s %-14s %-20r %r" % (
                tokenize.tok_name.get(toktype, toktype),
                "%d.%d-%d.%d" % (slineno, scol, elineno, ecol),
                ttext, ltext
                ))
        if slineno > last_lineno:
            last_col = 0
        if scol > last_col:
            mod.write(" " * (scol - last_col))
        if toktype == token.STRING and prev_toktype == token.INDENT:
            # Docstring
            mod.write("#--")
        elif toktype == tokenize.COMMENT:
            # Comment
            mod.write("##\n")
        else:
            mod.write(ttext)
        prev_toktype = toktype
        last_col = ecol
        last_lineno = elineno

if __name__ == '__main__':
	src = "src/"
	dest = "build/"
	try:
		shutil.rmtree(dest)
		os.remove("heos_controller.tar")
	except Exception:
		pass
	shutil.copytree(src, dest)
	
	for path, subdirs, files in os.walk(dest):
		for name in files:
			fullname = os.path.join(path, name)
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
				
