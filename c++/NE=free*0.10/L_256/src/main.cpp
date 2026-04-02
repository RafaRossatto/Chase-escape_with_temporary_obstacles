#include <iostream>
#include <map>
#include <vector>
#include <random>
#include <sstream>
#include <iomanip>
#include "cell_lattice.h"
#include "cell.h"
#include "simulation.h"
#include "globals.hpp"

double TRAIL_PROBABILITY = 0.5;

int main(int argc, char* argv[]) {
    // Valor padrão
    TRAIL_PROBABILITY = 0.5;
    
    // Se passar argumento, usa ele
    if (argc > 1) {
        TRAIL_PROBABILITY = std::stod(argv[1]);
    }
    
    std::cout << "Usando TRAIL_PROBABILITY = " << TRAIL_PROBABILITY << std::endl;
    
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
    
    // Loop sobre os runs
    for (int run = start_run; run <= end_run; run++) {
        std::cout << "\n========================================";
        std::cout << "\n=== PROCESSANDO FRAC=" << frac << " | RUN " << run << " DE " << end_run << " ===";
        std::cout << "\n========================================\n";
        
        // Criar o grid para cada run
        CellLattice lattice(WIDTH, HEIGHT);
        
        // Construir caminhos dos arquivos
        std::ostringstream oss_escaper;
        oss_escaper << "/home/camafeu/Documentos/rossatto/github/Chase-escape_with_temporary_obstacles/data/data_environment/simulation_frac_" 
                    << frac << "_run_" << run << "/escapers.csv";
        std::string escaper_file = oss_escaper.str();
        
        std::ostringstream oss_chaser;
        oss_chaser << "/home/camafeu/Documentos/rossatto/github/Chase-escape_with_temporary_obstacles/data/data_environment/simulation_frac_" 
                   << frac << "_run_" << run << "/chasers.csv";
        std::string chaser_file = oss_chaser.str();
        
        std::cout << "Carregando arquivos:\n";
        std::cout << "  Escapers: " << escaper_file << "\n";
        std::cout << "  Chasers: " << chaser_file << "\n";
        
        // Carregar células
        std::vector<Cell> escapers = Cell::loadFromCSV(escaper_file, "O", 2);
        std::vector<Cell> chasers = Cell::loadFromCSV(chaser_file, "N", 2);
        
        std::cout << "Total: " << escapers.size() << " escapers\n";
        std::cout << "Total: " << chasers.size() << " chasers\n";
        
        // Verificar se carregou células
        if (escapers.empty() && chasers.empty()) {
            std::cerr << "ERRO: Nenhuma célula carregada para frac=" << frac << " run=" << run << ". Pulando...\n";
            continue;
        }
        
        // Verificar dados
        if (!lattice.checkDuplicates(chasers, escapers, WIDTH, HEIGHT)) {
            std::cerr << "\nERRO CRÍTICO: Dados inválidos para frac=" << frac << " run=" << run << ". Pulando...\n";
            continue;
        }
        
        // Colocar objetos no grid
        lattice.placeObjects(chasers, escapers);
        
        // Verificação de sincronização
        std::cout << "\n=== VERIFICANDO SINCRONIZAÇÃO ===\n";
        
        int syncErrors = 0;
        
        // Verificar escapers
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
        
        // Verificar chasers
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
            std::cin.get();
        }
        
        // Semente para o run
        //unsigned int runSeed = 1801929750 + run;
        unsigned int runSeed = rd() + run;
        
        // Diretório de saída
        std::string path_out = "/home/camafeu/Documentos/rossatto/github/Chase-escape_with_temporary_obstacles/data/data_raw";
        
        // Nome do diretório
        std::ostringstream oss_dir;

        oss_dir << "simulation_frac_" << frac << "_run_" << run 
                << "_obsprob_" << std::fixed << std::setprecision(2) << TRAIL_PROBABILITY;
        std::string directory_name = oss_dir.str();
        std::string base_name = "results";
        
        // Criar simulação
        Simulation sim(lattice, chasers, escapers, runSeed, path_out, directory_name, base_name);
        
        // Executar simulação
        std::cout << "\nExecutando simulação para run " << run << "...\n";
        sim.runSingle(run);
        
        std::cout << "Run " << run << " concluído!\n";
    }
}

std::cout << "\n========================================";
std::cout << "\n=== TODOS OS RUNS CONCLUÍDOS PARA TODOS OS FRACS ===";
std::cout << "\n========================================\n";

return 0;
}