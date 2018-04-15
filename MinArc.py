"""
Bib + links:
[1] - Tintelnot, F., Kikkawa, K., Mogstad, M. and Dhyne, E., 2017.
      Trade and Domestic Production Networks. Unpublished Manuscript, University of Chicago.
      (http://felix-tintelnot.wdfiles.com/local--files/research/TKMD_draft.pdf)
[2] - Eades, P., X. Lin, and W. F. Smyth (1993): "A Fast and Effective Heuristic for the
      Feedback Arc Set Problem," Information Processing Letters, 47, 319-323.
     (http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.47.7745)
[3] - Simpson, M., V. Srinivasan, and A. Thomo (2016): "Efficient Computation of Feedback
      Arc Set at Web-Scale," Proceedings of the VLDB Endowment, 10, 133-144.
      (http://www.vldb.org/pvldb/vol10/p133-simpson.pdf)
"""
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout, to_agraph
from collections import deque
import math


class GreedyFAS:

    def __init__(self, G, weighted=False, debug=False):
        self.n = G.number_of_nodes()
        self.G = G # NetworkX graph
        self.DAG = G.copy() # local min arcset solution
        self.scores = {} #  dictionary of delta scores (indices to self.bucket)
        self.s_left = deque()
        self.s_right = deque()
        self.s = self.s_left
        self.lowest = float("inf")
        self.d = []
        self.debug = debug
        self.gen_scores(weighted)

    def gen_scores(self, weighted):
        """
        Helper method (to make constructor smaller)
        """
        if weighted:
            self.gen_scores_weighted()
        else:
            self.gen_scores_unweighted()

    def gen_scores_unweighted(self):
        """
        Sets up scores for unweighted graphs according to Eades et al. (1993)
        """
        for node, in_d in self.G.in_degree:
            self.scores[node] = in_d - self.G.out_degree[node]

    def gen_scores_weighted(self):
        """
        Sets up the scores for weighted graphs according to Simpson et al. (2016)
        """

        # normalise weights (Its very unclear about a sound statistical way of doing this)
        w_norm = max([ self.G.get_edge_data(x,y)['weight'] for x, y in self.G.edges])
        for x, y in self.G.edges:
            self.G[x][y]['weight'] /= w_norm # normalising weights

        # sets up scores using difference of w_in vs w_out as per [3] Simpson et al. (2016) 
        for node in self.G.nodes:
            w_in = sum([w['weight'] for x, y, w in self.G.in_edges(node, data=True)])
            w_out = sum([w['weight'] for x, y, w in self.G.out_edges(node, data=True)])
            # print w_in, w_out
            self.scores[node] = int(math.floor(w_in - w_out))


    def update_neighbours(self, neighbours, parity=1, node=None):
        """
        Loops over a set of neihbours (either ingoing or outgoing to a node) and
        updates the buckets given these edges (node-neigh) will be rremoved

        params:
            :param neighbours[list(str/int)]: list of nodes which have just lost a common neighbour
            :param parity [int]: positive indicates ingoing edges , negative outgoing
        output:
            void - this method returns nothing since it changes the state of the object inplace 
        """

        parity = -1 if parity < 0 else 1 # normalise parity
        mid = self.n - 1 # 

        for nd, _ in neighbours:
            nd = nd if parity >= 0 else _ # quick swap

            if nd in self.buckets[0] or nd in self.buckets[-1]: continue # if nd sink or source skip iretration
            
            ind = mid + self.scores[nd] # bucket index for node nd

            x = self.buckets[ind].pop(self.buckets[ind].index(nd))

            self.scores[nd] += parity

            # Check if nd becomes a sink or if it moves to an adjecent bucket
            if  self.G.in_degree(nd) > 0 and  self.G.out_degree(nd) > 0:
                self.buckets[self.scores[nd] + mid].append(nd)
            else:
                self.buckets[-1 if parity > 0 else 0].append(nd) 
            
            # Track the min in O(1)
            # (if the bucket with the min becomes null it means the min has been moved up by one)
            if not self.buckets[self.lowest + mid]:
                self.lowest = self.scores[nd]

    def update_buckets(self, node):
        """
        Update buckets and remove a node from the graph self.G

        params:
            :param node[str/int]: id corresponding to the node within self.G

        output:
            void - this method works inplace
        """
        mid = self.n - 1
        
        ine = list(self.G.in_edges(node)) # in going edges to node
        oute = list(self.G.out_edges(node)) # out going edges from node

        self.G.remove_node(node) # remove node from networkX graph data structure

        self.update_neighbours(ine, 1, node) # update buckets for ingoing nodes to node
        self.update_neighbours(oute, -1, node) # update buckets for outgoing nodes to node

    def remove_ind(self, ind):
        """
        Coordinates the removal of the top element at 
        particular index ind in  a bucket (which corresponds to removing a node):

        1. It appends node to s_left or s_right accordingly
        2. It pops element from bin/bucket
        3. it calls self.update_buckets on that popped element (say u) which:
            a - removes node from the graph G - u
            b - updates neighbours into buckets accordingly

        params:
            :param ind[int]: index within self.buckets corresponding to a bucket
        output:
            void - this method returns no output it changes the state of the object inplace
        """
        if self.buckets[ind]: # Can only remove node if it has not been removed already
            if ind < 0 or ind >= len(self.buckets) - 1:
                self.s_right.appendleft(self.buckets[ind][0])
            else:
                self.s_left.append(self.buckets[ind][0])
            self.update_buckets(self.buckets[ind].pop(0))
        else:
            pass # raise BaseException("Bucket %d already removed", ind)


    def gen_buckets(self):
        n = self.n

        # These lines are virtually unnnecesary and should be removed
        degrees = { k: (v, self.G.out_degree[k]) for k, v in self.G.in_degree }
        Vsource = [k for k, v in
                   degrees.items()  if v[0] == 0 and v[1] > 0]
        Vd = [(self.scores[k], k) for k, v in
              degrees.items() if v[0] > 0 and v[1] > 0]
        Vsink = [k for k, v in
                 degrees.items()  if v[0] > 0 and v[1] == 0]

        self.buckets = [[]] * ( 2 * n - 1 )
        mid = n - 1 # n - 1 but -1 for indexing at 0

        for score, node in Vd:

            if not self.buckets[mid + score]:
                self.buckets[mid + score] = []
            self.lowest = min(score, self.lowest)
            self.buckets[mid + score].append(node)

        self.buckets[0] = Vsource
        self.buckets[-1] = Vsink


    def eades(self):
        """
        Implementation of Greedy FAS algorithma according to  Eades et al. (1993)

        """
        self.gen_buckets()

        mid = self.n - 1

        while (self.G.number_of_nodes() > 0 ):

            while self.buckets[-1]:
                self.remove_ind(-1)

            while self.buckets[0]:
                self.remove_ind(0)

            if (self.G.number_of_nodes() > 0 ):
                self.remove_ind(mid + self.lowest)

        self.s_left = deque(self.s_left) # debugging purposes (creating derreferenced copy)
        self.s.extend(self.s_right) # construct partial order

    def build_dag(self):
        """
        DFS traversal of the partial 
        """

        if len(self.s) != self.n: # check if partial order has already been constructed
            self.eades()

        order = {x: i for i, x in enumerate(self.s)} # assign integers to ordering

        q = deque([self.s[0]])
        visited = set([self.s[0]]) # to not get stuck in cycles

        violator_set = []
        w_norm = sum([ self.DAG.get_edge_data(x,y)['weight'] for x, y in self.DAG.edges])
        violator_weights = []
        while q:
            cur_node = q.pop()
            for _, x in self.DAG.out_edges(cur_node):
                if order[x] < order[cur_node]: # if edge breaks order remove
                    violator_set.append((cur_node, x, self.DAG[cur_node][x]["weight"]))
                    print "violator edge: {0}-{1}".format(cur_node, x)
                if x not in visited:
                    q.append(x)
                    visited.add(x)
        
        for s, t, w in violator_set:
            self.DAG.remove_edge(s, t)
            violator_weights.append(w)

        print len(violator_set) * 100.0 / self.n, len(violator_set), self.n
        print sum(violator_weights) * 100 / w_norm
        # print nx.minimum_cut(self.DAG, self.s[0], self.s[-1])
        if self.debug: self.draw(self.DAG) # plot resulting DAG (debug)

        return self.DAG.copy()

    def draw(self, G = None):
        """
        Plots a networkX graph G defaults to self.G if
        G is None. (Used for debugging purposes)
        """
        if not G: G = self.G

        try:
            print nx.find_cycle(G), "found cycles"
        except nx.exception.NetworkXNoCycle:
            print "NO CYCLES FOUND "

        pos = nx.shell_layout(G)
        nx.draw_networkx_nodes(G, pos)
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos)
        plt.show()


if __name__ == '__main__':
    
    # Test/Demo usage
    G = nx.DiGraph()
    G.add_edge("A", "B", weight=1.0)
    G.add_edge("B", "D", weight=1.0)
    G.add_edge("D", "E", weight=1.0)
    G.add_edge("C", "B", weight=1.0)
    G.add_edge("D", "C", weight=1.0)
    af = GreedyFAS(G.copy(), weighted=True, debug=False)

    DAG = af.build_dag()
    print af.s, af.s_left, af.s_right
