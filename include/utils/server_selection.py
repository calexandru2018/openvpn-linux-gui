from include.logger import log

def auto_select_optimal_server(data, tier):
	"""Returns a tuple with information abou the most optimal server.
	Returns:
	-------
	tuple (connection_ID, best_score, server_name) 
	"""
	best_score = 999
	connection_ID = ''
	server_name = ''
	for server in data['serverList']:
		if (data['serverList'][server]['score'] < best_score) and (int(data['serverList'][server]['tier']) == tier):
			server_name = data['serverList'][server]['name']
			connection_ID = data['serverList'][server]['id']
			best_score = data['serverList'][server]['score']
			server_load = data['serverList'][server]['load']

	connectInfo = (connection_ID, best_score, server_name, server_load)
	log.debug(f"Connection information {connectInfo}")
	return connectInfo