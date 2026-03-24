from graph import VonNeumannGraph

def main() -> None:
    graph = VonNeumannGraph(n_nodes=256)

    print(f"Nós: {graph.get_num_nodes()}")    
    print(f"Arestas: {graph.get_num_edges()}")
    print(type(graph))  


if __name__ == "__main__":
    main()