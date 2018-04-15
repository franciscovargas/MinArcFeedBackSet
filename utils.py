import networkx as nx
import csv


def csv2graph(csv_name="FASG.csv"):
    edge_cache = set() # to keep track of repeats and take union
    G = G = nx.DiGraph() # Digraph to output

    with open(csv_name, "rb") as f:
        reader = csv.reader(f, delimiter=",")
        for i, line in enumerate(reader):
            if i < 1: continue
            v, u , t , w = line
            if (u, v) not in edge_cache:
                edge_cache.add((u, v))
                G.add_edge(u, v, weight = float(w))
            else:
                G[u][v]['weight'] += float(w)

    return G 

def graph2csv(G, csv_name="DAG.csv"):
    with open(csv_name, "wb") as f:
        writer = csv.writer(f)
        writer.writerow(['source', 'target', 'trade'])
        for u, v, w in G.edges(data=True):
            writer.writerow([u, v, w['w']])

def partial2csv(orderings, csv_name="partial.csv"):
    with open(csv_name, "wb") as f:
        writer = csv.writer(f)
        writer.writerow(['node'])
        for order in orderings:
            writer.writerow([order])

if __name__ == '__main__':
    from MinArc import GreedyFAS

    G = csv2graph()

    fs = GreedyFAS(G, weighted=True, debug=False)
    DAG = fs.build_dag()
    # print fs.s # , fs.s_left, fs.s_right
    graph2csv(DAG)
    partial2csv(fs.s)