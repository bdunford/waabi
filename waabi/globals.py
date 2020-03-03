import os


class Globals(object):

    def __init__(self):
        self.data_path = os.path.join(os.getcwd(),".waabi")
        self.wordlist_path = "{0}/wordlists".format(os.path.dirname(__file__))
