
class Options(object):
    
    def __init__(self):
        self._options = {}
        self.Set("render",False)
        self.Set("encode_path",True)
        self.Set("smart_encode",True)
        self.Set("canary_email","zi9bx6efmtutipfgpjwmhagil@canarytokens.org")
        self.Set("canary_url","http://nhw1mgnq5nlva5ex59avonda6.canarytokens.com/articles/lidukgiq45hkkpxfucuq5b1qo/")
        self.Set("canary_dns","nhw1mgnq5nlva5ex59avonda6.canarytokens.com")

    def List(self):
        return self._options

    def Get(self,key,default=False):
        if key in self._options.keys():
            return self._options[key]
        else: 
            return False
    
    def Set(self,key,value):
        self._options[key] = value


