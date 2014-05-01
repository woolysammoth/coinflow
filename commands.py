import netvend.netvend as netvend
import util
import sqlite3

def commandAdd(self, command):
	"""
		Add a new agent
		display the address and balance
		add the agent to the profiles
	"""
	if len(command) < 2:
		self.writeConsole('You need to supply a seed value')
		return
	util.getAgent(self, command)
	util.getAddress(self)
	util.initialTip(self)
	util.getBalance(self)
	self.agentNick = util.getNick(self, self.agentAddress)
	self.agentSeed = command[1]
	conn = sqlite3.connect('coinflow.db')
	c = conn.cursor()
	c.execute('select id from profiles where seed=?;', (command[1],))
	id = c.fetchone()
	if id is None:
		c.execute('insert into profiles (nick, seed) values (?,?);', (str(self.agentNick), str(self.agentSeed)))
	else:
		c.execute('update profiles set nick=? where seed=?;', (str(self.agentNick), str(self.agentSeed)))
	conn.commit()
	conn.close()
	self.writeConsole('Agent created.\nAddress is ' + str(self.agentAddress) + '\nBalance is ' + str(self.agentBalance))
	self.poll()
	return
			
def commandLogin(self, command):
	"""
		Login as an existing agent
		display the nickname (if present), address and balance
		check profiles and update or insert
	"""
	if len(command) < 2:
		self.writeConsole('You need to supply the seed value for the agent you want to login as.')
		return
	util.getAgent(self, command)
	util.getAddress(self)
	util.getBalance(self)
	self.agentNick = util.getNick(self, self.agentAddress)
	self.agentSeed = command[1]
	conn = sqlite3.connect('coinflow.db')
	c = conn.cursor()
	c.execute('select id from profiles where seed=?;', (command[1],))
	id = c.fetchone()
	if id is None:
		c.execute('insert into profiles (nick, seed) values (?,?);', (str(self.agentNick), str(self.agentSeed)))
	else:
		c.execute('update profiles set nick=? where seed=?;', (str(self.agentNick), str(self.agentSeed)))
	conn.commit()
	conn.close()
	self.writeConsole((('Logged in as ' + str(self.agentNick)) if len(self.agentNick) > 0 else ('Logged in'))  + '.\nAddress is ' + str(self.agentAddress) + '\nBalance is ' + str(self.agentBalance))
	self.poll()
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
		response = self.agent.tip(command[1], int(self.tipAmount), None)
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
	
def commandGetTipAmount(self, command):
	"""
		display the current tip amount
	"""
	if self.agent is None:
		self.writeConsole('You don\'t have an active agent.\n/add an agent or /login in order to view tip information.')
		return
	self.writeConsole('Current Tip Amount is ' + str(self.tipAmount) + ' musat')
	return

def commandSetTipAmount(self, command):
	"""
		set the current tip amount
		only in musat for the moment
	"""
	if self.agent is None:
		self.writeConsole('You don\'t have an active agent.\n/add an agent or /login in order to set tip information.')
		return
	if len(command) < 2:
		self.writeConsole('You need to supply the new tip amount in musat.')
		return
	self.tipAmount = command[1]
	self.writeConsole('Tip amount has been set to ' + str(command[1]) + ' musat.')
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
		response = self.agent.post('post:' + command[1])
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
		nick = self.agentNick
	self.writeConsole('\n== Last 10 Posts for ' + nick + ' ==\n')
	query = "select posts.post_id, posts.data, history.fee from posts inner join history on posts.history_id = history.history_id where posts.address = '" + str(command[1]) + "' order by posts.ts asc limit 10"
	rows = util.putQuery(self, query)
	if rows is False:
		self.writeConsole('No posts to display')
		return
	for row in rows['rows']:
		post = row[1].split(':', 1)
		self.writeConsole('Post ID: ' + str(row[0]) + ' Fee: ' + str(row[2]) + '\n>> ' + str(post[1]) + '\n')
	return
			
def commandNick(self, command):
	"""
		set a nickname for the user
		nickname needs to be unique
		update profile
	"""
	if self.agent is None:
		self.writeConsole('You don\'t have an active agent.\n/add an agent or /login in order to set your nickname.') 
		return
	if len(command) < 2:
		self.writeConsole('You need to specify a nickname')
		return
	util.getAllNicks(self)
	if command[1] in self.allNicks:
		self.writeConsole(command[1] + ' is already taken as a nickname.')
		return
	try:
		response = self.agent.post('nick:' + command[1])
		if response['success'] == 1:
			self.writeConsole('>> nick: ' + str(command[1]))
			self.agentNick = command[1]
			conn = sqlite3.connect('coinflow.db')
			c = conn.cursor()
			c.execute('select id from profiles where seed=?;', (str(self.agentSeed),))
			id = c.fetchone()
			if id is None:
				c.execute('insert into profiles (nick, seed) values (?,?);', (str(self.agentNick), str(self.agentSeed)))
			else:
				c.execute('update profiles set nick=? where seed=?;', (str(self.agentNick), str(self.agentSeed)))
			conn.commit()
			conn.close()
		else:
			self.writeConsole('Setting nick failed')
	except netvend.NetvendResponseError as e:
		self.writeConsole('Setting nick failed - ' + str(e))
	return

def commandListAgents(self, command):
	"""
		List all users in the system
	"""
	if self.agent is None:
		self.writeConsole('You don\'t have an active agent.\n/add an agent or /login in order to list agents.') 
		return
	self.writeConsole('\n== Agents ==\n')
	util.getAllNicks(self)
	for nick in self.allNicks:
		self.writeConsole(nick)
	return
	
def commandFollow(self, command):
	"""
		Follow the specified agent
		can specify address or nick
	"""
	if self.agent is None:
		self.writeConsole('You don\'t have an active agent.\n/add an agent or /login in order to follow agents.') 
		return
	if len(command) < 2:
		self.writeConsole('You need to specify an agent to follow')
		return
	if util.isAddress(command[1]):
		query = "select address from accounts where address = '" + command[1] + "';"
	else:
		query = "select address from posts where data like 'nick:" + command[1] + "%' order by ts desc limit 1;"
	rows = util.putQuery(self, query)
	if rows is False:
		self.writeConsole('Couldn\'t find agent ' + command[1])
		return
	if util.isAddress(command[1]):
		address = command[1]
		nick = util.getNick(self, address)
	else:
		address = rows['rows'][0]
		nick = command[1]
	conn = sqlite3.connect('coinflow.db')
	c = conn.cursor()
	c.execute("select id from follows where address = ?;", (str(address),))
	id = c.fetchone() 
	if id is None:
		c.execute("insert into follows (nick, address) values (?,?);", (str(nick), str(address)))
	else:
		c.execute("update follows set nick=? where address=?;", (str(nick), str(address)))
	conn.commit()
	conn.close()
	self.writeConsole('You are now following ' + nick)
	return
	
def commandListFollows(self, command):
	"""
		List all the agents you are following
	"""
	if self.agent is None:
		self.writeConsole('You don\'t have an active agent.\n/add an agent or /login in order to list the agents you follow.') 
		return
	follows = util.getfollows(self)
	if not follows:
		self.writeConsole('You don\'t follow anyone yet')
		return
	self.writeConsole('\n== Following ==\n')
	for follow in follows:
		self.writeConsole(follow[0])
	return

def commandListProfiles(self, command):
	"""
		list the profiles of the current user
		each profile has been logged into at least once
		you don't need to be logged in to view profiles 
	"""
	conn = sqlite3.connect('coinflow.db')
	c = conn.cursor()
	c.execute('select nick, seed from profiles;')
	profiles = c.fetchall()
	conn.close()
	if not profiles:
		self.writeConsole('You don\'t have any profiles.\nAdd an agent to add a profile.')
		return
	self.writeConsole('\n== Profiles ==\n')
	for profile in profiles:
		self.writeConsole(profile[0] + ' >> ' + profile[1])
	return
			
		
	