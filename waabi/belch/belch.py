import os
import sys
import waabi
from waabi.core import Base
from waabi.belch.parser import Parser
from waabi.utility.reader import Reader
from waabi.belch.generator import Generate
from waabi.belch.cli import Cli
import os

class Belch(Base):

    def Init(self):
        if self.options.parameter not in ["header","code","cli"]:
            raise ValueError("Invalid Action parameter")
        if not self.options.input:
            raise ValueError("Missing required option -i Burp xml export ")
        self._burp_xml = Reader.Xml(self.options.input)

    def Help(self):
        return "belch [header|code|cli] [options: -i burp xml export , -o output]"

    def Run(self):
        parsed = Parser.ParseBurpLog(self._burp_xml)
        if self.options.parameter == "header":
            fp = self.options.output if self.options.output else './header.json' 
            print(Generate.Header(parsed[0],fp)) 

        if self.options.parameter == "code":
            #TODO this needs to accepts more then one. 
            fp = self.options.output if self.options.output else './run.py' 
            print(Generate.Code(parsed[0],fp))
        
        #TODO Move this to top and only pass source to cli
        if self.options.parameter == "cli":
            x = Cli()
            x.Start(self.options.input,parsed)

