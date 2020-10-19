
class Options(object):
    
    def __init__(self):
        self._options = {}
        self.Set("render",False)
        self.Set("encode_path",True)

    def List(self):
        return self._options

    def Get(self,key,default=False):
        if key in self._options.keys():
            return self._options[key]
        else: 
            return False
    
    def Set(self,key,value):
        self._options[key] = value


