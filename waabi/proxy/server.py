import ipaddress
import proxy
import waabi


class Server(object):
    def __init__(self):
        pass

    def run(self):
        print(waabi.proxy.plugin.WaabiProxyPlugin)
        proxy.main([
            '--hostname', '127.0.0.1',
            '--port', '8899',
            '--plugin', 'waabi.proxy.plugin.WaabiProxyPlugin',
            '--log-level','c'
        ])


#http/proxy/server.py
#HttpProxyPlugin self.plugins.values() need to inject this
