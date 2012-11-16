#!/usr/bin/env python

import loadb
from common import Common

class ConfigBase(Common):

	def rebuild_config(self):
		raise Exception("Not supported")

	def _read_config(self):
		ecm_config = loadb.ECMConfig()
		return(ecm_config.read())

