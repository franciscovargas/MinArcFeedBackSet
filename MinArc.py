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
        self.scores = {} #  dictionary of delta scores (indices to self.bucket)
        self.s_left = deque()
        self.s_right = deque()
        self.s = self.s_left
        self.lowest = float("inf")
        self.removed_nodes = set()
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
        for x in self.G.nodes:
            wn = sum([self.G[nd][md]["weight"] for nd, md in self.G.in_edges(x)])
            for y, _ in self.G.in_edges(x):
                self.G[y][x]['w'] = float(self.G[y][x]['weight'])
                self.G[y][x]['weight'] /= wn # normalising weights
                # print((y ,x) , self.G[y][x]['weight'])

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

            if nd in self.buckets[0] or nd in self.buckets[-1] or nd in self.removed_nodes: continue # if nd sink, source or removed skip iretration

            ind = mid + self.scores[nd] # bucket index for node nd

            x = self.buckets[ind].remove(nd)

            self.scores[nd] += parity
            _deg = 1 if parity >= 0 else 0
            self.degrees[nd][_deg] -= 1

            # Check if nd becomes a sink/source or if it moves to an adjecent bucket
            if  self.degrees[nd][_deg] > 0 and  self.degrees[nd][not _deg] > 0:
                self.buckets[self.scores[nd] + mid].append(nd)
            else:
                self.buckets[-1 if parity > 0 else 0].append(nd)

            # Track the min in O(1) amortised
            # (if the bucket with the min becomes null it means the min has been moved up by one)
            if not self.buckets[self.lowest + mid] or self.scores[nd] < self.lowest:
                # print("track", self.scores[nd])
                # if self.scores[nd] == 5: import pdb; pdb.set_trace()
                if  self.degrees[nd][_deg] > 0 and  self.degrees[nd][ not _deg] > 0:
                    self.lowest = self.scores[nd]
                # else: # should hopefully be a rare case
                    # print("twice")
        if not self.buckets[self.lowest + mid] and  len(self.removed_nodes) < self.n :
            # import pdb; pdb.set_trace()
            self.lowest = min([self.scores[x] for x in self.scores if x not in  self.removed_nodes])

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
        self.removed_nodes.add(node) # Mark node as removed

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
        # print ind
        if self.buckets[ind]: # Can only remove node if it has not been removed already
            if ind < 0 or ind >= len(self.buckets) - 1:
                self.s_right.appendleft(self.buckets[ind][0])
            else:
                self.s_left.append(self.buckets[ind][0])
            self.update_buckets(self.buckets[ind].pop(0))
        else:
            # import pdb; pdb.set_trace()
            raise BaseException("Bucket %d already removed", ind)


    def gen_buckets(self):
        n = self.n

        # Degree dict to avoid modifying G on the fly
        self.degrees = { k: [v, self.G.out_degree[k]] for k, v in self.G.in_degree }

        self.buckets = [[] for i in  xrange( 2 * n - 1 )]
        mid = n - 1 # n - 1 but -1 for indexing at 0

        for node in set(self.G.nodes):
            if self.degrees[node][0] == 0 and  self.degrees[node][1] > 0:
                self.buckets[0].append(node)
            elif self.degrees[node][1] == 0 and  self.degrees[node][0] > 0:
                self.buckets[-1].append(node)
            else:
                score = self.scores[node]
                self.lowest = min(score, self.lowest)
                self.buckets[mid + score].append(node)


    def eades(self):
        """
        Implementation of Greedy FAS algorithm according to  Eades et al. (1993)

        Only difference is that it removes the minimum ranked node and not the maximum
        as per Tintelnot, F. et al. (2017)

        """
        self.gen_buckets()
        mid = self.n - 1
        while ( len(self.removed_nodes) < self.n ):

            while self.buckets[-1]:
                self.remove_ind(-1)

            while self.buckets[0]:
                self.remove_ind(0)

            if ( len(self.removed_nodes) < self.n ):
                self.remove_ind(mid + self.lowest)

        self.s_left = deque(self.s_left) # debugging purposes (creating derreferenced copy)
        self.s.extend(self.s_right) # construct partial order

    def build_dag(self):
        """
        DFS traversal of the ordering resulting from GR-FAS (eades)
        """

        if len(self.s) != self.n: # check if partial order has already been constructed
            self.eades()

        order = {x: i for i, x in enumerate(self.s)} # assign integers to ordering

        GG = self.G.to_undirected()

        starting_points = [x.pop() for x in nx.connected_components(GG)]
        visited = set([self.s[0]])
        violator_set = []
        w_norm = sum([ self.G.get_edge_data(x,y)['weight'] for x, y in self.G.in_edges])
        violator_weights = []
        for s_0 in starting_points:
            q = deque([s_0])
            while q:
                cur_node = q.pop()
                # print cur_node
                in_edges = [(x,y) for y,x in self.G.in_edges(cur_node)]
                # print(in_edges)
                edges = list(self.G.out_edges(cur_node)) + in_edges
                # print(edges)
                for _, x in edges:
                    if order[x] < order[cur_node]: # if edge breaks order remove
                        try:
                            if (cur_node, x, self.G[cur_node][x]["weight"]) not in violator_set:
                                print "violator edge: {0}-{1}".format(cur_node, x)
                                violator_set.append((cur_node, x, self.G[cur_node][x]["weight"]))
                        except KeyError:
                            pass
                    if x not in visited:
                        q.append(x)
                        visited.add(x)
        violator_set = set(violator_set)
        for s, t, w in violator_set:
            self.G.remove_edge(s, t)
            violator_weights.append(w)

        print( "% of removed edges: {0}, " +
               "number of removed edges {1}, " +
               "total number of edges: {2}").format(len(violator_set) * 100.0 / self.n,
                                                    len(violator_set),
                                                    self.n)
        print "% of weight \"mass\" removed: {0}".format(sum(violator_weights) * 100 / w_norm)
        print "violator set : {}".format(violator_set)

        if self.debug: self.draw(self.G) # plot resulting DAG (debug)

        try:
            print nx.find_cycle(self.G), "ERROR !!!! Found cycles"
            # print self.s, self.s_left, self.s_right
        except nx.exception.NetworkXNoCycle:
            print "NO CYCLES FOUND "

        return self.G.copy()

    def draw(self, G = None):
        """
        Plots a networkX graph G defaults to self.G if
        G is None. (Used for debugging purposes)
        """
        if not G: G = self.G


        pos = nx.shell_layout(G)
        nx.draw_networkx_nodes(G, pos)
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos)
        plt.show()


if __name__ == '__main__':

    # Test/Demo usage
    G = nx.DiGraph()
    G.add_edge("A", "B", weight=1.0)
    # G.add_edge("B", "A", weight=1.0)
    G.add_edge("B", "D", weight=1.0)
    G.add_edge("D", "E", weight=1.0)
    G.add_edge("C", "B", weight=1.0)
    G.add_edge("D", "C", weight=1.0)
    af = GreedyFAS(G.copy(), weighted=False, debug=True)

    DAG = af.build_dag()
    print af.s, af.s_left, af.s_right
