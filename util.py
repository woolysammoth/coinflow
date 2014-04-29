import netvend.netvend as netvend

def getAgent(self, command):
	try:
		self.agent = netvend.Agent(command[1], seed=True)
	except netvend.NetvendResponseError as e:
		self.writeConsole('Failed to create agent - ' + str(e))
	return
	
def getAddress(self):
	try:
		self.agentAddress = self.agent.get_address()
	except netvend.NetvendResponseError as e:
		self.writeConsole('Failed to get address - ' + str(e))
	return
	
def initialTip(self):
	try:
		response = self.chbsagent.tip(self.agentAddress, netvend.convert_value(1, 'satoshi', 'usat'), None)
	except netvend.NetvendResponseError as e:
		self.writeConsole('Failed to tip new agent - ' + str(e))
	return
	
def getBalance(self):
	try:
		self.agentBalance = self.agent.fetch_balance()
	except netvend.NetvendResponseError:
		self.agentBalance = 0
	return
	
def putQuery(self, query):
	try:
		response = self.agent.query(query)
	except netvend.NetvendResponseError as e:
		self.writeConsole('Query failed - ' + str(e))
		return
	if response['command_result']['num_rows'] < 1:
		self.writeConsole('No data returned')
		return
	return response['command_result']['rows']
		
def getNick(self, address):
	query = "select data from posts where address = '" + address + "' and data like 'nick:%' order by post_id desc limit 1"
	rows = putQuery(self, query)
	for row in rows:
		self.agentNick = row[0][5:]
	return
