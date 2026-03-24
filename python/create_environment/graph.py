import networkx as nx

class VonNeumannGraph:
    """Classe para criar um grafo de von Neumann (4-vizinhos) a partir de um grid."""
    
    def __init__(self, n_nodes: int):
        """
        Inicializa o grafo de von Neumann.
        
        Args:
            n_nodes: Número de nós em cada dimensão (grid n_nodes x n_nodes)
        """
        self.n_nodes = n_nodes
        self.G = nx.Graph()
        self._build_graph()
    
    def _build_graph(self):
        """Constrói o grafo com conectividade de von Neumann (4-vizinhos)."""
        # Adiciona todos os nós
        for i in range(self.n_nodes):
            for j in range(self.n_nodes):
                self.G.add_node((i, j))
        
        # Adiciona arestas para vizinhos 4-direções
        for i in range(self.n_nodes):
            for j in range(self.n_nodes):
                # Vizinho abaixo
                if i + 1 < self.n_nodes:
                    self.G.add_edge((i, j), (i + 1, j))
                # Vizinho à direita
                if j + 1 < self.n_nodes:
                    self.G.add_edge((i, j), (i, j + 1))
    
    def get_graph(self) -> nx.Graph:
        """Retorna o grafo NetworkX."""
        return self.G
    
    def get_num_nodes(self) -> int:
        """Retorna o número total de nós."""
        return self.G.number_of_nodes()
    
    def get_num_edges(self) -> int:
        """Retorna o número total de arestas."""
        return self.G.number_of_edges()