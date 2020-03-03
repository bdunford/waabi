import sys
import waabi
import waabi.proxy
import waabi.scan
from .globals import Globals
from .core import Options

def main():
    opts = Options.Get()
    waabi.globals = Globals()
    if opts.action == "proxy":
        pSrv = proxy.Server()
        pSrv.run()

    if opts.action == "scan":
        scan.Scanner(opts)




if __name__ == "__main__":
    main()
