import os
import shutil
import waabi
from waabi.core import Base
from waabi.utility import Payload
from waabi.utility import Writer
import sys

class Payloads(Base):

    def Init(self):
        if self.options.parameter not in (["extract","list"] + Payload.GetNames()):
            raise ValueError("Invalid Action parameter")
        if not self.options.output:
            self.options.output = "./waabi-payloads/"

    def Help(self):
        return "payloads [extract | list | (payload name)] [-o output directory]"

    def Run(self):
        if self.options.parameter == "extract":
            Writer.EnsureFilePath(os.path.join(self.options.output,"x"))
            for pl in Payload.GetPaths():
                shutil.copy2(pl,self.options.output)
            print("Payloads Extracted To: {0}".format(self.options.output))
        if self.options.parameter == "list":
            for pl in Payload.GetNames():
                print(pl)
        if self.options.parameter in Payload.GetNames():
            sys.stdout.buffer.write(Payload.Get(self.options.parameter))
            sys.stdout.buffer.write(b"\n")
            



        
        

