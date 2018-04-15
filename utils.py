import networkx as nx
import csv


def csv2graph(csv_name="FASG.csv"):
    edge_cache = set() # to keep track of repeats and take union
    G = G = nx.DiGraph() # Digraph to output

    with open(csv_name, "rb") as f:
        reader = csv.reader(f, delimiter=",")
        for i, line in enumerate(reader):
            if i < 1: continue
            u, v , t , w = line
            if (u, v) not in edge_cache:
                edge_cache.add((u, v))
                G.add_edge(u, v, weight = float(w))
            else:
                G[u][v]['weight'] += float(w)

    return G 


if __name__ == '__main__':
    from MinArc import GreedyFAS

    G = csv2graph()

    fs = GreedyFAS(G, weighted=True, debug=True)
    DAG = fs.build_dag()
    print fs.s # , fs.s_left, fs.s_right