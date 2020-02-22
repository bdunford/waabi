import waabi.proxy
import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "proxy":
        pSrv = proxy.Server()
        pSrv.run()

if __name__ == "__main__":
    main()
