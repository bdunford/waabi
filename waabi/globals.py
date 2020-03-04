import os


class Globals(object):

    def __init__(self):
        self.data_path = os.path.join(os.getcwd(),".waabi")
        self.wordlist_path = "{0}/wordlists".format(os.path.dirname(__file__))
        self.default_header = {
            "user-agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36",
            "accept" : "*/*",
            "accept-encoding" : "gzip, deflate",
            "accept-language" :"en-US,en;q=0.8"
        }

        
