import os
import sys
import waabi
from waabi.core import Base
from waabi.utility.reader import Reader
from waabi.utility.writer import Writer
from waabi.belch.parser import Parser
import os

class Belch(Base):

    def Init(self):
        if self.options.parameter not in ["header","code","parse"]:
            raise ValueError("Invalid Action parameter")
        if not self.options.input:
            raise ValueError("Missing required option -i Burp xml export ")
        self._burp_xml = Reader.Xml(self.options.input)


    def Help(self):
        return "belch [header|code|parse] [options: -i burp xml export , -o output]"

    def Run(self):
        parsed = Parser.ParseBurpLog(self._burp_xml)
        if self.options.parameter == "header":
            self.header(parsed[0])
        if self.options.parameter == "code":
            self.code(parsed[0])
        

    def header(self, record):
        if not self.options.output:
            self.options.output = "./header.json"
        Writer.Json(self.options.output,record.request.header)
        print("Header Written to: {0}".format(self.options.output))

    def code(self, record):
        if not self.options.output:
            self.options.output = "./run.py"
        t = Reader.Read("{0}/template.pyt".format(os.path.dirname(__file__)))
        t = Reader.Substitute(t,"@@URL",Reader.ToCode(record.request.uri))
        t = Reader.Substitute(t,"@@METHOD",Reader.ToCode(record.method))
        t = Reader.Substitute(t,"@@HEADER",Reader.ToCode(record.request.HeaderNoCookies()))
        t = Reader.Substitute(t,"@@COOKIES",Reader.ToCode(record.request.cookies))
        t = Reader.Substitute(t,"@@QUERY",Reader.ToCode(record.request.query))
        t = Reader.Substitute(t,"@@DATA",Reader.ToCode(record.request.body))
        Writer.Replace(self.options.output,t)
        print("Python Script Written to: {0}".format(self.options.output))
