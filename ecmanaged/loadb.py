#!/usr/bin/env python

import os, stat
import simplejson as json
from time import time

import keepalived
from common import Common

CONFIG_TPL_MAIN = {
	'services': {},
	'main': {},
	'config': {
		'balancer':		'keepalived',
		'keepalived': 	'/etc/keepalived/keepalived.conf',
		'init_d': 		'/etc/init.d/keepalived',
		'init_action':  'reload',
	}
}

CONFIG_TPL_SERVICE = {
	'ip': 	None,
	'port': None,
	'params': {
		'lb_algo':		'sh',
		'lb_kind':		'NAT',
		'nat_mask':		'255.255.255.248',
		'protocol':		'TCP',
		'sorry_server': None,
	}
}

CONFIG_TPL_NODE = {
	'ip':	None,
	'port': None,
	'params': {
		'weight': 				1,
		'check': 				'TCP_CHECK',
		'connect_timeout':		'3',
		'retry': 				'3',
		'delay_before_retry':	'3',
		'connect_port':			'587'
	}
}

CONFIG_FILE = '/etc/ecmanaged/loadb_config.json'
SECRET_FILE = '/etc/ecmanaged/secret.def'

class ECMLoadBalancer(Common):
	def __init__(self):
		self.ecm_config = ECMConfig()
		self.config = self.ecm_config.read()

	def config_get(self):
		return self.config

	def config_set(self,config_data,section):
		if config_data and section in ['main','config']:
			try:
				_config = self.config
				add_config_data = {}
				for index in config_data.keys():
					if config_data[index] and not index in add_config_data.keys():
						add_config_data[index] = str(config_data[index])

				# add previous config not overwritting
				for index in _config[section].keys():
					if _config[section][index] and not index in add_config_data.keys():
						add_config_data[index] = _config[section][index]

				_config[section] = add_config_data
				self._rebuild(_config)
				return self.config

			except Exception as e:
				pass

		raise Exception("Invalid data supplied %s" % config_data)

	def service_get(self,service_id):
		service_data = self._get_service(service_id)
		if not service_data:
			raise Exception("Service %s not found" % service_id)

		return service_data

	def service_add(self,service_id,service_data):
		if service_data:
			#try:
			if True:
				_config = self.config
				add_service_data = {}
				add_service_data['name'] = service_id
				add_service_data['time'] = str(int(time()))
				add_service_data['ip']   = service_data['ip']
				add_service_data['port'] = service_data['port']

				# add extra config
				for index in service_data.keys():
					if service_data[index] and not index in add_service_data.keys():
						add_service_data[index] = str(service_data[index])

				# add previous config not overwritting
				if _config['services'].get(service_id,None):
					for index in _config['services'][service_id].keys():
						if _config['services'][service_id][index] and not index in add_service_data.keys():
							add_service_data[index] = _config['services'][service_id][index]

				if not add_service_data.get('nodes',None):
					add_service_data['nodes'] = {}

				_config['services'][service_id] = {}
				_config['services'][service_id] = add_service_data
				self._rebuild(_config)
				return self.config

			#except:
			#	pass

		raise Exception("Invalid data supplied %s" % service_data)

	def service_delete(self,service_id):
		if not self._get_service(service_id):
			raise Exception("Service %s not found" % service_id)

		_config = self.config
		new_service = {}

		# add all other services except service_id
		for index in _config['services'].keys():
			if index !=  service_id:
				new_service[index] = _config['services'][index]

		_config['services'] = new_service
		self._rebuild(_config)
		return self.config

	def node_get(self,service_id,node_id):
		return self._get_node_in_service(service_id,node_id)

	def node_add_into_service(self,service_id,node_id,node_data):
		if not self._get_service(service_id):
			raise Exception("Service %s not found" % service_id)

		if node_data:
			#try:
			if True:
				_config = self.config
				add_node_data = {}
				add_node_data['name'] = node_id
				add_node_data['time'] = str(int(time()))
				add_node_data['ip']   = node_data['ip']
				add_node_data['port'] = node_data['port']

				# add extra config
				for index in node_data.keys():
					if node_data[index] and not index in add_node_data.keys():
						add_node_data[index] = str(node_data[index])

				# add previous config not overwritting
				if _config['services'][service_id]['nodes'].get(node_id,None):
					for index in _config['services'][service_id]['nodes'][node_id].keys():
						if _config['services'][service_id]['nodes'][node_id][index] and not index in add_node_data.keys():
							add_node_data[index] = _config['services'][service_id]['nodes'][node_id][index]

				_config['services'][service_id]['nodes'][node_id] = add_node_data
				self._rebuild(_config)
				return self.config

			#except Exception as e:
				#pass

		raise Exception("Invalid data supplied %s" % node_data)

	def node_delete_from_service(self,service_id,node_id):
		if not self._get_service(service_id):
			raise Exception("Service %s not found" % service_id)

		if node_id:
			try:
				_config = self.config
				node_new = {}
				hash_node = _config['services'][service_id].get('nodes',{})
				for node in hash_node.keys():
					if node != node_id:
						node_new[node] = hash_node[node]

				_config['services'][service_id]['nodes'] = node_new
				self._rebuild(_config)
				return self.config

			except Exception as e:
				pass

		raise Exception("Invalid data supplied")

	def _rebuild(self,config):
		self.ecm_config.write(config)

		_balancer_type = config['config'].get('balancer',None)

		if _balancer_type == 'keepalived':
			LoadBConfig = keepalived.Keepalived()
		else:
			raise Exception('balancer type: %s not supported' % _balancer_type)

		if LoadBConfig.rebuild_config():
			self.config = config
			self._reload()
			return True

		# Rollback to old config
		self.ecm_config.write(self.config)
		LoadBConfig.rebuild_config()
		raise Exception("Invalid configuration generated (rollback)")

	def _reload(self):
		try:
			_init_d = self.config['config']['init_d']
			_action = self.config['config']['init_action']
			if os.path.isfile(_init_d):
				os.system(_init_d + ' ' + _action)

		except Exception as e:
			raise

	def _get_service(self,service_id):
		service = self.config.get('services',{})
		for srv_id in service.keys():
			if srv_id == service_id:
				return service[srv_id]

		return False

	def _get_node_in_service(self,service_id,node_id):
		service = self._get_service(service_id)
		nodes = service.get(['nodes'],{})
		for node in nodes.keys():
			if node == node_id:
				return nodes[node_id]

		return False

	def secret_read(self):
		try:
			os.chmod(SECRET_FILE, stat.S_IREAD)
			return self._file_read(SECRET_FILE)

		except:
			try:
				retval = self._secret_gen()
				self._file_write(SECRET_FILE,None)
				os.chmod(SECRET_FILE, stat.S_IWRITE)

				self._file_write(SECRET_FILE,retval)
				os.chmod(SECRET_FILE, stat.S_IREAD)
				return retval

			except:
				raise Exception("Unable to write %s" %file)


class ECMConfig(Common):
	def write(self,config):
		self._file_write(CONFIG_FILE,json.dumps(config))
		return True

	def read(self):
		if os.path.isfile(CONFIG_FILE):
			try:
				_retval = self._file_read(CONFIG_FILE)
				_retval = json.loads(_retval)
				return _retval

			except:
				raise

		# write blank config
		self.write(CONFIG_TPL_MAIN)
		return self.read()
