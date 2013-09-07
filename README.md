Python_SSH_Script_Engine
========================

This is just a simple paramiko based engine for easy SSH command scripts.

Dependencies:
[paramiko](https://github.com/paramiko/paramiko)

Example script using this engine:

```python
import time;

# import the engine
from ssh_engine import SSH_Engine;

username = "anon";
password = "some_password123";
port = 22;
host = "your_site's domain or IP"; # e.g. your_domain.com

def example_cmd(engine,channel):
    channel.send("cd .."); # no reason to send here though, in my opinion.
    print engine.last_cmd; # print the last string command that was run.

# Instantiate the engine.
eng = SSH_Engine(username,password,port,host);
# Add your commands in order as strings (or add functions to be called internally in this script)
eng.add_cmd("cd some_folder\n"); # remember to add the newline at the end (to fire the command off).
eng.add_cmd("touch new_file.txt\n"); # creates new_file.txt if it's not there.

# Add a function instead of a string
example_funct = example_cmd;
eng.add_cmd(example_funct);

eng.run_ssh(); # and run the cmd sequence!
```

Using the FTP Engine to automate local and remote ftp client transfers/scripts:

```python
# import the engines
from ssh_engine import SSH_Engine;
from ftp_engine import FTP_Engine;

os.system("echo 'testing ftp engine' > send.txt");

user = "your_username";
password = "your_password";
ssh_port = 22;
ftp_port = 21;
host_a = "host a's domain goes here"; # e.g. domain.com
host_b = "host b's domain goes here";

def remote_ftp_recv_funct(engine,chan):
	global user;
	global password;
	global ftp_port;
	global host_a;
	# prepare to run an ftp script remotely (via the ssh engine).
	remote_ftp = FTP_Engine(user,password,ftp_port,host_a,True);
	remote_ftp.add_cmd("get send.txt\n");
	remote_ftp.run_remote_ftp(engine);

def remote_ftp_send_funct(engine,chan):
	global user;
	global password;
	global ftp_port;
	global host_a;
	# prepare to run an ftp script remotely (via the ssh engine).
	remote_ftp = FTP_Engine(user,password,ftp_port,host_a,True);
	remote_ftp.add_cmd("put recv.txt\n");
	remote_ftp.run_remote_ftp(engine);

# locally run ftp script.
local_ftp = FTP_Engine(user,password,ftp_port,host_a);
local_ftp.add_cmd("put send.txt\n");
local_ftp.run_local_ftp();

eng = SSH_Engine(user,password,ssh_port,host_b);
eng.add_cmd(remote_ftp_recv_funct);
eng.add_cmd("cp send.txt recv.txt\n");
eng.add_cmd("echo 'testing remote ftp send from ssh command engine' >> recv.txt\n");
eng.add_cmd(remote_ftp_send_funct);
eng.run_ssh();

local_ftp = FTP_Engine(user,password,ftp_port,host_a);
local_ftp.add_cmd("get recv.txt\n");
local_ftp.run_local_ftp();

```
