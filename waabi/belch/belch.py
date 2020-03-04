import os
import sys
import waabi
from waabi.core import Base
from waabi.utility.reader import Reader
from waabi.utility.writer import Writer
import base64

class Belch(Base):

    def Init(self):
        if not self.options.input: 
            raise ValueError("Missing required option -i Burp xml export ")
        self._burp_xml = Reader.Xml(self.options.input)

    def Help(self):
        return "belch [header|code|parse] [options: -i burp xml export , -o output]"

    def Run(self):
        self.header()
        #need to know the cmd

    def header(self):
        req = self._burp_xml[0].find("request")
        if req.get("base64"):
            raw = base64.b64decode(req.text)
        else: 
            raw = req.text

        header_parts = raw.split("\r\n\r\n")[0].split()
        print(headers_parts)    
    
    
