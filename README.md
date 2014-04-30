coinflow
========

Phase 1 CoinFlow app for the netvend network

current commands are:

/add [seed value] - create a new agent (small initial funding supplied)

/login [seed value] - login to existing agent

/tip [address] - tip a user or post

/post [message] - post a message 

/history [address] - show the last 10 posts for the specified agent. If address is blank, the currently logged in agent is used

/nick [nickname] - set a nickname for the logged in agent. nickname is checked for uniqueness

/listagents - display a list of all agents on the system. Shows nick name if they ave one otherwise default to address

/follow [agent] - follow the specified agent. can specify address or nickname

/listfollows - display a list of every one you follow with your currently logged in agent

/listprofiles - display a list of all agents you have created or logged in as. updated as nick changes

/gettipamount - display the current tip amount in musat (defaults to 1 each time you log in. saving this value is on the roadmap)

/settipamount [amount] - set the tip amount to the specified value in musat


More commands are coming as well as further functionality.
This software is just me finding out what netvend can do and messing around.
Don't trust it as it is fairly rough around the edges


It will require kivy <http://kivy.org> in order to work


Comments welcome
