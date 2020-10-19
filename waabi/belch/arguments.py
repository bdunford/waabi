import shlex


class Term(object):

   def __init__(self,name,keys=[],start=None,stop=None):
       self.name = name
       self.keys = keys
       self.start = start
       self.stop = stop
    
   def Parse(self,args):
        self.terms = []
        self.pairs = {}

        x = True if not self.start else False
        for a in args:
            if x and a != self.stop:
                parts = None
                for k in self.keys:
                    if a.find(k+"=") == 0 and len(a) > len(k) + 1:
                        parts = [k,a[len(k)+1:]]
                if parts:
                    self.pairs[parts[0]] = parts[1]
                else: 
                    self.terms.append(a)
            else: 
                if a == self.start:
                    x = True
        
class Args(object):


    def __init__(self,raw,actions,required=0,terms=[]):
        args = shlex.split(raw)
        stops = []
        for t in terms:
            if t.start:
                stops.append(t.start) 
            t.Parse(args)
            self._add(t.name,t)
        self._validate(args,actions,required,stops)
        
        

    def _validate(self,args,actions,required,stops):
        ret = {}
        i = 0
        for a in actions:
            if len(args) > i:
                if isinstance(a,str):
                    if a == args[i]:
                        ret[a] = True
                        i += 1
                    else: 
                        ret[a] = False
                else:
                    try:
                        ret[a[0]] = a[1](args[i]) if args[i] not in stops else None
                    except:
                        ret[a[0]] = None
                    i += 1
            else:
                if isinstance(a,str):
                    ret[a] = False
                else:
                    ret[a[0]] = None
                i += 1
        
        self.valid =  (len(list(filter(lambda x: x != None, list(ret.values())[:required]))) >= required)
        for k,v in ret.items():
            self._add(k,v)
        
    def _add(self,k,v):
        setattr(self,k,v)
    
    
