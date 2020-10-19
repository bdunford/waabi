import os
import shutil
import waabi
from waabi.core import Base
from waabi.utility import WordList
from waabi.utility import Writer

class WordLists(Base):

    def Init(self):
        if self.options.parameter not in ["extract","list"]:
            raise ValueError("Invalid Action parameter")
        if not self.options.output:
            self.options.output = "./waabi-wordlists/"

    def Help(self):
        return "wordlists [extract list] [-o output directory]"

    def Run(self):
        if self.options.parameter == "extract":
            Writer.EnsureFilePath(os.path.join(self.options.output,"x"))
            for wl in WordList.GetPaths():
                shutil.copy2(wl,self.options.output)
            print("Wordlists Extracted To: {0}".format(self.options.output))
        if self.options.parameter == "list":
            for wl in WordList.GetNames():
                print(wl)


