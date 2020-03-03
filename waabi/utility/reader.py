import sys
import os
import json

class Reader(object):

    @staticmethod
    def Wordlist(filepath):
        with open(filepath,'r') as r:
            return r.read().split("\n")

    @staticmethod
    def Read(filepath):
        with open(filepath,'r') as r:
            return r.read()

    @staticmethod
    def Json(filepath):
        with open(filepath,'r') as r:
            return json.loads(r.read())
