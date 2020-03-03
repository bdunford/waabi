import ipaddress
import proxy
import waabi

class Server(object):
    def __init__(self):
        waabi.globals.requests = {}

    def run(self):
        proxy.main([
            '--hostname', '127.0.0.1',
            '--port', '8899',
            '--plugin', 'waabi.proxy.plugin.WaabiProxyPlugin',
            '--log-level','e'
        ])





#http/proxy/server.py
#HttpProxyPlugin self.plugins.values() need to inject this
