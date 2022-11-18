import os
from waabi.utility.writer import Writer
from waabi.utility.reader import Reader

class Options(object):
    
    def __init__(self):
        self._file = os.path.expanduser("~/.waabi/options.json")
        self._options = {}
        self.Set("width",120)
        self.Set("render",False)
        self.Set("delay",25)
        self.Set("encode_path",True)
        self.Set("smart_encode",True)
        self.Set("canary_email","your-canary-email@canarytokens.com")
        self.Set("canary_url","https://canarytokens.com/articles/you-canary-url/")
        self.Set("canary_dns","your-canary-dns.canarytokens.com")
        self.Set("oauth_issuer","https://your-oauth2-issuer.com/")
        self.Set("oauth_keyfile","/path/to/your/private.pem")
        self.Set("oauth_kid","kid-from-your-oauth2-server")
        self.Set("highlight",["qwerty","ytrewq"])
        self.Set("nasty","AAA<\"})]'..%2f%250a\nAAA")
        self.load()
    
    def load(self):
        try: 
            if os.path.isfile(self._file):
                t = Reader.Json(self._file)
                for k,v in t.items(): 
                    self.Set(k,v)
            else:
                self.Save()
        except: 
            self.Save()


    def Save(self):
        Writer.Json(self._file,self._options)

    def List(self):
        return self._options

    def Get(self,key,default=False):
        if key in self._options.keys():
            return self._options[key]
        else: 
            return False
    
    def Set(self,key,value):
        self._options[key] = value


