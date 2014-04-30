import netvend.netvend as netvend

def getAgent(self, command):
	"""
		connect to nedvend using the specified seed
	"""
	try:
		self.agent = netvend.Agent(command[1], seed=True)
	except netvend.NetvendResponseError as e:
		self.writeConsole('Failed to create agent - ' + str(e))
	return
	
def getAddress(self):
	"""
		get the address for the currently logged in agent
	"""
	try:
		self.agentAddress = self.agent.get_address()
	except netvend.NetvendResponseError as e:
		self.writeConsole('Failed to get address - ' + str(e))
	return
	
def initialTip(self):
	"""
		send a tip from the correct horse battery staple agent to get the new agent funded
	"""
	try:
		response = self.chbsagent.tip(self.agentAddress, netvend.convert_value(1, 'satoshi', 'usat'), None)
	except netvend.NetvendResponseError as e:
		self.writeConsole('Failed to tip new agent - ' + str(e))
	return
	
def getBalance(self):
	"""
		get the balance for the logged in agent
	"""
	try:
		self.agentBalance = self.agent.fetch_balance()
	except netvend.NetvendResponseError:
		self.agentBalance = 0
	return
	
def putQuery(self, query):
	"""
		send the supplied query to netvend and return the response or False on error
	"""
	try:
		response = self.agent.query(query)
	except netvend.NetvendResponseError as e:
		if 'f:' in e:
			self.writeConsole('Not enough funds for query - ' + query)
		else:
			self.writeConsole('Query error - ' + str(e) + '\n' + query)
		return False
	if response['command_result']['num_rows'] < 1:
		self.writeConsole('No rows returned')
		return False
	return response['command_result']
		
def getNick(self, address):
	"""
		get the nickname associated with the specified address
	"""
	query = "select data from posts where address = '" + address + "' and data like 'nick:%' order by post_id desc limit 1"
	rows = putQuery(self, query)
	if rows is False:
		return address
	for row in rows['rows']:
		data = row[0]
	print(data)
	return data[5:]
	
	
def isAddress(check):
	"""
		return True if the check string is a bitcoin address
	"""
	import re
	if re.search('^[13][a-zA-Z0-9]{26,33}$', check):
		return True
	else:
		return False

def getAllNicks(self):
	"""
		return a list of nicknames for all users
	"""
	query = "select address from accounts"
	rows = putQuery(self, query)
	if rows is False:
		self.writeConsole('No agents to display')
		return
	self.allNicks = []
	for row in rows['rows']:
		nick = getNick(self, str(row[0]))
		self.allNicks.append(nick)
	return