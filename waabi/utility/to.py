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

    @staticmethod
    def SingleDemension(mixed,key=None):
        if key != None and len(key) == 0: 
            key = "_BLANK_"
        ret = {}
        if isinstance(mixed,(list, dict, tuple)): 
            if isinstance(mixed,dict): 
                for k,v in mixed.items():
                    ret.update(To.SingleDemension(v,"{0}.{1}".format(key,k) if key != None else str(k)))
                return ret
            else:
                if len(mixed) == 1: 
                    return To.SingleDemension(mixed[0],key)
                i = 0 
                for m in mixed:
                    ret.update(To.SingleDemension(m,"{0}[{1}]".format(key,i) if key != None else "[{0}]".format(i)))
                    i += 1
                return ret 
        else: 
            if key != None: 
                return {key:str(mixed)}
            else: 
                return False

    @staticmethod
    def SimpleStrArray(mixed): 
        if isinstance(mixed,(list, dict, tuple)):
            ret = []
            if isinstance(mixed,dict):
                for k,v in mixed.items(): 
                    ret.append(str(k))
                    ret += To.SimpleStrArray(v)
            else: 
                for v in mixed: 
                    ret += To.SimpleStrArray(v)
            return ret
        else: 
            return [str(mixed)]
        

        


    @staticmethod
    def SafeDecode(mixed): 
        if isinstance(mixed,bytes):
            return mixed.decode("utf-8", "ignore")
        else: 
            return mixed

