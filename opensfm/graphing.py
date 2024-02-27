import logging
import typing as t
import networkx as nx
import matplotlib.pyplot as plt
from opensfm import tracking
from opensfm.dataset_base import DataSetBase

def update_graph(graph):
    nx.draw_networkx(graph, with_labels=True)
    plt.savefig("graph.png")
    # Compute communities using modularity
    C = nx.community.greedy_modularity_communities(graph, "weight")
    MST = nx.maximum_spanning_tree(graph, "weight")
    i = 0
    Cs = []
    for c in C:
        Cg = graph.subgraph(c)  # Draw communities with different colors
        MST.add_edges_from(Cg.edges(data=True))
        for n in Cg.nodes():
            graph.nodes[n]["group"] = i
        i += 1
        Cs.append(Cg.number_of_nodes())

    l = []
    # Find edges between communities
    for e in MST.edges():
        # Adjacent communities
        if (graph.nodes[e[0]]["group"] != graph.nodes[e[1]]["group"]):
            #MST.edges[e]["inter_comm"] = True
            l = [(u, v, d) for u, v, d in graph.edges(data=True) if 
                 (lambda u,v,d: 
                    graph.nodes[u]["group"] == graph.nodes[e[0]]["group"] and
                    graph.nodes[v]["group"] == graph.nodes[e[1]]["group"])
                    (u, v, d)]
            
            MST.add_edges_from(l)
    plt.close()
    nx.draw_networkx(MST, with_labels=True)
    plt.savefig("MST.png")
    return list(nx.non_edges(MST))

