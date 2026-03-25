// #include "simulation.h"
// #include "obstacle.h"
// #include "config.h"
// #include "utils.h"
// #include "cell.h"
// #include "cell_lattice.h"
// #include <iostream>
// #include <fstream>
// #include <vector>
// #include <omp.h>
// #include <filesystem>

#include <iostream>
#include <map>
#include "cell_lattice.h"
#include "cell.h"
#include "simulation.h"

// namespace fs = std::filesystem;

// /**
//  * @file main.cpp
//  * @brief Main simulation driver program
//  * 
//  * This program runs multiple simulation runs sequentially and collects
//  * statistical results for analysis.
//  */

// std::random_device rd;
// unsigned int GLOBAL_SEED = rd(); /**< Global random seed for reproducibility */

// /**
//  * @struct RunResult
//  * @brief Stores the results of a single simulation run
//  */
// struct RunResult {
//     int run;                /**< Run identifier number */
//     double steps;           /**< Number of steps executed */
//     int remainingPrey;      /**< Number of remaining prey cells */
//     unsigned int seed;      /**< Random seed used for this run */
// };

// /**
//  * @brief Main function that drives the simulation
//  * 
//  * @return int Exit status (0 for success)



int main() {
    // // Basic configuration
    // const int NUM_RUNS = 200;      /**< Number of simulation runs to execute */
    // SIZE = 128;                    /**< Grid size (will be square grid) */
    // WIDTH = SIZE;                  /**< Grid width */
    // HEIGHT = SIZE;                 /**< Grid height */

    // // Simulation parameters
    // std::vector<int> numHuntersValues = {1433};        /**< Number of hunter cells */
    // std::vector<int> numObstaclesValues = {4915};      /**< Number of obstacles */
    // std::vector<double> hunterNoiseValues = {1.00};    /**< Hunter movement noise */
    // std::vector<double> preyNoiseValues = {1.00};      /**< Prey movement noise */
    // const int HUNTER_SEARCH_RADIUS = 2;               /**< Search radius for hunters */
    // const int PREY_SEARCH_RADIUS = 2;                 /**< Search radius for prey */

    // // Initialize lattice and obstacles
    // CellLattice lattice(WIDTH, HEIGHT);
    // std::vector<Obstacle> obstacles;

 
    // // Vector to store results from all runs
    // std::vector<RunResult> results(NUM_RUNS);

    // logInfo("Starting " + std::to_string(NUM_RUNS) + " simulation runs in parallel");

    // // Execute runs in parallel with OpenMP
    // #pragma omp parallel for
    // for (int run = 0; run < NUM_RUNS; run++) 
    // {
    //     // Generate unique seed for each run based on parameters
    //     unsigned int runSeed = 1801929750 + run;
    //     std::mt19937 rng(runSeed);
        
    //     // Create simulation instance for this thread
    //     Simulation sim(lattice, numHunters, numPrey, numObstacles,
    //                   hunterNoiseValues[0], preyNoiseValues[0],
    //                   obstacles, HUNTER_SEARCH_RADIUS, PREY_SEARCH_RADIUS,
    //                   runSeed);
        
    //     logInfo("Processing run " + std::to_string(run));
        
    //     // Execute simulation run and collect results
    //     SimulationResult result = sim.runSingle(run, rng);
        
    //     results[run] = {run, result.steps, result.remainingPrey, runSeed};
    //     logInfo("Completed run " + std::to_string(run));
    // }
    
    // // Write results to file (serial section)
    // std::ofstream outputFile("simulation_results.csv");
    // if (!outputFile.is_open()) {
    //     logError("Failed to open output file: simulation_results.csv");
    //     return 1;
    // }
    
    // // Write CSV header
    // outputFile << "run,steps,remaining_prey,seed\n";
    
    // // Write results for all runs
    // for (const auto& result : results) {
    //     outputFile << result.run << "," 
    //                << result.steps << "," 
    //                << result.remainingPrey << "," 
    //                << result.seed << "\n";
    // }
    // outputFile.close();
    
    // logInfo("All simulation runs completed! Results saved to: simulation_results.csv");

    // criar o grid

    const int SIZE = 256;
    const int WIDTH = SIZE;
    const int HEIGHT = SIZE;
    
    CellLattice lattice(WIDTH, HEIGHT);
    
    // Teste 1: Verificar se o grid tem o tamanho esperado
    std::cout << "Testando tamanho do grid...\n";
    std::cout << "Esperado: " << HEIGHT << " linhas e " << WIDTH << " colunas\n";
    
    // Tenta acessar os limites do grid
    std::string valor = lattice.getGridValue(0, 0);
    std::cout << "Acessando (0,0): " << valor << "\n";
    
    valor = lattice.getGridValue(WIDTH - 1, HEIGHT - 1);
    std::cout << "Acessando (" << WIDTH - 1 << "," << HEIGHT - 1 << "): " << valor << "\n";
    
    // Testa se o grid está inicializado com "L" (ou o valor padrão)
    std::cout << "\nVerificando inicializacao...\n";
    bool allCorrect = true;
    for(int y = 0; y < HEIGHT && allCorrect; y++) {
        for(int x = 0; x < WIDTH && allCorrect; x++) {
            if(lattice.getGridValue(x, y) != "L") {
                allCorrect = false;
                std::cout << "Erro em (" << x << "," << y << "): esperado 'L', encontrado '" 
                          << lattice.getGridValue(x, y) << "'\n";
            }
        }
    }
    
    if(allCorrect) {
        std::cout << "Grid inicializado corretamente com 'L' em todas as posicoes\n";
    }
    
    std::cout << "\nTeste concluido!\n";
    

    std::string escaper_file = "/home/camafeu/Documentos/rossatto/github/Chase-escape_with_temporary_obstacles/data/data_environment/simulation_frac_25_run_1/escapers.csv";
    std::string chaser_file = "/home/camafeu/Documentos/rossatto/github/Chase-escape_with_temporary_obstacles/data/data_environment/simulation_frac_25_run_1/chasers.csv";
    
    std::cout << "=== Carregando células do arquivo ===\n\n";
    
    // Carregar células cancerígenas
    std::vector<Cell> escapers = Cell::loadFromCSV(escaper_file, "O",2);
    std::vector<Cell> chasers = Cell::loadFromCSV(chaser_file, "N",2);
    
    std::cout << "Total: " << escapers.size() << " escapers\n";
    std::cout << "Total: " << chasers.size() << " chasers\n";
    std:: cin.get();
    

    // std::cout << "Bloco escapers\n";
    // if (!escapers.empty()) {
    //     std::cout << "\nPrimeiras 10 células:\n";
    //     for (size_t i = 0; i < std::min(escapers.size(), size_t(10)); i++) {
    //         const auto& cell = escapers[i];
    //         std::cout << "  [" << i << "] ID=" << cell.getId() 
    //                   << " Pos=(" << cell.getPositionX() 
    //                   << "," << cell.getPositionY() << ")\n";
    //     }
        
    //     std::cout << "\nÚltimas 10 células:\n";
    //     size_t start = escapers.size() > 10 ? escapers.size() - 10 : 0;
    //     for (size_t i = start; i < escapers.size(); i++) {
    //         const auto& cell = escapers[i];
    //         std::cout << "  [" << i << "] ID=" << cell.getId() 
    //                   << " Pos=(" << cell.getPositionX() 
    //                   << "," << cell.getPositionY() << ")\n";
    //     }
    // }

    // std::cout << "Bloco chasers\n";
    // if (!chasers.empty()) {
    //     std::cout << "\nPrimeiras 10 células:\n";
    //     for (size_t i = 0; i < std::min(chasers.size(), size_t(10)); i++) {
    //         const auto& cell = chasers[i];
    //         std::cout << "  [" << i << "] ID=" << cell.getId() 
    //                   << " Pos=(" << cell.getPositionX() 
    //                   << "," << cell.getPositionY() << ")\n";
    //     }
        
    //     std::cout << "\nÚltimas 10 células:\n";
    //     size_t start = chasers.size() > 10 ? chasers.size() - 10 : 0;
    //     for (size_t i = start; i < chasers.size(); i++) {
    //         const auto& cell = chasers[i];
    //         std::cout << "  [" << i << "] ID=" << cell.getId() 
    //                   << " Pos=(" << cell.getPositionX() 
    //                   << "," << cell.getPositionY() << ")\n";
    //     }
    // }
    
        // Chamar a verificação
    // Verificar dados
    if (!lattice.checkDuplicates(chasers, escapers, WIDTH, HEIGHT)) {
        std::cerr << "\nERRO CRÍTICO: Dados inválidos. Abortando execução.\n";
        return 1;  // ou exit(1);
    }

    lattice.placeObjects(chasers,escapers);

    // Verificar
    if (lattice.verifyPlacement(chasers, escapers)) {
        // Continua com a simulação
        std::cout << "Placement OK. Starting simulation...\n";
    } else {
        // Trata o erro
        std::cerr << "Cannot proceed with simulation due to placement error.\n";
        return 1;
    }
    
    //lattice.printGrid();
    
    //Aqui vamos criar o objeto da simulação
    //     unsigned int runSeed = 1801929750 + run;
    //     std::mt19937 rng(runSeed);
        
    //     // Create simulation instance for this thread
    //     Simulation sim(lattice,runSeed, path_out,base_directory_name, base_name);
    //     logInfo("Processing run " + std::to_string(run));
        
    //     // Execute simulation run and collect results
    //     SimulationResult result = sim.runSingle(run, rng);

        unsigned int runSeed = 12345;
    std::string path_out = "/home/camafeu/Documentos/rossatto/github/Chase-escape_with_temporary_obstacles/data/data_environment/data_raw";
    std::string directory_name = "simulation_frac_25_run_1";
    std::string base_name = "results";
    
    // Criar simulação
    Simulation sim(lattice, runSeed, path_out, directory_name, base_name);
    
    // Para salvar um arquivo
    //std::string chaserFile = sim.getOutputFilePath("chasers.csv");
    //std::cout << "Arquivo de saída: " << chaserFile << std::endl;
    // Isso irá gerar: output/simulation_frac_25_run_1/results_chasers.csv
    
    return 0;
}
