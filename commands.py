import netvend.netvend as netvend
import util

def commandAdd(self, command):
	"""
		Add a new agent
		display the address and balance
	"""
	if len(command) < 2:
		self.writeConsole('You need to supply a seed value')
		return
	util.getAgent(self, command)
	util.getAddress(self)
	util.initialTip(self)
	util.getBalance(self)
	self.writeConsole('Agent created.\nAddress is ' + str(self.agentAddress) + '\nBalance is ' + str(self.agentBalance))
	return
			
def commandLogin(self, command):
	"""
		Login as an existing agent
		display the nickname (if present), address and balance
	"""
	if len(command) < 2:
		self.writeConsole('You need to supply the seed value for the agent you want to login as.')
		return
	util.getAgent(self, command)
	util.getAddress(self)
	util.getBalance(self)
	util.getNick(self, self.agentAddress)
	self.writeConsole((('Logged in as ' + str(self.agentNick)) if len(self.agentNick) > 0 else ('Logged in'))  + '.\nAddress is ' + str(self.agentAddress) + '\nBalance is ' + str(self.agentBalance))
	return
			
def commandTip(self, command):
	"""
		Tip a nickname, address or post_id
		nickname tipping still in progress
	"""
	if self.agent is None:
		self.writeConsole('You don\'t have an active agent.\n/add an agent or /login in order to tip.')
		return
	elif len(command) < 2:
		self.writeConsole('You need to supply the address of the agent or post you wish to tip.')
		return
	try:
		response = self.agent.tip(command[1], netvend.convert_value(1, 'usat', 'usat'), None)
		if response['success'] == 1:
			try:
				self.agentBalance = self.agent.fetch_balance()
			except netvend.NetvendResponseError as e:
				self.agentBalance = 0
			self.writeConsole('Tip successful.\nHistory ID is ' + str(response['history_id']) + '\nTip ID is ' + str(response['command_result']) + '\nNew Balance is ' + str(self.agentBalance))
		else:
			self.writeConsole('Tip Failed')
			return
	except netvend.NetvendResponseError as e:
		self.writeConsole('Tip failed - ' + str(e))
	return
		
def commandPost(self, command):
	"""
		Post a message to netvend
	"""
	if self.agent is None:
		self.writeConsole('You don\'t have an active agent.\n/add an agent or /login in order to post.') 
		return
	if len(command) < 2:
		self.writeConsole('You need to supply the message to post.')
		return
	try:
		response = self.agent.post(command[1])
		if response['success'] == 1:
			self.writeConsole('>> ' + str(command[1]) + '\nPost ID is ' + str(response['command_result']))
		else:
			self.writeConsole('Post failed')
	except netvend.NetvendResponseError as e:
		self.writeConsole('Post failed - ' + str(e))
	return
		
def commandHistory(self, command):
	"""
		Display the last ten posts for the specified user
		the users current agents posts are shown if no address/nick is given
	"""
	if self.agent is None:
		self.writeConsole('You don\'t have an active agent.\n/add an agent or /login in order to view history.') 
		return
	if len(command) < 2:
		command.append(self.agentAddress)
	self.writeConsole('\n== Last 10 Posts for ' + self.agentNick + ' ==\n')
	query = "select posts.post_id, posts.data, history.fee from posts inner join history on posts.history_id = history.history_id where posts.address = '" + str(command[1]) + "' order by posts.ts asc limit 10"
	rows = util.putQuery(self, query)
	for row in rows:
		self.writeConsole('Post ID: ' + str(row[0]) + ' Fee: ' + str(row[2]) + '\n>> ' + str(row[1]) + '\n')
	return
			
def commandNick(self, command):
	"""
		set a nickname for the user
	"""
	if self.agent is None:
		self.writeConsole('You don\'t have an active agent.\n/add an agent or /login in order to set your nickname.') 
		return
	if len(command) < 2:
		self.writeConsole('You need to specify a nickname')
		return
	try:
		response = self.agent.post('nick:' + command[1])
		if response['success'] == 1:
			self.writeConsole('>> nick: ' + str(command[1]))
		else:
			self.writeConsole('Setting nick failed')
	except netvend.NetvendResponseError as e:
		self.writeConsole('Setting nick failed - ' + str(e))
	return
