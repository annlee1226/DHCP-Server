"""
Custom Topology:
+--------+       +--------+
| client |-------| server |
+--------+       +--------+
"""

from mininet.topo import Topo

class MyTopo(Topo):
    def build(self):
        # Add hosts
        client = self.addHost('client')
        server = self.addHost('server')

        # Add link between them
        self.addLink(client, server)


# Register the topology so Mininet can use it
topos = {'mytopo': (lambda: MyTopo())}