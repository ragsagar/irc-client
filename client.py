#!/usr/bin/python

import sys, select, socket, gtk.glade



class ClientGui:
	"""the class which deals with the gui layer """
	
	def __init__(self) :
		
		self.wTree = gtk.glade.XML("pirc.glade", "window1")
		dic = { "on_button1_clicked" : self.sendData,
				"on_window1_destroy" : self.quit,}
		self.wTree.signal_autoconnect(dic)
		self.logView = self.wTree.get_widget("textview1")
		self.logWindow = gtk.TextBuffer(None)
		self.logView.set_buffer(self.logWindow)
		self.nickView = self.wTree.get_widget("textview2")
		
	def sendData(self) :
		""" get message from entry widget and send it to sys.stdin """
		self.textentry = self.wTree.get_widget("entry1")
		Msgtext =  	self.textentry.get_text()
		sys.stdin.write(Msgtext)

	def quit(self, widget) :
		"""Handles the destroy signal"""
		gtk.main_quit()
		sys.exit(1)
			
	def log(self, message) :
		"""logs message to the log window and scrolls it to the bottom """
		message = message + '\n'
		buffer = self.logWindow
		iter = buffer.get_end_iter()
		self.logWindow.insert(iter, message)
		mark = buffer.create_mark("end", buffer.get_end_iter(), False)
		self.logView.scroll_to_mark(mark, 0.05, True, 0.0, 1.0)
		
	
class IRCclient(ClientGui):
	"""the main client class"""
	
	def __init__(self, server = 'irc.freenode.net', port = 6667) :
		"""create input and output files.."""
		ClientGui.__init__(self)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		addr = (server, port)
		connection = self.sock.connect_ex(addr)
		self.input = self.sock.makefile('rb', 0)
		self.output = self.sock.makefile('wb', 0)
		if connection is 0 :
			print "Connected"
					
	def identify(self, nick = 'ragas', realname = 'Rag Sagar.V') :
		"""replies to the server queries"""
		self.nick = nick
		self.output.write('NICK '+self.nick+'\r\n')
		self.output.write('USER '+self.nick+' 8 * :'+realname+'\r\n')
		
	def join_channel(self, channel = '#orkut_linux') :
		"""Join channel after the message of the day from server """	
		self.channel = channel
		done = False
		while not done :
			inMsg = self.input.readline().strip()
			print inMsg
			if inMsg.find('PRIVMSG') != -1 :
				done = True
		self.output.write('JOIN '+self.channel+'\r\n')
		print self.input.readline().strip()
		self.output.write('NAMES '+self.channel+'\r\n')
		print self.input.readline().strip()
		return 0
			
	def work(self):
		""" Handles the part of sending user's message to server and vice versa """
		socketClosed = False
		while not socketClosed :
			toRead, ignore, ignore = select.select([self.input, sys.stdin], [], [])
			for input in toRead	:
				if input == self.input : #message from server
					message = self.input.readline().strip()
					if message :
						if message.split()[0] is 'PING' :
							self.output.write('PONG '+message.split()[1]+'\r\n')
						else :
							self.parseRecievedMessage(message)	
					else :
						#the attempt to read failed. The socket is closed..
						socketClosed = True	
				elif input == sys.stdin :  #message from user
					message = sys.stdin.readline().strip() 
					if message :
						self.parseSendingMessage(message)
						
	def parseRecievedMessage(self, message)	:
		
		""" Filters the message from the server and makes it sensible """
		
		if message.find('PRIVMSG') != -1 :
			sender = message.split(':')[1].split('!')[0]
			sentMessage = ' '.join(message.strip().split(' ')[3:])[1:]	
			print '%s : %s ' % (sender, sentMessage)
			self.log(sentMessage)				
		
		elif message.find('QUIT :') != -1 or message.find('PART :') != -1 :
			print message.split('!')[0][1:], 'has quit '
		
		elif message.find('JOIN :'+self.channel) != -1 :
			print message.split('!')[0][1:], 'has joined this channel'
			
		elif message.find('freenode-connect : VERSION') != -1 :  #only applicable to freenode
			pass 	
				
					
	def parseSendingMessage(self, message) :
		
		""" finds if the message from server is command or message and does the needed things """
		
		if message[0] is '/' :
			print "that is a command"
			if message[1:].split()[0] is 'names' :
				print "you are here"
				self.output.write('NAMES '+self.channel)
		else :
			try :
				self.output.write('PRIVMSG '+self.channel+' :'+message+'\r\n')	
			except :
				pass 
			print "%s : %s" % (self.nick,message)
					
					
									
		
						
client = IRCclient('irc.freenode.net')
client.identify('ragas','Rag Sagar.V')
client.join_channel('#ilugkochi')	
gtk.main()
client.work()
				
					
					
