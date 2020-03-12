import os
import waabi
from waabi.utility.reader import Reader

class WordList(object):

    @staticmethod
    def Get(name):
        if name in WordList.GetNames():
            return Reader.List(os.path.join(waabi.globals.wordlist_path,"{0}.txt".format(name)))
        return False

    @staticmethod
    def GetPaths():
        results = []
        for fn in os.listdir(waabi.globals.wordlist_path):
            x,ext = os.path.splitext(fn)
            if ext == ".txt":
                results.append(os.path.join(waabi.globals.wordlist_path,fn))
        return results

    @staticmethod
    def GetNames():
        results = []
        for fp in WordList.GetPaths():
            results.append(os.path.basename(fp).replace(".txt",""))
        return results
