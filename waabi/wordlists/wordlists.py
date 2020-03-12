import os
import shutil
import waabi
from waabi.core import Base
from waabi.utility import WordList
from waabi.utility import Writer

class WordLists(Base):

    def Init(self):
        if self.options.parameter not in ["extract"]:
            raise ValueError("Invalid Action parameter")
        if not self.options.output:
            self.options.output = "./waabiLists"

    def Help(self):
        return "wordlists [extract] [-o output directory]"

    def Run(self):
        if self.options.parameter == "extract":
            Writer.EnsureFilePath(os.path.join(self.options.output,"x"))
            for wl in WordList.GetPaths():
                shutil.copy2(wl,self.options.output)
            print("Wordlists Extracted To: {0}".format(self.options.output))
