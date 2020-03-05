import os
import sys
import waabi
from waabi.core import Base
from waabi.utility.reader import Reader
from waabi.utility.writer import Writer
from waabi.belch.parser import Parser

class Belch(Base):

    def Init(self):
        if not self.options.input:
            raise ValueError("Missing required option -i Burp xml export ")
        self._burp_xml = Reader.Xml(self.options.input)

        if not self.options.output:
            self.options.output = "./header.json"

    def Help(self):
        return "belch [header|code|parse] [options: -i burp xml export , -o output]"

    def Run(self):
        self.header()
        #need to know the cmd

    def header(self):
        p = Parser.ParseBurpLog(self._burp_xml)

        Writer.Json(self.options.output,p[0].request.header)
        print("Header Written to: {0}".format(self.options.output))
        
        #print(p[0].request.raw)
        #for r in p:
        #    if r.status == "504":
        #        print(r.response.raw)
        #print(p[0].request.cookies)
        #print(p[0].response.cookies)

        #if req.get("base64") == "true":
        #    print("enc")
        #    raw = str(base64.b64decode(req.text),'utf-8')
        #else:
        #    print("unenc")
        #    raw = req.text

#        print(raw)

        #header_parts = raw.split("\r\n\r\n")[0].split("\r\n")[1:]
        #header = {}
        #for r in header_parts:

        #    header[r.split(":")[0]] = r.split(":")[1].strip()

        #print(header)
