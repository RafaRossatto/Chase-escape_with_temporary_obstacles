#include "simulation.h"
#include "utils.h"
#include <iomanip>
#include <fstream>
#include "temp_obs.h"
#include "cell_lattice.h"
#include <filesystem>
#include "globals.hpp"

namespace fs = std::filesystem;

Simulation::Simulation(CellLattice& lattice, 
                       std::vector<Cell>& chasers,
                       std::vector<Cell>& escapers,
                       unsigned int seed,
                       const std::string& path_out, 
                       const std::string& directory_name,
                       const std::string& base_name)
    : m_lattice(lattice),
      m_chasers(chasers),
      m_escapers(escapers),
      m_seed(seed),
      m_pathOut(path_out),
      m_directoryName(directory_name),
      m_baseName(base_name)

{
    // Construct complete output path by joining base path and subdirectory
    m_outputPath = fs::path(path_out) / directory_name;
    
    // Create output directory if it doesn't exist
    if (!fs::exists(m_outputPath)) {
        if (fs::create_directories(m_outputPath)) {
            std::cout << "[INFO] Output directory created: " << m_outputPath << std::endl;
        } else {
            std::cerr << "[ERROR] Failed to create output directory: " 
                      << m_outputPath << std::endl;
        }
    } else {
        std::cout << "[INFO] Using existing output directory: " << m_outputPath << std::endl;
    }
}

void Simulation::createEmptyOutputFiles()
{
    // Create chaser positions file with header
    std::string chaserFile = getFilePath("chasers.csv");
    std::ofstream chaserOut(chaserFile);
    if (chaserOut.is_open()) {
        chaserOut << "x,y,id\n";
        chaserOut.close();
        std::cout << "[INFO] Created chaser output file: " << chaserFile << std::endl;
    } else {
        std::cerr << "[ERROR] Failed to create chaser output file: " << chaserFile << std::endl;
    }
    
    // Create escaper positions file with header
    std::string escaperFile = getFilePath("escapers.csv");
    std::ofstream escaperOut(escaperFile);
    if (escaperOut.is_open()) {
        escaperOut << "x,y,id\n";
        escaperOut.close();
        std::cout << "[INFO] Created escaper output file: " << escaperFile << std::endl;
    } else {
        std::cerr << "[ERROR] Failed to create escaper output file: " << escaperFile << std::endl;
    }
    
    // Create seed file with simulation metadata
    std::string seedFile = getFilePath("seed.txt");
    std::ofstream seedOut(seedFile);
    if (seedOut.is_open()) {
        seedOut << "Seed: " << static_cast<unsigned int>(m_seed) << "\n";
        // Ou use:
        // seedOut << "Seed: " << (unsigned int)m_seed << "\n";
        seedOut.close();
        std::cout << "[INFO] Created seed file: " << seedFile << std::endl;
    } else {
        std::cerr << "[ERROR] Failed to create seed file: " << seedFile << std::endl;
    }
}

std::string Simulation::getFilePath(const std::string& filename) const
{
    return m_outputPath + "/" + m_baseName + "_" + filename;
}

void Simulation::runSingle(int run) 
{
    const int gridSize = m_lattice.getWidth();
    
    // Gerador de números aleatórios
    std::mt19937 rng(m_seed);
    std::uniform_int_distribution<int> distPos(0, gridSize - 1);
    
    // Probabilidade para criação de rastro
    // const double TRAIL_PROBABILITY = 0.5;
    std::uniform_real_distribution<double> probDist(0.0, 1.0);
    
    // Criar arquivos de saída
    std::string chaserFile = getFilePath("chasers_run" + std::to_string(run) + ".csv");
    std::string escaperFile = getFilePath("escapers_run" + std::to_string(run) + ".csv");
    std::string tempObstaclesFile = getFilePath("tempObs_run" + std::to_string(run) + ".csv");
    std::string nescepers = getFilePath("N_escapers_run" + std::to_string(run) + ".csv");
    std::string seedFile = getFilePath("seed_run" + std::to_string(run) + ".txt");
    
    std::ofstream chaserOut(chaserFile);
    std::ofstream escaperOut(escaperFile);
    std::ofstream tempObsOut(tempObstaclesFile);
    std::ofstream nescepersOut(nescepers);  
    std::ofstream seedOut(seedFile);
    
    if (!chaserOut.is_open() || !escaperOut.is_open() || !tempObsOut.is_open() || !seedOut.is_open()) {
        std::cerr << "[ERROR] Failed to create output files!" << std::endl;
        return;
    }
    
    // Escrever cabeçalhos
    chaserOut << "time,x,y,id\n";
    escaperOut << "time,x,y,id\n";
    tempObsOut << "time,x,y,id\n";
    nescepersOut << "time,NE\n";
    
    // Salvar seed
    seedOut << "Simulation Seed: " << m_seed << "\n";
    //seedOut << "Total Steps: " << m_totalSteps << "\n";
    seedOut << "Grid Size: " << gridSize << "x" << gridSize << "\n";
    seedOut << "Initial Chasers: " << m_chasers.size() << "\n";
    seedOut << "Initial Escapers: " << m_escapers.size() << "\n";
    
    double currentTime = 0.0;
    const double timeStep = 1.0;
    
    // Buffer para escrita
    std::vector<std::string> chaserBuffer;
    std::vector<std::string> escaperBuffer;
    std::vector<std::string> tempObsBuffer;
    chaserBuffer.reserve(10000);
    escaperBuffer.reserve(10000);
    tempObsBuffer.reserve(10000);
      
    int m_totalSteps = 1e6;

    std::cout << "\n=== Starting Simulation - Run " << run << " ===" << std::endl;
    std::cout << "Total steps: " << m_totalSteps << std::endl;
    std::cout << "Initial chasers: " << m_chasers.size() << std::endl;
    std::cout << "Initial escapers: " << m_escapers.size() << std::endl;
    std::cout << "Progress: " << std::flush;

    int randomX, randomY;
    std::string cellType;
  
    // Loop principal
    for (int step = 0; step < m_totalSteps; ++step) {
        // ESCOLHER POSIÇÃO ALEATÓRIA
      do {
          randomX = distPos(rng);
          randomY = distPos(rng);
          cellType = m_lattice.getGridValue(randomX, randomY);
      } while (cellType != "N" && cellType != "O");
        
        // SE FOR CHASER (N)
        if (cellType == "N") {
            // Encontrar o chaser na posição
            for (auto& chaser : m_chasers) {
                if (chaser.getPositionX() == randomX && chaser.getPositionY() == randomY) {
                                m_lattice.moveNormalCell(chaser, 
                                     m_chasers,      // normalCells
                                     m_escapers,     // cancerCells
                                     rng, 
                                     true,          // checkCancer
                                     m_tempObstacles);
                    break;
                }
            }
        }
        // SE FOR ESCAPER (O)
        else if (cellType == "O") {
            // Encontrar o escaper na posição
            for (auto& escaper : m_escapers) {
                if (escaper.getPositionX() == randomX && escaper.getPositionY() == randomY) {
                    m_lattice.moveCancerCell                    (escaper, 
                                     m_chasers,      // normalCells
                                     m_escapers,     // cancerCells
                                     rng, 
                                     false,          // checkCancer
                                     m_tempObstacles);
                    break;
                }
            }
        }
        // OUTROS TIPOS (L, T, B) - não faz nada
               
        // EXPORTAR DADOS (a cada N passos)
        //const int EXPORT_INTERVAL = 500;

            // Exportar N_E (leve, alta resolução)
      if (step % N_ESCAPER_EXPORT_INTERVAL == 0) {
          nescepersOut << step << ","
                << m_escapers.size() << "\n"
          nescepersOut.flush();  // opcional: garante que os dados sejam escritos
      }
    

      
        if (step % EXPORT_INTERVAL == 0 || step == m_totalSteps - 1) {
            // Exportar chasers
            for (const auto& chaser : m_chasers) {
                chaserBuffer.push_back(std::to_string(step) + "," + 
                                       std::to_string(chaser.getPositionX()) + "," + 
                                       std::to_string(chaser.getPositionY()) + "," + 
                                       std::to_string(chaser.getId()) + "\n");
            }
            
            // Exportar escapers
            for (const auto& escaper : m_escapers) {
                escaperBuffer.push_back(std::to_string(step) + "," + 
                                        std::to_string(escaper.getPositionX()) + "," + 
                                        std::to_string(escaper.getPositionY()) + "," + 
                                        std::to_string(escaper.getId()) + "\n");
            }
            
            // Exportar obstáculos temporários
            for (const auto& t_obs : m_tempObstacles) {
                tempObsBuffer.push_back(std::to_string(step) + "," + 
                                        std::to_string(t_obs.getPositionX()) + "," + 
                                        std::to_string(t_obs.getPositionY()) + "," + 
                                        std::to_string(t_obs.getId()) + "\n");
            }
            
            // Escrever buffers em lote
            if (chaserBuffer.size() >= 5000) {
                for (const auto& line : chaserBuffer) chaserOut << line;
                for (const auto& line : escaperBuffer) escaperOut << line;
                for (const auto& line : tempObsBuffer) tempObsOut << line;
                
                chaserBuffer.clear();
                escaperBuffer.clear();
                tempObsBuffer.clear();
            }
        }
    }


    // Escrever dados restantes
    for (const auto& line : chaserBuffer) chaserOut << line;
    for (const auto& line : escaperBuffer) escaperOut << line;
    for (const auto& line : tempObsBuffer) tempObsOut << line;
    
    // Fechar arquivos
    nescepersOut.close();
    chaserOut.close();
    escaperOut.close();
    tempObsOut.close();
    seedOut.close();

    int initialEscapers = 6553; // ou use uma variável guardada no início
    int captured = initialEscapers - m_escapers.size();
    std::cout << "Final chasers: " << m_chasers.size() << std::endl;
    std::cout << "Captured escapers: " << captured << std::endl;
    std::cout << "Final temp obstacles: " << m_tempObstacles.size() << std::endl;
    std::cout << "================================" << std::endl;
    // std:: cin.get();
}
