from features.graph import VonNeumannGraph
from features.graph import random

def main() -> None:
    graph = VonNeumannGraph(n_nodes=128)

    # print(f"Nós: {graph.get_num_nodes()}")    
    # print(f"Arestas: {graph.get_num_edges()}")

    # seed = random.randint(0, 1000000)
    
    # escapers = graph.posicionar_agentes(fracao=0.1, seed=seed, flag="escaper")
    # num_escapers = len(escapers)

    # # Calcula automaticamente a fração
    # fracao_chasers = graph.calcular_fracao_para_chasers(num_escapers, 0.25)

    # # Posiciona os chasers com a fração calculada
    # chasers = graph.posicionar_agentes(fracao=fracao_chasers, seed=seed, flag="chasers")

    # print(f"Escapers: {num_escapers}")
    # print(f"Chasers: {len(chasers)}")
    # print(f"Fração usada: {fracao_chasers:.6f}")

    # graph.salvar_posicoes_csv(escapers, chasers, prefixo="simulation_1", seed=seed)


    # # Executa 100 simulações
    # for i in range(100):
    #     # Gera seed aleatória para cada simulação
    #     seed = random.randint(0, 1000000)
        
    #     print(f"\nSimulação {i+1}/100 - Seed: {seed}")
        
    #     # Posiciona agentes com a seed
    #     escapers = graph.posicionar_agentes(fracao=0.1, seed=seed, flag="escaper")
    #     num_escapers = len(escapers)

    #     # Calcula automaticamente a fração
    #     fracao_chasers = graph.calcular_fracao_para_chasers(num_escapers, 0.25)
    #     chasers = graph.posicionar_agentes(fracao=fracao_chasers, seed=seed, flag="chasers")
        
    #     # Salva com prefixo diferente para cada simulação
    #     graph.salvar_posicoes_csv(escapers, chasers, prefixo=f"simulation_{i+1}", seed=seed)
        



    # Executa 100 simulações para cada fração
    fracoes_chasers = [0.05, 0.50, 1.0]
    #fracoes_chasers = [0.05,0.10,0.15,0.20,0.30,0.35,0.40,0.45,0.55,0.60,0.65,0.70,0.75,0.80,0.85,0.90,0.95]

    for fracao in fracoes_chasers:
        print(f"\n=== Configuração: {fracao*100}% dos escapers ===")
        
        for i in range(100):
            # # Gera seed aleatória para cada simulação
            # seed = random.randint(0, 1000000)
            
            # print(f"\nSimulação {i+1}/100 - Fração: {fracao*100}% - Seed: {seed}")
            
            # # Posiciona agentes com a seed
            # escapers = graph.posicionar_agentes(fracao=0.1, seed=seed, flag="escaper")
            # num_escapers = len(escapers)
            
            # # Calcula automaticamente a fração do grid para os chasers
            # fracao_grid = graph.calcular_fracao_para_chasers(num_escapers, fracao)
            
            # # Posiciona os chasers
            # chasers = graph.posicionar_agentes(fracao=fracao_grid, seed=seed, flag="chasers")
            
            # # Salva com prefixo incluindo a fração
            # prefixo = f"simulation_frac_{int(fracao*100)}_run_{i+1}"
            # graph.salvar_posicoes_csv(escapers, chasers, prefixo=prefixo, seed=seed)
            
            # print(f"  - Escapers: {len(escapers)}")
            # print(f"  - Chasers: {len(chasers)}")
            # Gera seed aleatória para cada simulação
            seed = random.randint(0, 1000000)
            
            #print(f"\nSimulação {i+1}/{num_simulacoes} - Fração: {fracao*100}% - Seed: {seed}")
            
            # Posiciona escapers primeiro
            escapers = graph.posicionar_agentes(
                fracao=0.1,  # 10% do grid para escapers
                seed=seed, 
                flag="escaper"
            )
            num_escapers = len(escapers)
            
            # Pega as posições ocupadas pelos escapers
            posicoes_ocupadas = set(escapers.keys())
            
            # Calcula número de chasers baseado na fração dos escapers
            num_chasers = int(fracao * num_escapers)
            
            # Calcula fração baseada nos vértices restantes
            total_vertices = graph.get_num_nodes()
            vertices_restantes = total_vertices - num_escapers
            
            if vertices_restantes > 0:
                fracao_chasers = num_chasers / vertices_restantes
            else:
                fracao_chasers = 0
            
            # Posiciona chasers evitando posições dos escapers
            chasers = graph.posicionar_agentes(
                fracao=fracao_chasers,
                seed=seed,
                flag="chasers",
                posicoes_ocupadas=posicoes_ocupadas
            )
            
            # Verifica sobreposição
            sobreposicao = set(escapers.keys()) & set(chasers.keys())
            if sobreposicao:
                print(f"  AVISO: {len(sobreposicao)} posições sobrepostas!")
                input()
            
            # Salva com prefixo incluindo a fração
            prefixo = f"simulation_frac_{int(fracao*100)}_run_{i+1}"
            graph.salvar_posicoes_csv(escapers, chasers, prefixo=prefixo, seed=seed)
            
            print(f"  - Escapers: {len(escapers)} (10% do grid)")
            print(f"  - Chasers: {len(chasers)} ({fracao*100:.0f}% dos escapers)")
            print(f"  - Total ocupado: {len(escapers) + len(chasers)}/{total_vertices} ({((len(escapers) + len(chasers))/total_vertices)*100:.1f}%)")


    print("\nTodas as 100 simulações concluídas!")

if __name__ == "__main__":
    main()