import base64
import getpass
import os
import socket
import sys
import traceback

import paramiko
import time;

class SSH_Cmd:

	def __init__(self,cmd,nowait=False):
		self.cmd = cmd;
		self.is_funct = False;
		self.no_wait=nowait;
		if(hasattr(self.cmd, "__call__")):
			self.is_funct = True;

class SSH_Engine:

	def __init__(self,user,passwd,port,host,silent=False,log_mode=0,log_funct=None):
		self.username = user;
		self.password = passwd;
		self.port = port;
		self.hostname = host;
		self.log_funct = log_funct;
		self.silent=silent;
		self.client_log = False;
		self.log_mode = log_mode; # 0 = No logging, 1 = log to file.
		if(hasattr(self.log_funct, "__call__")):
			self.client_log = True;
		# public
		self.log = [];
		# internal
		self.cmd_list = [];
		self.cmd_out = "";
		self.cmd_done = True;
		self.last_cmd = "";
		self.engine_active = False;
	
	def add_cmd(self,cmd,nowait=False):
		self.cmd_list.append(SSH_Cmd(cmd,nowait));

	def disconnect(self,chan):
		self.engine_active = False;
		chan.send("\n"); # attempt to send EOF.
		#!!! chan.send("exit\n"); # users should beware that this won't be enough if you sudo'd another user or root. Also if you're inside another CLI's interactive shell, this won't do the trick either.

	"""
	!!! This method is too brittle; it might result in multiple lingering 'shell_internal_write' threads, one from each previous disconnect call (it checks self.engine_active to see when to quit).
	def reconnect(self,chan):
		self.disconnect(chan);
		self.run_ssh();
	"""

	def check_data(self):
		#print "\n\n-------\nchecking for match("+self.last_cmd+"): "+self.cmd_out+"\n---------\n";
		# if cmd is in the output, it's been output. We're ready to push the next command.
		if(not (self.cmd_out.find(self.last_cmd.replace("\n","").replace("\r","")) == -1)):
			self.cmd_done = True;
			self.cmd_out = "";

	def internal_command(self,chan):
		for c in self.cmd_list:
			cwait = c.no_wait;
			if(c.is_funct):
				c.cmd(self,chan);
			else:
				#print "Running cmd: "+str(c.cmd)+"\n";
				self.cmd_done = False;
				self.last_cmd = c.cmd;
				chan.send(c.cmd);
				while(not self.cmd_done):
					time.sleep(0.1);
		# Finished running all commands; disconnect.
		self.disconnect(chan);

	# Not for public use!  Only for windows_shell method internal usage.
	# ------------------------------------------------------------------
	def shell_internal_write(self,sock):
		while True:
			data = sock.recv(256)
			if not data:
				if(self.log_mode == 1):
					self.log('\r\n*** EOF ***\r\n\r\n');
				if(self.client_log):
					self.log_funct('\r\n*** EOF ***\r\n\r\n');
				if(not self.silent):
					sys.stdout.write('\r\n*** EOF ***\r\n\r\n')
					sys.stdout.flush()
				break
			self.cmd_out += data;
			if(self.log_mode == 1):
				self.log(data);
			if(self.client_log):
				self.log_funct(data);
			if(not self.silent):
				sys.stdout.write(data)
				sys.stdout.flush()
			self.check_data();
			if(not self.engine_active):
				break;
	
	# Not for public use! 
	# ------------------------------------------------------------------
	def windows_shell(self,chan):
		import threading;
		
		writer = threading.Thread(target=self.shell_internal_write, args=(chan,));
		writer.start();
	    
		self.internal_command(chan);
		while(self.engine_active):
			time.sleep(0.2);
	# ------------------------------------------------------------------

	def run_ssh(self):
		try:
		    client = paramiko.SSHClient();
		    client.load_system_host_keys();
		    client.set_missing_host_key_policy(paramiko.WarningPolicy);
		    print '*** Connecting...';
		    client.connect(self.hostname, self.port, self.username, self.password);
		    chan = client.invoke_shell();
		    #print repr(client.get_transport());
		    print '*** Successfully connected.';
		    print;
		    self.engine_active = True;
		    #chan.send("exit\n");
		    self.windows_shell(chan);
		    #interactive.interactive_shell(chan);
		    chan.close();
		    client.close();

		except Exception, e:
		    print '*** Caught exception: %s: %s' % (e.__class__, e)
		    traceback.print_exc()
		    try:
			client.close()
		    except:
			pass
		    #sys.exit(1)
