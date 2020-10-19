from waabi.belch.parser import Parser
from waabi.utility.reader import Reader
from waabi.utility.to import To




class Logs(object):


    def __init__(self,source):
       self.source = source
       self.Reload()
    
    def exists(self,needle,haystack):
        if isinstance(haystack,bytes):
            needle = needle.encode()
        return True if haystack and haystack.find(needle) > -1 else False

    def is_match(self,log,terms,pairs):
        weight = 0 
        for t in terms: 
            for k,v in log.__dict__.items():
                x = v.raw if k in ['request','response'] else v
                if self.exists(t,x):
                    weight += 1
                    break
        for k,v in pairs.items():
            if k in log.__dict__.keys():
                x = log.__dict__[k].raw if k in ['request','response'] else log.__dict__[k] 
                if self.exists(v,x):
                    weight += 1
        return (len(terms) + len(pairs.keys()) <= weight)

    def get_parameters(self,log_id):
        l = self.Get(log_id)
        if not l:
            return []
        req = l.request
        ret = {
            "headers": list(req.HeaderNoCookies().keys()),
            "cookies": list(req.cookies.keys()) if req.cookies else None,
            "query": list(req.query.keys()) if req.query else None,
            "body": list(req.body.keys()) if req.body and isinstance(req.body,dict) else None
        }
 
        return ret

    def Get(self,log_id):
        return self._logs[log_id - 1] if self.Exists(log_id) else False

    def Search(self,terms,pairs):
        ret = []
        i = 0 
        for l in self._logs:
            i += 1
            if self.is_match(l,terms,pairs):
                ret.append((i,l))
        return ret


    def Exists(self,log_id):
        return True if log_id <= len(self._logs) else False
    
    
    def Reload(self):
        self._logs = Parser.ParseBurpLog(Reader.Xml(self.source))

    def Count(self):
        return len(self._logs)

    def Keys(self): 
        return [k for k in self.Get(1).__dict__.keys()]

    def Parameters(self,log_id=False):
        result = {}
        if log_id:
            ids = [log_id]
        else: 
            ids = range(1,self.Count() + 1)

        for i in ids:
            for k,v in self.get_parameters(i).items():
                if k in result.keys():
                    if result[k] == None:
                        result[k] = []
                    if not v == None:
                        result[k] = list(set(result[k] + v))
                else: 
                    result[k] = [] if v == None else v
        return result

    def Permutations(self,log_id,options):
        section = None
        value = "AAAAAAA"
        for o in options:
            if o:
                if o in ["headers","cookies","query","body"]:
                    section = o
                else:
                    value = o 
        ret = []
        for key,parms in self.Parameters(log_id).items():
            if parms:
                if not section or section == key:
                    for p in parms:
                        r_pram = "{0}.{1}".format(key,p) if p.find(".") == -1 else "{0}.[{1}]".format(key,p) 
                        ret.append(To.Dict(r_pram,value))
        return ret

