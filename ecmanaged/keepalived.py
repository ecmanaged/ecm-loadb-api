#!/usr/bin/env python

import os, re
from time import time

from config_base import ConfigBase

class Keepalived(ConfigBase):
	cwd = os.path.dirname(os.path.abspath( __file__ ))
	tpl_header  = cwd + '/../templates/keepalived_header.tpl'
	tpl_virtual_server = cwd + '/../templates/keepalived_virtual_server.tpl'
	tpl_real_server = cwd + '/../templates/keepalived_real_server.tpl'

	def rebuild_config(self):
		# Read and mount templates
		tpl_header  = self._read_tpl(self.tpl_header)
		tpl_virtual_server = self._read_tpl(self.tpl_virtual_server)
		tpl_real_server = self._read_tpl(self.tpl_real_server)

		real_server_config = ''
		virtual_server_config = ''
		config = self._read_config()
		balancer_config = {}

		_file = str(config['config']['keepalived'])
		print str(config)
		for service_id in config.get('services',{}).keys():
			service = config['services'][service_id]
			if service.get('nodes',None):
				for node_id in service['nodes'].keys():
					node = service['nodes'][node_id]
					real_server_config += self._parse_tpl(tpl_real_server,node)
					balancer_config['real_servers'] = real_server_config

				balancer_config = service
				balancer_config['real_servers']= real_server_config
				virtual_server_config += self._parse_tpl(tpl_virtual_server,balancer_config)

		balancer_config = config.get('main',{})
		balancer_config['virtual_servers'] = virtual_server_config
		balancer_full_config = self._parse_tpl(tpl_header,balancer_config)

		if self._test_config(balancer_full_config):
			self._file_write(_file,balancer_full_config)

		return False

	def _read_tpl(self,file):
		ret = None
		if os.path.isfile(file):
			f  = open(file,'r')
			ret = f.read()
			f.close()
			return ret
		else:
			raise Exception("Unable to open template: %s" % file)

	def _parse_tpl(self,tpl,data):
		# Replace values from data
		for index in data.keys():
			if not data[index]: data[index] = ''
			try: tpl = re.sub(r'\$\{' + index + '(:.*?)*\}', data[index], tpl)
			except: pass

		# Add default values from template to data
		for line in tpl.split('\n'):
			matchObj = re.match( r'.+\$\{(.*)[^:(.*?)]*\}.*', line)
			if matchObj:
				try:
					[name,value] = matchObj.group(1).split(':')
					if value: data[name] = value

				except:
					pass

		# Add time value
		if not data.get('time',None):
			data['time'] = str(int(time()))

		# Replace again with default values
		for index in data.keys():
			if data[index]:
				try: tpl = re.sub(r'\$\{' + index + '(:.*?)*\}', data[index], tpl)
				except: pass

		return tpl

	def _test_config(self,tpl):
		for line in tpl.split('\n'):
			matchObj = re.match( r'.+\$\{(.*)[^:(.*)]*\}.*', line)
			if matchObj:
				return False

		return True

