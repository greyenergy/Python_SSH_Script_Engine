Python_SSH_Script_Engine
========================

This is just a simple paramiko based engine for easy SSH command scripts.

Example script using this engine:

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
