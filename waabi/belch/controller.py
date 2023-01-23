import re
import json
import traceback
from waabi.belch.options import Options
from waabi.belch.logs import Logs
from waabi.belch.hunt import Hunt
from waabi.belch.display import Display
from waabi.belch.arguments import Args, Term
from waabi.belch.results import Results
from waabi.belch.generator import Generate
from waabi.belch.replay import Replay
from waabi.belch.parser import Parser
from waabi.belch.wizzard import Wizzard
from waabi.utility.writer import Writer
from waabi.utility.html import Html
from waabi.utility.to import To
from waabi.utility.wordlist import WordList
from waabi.utility.jwty import Jwty

class Controller(object):

    def __init__(self,source):
        self.logs = Logs(source)
        self.options = Options() 
        self.display = Display(self.options)
        self.results = Results()
        self.replay = Replay(self.options)
        self.proxies = {
            "http" : "http://127.0.0.1:8080",
            "https" : "http://127.0.0.1:8080"
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

    def _substitute(self, values):
        if not values:
            return values
        subs = {
            "@canary_email": self.options.Get("canary_email"),
            "@canary_url": self.options.Get("canary_url"),
            "@canary_dns": self.options.Get("canary_dns")
        }
        single = not isinstance(values,list)
        values = [values] if single else values
        ret = []
        for v in values:
            for k,r in subs.items():
                v = v.replace(k,r)
            ret.append(v)
        return ret[0] if single else ret
            
        
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
    
    def _fuzz(self,result_type,wordlist_name,raw):
        try:
            args = Args(raw,[("log_id",int),("parm",str),("opt1",str),("opt2",str)],2)                
            if self._validate(args,"log_id"):
                log = self.logs.Get(args.log_id)
                self.display.ResultHeader()
                self.replay.Repeat(
                    args.log_id,log,result_type,args.parm,
                    self._substitute(WordList.Get(wordlist_name)),[args.opt1,args.opt2],
                    [lambda res: (True if res.status_code == 500 else False,None)],
                    self._result,self.display.Error
                )

                self.display.BR()
                return True
        except:
            self._error()
        return False


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
                content = self.logs.Get(args.log_id).response.body
                if isinstance(content,(list,dict)): 
                    Writer.Json(args.fp,content)
                else: 
                    Writer.Replace(args.fp,content)
                self.display.Format("Log: {0} Extracted: {1}",True,args.log_id,args.fp)
                return True
        except: 
            self._error()
        return False


    def unique_cmd(self,raw):
        try:
            args = Args(raw,[("field",str),("regex",str)],1,[Term("where",keys=self.logs.Keys(),start="where")])
            if self._validate(args):
                ret = self.logs.Unique(args.field,args.regex,args.where.terms,args.where.pairs)
                self.display.List(ret)
                self.display.Pair("Results",len(ret),True,True)
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

    def burp_cmd(self,raw): 
        try: 
            args = Args(raw,[("result_id",int)],1)
            if self._validate(args,"result_id"):
                result = self.results.Get(args.result_id)
                r = self.replay.Result(result,self.proxies)
                self.display.Header("Result: {0} Sent Through Burp Proxy".format(result.result_id))
                self.display.Pair(r.request.method.upper(),r.request.url)
                self.display.BR()
                return True
        except:
            self._error()
        return False
           



    def options_cmd(self, raw):
        self.display.Header("Belch Cli Options")
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
                value = args.value.split(",") if args.value.find(",") > -1 else args.value
                self.options.Set(args.key,value)
                self.display.Header("Belch Cli Options Updated")
                self.display.Pair(args.key,value)
                self.display.BR()
                return True
        except:
            self._error()
        return False

    def save_cmd(self,raw):
        self.display.Header("Saving Belch Cli Options")
        self.options.Save()
        self.display.Format("Options saved to: {0}",True,self.options._file)
        self.display.BR()
        return True
            
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

    def jwts_cmd(self, raw):
        try:
            args = Args(raw,[("log_id",int)],1)
            if self._validate(args,"log_id"):
                log = self.logs.Get(args.log_id)
                x = log.request.raw
                if log.response and log.response.raw:
                    x += log.response.raw
                jwts = Parser.FindJWTs(x)
                self.display.JWT(
                    (args.log_id,log),
                    jwts,
                    self.options.Get("canary_url"),
                    self.options.Get("oauth_issuer"),
                    self.options.Get("oauth_keyfile"),
                    self.options.Get("oauth_kid"),
                )
                return True
        except:
            self._error()
        return False

    def jwt_cmd(self,raw):
        try: 
            args = Args(raw,[("token",str)],0)
                    
            canary = self.options.Get("canary_url")
            issuer = self.options.Get("oauth_issuer")
            keyfile = self.options.Get("oauth_keyfile")
            kid = self.options.Get("oauth_kid")

            if args.token: 
                jwt = Jwty(args.token)
                self.display.JWT(
                    False,
                    jwt,
                    canary,
                    issuer,
                    keyfile,
                    kid
                )
            else:
                wzd = Wizzard({
                    "header":("Enter Header (Default None):",dict,True,{}),
                    "payload":("Enter Payload (Default None):",dict,True,{}),
                    "secret":("Enter HS Secret or RS Key (Default None):",str,True,False),
                    "signature":("Enter Signature (Default None): ",str,False,False)
                })
                self.display.Header("JWT Builder")
                wzd.Launch()
                j = Jwty.Construct(
                    wzd.payload, 
                    keyfile, 
                    kid, 
                    issuer, 
                    wzd.header, 
                    wzd.secret, 
                    wzd.signature
                )
                self.display.Header("ENCODED TOKEN: ")
                print(j)
                self.display.BR()

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
            args.val = self._substitute(args.val)
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
            args.val = self._substitute(args.val)
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
                    self._substitute(WordList.Get("xss")),[args.opt1,args.opt2],
                    [Html.FindExecJs,"console.log(742)",["onerror","onpointermove","href","src","onload","BACKGROUND","STYLE"],self.options.Get("render")],
                    self._result,self.display.Error
                )
                self.display.BR()
                return True
        except:
            self._error()
        return False

    def fuzz_cmd(self,raw):
        return self._fuzz("FUZZ","fuzz",raw)

    def quick_cmd(self,raw):
        return self._fuzz("QUIK","quick",raw)
    
    def chars_cmd(self,raw):
        return self._fuzz("CHAR","chars",raw)

    def sqli_cmd(self,raw):
        return self._fuzz("SQLI","sqli",raw)

    def traversal_cmd(self,raw):
        return self._fuzz("TRVS","traversal",raw)

    def discover_cmd(self,raw):
        encpth = self.options.Get("encode_path")
        try:
            args = Args(raw,[("log_id",int)],1)                
            if self._validate(args,"log_id"):
                self.options.Set("encode_path",False)
                log = self.logs.Get(args.log_id)
                tpl = "/".join(log.path.split("/")[:-1]) + "/{0}"
                self.display.ResultHeader()
                self.replay.Repeat(
                    args.log_id,log,"DISC","path",
                    list(filter(lambda f: (len(f) > 0 and f[0] != "#"),WordList.Get("discover"))),
                    [tpl],
                    [lambda res: (False if res.status_code == 404 else True,None)],
                    self._result,
                    self.display.Error
                )
                self.display.BR()
                self.options.Set("encode_path",encpth)
                return True
        except: 
            self.options.Set("encode_path",encpth)
            self._error()
        return False

    def permutate_cmd(self,raw):
        try:
            args = Args(raw,[("log_id",int),"ALL",("opt1",str),("opt2",str)],1)
            opts = [
                self._substitute(args.opt1),
                self._substitute(args.opt2)
            ]

            section = None
            value = self.options.Get("nasty")

            for o in opts:
                if o:
                    if o in ["headers","cookies","query","body"]:
                        section = o
                    else:
                        value = o 


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
                    self.logs.Permutations(False if args.ALL else args.log_id,section,value),None,None,
                    [Html.Compare,orig], self._result, self.display.Error
                )
                self.display.BR()
                return True
        except:
            self._error()
        return False

    def hunt_cmd(self,raw):
        try: 
            args = Args(raw,[("category",str)],0)
            for k,v in Hunt(self.logs,args.category).results.items():
                self.display.Header(k)
                self.display.List(v)
            return True
        except:
            self._error()
        return False
