import argparse
import sys
import waabi

class Options(object):

    @staticmethod
    def Get(actions):

        parser = argparse.ArgumentParser(
            prog="waabi",
            usage="%(prog)s [action] [parameter] [options]"
        )
        parser.add_argument("action", help="Action to perform [{0}]".format("|".join(actions)))
        parser.add_argument("parameter", help="Action parameter a command or parmaeter that directory supports the action.")

        parser.add_argument(
            "-H",
            dest="header",
            help="File containing http Header in json format"
        )

        parser.add_argument(
            "-w",
            dest="wordlist",
            help="Custom Wordlist file"
        )

        parser.add_argument(
            "-o",
            dest="output",
            help="Destination of output"
        )

        parser.add_argument(
            "-i",
            dest="input",
            help="Input file to be loaded for Parsing"
        )

        parser.add_argument(
            "-t",
            dest="threads",
            type=int,
            help="Number of Threads for Requests"
        )

        options = parser.parse_args()
        return options



class Base(object):
    def __init__(self,options):
        self.options = options
        try:
            self.Init()
        except Exception as e:
            print("{0}: {1} Failed to Initialize........".format(self.options.action,self.options.parameter))
            print(e)
            waabi.print_help(self.Help())
            sys.exit()
        self.Run()
