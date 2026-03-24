from features.graph import VonNeumannGraph
from features.graph import random

def main() -> None:
    graph = VonNeumannGraph(n_nodes=256)

    print(f"Nós: {graph.get_num_nodes()}")    
    print(f"Arestas: {graph.get_num_edges()}")

    seed = random.randint(0, 1000000)
    
    escapers = graph.posicionar_agentes(fracao=0.1, seed=seed, flag="escaper")
    num_escapers = len(escapers)

    # Calcula automaticamente a fração
    fracao_chasers = graph.calcular_fracao_para_chasers(num_escapers, 0.25)

    # Posiciona os chasers com a fração calculada
    chasers = graph.posicionar_agentes(fracao=fracao_chasers, seed=seed, flag="chasers")

    print(f"Escapers: {num_escapers}")
    print(f"Chasers: {len(chasers)}")
    print(f"Fração usada: {fracao_chasers:.6f}")

    graph.salvar_posicoes_csv(escapers, chasers, prefixo="simulation_1", seed=seed)


    # Executa 100 simulações
    for i in range(100):
        # Gera seed aleatória para cada simulação
        seed = random.randint(0, 1000000)
        
        print(f"\nSimulação {i+1}/100 - Seed: {seed}")
        
        # Posiciona agentes com a seed
        escapers = graph.posicionar_agentes(fracao=0.1, seed=seed, flag="escaper")
        num_escapers = len(escapers)

        # Calcula automaticamente a fração
        fracao_chasers = graph.calcular_fracao_para_chasers(num_escapers, 0.25)
        chasers = graph.posicionar_agentes(fracao=fracao_chasers, seed=seed, flag="chasers")
        
        # Salva com prefixo diferente para cada simulação
        graph.salvar_posicoes_csv(escapers, chasers, prefixo=f"simulacao_{i+1}", seed=seed)
        
    print("\nTodas as 100 simulações concluídas!")

if __name__ == "__main__":
    main()