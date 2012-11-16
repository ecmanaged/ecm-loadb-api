#!/usr/bin/env python

import os, string, random

class Common(object):

	def _file_write(self,file,content=None):
		try:
			_path = os.path.dirname(file)
			if not os.path.exists(_path):
				os.mkdir(_path)

			f  = open(file,'w')
			if content:
				f.write(content)
			f.close()

		except:
			raise Exception("Unable to write file: %s" % file)

	def _file_read(self,file):
		try:
			if os.path.isfile(file):
				f  = open(file,'r')
				retval = f.read()
				f.close()
				return retval

		except:
			raise Exception("Unable to read file: %s" % file)

	def _secret_gen(self):
		chars = string.ascii_uppercase + string.digits  + '!@#$%^&*()'
		return ''.join(random.choice(chars) for x in range(60))
