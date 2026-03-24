import networkx as nx
import random
import csv
import os

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
    
    def posicionar_agentes(self, fracao: float, seed: int = None, flag: str = "agente") -> dict:
        """
        Posiciona agentes aleatoriamente nos vértices do grafo.
        
        Args:
            fracao: Fração de vértices que receberão agentes (entre 0 e 1)
            seed: Semente para o gerador de números aleatórios (opcional)
            flag: Nome/flag para identificar os agentes
            
        Returns:
            dict: Dicionário com as posições dos agentes {posicao: flag_id}
        """
        # Configura a semente
        if seed is not None:
            random.seed(seed)
        
        # Obtém todos os vértices
        vertices = list(self.G.nodes())
        total_vertices = len(vertices)
        
        # Calcula número de agentes
        num_agentes = int(total_vertices * fracao)
        
        # Seleciona vértices aleatórios
        vertices_escolhidos = random.sample(vertices, num_agentes)
        
        # Cria dicionário de agentes com a flag
        self.agentes = {}
        for i, vertice in enumerate(vertices_escolhidos):
            self.agentes[vertice] = f"{i}"
        
        return self.agentes

    def calcular_fracao_para_chasers(self, num_escapers: int, fracao_escapers: float) -> float:
        """
        Calcula a fração do grid total para posicionar chasers baseado em uma fração dos escapers.
        
        Args:
            num_escapers: Número de escapers
            fracao_escapers: Fração dos escapers que serão chasers (ex: 0.25)
        
        Returns:
            float: Fração do grid total para posicionar os chasers
        """
        total_vertices = self.get_num_nodes()
        num_chasers = int(fracao_escapers * num_escapers)
        return num_chasers / total_vertices
    
    # def salvar_posicoes_csv(self, escapers: dict, chasers: dict, prefixo: str = "posicoes", 
    #                         seed: int = None):
    #     """
    #     Salva as posições dos escapers e chasers em arquivos CSV e a seed em um arquivo separado.
        
    #     Args:
    #         escapers: Dicionário de escapers {posicao: id}
    #         chasers: Dicionário de chasers {posicao: id}
    #         prefixo: Prefixo para os nomes dos arquivos
    #         seed: Seed usada na simulação
    #     """
    #     # Salva escapers
    #     with open(f"{prefixo}_escapers.csv", 'w', newline='') as arquivo:
    #         escritor = csv.writer(arquivo)
    #         escritor.writerow(['x', 'y', 'id'])
            
    #         for (x, y), id_agente in escapers.items():
    #             escritor.writerow([x, y, id_agente])
        
    #     # Salva chasers
    #     with open(f"{prefixo}_chasers.csv", 'w', newline='') as arquivo:
    #         escritor = csv.writer(arquivo)
    #         escritor.writerow(['x', 'y', 'id'])
            
    #         for (x, y), id_agente in chasers.items():
    #             escritor.writerow([x, y, id_agente])
        
    #     # Salva seed
    #     with open(f"{prefixo}_seed.txt", 'w') as arquivo:
    #         arquivo.write(f"Seed: {seed}")
        
    #     print(f"Arquivos salvos: {prefixo}_escapers.csv, {prefixo}_chasers.csv e {prefixo}_seed.txt")
   
    def salvar_posicoes_csv(self, escapers: dict, chasers: dict, prefixo: str = "posicoes", 
                                seed: int = None):
        """
        Salva as posições dos escapers e chasers em arquivos CSV e a seed em um arquivo separado.
        Os arquivos são salvos no diretório ../../data/data_environment/[prefixo]/
        
        Args:
            escapers: Dicionário de escapers {posicao: id}
            chasers: Dicionário de chasers {posicao: id}
            prefixo: Prefixo para os nomes dos arquivos (também usado como nome da pasta)
            seed: Seed usada na simulação
        """
        # Define o diretório base com o prefixo como subpasta
        diretorio_base = f"../../data/data_environment/{prefixo}"
        
        # Cria o diretório se não existir
        os.makedirs(diretorio_base, exist_ok=True)
        
        # Caminhos completos dos arquivos (agora dentro da pasta do prefixo)
        caminho_escapers = os.path.join(diretorio_base, f"escapers.csv")
        caminho_chasers = os.path.join(diretorio_base, f"chasers.csv")
        caminho_seed = os.path.join(diretorio_base, f"seed.txt")
        
        # Salva escapers
        with open(caminho_escapers, 'w', newline='') as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerow(['x', 'y', 'id'])
            
            for (x, y), id_agente in escapers.items():
                escritor.writerow([x, y, id_agente])
        
        # Salva chasers
        with open(caminho_chasers, 'w', newline='') as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerow(['x', 'y', 'id'])
            
            for (x, y), id_agente in chasers.items():
                escritor.writerow([x, y, id_agente])
        
        # Salva seed
        with open(caminho_seed, 'w') as arquivo:
            arquivo.write(f"Seed: {seed}")
        
        print(f"Arquivos salvos em: {diretorio_base}/")
        print(f"  - escapers.csv")
        print(f"  - chasers.csv")
        print(f"  - seed.txt")