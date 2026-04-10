#include <iostream>
#include <map>
#include <vector>
#include <random>
#include <sstream>
#include <iomanip>
#include <omp.h>
#include "cell_lattice.h"
#include "cell.h"
#include "simulation.h"
#include "globals.hpp"

double TRAIL_PROBABILITY = 0.5;
int SR_C_VALUES = 2;
int SR_E_VALUES = 2;

int main(int argc, char* argv[]) {
    // Valores padrão
    double TRAIL_PROBABILITY = 0.5;
    int SR_C_VALUE = 2;
    int SR_E_VALUE = 2;
    
    // Parse dos argumentos
    // Exemplo de uso: ./programa 0.5 2 4
    if (argc > 1) {
        TRAIL_PROBABILITY = std::stod(argv[1]);
    }
    if (argc > 2) {
        SR_C_VALUE = std::stoi(argv[2]);
    }
    if (argc > 3) {
        SR_E_VALUE = std::stoi(argv[3]);
    }
    
    std::cout << "Usando TRAIL_PROBABILITY = " << TRAIL_PROBABILITY << std::endl;
    std::cout << "Usando SR_C_VALUE = " << SR_C_VALUE << std::endl;
    std::cout << "Usando SR_E_VALUE = " << SR_E_VALUE << std::endl;
    
    const int SIZE = 256;
    const int WIDTH = SIZE;
    const int HEIGHT = SIZE;
    
    std::random_device rd;
    
    // Parâmetros
    std::vector<int> frac_values = {25, 50, 100};
    int start_run = 1;
    int end_run = 100;

// Loop sobre os valores de frac
for (int frac : frac_values) {
    std::cout << "\n\n";
    std::cout << "########################################";
    std::cout << "\n### INICIANDO SIMULAÇÕES PARA FRAC = " << frac << " ###";
    std::cout << "\n########################################\n";
    
#pragma omp parallel for
for (int run = start_run; run <= end_run; run++) {
    // Cada thread executa uma run completa
    // Todos os objetos são locais à thread
    
    std::cout << "\n========================================";
    std::cout << "\n=== PROCESSANDO FRAC=" << frac << " | RUN " << run << " DE " << end_run << " ===";
    std::cout << "\n========================================\n";
    
    // Criar o grid para cada run (cada thread tem o seu)
    CellLattice lattice(WIDTH, HEIGHT);
    
    // Construir caminhos dos arquivos
    std::ostringstream oss_escaper;
    oss_escaper << "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_environment/simulation_frac_" 
                << frac << "_run_" << run << "/escapers.csv";
    std::string escaper_file = oss_escaper.str();
    
    std::ostringstream oss_chaser;
    oss_chaser << "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_environment/simulation_frac_" 
               << frac << "_run_" << run << "/chasers.csv";
    std::string chaser_file = oss_chaser.str();
    
    // ⚠️ Proteger cout para não misturar saídas
    #pragma omp critical
    {
        std::cout << "Thread " << omp_get_thread_num() << " - Run " << run << "\n";
        std::cout << "  Escapers: " << escaper_file << "\n";
        std::cout << "  Chasers: " << chaser_file << "\n";
    }
    
    // Carregar células
    std::vector<Cell> escapers = Cell::loadFromCSV(escaper_file, "O", SR_E_VALUE);
    std::vector<Cell> chasers = Cell::loadFromCSV(chaser_file, "N", SR_C_VALUE);
    
    // Verificar se carregou células (sem cout protegido é ok, mas pode misturar)
    if (escapers.empty() && chasers.empty()) {
        #pragma omp critical
        {
            std::cerr << "ERRO: Nenhuma célula carregada para frac=" << frac << " run=" << run << ". Pulando...\n";
        }
        continue;
    }
    
    // Verificar dados
    if (!lattice.checkDuplicates(chasers, escapers, WIDTH, HEIGHT)) {
        #pragma omp critical
        {
            std::cerr << "\nERRO CRÍTICO: Dados inválidos para frac=" << frac << " run=" << run << ". Pulando...\n";
        }
        continue;
    }
    
    // Colocar objetos no grid
    lattice.placeObjects(chasers, escapers);
    
    // Semente para o run (thread-safe)
    //unsigned int runSeed = rd() + run;
    //unsigned int runSeed = static_cast<unsigned int>(rd()) + static_cast<unsigned int>(run);
    unsigned int runSeed = (static_cast<unsigned int>(rd()) + static_cast<unsigned int>(run)) % 2147483647;
    
    // Diretório de saída
    std::string path_out = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_raw";
    
    std::ostringstream oss_dir;
    oss_dir << "simulation_frac_" << frac 
            << "_run_" << run 
            << "_obsprob_" << std::fixed << std::setprecision(2) << TRAIL_PROBABILITY
            << "_SRC_" << SR_C_VALUE
            << "_SRE_" << SR_E_VALUE;
    std::string directory_name = oss_dir.str();
    std::string base_name = "results";
    
    // Criar simulação (cada thread tem a sua)
    Simulation sim(lattice, chasers, escapers, runSeed, path_out, directory_name, base_name);
    
    // Executar simulação
    #pragma omp critical
    {
        std::cout << "Executando simulação para run " << run << "...\n";
    }
    
    sim.runSingle(run);  // Os buffers internos são locais à thread
    
    #pragma omp critical
    {
        std::cout << "Run " << run << " concluído!\n";
    }
}
}

std::cout << "\n========================================";
std::cout << "\n=== TODOS OS RUNS CONCLUÍDOS PARA TODOS OS FRACS ===";
std::cout << "\n========================================\n";

return 0;
}