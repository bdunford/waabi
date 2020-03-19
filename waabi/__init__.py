import sys
import waabi
import waabi.proxy
import waabi.scan
import waabi.belch
import waabi.utility
import waabi.wordlists
from .globals import Globals
from .core import Options

waabi.globals = Globals()


def main():
    opts = Options.Get()

    #fit into new model
    if opts.action == "proxy":
        pSrv = proxy.Server()
        pSrv.run()

    if opts.action == "scan":
        scan.Scanner(opts)

    if opts.action == "belch":
        belch.Belch(opts)

    if opts.action == "wordlists":
        wordlists.WordLists(opts)




if __name__ == "__main__":
    main()
