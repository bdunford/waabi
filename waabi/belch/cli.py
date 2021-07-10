from cmd import Cmd
import sys 
import os
from waabi.belch.controller import Controller

class Cli(Cmd):

    def Start(self,source,parsed): 
        self.ctlr = Controller(source)
        self.prompt = self.ctlr.prompt()
        self.intro = self.ctlr.intro()
        self.cmdloop()


    def _invalid(self,command):
        self.onecmd("help {0}".format(command))

    def do_exit(self,args):
        """Exit belch cli"""
        self.ctlr.display.P("Exiting Belch CLi...",True) 
        raise SystemExit
    
    def do_search(self,args):
        """
           Search burp logs by full-text keywords and or values contained in specific fields. 
           Usage: search [key=value] [keyword]
           Examples: search api method=POST
                     search api POST application/json
                     search method=GET mime=HTML script
        """
        self.ctlr.search_cmd(args)
    
    def do_keys(self,args):
        """Displays a list of supported keys (fields) for searching"""
        self.ctlr.keys_cmd(args)  

    def do_view(self,args):
        """
            View specific burp log, optionally include full response body
            Usage: view [log number] [full] [highlight as regex] [skip] [take]\n
            Examples: view 123
                      view 123 full
                      view 123 w1ndsor
                      view 123 full \<script.*?\<\/script\>
                      view 123 full 10 15

        """
        if not self.ctlr.view_cmd(args):
            self._invalid("view")

    def do_extract(self, args):
        """
            Extract the response body of a burp log to file
            Usage: extract [log number] [filepath]
            Examples: extract 123 ./index.html
                      extract 123 ./document.pdf
        """
        if not self.ctlr.extract_cmd(args):
            self._invalid("extract")
        

    def do_unique(self,args):
        """
            Diplay unique values of a given key (key) with an optional regex match and or search clause
            Usage: unique [key] [regex] where [key=value] [keyword]
            Examples: unique path
                      unique query where method=POST
                      unique request "Authorization\:\sBearer\s.*" where POST
        """
        if not self.ctlr.unique_cmd(args):
            self._invalid("unique")

    def do_reload(self,args):
        """
        Reload Burp Log file
        Usage: reload
        """
        self.ctlr.reload_cmd(args)

    def do_code(self,args):
        """
        Generate code from burp logs
        Usage: code [log number(s)] [path]
        Examples: code 123
                  code 123,456,789
                  code 123,456 ./test-xxs.py
        """
        if not self.ctlr.code_cmd(args):
            self._invalid("code")
        
    def do_header(self,args):
        """
        Generate header from burp logs
        Usage: header [log number] [path]
        Examples: header 123
                  header 123 ./header.json
        """
        if not self.ctlr.header_cmd(args):
            self._invalid("header")

               
    def do_jwt(self, args):
        """
        Attempt to find a Parse JWT's found on a record.
        Usage: jwt [log number]
        Examples: jwt 123
        """
        if not self.ctlr.jwt_cmd(args):
            self._invalid("jwt")

           
    def do_reflected(self,args):
        """
        Replay a request to check if parameters are reflected in the response
        Usage: reflected [log number] parameter value [find]
        Examples: reflected 123 query.id w1ndsor
                  reflected 123 path w1ndsor 
                  reflected 123 body.name w1ndsor
        """    
        if not self.ctlr.reflected_cmd(args):
            self._invalid("reflected")

    def do_replay(self,args):
        """
        Replay a request tampering with parameters
        Usage: replay [log number] [parameter] [value] [find]
        Examples: replay 123 query.id w1ndsor
                  replay 123 query id=w1ndsor
                  replay 123 query.[first.name] w1ndsor
                  replay 123 path w1ndsor 1234
                  replay 123 body.name w1ndsor
                  TODO: accept multipule parameters this means replay has to change and the following commands could be used
                  replay 123 query.id w1ndsor path windsor 1234 body form=submit

        """
        if not self.ctlr.replay_cmd(args):
            self._invalid("replay")
    
    def do_flip(self,args):
        """
        Change a request method and funnel it back through the proxy
        Usage: flip [log number] [method]
        Examples: flip 123 GET
                  flip 123 POST
                  flip 123 PUT
                  flip 123 DELETE
                  flip 123 OPTIONS
                  flip 123 TRACE
                  flip 123 CONNECT
        """
        if not self.ctlr.flip_cmd(args):
            self._invalid("flip")




    def do_xss(self,args):
        """
        Fuzz a request for XSS vulnerabilities
        Usage: xss [log number] parameter [template] [find]
        Examples: xss 123 query.id  
                  xss 123 path test/{0}/route 
                  xss 123 path 554324
                  xss 123,124 body.name (TODO) 
        """
        if not self.ctlr.xss_cmd(args):
            self._invalid("xss")

          

    def do_fuzz(self,args):
        """
        Fuzz a series of requests against a full list of common problem causing strings
        Usage: fuzz [log number] parameter [template] [find]
        Examples: fuzz 123 query.id
                  fuzz 123 path test/{0}/route 
                  fuzz 123 path 554324
        """
        if not self.ctlr.fuzz_cmd(args):
            self._invalid("fuzz")

    def do_quick(self,args):
        """
        Quick a series of requests against a small list of common problem causing strings
        Usage: quick [log number] parameter [template] [find]
        Examples: quick 123 query.id
                  quick 123 path test/{0}/route 
                  quick 123 path 554324
        """
        if not self.ctlr.quick_cmd(args):
            self._invalid("quick")
    
    def do_chars(self,args):
        """
        Chars a series of requests against a list of each url encoded char 00 - ff
        Usage: chars [log number] parameter [template] [find]
        Examples: chars 123 query.id
                  chars 123 path test/{0}/route 
                  chars 123 path 554324
        """
        if not self.ctlr.chars_cmd(args):
            self._invalid("chars")

    def do_sqli(self,args):
        """
        SQLi a series of requests against a list of sql injection strings
        Usage: sqli [log number] parameter [template] [find]
        Examples: sqli 123 query.id
                  sqli 123 path test/{0}/route 
                  sqli 123 path 554324
        """

        if not self.ctlr.sqli_cmd(args):
            self._invalid("sqli")

    def do_traversal(self,args):
        """
        Traversal a series of requests against a list of directory traversal strings
        Usage: traversal [log number] parameter [template] [find]
        Examples: traversal 123 query.id
                  traversal 123 path test/{0}/route 
                  traversal 123 path 554324
        """

        if not self.ctlr.traversal_cmd(args):
            self._invalid("traversal")
    
    def do_permutate(self,args):
        """
        Permutate all availible parameters (query,cookies,headers,body) to identify differences in response
        Usage: permutate [log number] [section] [value] [ALL]
        Examples: permutate 123
                  permutate 123 "' or 1=1"
                  permutate 123 query <script
                  permutate 123 headers
                  permutate 123 body ${self}
                    
        Note: ALL command sources parameters from all requests in the current log.
        """
        if not self.ctlr.permutate_cmd(args):
            self._invalid("permutate")
        

    def do_result(self,args):
        """
        Dispay specific result from replay, optionally include full response body
        Usage: result [result number] [full] [highlight as regex] [skip] [take]\n
        Examples: result 123
                  result 123 full
                  result 123 full w1ndsor
                  result 123 full \<script.*?\<\/script\>
                  result 123 full 10 5
        """
        if not self.ctlr.result_cmd(args):
            self._invalid("result")
        
    def do_results(self,args):
       
        """
        TODO: need header  Id Flag Status, Length, Mime, type Parameter, value
        Display Search Order or Clear results from replay  
        Usage results [clear where order] [criteria]
        Examples: results where field=value
                  results clear
                  results order length
                  results where status=500 order length
        """
        self.ctlr.results_cmd(args)

    def do_options(self, args):
        """
        List Belch CLI Options
        Usage options
        Examples: options
        """
        self.ctlr.options_cmd(args)

    def do_set(self,args):
        """
        Change Belch CLI Setting
        Usage set [name] [value]
        Examples: set render False
        """
        if not self.ctlr.set_cmd(args):
            self._invalid("set")
        
    def do_parameters(self,args):
        """
        Display all unique header, cookie, query and post parameters for a given log or all logs.
        Usage parameters [log id]
        Examples: parameters
                  parameters 123
        """
        if not self.ctlr.parameters_cmd(args):
            self._invalid("parameters")

    def do_hunt(self,args):
        """
        Search for interesting requests, responses, headers, cookies. All things that might be worth taking a deeper look at. 
        Usage hunt [optional category - paths headers whatever]
        sub commands "paths, headers, reflected, cookies,"
        """

        if not self.ctlr.hunt_cmd(args):
            self._invalid("hunt")

    def do_burp(self,args):
        """
        Replays a result through the burp proxy for further tampering
        Usage burp [result id]
        Examples: burp 123
        """
        if not self.ctlr.burp_cmd(args):
            self._invalid("burp")




                
