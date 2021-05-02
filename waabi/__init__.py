import sys
import waabi
import waabi.scan
import waabi.belch
import waabi.utility
import waabi.wordlists
import waabi.payloads
import waabi.target
from .globals import Globals
from .core import Options

waabi.globals = Globals()

def action_help(opts):
    if opts.parameter in actions.keys():
        print_help(actions[opts.parameter].Help())
    else: 
        print("waabi Help not found for action: {0}".format(opts.parameter))
    return True

def print_help(h):
    print("Description: {0}\nUsage: waabi {1}".format(h[0],h[1]))


#Add new actions here everything else is dynamic.
actions = {
    "scan": scan.Scanner,
    "belch": belch.Belch,
    "wordlists": wordlists.WordLists,
    "payloads": payloads.Payloads,
    "target": target.Target,
    "help": action_help,
}


def main():
     
    opts = Options.Get(actions.keys()) 
    for k,v in actions.items():
        if k == opts.action:
            v(opts)
            return 0
    
   
if __name__ == "__main__":
    main()



