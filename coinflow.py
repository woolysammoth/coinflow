import netvend.netvend as netvend
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
import json


class CoinFlowApp(App):
	
	chbsagent = netvend.Agent('correct horse battery staple', seed=True)
	agent = None
	
	def sendCommand(self, instance, value=False):
		if value:
			return
		#get the command and clear the input box
		inText = self.input.text
		if inText == '':
			return
		self.input.text = ''
		
		#options
		command = inText.split(None, 1)
		
		#/add [seed] - set up a new agent using the supplied seed
		#for the time being we add a simple balance to allow for testing
		if command[0] == '/add':
			if len(command) < 2:
				self.writeConsole('/add requires a seed as a second parameter.\nMake it a strong one as it will be used to generate your key pairs')
				return
			try:
				self.agent = netvend.Agent(command[1], seed=True)
			except netvend.NetvendResponseError as e:
				self.writeConsole('Failed to create agent - ' + str(e))
				return
			try:
				self.agentAddress = self.agent.get_address()
			except netvend.NetvendResponseError as e:
				self.writeConsole('Failed to get address - ' + str(e))
				return
			try:
				response = self.chbsagent.tip(self.agentAddress, netvend.convert_value(1, 'satoshi', 'usat'), None)
			except netvend.NetvendResponseError as e:
				self.writeConsole('Failed to tip new agent - ' + str(e))
				return
			try:
				self.agentBalance = self.agent.fetch_balance()
			except netvend.NetvendResponseError as e:
				self.agentBalance = 0
			self.writeConsole('Agent created.\nAddress is ' + str(self.agentAddress) + '\nBalance is ' + str(self.agentBalance))
			return
			
		#/login [seed] - login as an existing agent
		elif command[0] == '/login':
			if len(command) < 2:
				self.writeConsole('You need to supply the seed for the agent you want to login as.')
				return
			try:
				self.agent = netvend.Agent(command[1], seed=True)
			except netvend.NetvendResponseError as e:
				self.writeConsole('Failed to create agent - ' + str(e))
				return
			try:
				self.agentAddress = self.agent.get_address()
			except netvend.NetvendResponseError as e:
				self.writeConsole('Failed to get address - ' + str(e))
				return
			try:
				self.agentBalance = self.agent.fetch_balance()
			except netvend.NetvendResponseError as e:
				self.agentBalance = 0
			self.writeConsole('Logged in.\nAddress is ' + str(self.agentAddress) + '\nBalance is ' + str(self.agentBalance))
			return
			
		#/tip [address]
		elif command[0] == '/tip':
			if self.agent is None:
				self.writeConsole('You don\'t have an active agent.\n/add an agent or /login in order to tip.')
				return
			elif len(command) < 2:
				self.writeConsole('You need to supply the address of the agent you wish to tip.')
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
		
		#/post [message]		
		elif command[0] == '/post':
			if self.agent is None:
				self.writeConsole('You don\'t have an active agent.\n/add an agent or /login in order to post.') 
				return
			if len(command) < 2:
				self.writeConsole('You need to supply the message to post.')
				return
			try:
				response = self.agent.post(command[1])
				if response['success'] == 1:
					self.writeConsole('>>' + str(command[1]) + '\nPost ID is ' + str(response['command_result']))
				else:
					self.writeConsole('Post failed')
			except netvend.NetvendResponseError as e:
				self.writeConsole('Post failed - ' + str(e))
		
		#/history [address]		
		elif command[0] == '/history':
			if self.agent is None:
				self.writeConsole('You don\'t have an active agent.\n/add an agent or /login in order to view history.') 
				return
			if len(command) < 2:
				command.append(self.agentAddress)
			query = "select posts.post_id, posts.data, history.fee from posts inner join history on posts.history_id = history.history_id where posts.address = '" + str(command[1]) + "' order by posts.ts asc limit 10"
			try:
				response = self.agent.query(query)
			except netvend.NetvendResponseError as e:
				self.writeConsole('Failed to get post history - ' + str(e))
				return
			#get the returned rows from the server's response
			if response['command_result']['num_rows'] < 1:
				self.writeConsole('No post history to display')
				return
			rows = response['command_result']['rows']
			self.writeConsole('\n==Posts==\n')
			for row in rows:
				self.writeConsole('Post ID: ' + str(row[0]) + ' Fee: ' + str(row[2]) + '\nPost: ' + str(row[1]) + '\n')
			return
			
				
			
		
		else:
			self.writeConsole(command[0] + ' is not a recognised command')
			return
		
	def writeConsole(self, text):
		#get the current output text and store it
		outText = self.output.text
		#once we've figured out what to do, write to the console and return focus to the input box
		self.output.text = outText + text + '\n'
		self.input.focus = True

	def build(self):
		self.root = BoxLayout(orientation='vertical')
		self.output = TextInput(size_hint=(1,.9), background_color=[0,0,0,0], foreground_color=[1,1,1,1], readonly=True)
		self.input = TextInput(size_hint_y=None, height=30, multiline=False, focus=True)
		self.input.bind(focus=self.sendCommand)	
		self.root.add_widget(self.output)
		self.root.add_widget(self.input)
		return self.root

if __name__ == '__main__':
	CoinFlowApp().run()