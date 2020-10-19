import json

class To(object):

    @staticmethod
    def String(v):
        if isinstance(v,bytes):
            try: 
               return v.decode()
            except: 
               pass
        return str(v)
        
    @staticmethod
    def Code(obj,pad=0):
        
        if obj == None:
            return "None"

        if isinstance(obj,str):
            if obj.find("\n") > -1 or obj.find('"') > -1:
                return '"""{0}"""'.format(obj).replace("\\n","\\\\n")
            else:
                return '"{0}"'.format(obj)
                    
        if isinstance(obj,bytes):
            return str(obj)

        
        return json.dumps(obj,indent=4).replace("\n","\n" + (" " * pad) )

    @staticmethod
    def Array(s,d,wrap=("[","]")):
        q = False
        cur = ""
        ret = []
    
        for c in s:
            if not q and c == d and len(cur) > 0:
                ret.append(cur)
                cur = ""
            elif c == wrap[0] and cur == "":
                q = True
            elif q and c == wrap[1] and len(cur) > 0:
                q = False
            else:
                cur += c

        if len(cur) > 0: 
            ret.append(cur)

        return ret

    
    @staticmethod
    def Dict(k,v):
        ret = {}
        ret[k] = v
        return ret
