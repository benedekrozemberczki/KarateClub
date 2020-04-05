import random
import numpy as np
import networkx as nx
from tqdm import tqdm
from karateclub.utils.walker import RandomWalker
from karateclub.estimator import Estimator

class GEMSEC(Estimator):
    r"""An implementation of `"GEMSEC" <https://arxiv.org/abs/1802.03997>`_
    from the ASONAM '19 paper "GEMSEC: Graph Embedding with Self Clustering".
    The procedure uses random walks to approximate the pointwise mutual information
    matrix obtained by pooling normalized adjacency matrix powers. This matrix
    is decomposed by an approximate factorization technique.

    Args:
        walk_number (int): Number of random walks. Default is 10.
        walk_length (int): Length of random walks. Default is 80.
        dimensions (int): Dimensionality of embedding. Default is 128.
        negative_samples (int): Number of negative samples. Default is 5.
        window_size (int): Matrix power order. Default is 5.
        learning_rate (float): Gradient descent learning rate. Default is 0.05.
        clusters (int): Number of cluster centers. Default is 10.
        gamma (float): Clustering cost weight coefficient. Default is 0.01.
    """
    def __init__(self, walk_number=10, walk_length=80, dimensions=128, negative_samples=5,
                 window_size=5, learning_rate=0.01, clusters=10, gamma=0.01):

        self.walk_number = walk_number
        self.walk_length = walk_length
        self.dimensions = dimensions
        self.negative_samples = negative_samples
        self.window_size = window_size
        self.learning_rate = learning_rate
        self.clusters = clusters
        self.gamma = gamma

    def _setup_sampling_weights(self, graph):
        self.sampler = {}
        index = 0
        for node in graph.nodes():
            for _ in range(graph.degree(node)):
                self.sampler[index] = node
                index = index + 1
        self.global_index = index + 1

    def _initialize_node_embeddings(self, graph):
        shape = (graph.number_of_nodes(), self.dimensions)
        self._base_embedding = np.random.normal(0, 1.0/self.dimensions, shape)
        self._noise_embedding = np.random.normal(0, 1.0/self.dimensions, shape)

    def _initialize_cluster_centers(self, graph):
        shape = (self.dimensions, self.clusters)
        self._cluster_centers = np.random.normal(0, 1.0/self.dimensions, shape)

    def _sample_negative_samples(self):
        negative_samples = [for _ in range(self.negative_samples)]

    def _update_a_weight(self, source_node, target_node):
        self._sample_negative_samples()

    def _do_gradient_descent(self):
        random.shuffle(self.walker.walks)
        for walk in tqdm(self.walker.walks):
            for i, source_node in enumerate(walk[:self.walk_length-self.window_size]):
                for step in range(1,self.window_size+1):
                    target_node = walk[i+step]
                    self._update_a_weight(source_node, target_node)

    def fit(self, graph):
        """
        Fitting a GEMSEC model.

        Arg types:
            * **graph** *(NetworkX graph)* - The graph to be embedded.
        """
        self._check_graph(graph)
        self._setup_sampling_weights(graph)
        self.walker = RandomWalker(self.walk_length, self.walk_number)
        self.walker.do_walks(graph)
        self._initialize_node_embeddings(graph)
        self._initialize_cluster_centers(graph)
        self._do_gradient_descent()


    def get_embedding(self):
        r"""Getting the node embedding.

        Return types:
            * **embedding** *(Numpy array)* - The embedding of nodes.
        """
        return np.array(self._embedding)