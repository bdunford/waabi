import proxy
import waabi
#from typing import Optional
#from ..common.constants import DOT, SLASH
#from ..common.utils import build_http_response
#from ..http.parser import HttpParser

class WaabiProxyPlugin(proxy.http.proxy.plugin.HttpProxyBasePlugin):
    #Need to use EnvVars or Globals in Python to pass to this method.
    #Probably going to load some global object to collect data and  use threadding to make it a fast in.

    def before_upstream_connection(self, request):
        return request

    def handle_client_request(self, r):

        message = {
            "method": self.xb(r.method),
            "url": self.xb(r.url.geturl()),
            "headers": {self.xb(v[0]):self.xb(v[1]) for k,v in r.headers.items()},
            "body": self.xb(r.body)
        }

        waabi.proxy.logger.WaabiProxyLogger.Log(message) 
        return r

    def handle_upstream_chunk(self, chunk: memoryview) -> memoryview:
        #this is the raw response might be able to use HttpParser resposne
        #this is future state
        return chunk

    def on_upstream_connection_close(self) -> None:
        pass

    def xb(self,v):
        return str(v,'utf-8')
