import os
import sys
import waabi
import requests
from waabi.core import Base
from waabi.utility.reader import Reader
from waabi.utility.threads import Threader
from waabi.utility.writer import Writer
from waabi.utility.wordlist import WordList
import time
requests.packages.urllib3.disable_warnings()


class Scanner(Base):

    def Init(self):
        if self.options.wordlist:
            self._wl = Reader.List(self.options.wordlist)
        else:
            self._wl = WordList.Get("web-common")

        if not self.options.output:
            self.options.output = "./dirscan.txt"

        if self.options.header:
            self._header = Reader.Json(self.options.header)
        else:
            self._header = waabi.globals.default_header

        if not self.options.threads:
            self.options.threads = 5

        self._counter = 0
        self._errors = 0
        self._found = []
        self._counts = {}

    @staticmethod
    def Help():
        return ("Preform a Directory/File Bruteforce against a given url","scan [url] [options: -o output, -w wordlist, -H header.json -t 5]")

    def Run(self):
            s = time.time()
            t = Threader(self.options.threads,self.results)

            for w in self._wl:
                url = self.build_url(w)
                t.add((self.req,{"url" : url}))

            t.start()
            elapsed = time.gmtime(time.time() - s)
            final = self.update_display(True)
            print(t.errors)

            Writer.Replace(self.options.output,final)


    def build_url(self,w):
        u = self.options.parameter
        if u[-1:] != "/":
            u += "/"
        return u + w

    def req(self,url):
        try:
            r = requests.get(url, headers=self._header, verify=False,timeout=5)
            return {"url" : url, "status" : r.status_code, "length": len(r.text)}
        except Exception as ex:
            return {"url" : url, "status" : 999, "length": 0}

    def results(self,r):
            if r["status"] not in [404]:
                if r["status"] == 999:
                    self._errors += 1
                else:
                    self._found.append(r)
                    self.update_counts(r)
            self._counter += 1
            if (self._counter % self.options.threads == 0):
                self.update_display(False)

    def update_counts(self,r):
        if str(r["status"]) in self._counts:
            self._counts[str(r["status"])] += 1
        else:
            self._counts[str(r["status"])] = 1

    def update_display(self,finished):
        buff = []
        os.system('clear')

        buff.append(("-" * 28) + "waabi WEB DIR/FILE SCAN" + ("-" * 29) + "\n")
        if finished:
            for x in self._found:
                buff.append("{0} {1} {2}".format(x["status"],str(x["length"]).rjust(15),x["url"]))
            buff.append(("-" * 80))

        for k,v in self._counts.items():
            buff.append("Status: {0} Found: {1}".format(k,v))

        buff.append("Errors: {0}".format(self._errors))
        buff.append("Total: {0}".format(self._counter))
        sys.stdout.write("\n".join(buff) + "\n")
        sys.stdout.flush()

        return "\n".join(buff)
