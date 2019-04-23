"""
Mininet Network Generation
====================================
"""

import networkx
from mininet.link import Link
from mininet.net import Mininet
from mininet.node import OVSSwitch
from typing import Callable, Any, Tuple, List


def add_switches(net, count, graph_method=networkx.path_graph, **switch_kwargs):
    # type: (Mininet, int, Callable, **Any) -> Tuple[List[Any], List[Link]]
    """
    Generates a network graph and adds switches to it, returning the switches and links between them

    :param net: A Mininet/Containernet network to add switches to
    :param count: The amount of switches to be added
    :param graph_method: A networkx graph generator see https://networkx.github.io/documentation/networkx-1.10/reference/generators.html
    :param switch_kwargs: Arguments to be passed to 'Mininet.addSwitch'
    :return: A tuple containing a list of switches added, and a list of links created.
    """
    # Set default switch parametes if not set
    if 'cls' not in switch_kwargs:
        switch_kwargs['cls'] = OVSSwitch
    if 'failMode' not in switch_kwargs:
        switch_kwargs['failMode'] = 'standalone'
        
    # Create a graph of switches
    graph = graph_method(count)  # type: networkx.path_graph
    
    # Add a switch for each node in the graph
    switches = [net.addSwitch('s' + str(node), **switch_kwargs) for node in graph.nodes]
    
    # Link switches as they are linked by edges in the graph
    links = [net.addLink(switches[edge[0]], switches[edge[1]]) for edge in graph.edges]
    
    return switches, links 
