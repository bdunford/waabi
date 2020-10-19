import re
import traceback
from waabi.belch.options import Options
from waabi.belch.logs import Logs
from waabi.belch.display import Display
from waabi.belch.arguments import Args, Term
from waabi.belch.results import Results
from waabi.belch.generator import Generate
from waabi.belch.replay import Replay
from waabi.belch.parser import Parser
from waabi.utility.writer import Writer
from waabi.utility.html import Html
from waabi.utility.to import To
from waabi.utility.wordlist import WordList

class Controller(object):

    def __init__(self,source):
        self.logs = Logs(source)
        self.options = Options() 
        self.display = Display()
        self.results = Results()
        self.replay = Replay(self.options)
        self.proxies = {
            "http" : "http://127.0.0.1:8080",
            "https" : "https://127.0.0.1:8080"
        } 
        
    def _error(self):
        self.display.BR()
        self.display.Error(("<" * 53) + "FATAL ERROR:" + (">") * 53)
        self.display.Error(traceback.format_exc())

    def _validate(self,args,id_type=False): 
        err = False
        tpl = " No {0} exists for id: {1}"
        if args.valid:
            if id_type: 
                var = getattr(args,id_type,False)
                if var:
                    var = [var] if not isinstance(var,list) else var
                    for i in var:            
                        if id_type == "log_id" and not self.logs.Exists(i):
                            err = tpl.format("Log",i)

                        if id_type == "result_id" and not self.results.Exists(i):
                            err = tpl.format("Result",i)
        else:
            err =  " Invalid Command Arguments (SEEK HELP)..."
        if err: 
            self.display.BR()
            self.display.Error(err)
            self.display.BR()
            return False
        return True
        
    def _result(self,log_id,rslt_type,pv,res,flag,meta):
        skip = False
        if rslt_type == "PERM" and meta and meta["count"] == 0:
            skip = True

        if not skip:
            rslt_id = self.results.Add(log_id,rslt_type,pv,res,flag,meta)
            self.display.Result(self.results.Get(rslt_id))

    def _replay_opts(self,opt1,opt2):
        find = False
        template = False
        for o in [opt1,opt2]:
            if o:
                if o.find("{0}") > -1:
                    template = o
                else:
                    find = o
        return find,template
    
    def intro(self,prnt=False):
        x = self.display.Intro(self.logs.source,self.logs.Count())
        if prnt:
            self.display.P(x)
        else:
            return x

    def prompt(self):
        return self.display.GetPrompt()
   
    def search_cmd(self,raw):
        try:    
            args = Args(raw,(),0,[Term("search",keys=self.logs.Keys())])
            results = self.logs.Search(args.search.terms,args.search.pairs)
            for r in results:
                self.display.Log(r)
            self.display.Pair("Results",len(results),True,True)
            return True
        except Exception: 
            self._error()
            return False

    def keys_cmd(self,raw):
        try:
            self.display.List(self.logs.Keys())
        except Exception: 
            self._error()
        return True
           
    def view_cmd(self,raw):
        try:
            args = Args(raw,[("log_id",int),"full",("opt1",str),("opt2",str),("opt3",str)],1)
            if self._validate(args,"log_id"):
                self.display.Log((args.log_id,self.logs.Get(args.log_id)),True,args.full,args.opt1,args.opt2,args.opt3)
                return True
        except:
            self._error()
        return False

    def extract_cmd(self, raw):
        try:
            args = Args(raw,[("log_id",int),("fp",str)],2)
            if self._validate(args,"log_id"):
                Writer.Replace(args.fp,self.logs.Get(args.log_id).response.body)
                self.display.Format("Log: {0} Extracted: {1}",True,args.log_id,args.fp)
                return self._invalid()
        except: 
            self._error()
        return False

    def unique_cmd(self,raw):
        try:
            args = Args(raw,[("field",str),("regex",str)],1,[Term("where",keys=self.logs.Keys(),start="where")])
            if self._validate(args):
                results = self.logs.Search(args.where.terms,args.where.pairs)
                ret = []
                for r in results:
                    v = r[1].__dict__[args.field].raw if args.field in ['request','response'] else r[1].__dict__[args.field]
                    if args.regex:
                        if v: 
                            if isinstance(v,bytes):
                                m = re.findall(args.regex.encode(),v)
                            else: 
                                m = re.findall(args.regex,v)
                            if m:
                                for x in m: 
                                    ret.append(To.String(x))
                    else: 
                        ret.append(To.String(v))            
                final = sorted(list(set(ret))) 
                self.display.List(final)
                self.display.Pair("Results",len(final),True,True)
                return True
        except:
            self._error()
        return False

    def results_cmd(self,raw):
        try:
            args = Args(raw,["clear"],0,[
                Term("where",keys=self.results.Keys(),start="where",stop="order"),
                Term("order",keys=self.results.Keys(),start="order",stop="where"),
            ])
            if args.clear:
                self.results.Clear()
                self.display.P("Results Cleared...",True)
            else: 
                self.display.ResultHeader()
                for r in self.results.Search(args.where.pairs,args.order.terms):
                    self.display.Result(r)
                self.display.BR()
            return True
        except:
            self._error()
        return False
        

    def result_cmd(self,raw):
        try:
            args = Args(raw,[("result_id",int),"full",("opt1",str),("opt2",str),("opt3",str)],1)
            if self._validate(args,"result_id"):
                self.display.Result(self.results.Get(args.result_id),True,args.full,args.opt1,args.opt2,args.opt3)
                return True
        except:
            self._error()
        return False

    def options_cmd(self, raw):
        self.display.Header("Belch Cil Options")
        self.display.Dict(self.options.List())
        self.display.BR()
        return True

    def set_cmd(self,raw):
        try:
            args = Args(raw,[("key",str),("value",str)],2)
            if self._validate(args): 
                value = int(args.value) if args.value.isdigit() else args.value
                value = True if str(args.value).lower() == "true" else args.value
                value = False if str(args.value).lower() == "false" else args.value
                self.options.Set(args.key,value)     
                self.display.Header("Belch Cli Options Updated")
                self.display.Pair(args.key,value)
                self.display.BR()
                return True
        except:
            self._error()
        return False
            
    def reload_cmd(self,raw):
        try:
           self.display.P("Reloading...",True)
           self.logs.Reload()
           self.display.Intro(self.logs.source,self.logs.Count(),True)
        except: 
            self._error()
        return True

    def code_cmd(self,raw):
        try:
            args = Args(raw,[("log_id",lambda l: [int(x) for x in l.split(',')]),("fp",str)],1)
            if self._validate(args,"log_id"):
                fp = args.fp if args.fp else "./run-{0}.py".format("-".join([str(x) for x in args.log_id]))
                msg = Generate.Code([self.logs.Get(i) for i in args.log_id],fp)
                self.display.P(msg,True)
                return True
        except: 
            self._error()
        return False

    def header_cmd(self,raw):
        try:
            args = Args(raw,[("log_id",int),("fp",str)],1)
            if self._validate(args,"log_id"):
                fp = args.fp if args.fp else "./header.json"
                msg = Generate.Header(self.logs.Get(args.log_id),fp)
                self.display.P(msg,True)
                return True
        except:
            self._error()
        return False

    def jwt_cmd(self, raw):
        try:
            args = Args(raw,[("log_id",int)],1)
            if self._validate(args,"log_id"):
                log = self.logs.Get(args.log_id)
                x = log.request.raw
                if log.response and log.response.raw:
                    x += log.response.raw
                jwts = Parser.FindJWTs(x)
                self.display.JWT((args.log_id,log),jwts)
                return True
        except:
            self._error()
        return False

    def parameters_cmd(self,raw):
        try:
            args = Args(raw,[("log_id",int)],0)
            if self._validate(args,"log_id"):
                result = self.logs.Parameters(args.log_id) 
                for s in ["Headers","Cookies","Query","Body"]:
                    self.display.Header(s)
                    for v in result[s.lower()]:
                        self.display.P(v)
                    self.display.BR()
                return True
        except:
            self._error()
        return False

    def reflected_cmd(self,raw):
        try:
            args = Args(raw,[("log_id",int),("parm",str),("val",str),("find",str)],3)                
            if self._validate(args,"log_id"):
                log = self.logs.Get(args.log_id)
                pv = To.Dict(args.parm,args.val) 
                res, err = self.replay.Request(log,pv,args.find)
                if not err:
                    self.display.ResultHeader()
                    flag,meta = Html.Reflected(res,args.val,self.options.Get("render"))
                    self._result(args.log_id,"RFLCT",pv,res,flag,meta)
                    self.display.BR()
                else:
                    self.display.Error(err)
                return True
        except: 
            self._error()
        return False

    def replay_cmd(self,raw):
        try:
            args = Args(raw,[("log_id",int),("parm",str),("val",str),("find",str)],1)                
            if self._validate(args,"log_id"):
                log = self.logs.Get(args.log_id)
                pv = To.Dict(args.parm,args.val) if args.parm else None
                res, err = self.replay.Request(log,pv,args.find)
                if not err:
                    self.display.ResultHeader()
                    self._result(args.log_id,"REPLY",pv,res,False,None)
                    self.display.BR()
                else:
                    self.display.Error(err)
                return True
        except: 
            self._error()
        return False

    def flip_cmd(self,raw):
        try:
            args = Args(raw,[("log_id",int),("method",str)],2)                
            if self._validate(args,"log_id"):
                log = self.logs.Get(args.log_id)
                pv = To.Dict("method",args.method)
                res, err = self.replay.Request(log,pv,None,True,self.proxies)
                if not err:
                    self.display.ResultHeader()
                    flag = (str(log.status) == str(res.status_code))
                    self._result(args.log_id,"FLIP",pv,res,flag,None)
                    self.display.BR()
                else:
                    self.display.Error(err)
                return True
        except: 
            self._error()
        return False

    def xss_cmd(self,raw):
        try:
            args = Args(raw,[("log_id",int),("parm",str),("opt1",str),("opt2",str)],2)                
            if self._validate(args,"log_id"):
                log = self.logs.Get(args.log_id)
                self.display.ResultHeader()
                self.replay.Repeat(
                    args.log_id,log,"XSS",args.parm,
                    WordList.Get("xss"),[args.opt1,args.opt2],
                    [Html.FindExecJs,"console.log(742)",["onerror","onpointermove","href","src","onload"],self.options.Get("render")],
                    self._result,self.display.Error
                )
                self.display.BR()
                return True
        except:
            self._error()
        return False

    def fuzz_cmd(self,raw):
        try:
            args = Args(raw,[("log_id",int),("parm",str),("opt1",str),("opt2",str)],2)                
            if self._validate(args,"log_id"):
                log = self.logs.Get(args.log_id)
                self.display.ResultHeader()
                self.replay.Repeat(
                    args.log_id,log,"FUZZ",args.parm,
                    WordList.Get("fuzz"),[args.opt1,args.opt2],
                    [lambda res: (True if res.status_code == 500 else False,None)],
                    self._result,self.display.Error
                )

                self.display.BR()
                return True
        except:
            self._error()
        return False
     
    def permutate_cmd(self,raw):
        try:
            args = Args(raw,[("log_id",int),"ALL",("opt1",str),("opt2",str)],1)
            print(args.ALL)
            if self._validate(args,"log_id"):
                log = self.logs.Get(args.log_id)
                orig, err = self.replay.Request(log,None)
                self.display.ResultHeader()
                if err:
                    self.display.Error("Base Request Failed for log: {0}".format(args.log_id))
                    return True
                self._result(args.log_id,"PERM",{"Base Line":""},orig,False,None)
                self.replay.Repeat(
                    args.log_id,log,"PERM",
                    self.logs.Permutations(False if args.ALL else args.log_id,[args.opt1,args.opt2]),None,None,
                    [Html.Compare,orig], self._result, self.display.Error
                )
                self.display.BR()
                return True
        except:
            self._error()
        return False
