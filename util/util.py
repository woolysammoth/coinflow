import netvend.netvend as netvend
import db as db
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


def checkLogin(self):
	"""
		check for an active agent.
		return True if one is found
		False otherwise
	"""
	if self.agent is None:
		self.writeConsole('You do not have an active agent.')
		return False
	else:
		return True


def getAgent(self):
	"""
		connect to netvend agent using the specified seed
		agent is created if it doesn't already exist
	"""
	try:
		self.agent = netvend.Agent(self.agentSeed, seed=True)
	except netvend.NetvendResponseError as e:
		self.writeConsole('Failed to get agent - ' + str(e))
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
		chbsagent = netvend.Agent('correct horse battery staple', seed=True)
		response = chbsagent.tip(self.agentAddress, netvend.convert_value(10, 'satoshi', 'usat'), None)
	except netvend.NetvendResponseError as e:
		self.writeConsole('Failed to tip new agent - ' + str(e))
	return


def getBalance(self):
	"""
		get the balance for the logged in agent
	"""
	self.unit = db.getSetting(self, 'unit', 'satoshi')
	try:
		self.agentBalance = netvend.convert_value(self.agent.fetch_balance(), 'usat', self.unit)
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
		if 'f:' in str(e):
			self.writeConsole('Not enough funds for query - ' + str(e) + ' - ' + query)
		else:
			self.writeConsole('Query error - ' + str(e) + ' - ' + query)
		return False
	if response['command_result']['num_rows'] < 1:
		#self.writeConsole('No rows returned - ' + query)
		return False
	return response['command_result']


def getNick(self, address):
	"""
		get the nickname associated with the specified address
	"""
	conn = db.open()
	c = conn.cursor()
	c.execute('select nick from nicks where address = ?;', (address,))
	nick = c.fetchone()
	db.close(conn)
	if nick is None:
		return address
	else:
		return nick[0]


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
	self.allNicks = []
	query = "select address from accounts"
	rows = putQuery(self, query)
	if rows is False:
		return False
	for row in rows['rows']:
		nick = getNick(self, str(row[0]))
		self.allNicks.append(nick)
	return


def pollAllPosts(self):
	"""
		get the highest post id and compare it to our last known post id
		save it and alert if higher
	"""
	query = "select post_id from posts order by post_id desc limit 1"
	rows = putQuery(self, query)
	if rows is False:
		return False
	self.newAllPostId = rows['rows'][0][0]
	self.savedAllPostId = db.getData(self, 'all_post_id', 0)
	if self.newAllPostId > self.savedAllPostId:
		db.setData(self, 'all_post_id', self.newAllPostId)
		return True
	else:
		return False


def checkAllPosts(self):
	"""
		check any new posts for save-able information
	"""
	return


def checkNewNicks(self):
	"""
		check any new posts for new nicknames	
	"""
	query = "select address, data from posts where post_id > " + str(self.savedAllPostId) + " and data like 'nick:%'"
	rows = putQuery(self, query)
	if rows is False:
		return False
	conn = db.open()
	c = conn.cursor()
	for row in rows['rows']:
		c.execute('select id from nicks where address = ?;', (row[0],))
		nickId = c.fetchone()
		nick = row[1].split(':', 1)
		if nickId is None:
			c.execute('insert into nicks (nick, address) values (?,?);', (nick[1], row[0]))
		else:
			c.execute('update nicks set nick = ? where address = ?;', (nick[1], row[0]))
		#also check follows for potential updates
		c.execute('select nick from follows where address = ?;', (row[0],))
		checkNick = c.fetchone()
		if checkNick is not None:
			if nick[1] != checkNick[0]:
				c.execute('update follows set nick=? where address=?;', (nick[1], row[0]))
	db.close(conn)
	return


def getFollows(self):
	"""
		return the list of follows from the db
		update the list of nicks first
	"""
	if pollAllPosts(self):
		checkNewNicks(self)
	conn = db.open()
	c = conn.cursor()
	c.execute('select nick, address from follows where profile=?;', (str(self.agentAddress),))
	follows = c.fetchall()
	db.close(conn)
	return follows


def pollFollowsPosts(self):
	"""
		get the highest post id of posts made by our follows
		compare to our stored id and report
	"""
	follows = getFollows(self)
	if not follows:
		return False
	followList = ''
	for follow in follows:
		followList += '\'' + str(follow[1]) + '\','
	query = "select post_id from posts where address in (" + followList[:-1] + ") order by post_id desc limit 1"
	rows = putQuery(self, query)
	if rows is False:
		return False
	self.newFollowPostId = rows['rows'][0][0]
	self.savedFollowPostId = db.getData(self, 'follow_post_id', 0)
	if self.newFollowPostId > self.savedFollowPostId:
		db.setData(self, 'follow_post_id', self.newFollowPostId)
		return True
	else:
		return False


def displayFollowsPosts(self):
	"""
		display latest posts by your follows
	"""
	follows = getFollows(self)
	if not follows:
		return False
	followList = ''
	for follow in follows:
		followList += '\'' + str(follow[1]) + '\','
	query = "select post_id, address, data, ts from posts where address in (" + followList[
																				:-1] + ") and post_id > " + str(
		self.savedFollowPostId) + " order by ts asc"
	rows = putQuery(self, query)
	if rows is False:
		return False
	if 'post:' in rows['rows']:
		self.writeConsole('\n== New Posts from your followed agents ==\n')
	for row in rows['rows']:
		if 'post:' in row[2]:
			post = row[2].split(':', 1)[1]
		else:
			continue
		self.writeConsole(str(getNick(self, row[1])) + " [" + str(row[3]) + '] (' + str(row[0]) + ') >> ' + str(post))
	return


def getSeedFromNick(nick):
	"""
		find and return the seed value for the associated nick
		check profiles as we only store seeds for those
		nick is automatically the address if no nick is set
		return False if nick not found
	"""
	conn = db.open()
	c = conn.cursor()
	c.execute('select seed from profiles where nick=?;', (nick,))
	data = c.fetchone()
	if data is None:
		return False
	else:
		return data[0]


def getAddressFromNick(nick):
	"""
		find and return the address value for the associated nick
		check nicks as we should store every possible one
		nick is automatically the address if no nick is set
		return False if nick not found
	"""
	conn = db.open()
	c = conn.cursor()
	c.execute('select address from nicks where nick=?;', (nick,))
	data = c.fetchone()
	if data is None:
		return False
	else:
		return data[0]


def getAddressFromPostID(self, postId):
	"""
		get the address of the agent who created the post with the specified ID
		For tipping purposes
		return False if nothing found
	"""
	query = "select address from posts where post_id = " + postId
	rows = putQuery(self, query)
	if rows is False:
		return False
	return rows['rows'][0][0]


def chatPoll(self):
	"""
		poll the server for new chat messages
	"""
	#first get the chat_post_id from local db
	chatPostId = db.getData(self, 'chat_post_id', 0)
	query = "select post_id, address, data from posts where post_id > " + str(chatPostId) + " and data like 'chat:%' order by ts asc"
	rows = putQuery(self, query)
	if rows is not False:
		for post in rows['rows']:
			if post[1] == self.agentAddress:
				continue
			self.writeConsole(getNick(self, post[1]) + ' (' + post[0] + ') >> ' + post[2].split(':',1)[1])
			chatPostId = post[0]
	db.setData(self, 'chat_post_id', chatPostId)
	return


def getChatters(self):
	"""
		fetch and return a list of currently chatting agents
	"""
	query = "select address, data from posts where data like 'chatting:%' order by ts desc"
	rows = putQuery(self, query)
	if rows is not False:
		addresses = []
		chatList = []
		for row in rows['rows']:
			if row[0] not in addresses:
				addresses.append(row[0])
				if row[1].split(':',1)[1] == 'True':
					chatList.append(getNick(self, row[0]))
	return chatList


def checkAddress(check):
	"""
		Check the supplied string for bitcoin address.
		return address if it's a nick
	"""
	if isAddress(check):
		return check
	#otherwise test for nickname
	elif getAddressFromNick(check) is not False:
		return getAddressFromNick(check)
	else:
		return False


def genPubKey(self):
	"""
		Using PyCrypto, generate a new public/private key pair
		save to the database
	"""
	#generate a random number
	key = RSA.generate(2048)
	pubKey = key.publickey()
	pubKey = pubKey.exportKey(passphrase=self.password)
	privKey = key.exportKey(passphrase=self.password)
	try:
		self.agent.post('whisperpubkey:' + pubKey)
	except netvend.NetvendResponseError as e:
		return False
	db.setData(self, pubKey, privKey)
	return pubKey


def whisperPoll(self):
	"""
		Poll netvend for new tip information send our way
	"""
	whisperId = db.getData(self,'whisper_id',0)
	query = "select t.tip_id, p.data, t.from_address from posts as p inner join tips as t on t.post_id = p.post_id where t.to_address = '" + str(self.agentAddress) + "' and t.tip_id > " + str(whisperId) + " and p.data like 'whisper:%' order by t.ts asc"
	rows = putQuery(self, query)
	if rows is not False:
		self.writeConsole('')
		self.writeConsole('===== New Whispers =====')
		self.writeConsole('')
		for whisper in rows['rows']:
			self.writeConsole(str(getNick(self,whisper[2])) + ' [whisper] >> ' + str(decryptWhisper(self, whisper[1])))
			whisperId = whisper[0]
		self.writeConsole('')
	db.setData(self, 'whisper_id', whisperId)
	return


def decryptWhisper(self, text):
	"""
		decrypt a whisper post using the correct privatekey from the database
	"""
	text = text.split(':', 1)[1].split('|',1)
	pubK = text[0]
	whisper = text[1].decode('base64','strict')
	privK = db.getData(self,pubK,None)
	if privK is None:
		return 'Couldn\'t find the private key to decrypt this whisper'
	privK = RSA.importKey(privK, self.password)
	cipher = PKCS1_OAEP.new(privK)
	return cipher.decrypt(whisper)



