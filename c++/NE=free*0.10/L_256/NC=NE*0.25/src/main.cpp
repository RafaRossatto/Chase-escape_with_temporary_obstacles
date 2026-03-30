#include <iostream>
#include <map>
#include "cell_lattice.h"
#include "cell.h"
#include "simulation.h"

int main() {

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
std::cout << "\n=== VERIFICANDO SINCRONIZAÇÃO ===\n";

// Pegar uma posição aleatória do vetor de escapers
if (!escapers.empty()) {
    int randomIndex = rand() % escapers.size();
    int x = escapers[randomIndex].getPositionX();
    int y = escapers[randomIndex].getPositionY();
    std::string gridVal = lattice.getGridValue(x, y);
    
    std::cout << "Escaper aleatório (ID=" << escapers[randomIndex].getId() 
              << "): Posição no vetor = (" << x << "," << y << ")\n";
    std::cout << "Valor no grid na mesma posição: '" << gridVal << "'\n";
    
    if (gridVal == "O") {
        std::cout << "✅ Sincronizado! Grid tem 'O' na posição correta.\n";
    } else {
        std::cout << "❌ DESSINCRONIZADO! Grid tem '" << gridVal << "' deveria ter 'O'\n";
    }
}

// Pegar uma posição aleatória do vetor de chasers
if (!chasers.empty()) {
    int randomIndex = rand() % chasers.size();
    int x = chasers[randomIndex].getPositionX();
    int y = chasers[randomIndex].getPositionY();
    std::string gridVal = lattice.getGridValue(x, y);
    
    std::cout << "\nChaser aleatório (ID=" << chasers[randomIndex].getId() 
              << "): Posição no vetor = (" << x << "," << y << ")\n";
    std::cout << "Valor no grid na mesma posição: '" << gridVal << "'\n";
    
    if (gridVal == "N") {
        std::cout << "✅ Sincronizado! Grid tem 'N' na posição correta.\n";
    } else {
        std::cout << "❌ DESSINCRONIZADO! Grid tem '" << gridVal << "' deveria ter 'N'\n";
    }
}

// Verificar algumas posições aleatórias do grid
std::cout << "\n=== VERIFICANDO POSIÇÕES ALEATÓRIAS DO GRID ===\n";
for (int i = 0; i < 10; i++) {
    int randX = rand() % lattice.getWidth();
    int randY = rand() % lattice.getHeight();
    std::string gridVal = lattice.getGridValue(randX, randY);
    
    if (gridVal == "O") {
        // Procurar se tem um escaper com essa posição
        bool found = false;
        for (const auto& escaper : escapers) {
            if (escaper.getPositionX() == randX && escaper.getPositionY() == randY) {
                std::cout << "Grid tem 'O' em (" << randX << "," << randY 
                          << ") -> Escaper ID=" << escaper.getId() << " encontrado no vetor\n";
                found = true;
                break;
            }
        }
        if (!found) {
            std::cout << "❌ Grid tem 'O' em (" << randX << "," << randY 
                      << ") mas NÃO tem escaper no vetor!\n";
        }
    }
    
    if (gridVal == "N") {
        // Procurar se tem um chaser com essa posição
        bool found = false;
        for (const auto& chaser : chasers) {
            if (chaser.getPositionX() == randX && chaser.getPositionY() == randY) {
                std::cout << "Grid tem 'N' em (" << randX << "," << randY 
                          << ") -> Chaser ID=" << chaser.getId() << " encontrado no vetor\n";
                found = true;
                break;
            }
        }
        if (!found) {
            std::cout << "❌ Grid tem 'N' em (" << randX << "," << randY 
                      << ") mas NÃO tem chaser no vetor!\n";
        }
    }
}

std::cin.get();






std::cout << "\n=== VERIFICAÇÃO FINAL ANTES DA SIMULAÇÃO ===\n";

// Verificar se os vetores e o grid estão sincronizados
int syncErrors = 0;

// 1. Verificar escapers
for (const auto& escaper : escapers) {
    int x = escaper.getPositionX();
    int y = escaper.getPositionY();
    std::string gridVal = lattice.getGridValue(x, y);
    if (gridVal != "O") {
        std::cout << "ERRO: Escaper ID=" << escaper.getId() 
                  << " em (" << x << "," << y << ") - Grid tem '" << gridVal << "'\n";
        syncErrors++;
    }
}

// 2. Verificar chasers
for (const auto& chaser : chasers) {
    int x = chaser.getPositionX();
    int y = chaser.getPositionY();
    std::string gridVal = lattice.getGridValue(x, y);
    if (gridVal != "N") {
        std::cout << "ERRO: Chaser ID=" << chaser.getId() 
                  << " em (" << x << "," << y << ") - Grid tem '" << gridVal << "'\n";
        syncErrors++;
    }
}

if (syncErrors == 0) {
    std::cout << "✅ Tudo sincronizado! " << escapers.size() << " escapers e " 
              << chasers.size() << " chasers no grid.\n";
} else {
    std::cout << "❌ " << syncErrors << " erros de sincronização encontrados!\n";
}
std::cin.get();












    // // Verificar
    // if (lattice.verifyPlacement(chasers, escapers)) {
    //     // Continua com a simulação
    //     std::cout << "Placement OK. Starting simulation...\n";
    // } else {
    //     // Trata o erro
    //     std::cerr << "Cannot proceed with simulation due to placement error.\n";
    //     return 1;
    // }
    

    
    unsigned int runSeed = 12348;
    std::string path_out = "/home/camafeu/Documentos/rossatto/github/Chase-escape_with_temporary_obstacles/data/data_raw";
    std::string directory_name = "simulation_frac_25_run_2";
    std::string base_name = "results";
    
    // // Criar simulação
    Simulation sim(lattice,chasers,escapers, runSeed, path_out, directory_name, base_name);

   
    // std::cout << "\nArquivos criados em: " << sim.getOutputPath() << std::endl;
    // std::cout << "  - results_chasers.csv" << std::endl;
    // std::cout << "  - results_escapers.csv" << std::endl;
    // std::cout << "  - results_seed.txt" << std::endl;
    sim.runSingle(1);

   
    return 0;
}
