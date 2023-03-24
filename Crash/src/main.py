#thank you Danish Prakash
import os
import subprocess
import socket
import getpass
from termcolor import colored
from colorama import just_fix_windows_console
from getmac import get_mac_address as gma
from pathlib import Path
import glob
import lupa
import json
import platform
import distro
from math import *
from random import *

# user = getpass.getuser()
# password = getpass.getpass()

lua = lupa.LuaRuntime()
just_fix_windows_console()
home_directory = Path.home()
try:
  with open("settings.json") as o:
    settings = json.load(o)
except Exception as o:
  print(f"Json Error: {o}")

def execute_command(command):
    """execute commands and handle piping"""
    try:
        if "|" in command:
            # save for restoring later on
            s_in, s_out = (0, 0)
            s_in = os.dup(0)
            s_out = os.dup(1)

            # first command takes commandut from stdin
            fdin = os.dup(s_in)

            # iterate over all the commands that are piped
            for cmd in command.split("|"):
                # fdin will be stdin if it's the first iteration
                # and the readable end of the pipe if not.
                os.dup2(fdin, 0)
                os.close(fdin)

                # restore stdout if this is the last command
                if cmd == command.split("|")[-1]:
                    fdout = os.dup(s_out)
                else:
                    fdin, fdout = os.pipe()

                # redirect stdout to pipe
                os.dup2(fdout, 1)
                os.close(fdout)

                try:
                    subprocess.run(cmd.strip().split(" "))
                except Exception as o:
                    print("crash: ", colored(o,settings["color"]["error"]))
                    print(o)

            # restore stdout and stdin
            os.dup2(s_in, 0)
            os.dup2(s_out, 1)
            os.close(s_in)
            os.close(s_out)
        else:
          subprocess.run(command.strip().split(" "))
            # subprocess.run(command)
    
    except Exception as o:
        print("crash: ",colored(o,settings["color"]["error"]))


def cd(path):
    """convert to absolute path and change directory"""
    if path == '':
      os.chdir(home_directory)
    try:
        os.chdir(os.path.abspath(path))
    except Exception:
      print(colored("cd: no such file or directory:",settings["color"]["error"]), colored(str(path),"green"))
      
def help():
    print("""Crash: shell implementation in Python. In progress...""")

def main():
  #run prelude 
    try:
      if settings["prelude"] == "True":subprocess.run(["sh","prelude.sh"])
    except Exception as o:
      print(f"Prelude Error,{o}")
  #aliases
    with open("alias.json") as o:
      permalias = json.load(o)
    alias = {"mark":"curl","marcus":"echo really josh?","muurk":"echo CALEB!?!?","leave me in peace":"exit"}
    if settings["info"] == "True":
      hname = settings["color"]["hname"]
      uname = settings["color"]["uname"]
      pform = settings["color"]["pform"]
      maccolor = settings["color"]["maccolor"]
      mac = gma()
      system = platform.system().replace("Darwin","Mac").replace("Linux",distro.name())
      print(f"Running on {colored(system,pform)} {colored(platform.release(),pform)} \nVersion is {colored(platform.version(),pform)}")
      print(f'Hostname is {colored(socket.gethostname(),hname)}')
      print(f"Username is {colored(getpass.getuser(),uname)}")
      print(f"Mac Address is {colored(mac,maccolor)}\n")

    while 1:
        try:
          # inp = input(colored(f"{os.getcwd()}{'#' if os.geteuid() == 0 else''}> ",settings["color"]["prompt"]))
          inp = input(colored(f"{os.getcwd()}{'#' if os.geteuid() == 0 else''}{settings['prompt']} ",settings["color"]["prompt"]))
          # inp = ObjectName.getip(f"{os.getcwd()}{'#' if os.geteuid() == 0 else''}>", "str",caseSensitive="y",compulsoryInput="n")
          #alias swap
          with open("history.txt","a",) as o:
            o.write(f"{inp}\n")
          for x in alias:
            inp = inp.replace(x,alias[x]) 
          for x in permalias:
              inp = inp.replace(x,alias[x]) 
         
          #multiline stuff
          inp = inp.replace("and ","&").replace("&&","&").replace(";","&")
          inp = inp.replace("\n","&")
          inp_split = [x for x in inp.split("&")]
          for x in inp_split:
            x=x.strip()
            if x == "exit": 
                break
            elif os.path.isdir(x) == True:
              cd(x)
            elif x.startswith("cd ") or inp.endswith("cd"):
                cd(x.removeprefix("cd").strip())
            elif x == "help " or x.endswith(" help"):
                help()
            elif x.strip().startswith("alias"):
              y = x.replace("alias ",'').replace('"','').replace("'","").split("=")
              alias [y[0].strip()] = y[1].strip()
            elif x.strip().startswith("glob ") or x.strip().endswith("glob"):
              print(glob.glob(x.strip().removeprefix("glob ")))
            elif x == "import antigravity":
              import antigravity
            else:
              try:
                print(eval(x))
              except Exception:
                try:
                  execute_command(x)
                except Exception as o:
                  print(o)
        except KeyboardInterrupt:
          print("\n")
          continue
        except Exception as o:
          print(o)
          continue

if '__main__' == __name__:
  try:
    main()
  except Exception as o:
    print(f"Error:{o}")
