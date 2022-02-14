# -*- coding: utf-8 -*-
import logging

import networkx as nx
import warnings

LINK_COUNTER = 0
LINK_LIST = {}


class Topology:
    """
    This class unifies the functions to deal with **Complex Networks** as a network topology within of the simulator. In addition, it facilitates its creation, and assignment of attributes.
    """

    LINK_BW = "BW"
    "Link feature: Bandwidth"

    LINK_PR = "PR"
    "Link feauture:  Propagation delay"

    # LINK_LATENCY = "LATENCY"
    # " A edge or a network link has a Bandwidth"

    NODE_IPT = "IPT"
    "Node feature: IPS . Instructions per Simulation Time "

    def __init__(self, logger=None):

        # G is a nx.networkx graph
        self.G = None
        self.nodeAttributes = {}
        self.logger = logger or logging.getLogger(__name__)

    def __init_uptimes(self):
        for key in self.nodeAttributes:
            self.nodeAttributes[key].uptime = (0, None)

    def get_edges(self):
        """
        Returns:
            list: a list of graph edges, i.e.: ((1,0),(0,2),...)
        """
        return self.G.edges

    def get_edge(self, key):
        """
        Args:
            key (str): a edge identifier, i.e. (1,9)

        Returns:
            list: a list of edge attributes
        """
        # print("IM HERE TO2")
        # print("KEY")
        # print(key)
        # print("GEDGES")
        # print(self.G.edges)
        # print(self.G.edges[key])
        return self.G.edges[key]

    def get_nodes(self):
        """
        Returns:
            list: a list of all nodes features
        """
        return self.G.nodes

    def get_node(self, key):
        """
        Args:
            key (int): a node identifier

        Returns:
            list: a list of node features
        """
        return self.G.node[key]

    def get_info(self):
        return self.nodeAttributes

    def create_topology_from_graph(self, G):
        """
        It generates the topology from a NetworkX graph

        Args:
             G (*networkx.classes.graph.Graph*)
        """
        # if isinstance(G, nx.classes.graph.Graph):
        if isinstance(G, nx.classes.digraph.DiGraph):
            # if isinstance(G, nx.classes.multidigraph.MultiDiGraph):
            self.G = G
        else:
            raise TypeError

    def create_random_topology(self, nxGraphGenerator, params):
        """
        It generates the topology from a Graph generators of NetworkX

        Args:
             nxGraphGenerator (function): a graph generator function

        Kwargs:
            params (dict): a list of parameters of *nxGraphGenerator* function
        """
        try:
            self.G = nxGraphGenerator(*params)
        except:
            raise Exception

    def load(self, data):
        warnings.warn("The load function will merged with load_all_node_attr function",
                      FutureWarning,
                      stacklevel=8
                      )
        """
            It generates the topology from a JSON file
            see project example: Tutorial_JSONModelling

            Args:
                 data (str): a json
        """
        # self.G = nx.Graph()
        self.G = nx.DiGraph()
        # self.G = nx.MultiDiGraph()
        # nx.DiGraph
        for edge in data["link"].values():
            print("DATA_LINK")
            print(data["link"])
            print("EDGE")
            print(edge)
            self.G.add_edge(edge.source_id, edge.destination_id, BW=edge.bandwidth, PR=edge.latency)

        for node in data["entity"].values():
            self.nodeAttributes[node.id] = node
        # end remove

        # Correct way to use custom and mandatory topology attributes

        valuesIPT = {}
        # valuesRAM = {}
        for node in data["entity"].values():
            try:
                valuesIPT[node.id] = node.ipt
            except KeyError:
                valuesIPT[node.id] = 0
            # try:
            #     valuesRAM[node["id"]] = node["RAM"]
            # except KeyError:
            #     valuesRAM[node["id"]] = 0

        nx.set_node_attributes(self.G, values=valuesIPT, name="IPT")
        # nx.set_node_attributes(self.G,values=valuesRAM,name="RAM")

        self.__init_uptimes()

    def load_all_node_attr(self, data):
        # self.G = nx.Graph()
        # self.G = nx.MultiDiGraph()
        self.G = nx.DiGraph()
        for edge in data["link"]:
            self.G.add_edge(edge.source, edge.destination, BW=edge.bw, PR=edge.latency)

        dc = {str(x): {} for x in data["entity"][0].keys()}
        for ent in data["entity"]:
            for key in ent.keys():
                dc[key][ent.id] = ent[key]
        for x in data["entity"][0].keys():
            nx.set_node_attributes(self.G, values=dc[x], name=str(x))

        for node in data["entity"]:
            self.nodeAttributes[node.id] = node

        print("ATTRIBUTES")
        print(self.G)

        self.__idNode = len(self.G.nodes)
        self.__init_uptimes()

    def load_graphml(self, filename):
        warnings.warn("The load_graphml function is deprecated and "
                      "will be removed in version 2.0.0. "
                      "Use NX.READ_GRAPHML function instead.",
                      FutureWarning,
                      stacklevel=8
                      )

        self.G = nx.read_graphml(filename)
        attEdges = {}
        for k in self.G.edges():
            attEdges[k] = {"BW": 1, "PR": 1}
        nx.set_edge_attributes(self.G, values=attEdges)
        attNodes = {}
        for k in self.G.nodes():
            attNodes[k] = {"IPT": 1}
        nx.set_node_attributes(self.G, values=attNodes)
        for k in self.G.nodes():
            self.nodeAttributes[k] = self.G.node[k]  # it has "id" att. TODO IMPROVE

    def get_nodes_att(self):
        """
        Returns:
            A dictionary with the features of the nodes
        """
        return self.nodeAttributes

    def find_IDs(self, value):
        """
        Search for nodes with the same attributes that value

        Args:
             value (dict). example value = {"model": "m-"}. Only one key is admitted

        Returns:
            A list with the ID of each node that have the same attribute that the value.value
        """
        keyS = list(value.keys())[0]

        result = []
        for key in self.nodeAttributes.keys():
            val = self.nodeAttributes[key]
            if value[keyS] == val.mytag:
                result.append(key)
        return result

    def size(self):
        """
        Returns:
            an int with the number of nodes
        """
        return len(self.G.nodes)

    def add_node(self, nodes, edges=None):
        """
        Add a list of nodes in the topology

        Args:
            nodes (list): a list of identifiers

            edges (list): a list of destination edges
        """
        self.__idNode = + 1
        self.G.add_node(self.__idNode)
        self.G.add_edges_from(zip(nodes, [self.__idNode] * len(nodes)))

        return self.__idNode

    def remove_node(self, id_node):
        """
        Remove a node of the topology

        Args:
            id_node (int): node identifier
        """

        self.G.remove_node(id_node)
        return self.size()


class Link:
    LINK_BW = "BW"
    "Link feature: Bandwidth"

    LINK_PR = "PR"
    "Link feature:  Propagation delay"
    global LINK_COUNTER

    def __init__(self, source_id=None, destination_id=None, bandwidth=None, latency=None, id = None):
        global LINK_COUNTER
        self.bandwidth = bandwidth
        self.source_id = source_id
        self.destination_id = destination_id
        self.latency = latency
        self.id = id
        LINK_LIST[LINK_COUNTER] = self
        LINK_COUNTER += 1

    def get_bandwidth(self):
        return self.bandwidth

    def update_bandwidth(self, bw):
        self.bandwidth = bw

    def get_latency(self):
        return self.latency

    def update_latency(self, latency):
        self.latency = latency


def add_link(source_id=None, destination_id=None, bandwidth=None, latency=None, id = None):
    return Link(source_id, destination_id, bandwidth, latency, id)


def get_link_w_id(self, link_id):
    return LINK_LIST[link_id]
