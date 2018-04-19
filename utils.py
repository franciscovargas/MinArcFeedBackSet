#!/usr/bin/python
import networkx as nx
import csv
import argparse
from MinArc import GreedyFAS


def csv2graph(csv_name="FASG.csv"):
    """
    This function converts a csv with format:

    target, source, timestamp, share, ...
    v,      u,        t ,      w 

    into a networkX graph
    """
    edge_cache = set() # to keep track of repeats and take union
    G = G = nx.DiGraph() # Digraph to output

    with open(csv_name, "rb") as f:
        reader = csv.reader(f, delimiter=",")
        for i, line in enumerate(reader):
            if i < 1: continue # ignores header of the file
            v, u , t , w = line
            if (u, v) not in edge_cache:
                edge_cache.add((u, v))
                G.add_edge(u, v, weight = float(w))
            else:
                G[u][v]['weight'] += float(w)

    return G 


def graph2csv(G, csv_name="DAG"):
    """
    Takes as input a weighted networkX graph and creates
    a csv of the form :

    source, target, weight
    u,       v,     w
    """
    csv_name = "DAG_{0}.csv".format(csv_name)
    with open(csv_name, "wb") as f:
        writer = csv.writer(f)
        writer.writerow(['source', 'target', 'trade'])
        for u, v, w in G.edges(data=True):
            writer.writerow([u, v, w['w']])


def partial2csv(orderings, csv_name="partial"):
    """
    Takes in a list of strings and dumps them in a csv

    intended to be used to output the ordering from Eades
    into a csv file
    """
    csv_name = "partial_{0}.csv".format(csv_name)
    with open(csv_name, "wb") as f:
        writer = csv.writer(f)
        writer.writerow(['node'])
        for order in orderings:
            writer.writerow([order])


def csv2Dag(input_file, output_name):

    G = csv2graph(input_file)

    fs = GreedyFAS(G, weighted=True, debug=False)
    DAG = fs.build_dag()
    
    graph2csv(DAG, output_name)
    partial2csv(fs.s, output_name)

if __name__ == '__main__':
    # Command line tool to create DAG
    parser = argparse.ArgumentParser(description="Command line tool to generate CSV outputs relating  Eades GR-FAS Algo on an input graph")
    parser.add_argument("input_csv", help="name of csv file containing the graph to run Eades GR-FAS algorithm on (i.e. transactions.csv)")
    parser.add_argument("output_name", help="Postfix name for the output CSV files ( i.e. example_name)")
    args = parser.parse_args()

    csv2Dag(args.input_csv, args.output_name)