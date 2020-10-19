from waabi.utility.html import Html

class Result(object):

    def __init__(self,result_type,result_id,log_id,pv,res,flag=False,meta=False):
        self.type = result_type
        self.result_id = result_id
        self.log_id = log_id
        self.pv = pv
        if pv: 
            self.parameter,self.value = next(iter(pv.items()))
        else: 
            self.parameter = None
            self.value = None
        self.response = res
        self.flag = flag
        self.meta = meta

class Results(object):

    def __init__(self):
        self._results = [];

    
    def Add(self, log_id, result_type, pv, res, flag, meta):
        result_id = len(self._results) + 1
        self._results.append(
            Result(result_type,result_id,log_id,pv,res,flag,meta)
        )
        return result_id

    def Get(self,result_id):
        return self._results[result_id - 1] if self.Exists(result_id) else False
 

    def Search(self,where,order):
        ret = []
        for r in self._results: 
            x  = {
                "log": str(r.log_id),
                "flag": str(r.flag),
                "status": int(r.response.status_code),
                "length": len(r.response.text),
                "mime": Html.GetMime(r.response),
                "type": r.type,
                "time": int(r.response.elapsed.microseconds / 1000), 
                "parameter": r.parameter,
                "value": r.value,
                "result": r
            }
            if where:
                m = True
                for k,v in where.items():
                    if k in x.keys() and str(v) != str(x[k]):
                        m = False
                        break        
                if m:
                    ret.append(x)
                
            else: 
                ret.append(x)

        if order and len(ret) > 0 and order[0] in ret[0].keys():
            ret = sorted(ret,key=lambda x: x[order[0]])
        return list(map(lambda x: x["result"],ret))   
 
    def Clear(self):
        self._results = []

    def Keys(self):
        return [
            "log",            
            "flag",
            "status",
            "length",
            "mime",
            "type",
            "time", 
            "parameter",
            "value",
        ]
    
    def Exists(self,result_id):
        return True if result_id <= len(self._results) else False
    

