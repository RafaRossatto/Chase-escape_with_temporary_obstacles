#include "simulation.h"
#include "utils.h"
#include <iomanip>
#include <fstream>
#include "temp_obs.h"
#include "cell_lattice.h"
#include <filesystem>

// /**
//  * @brief Constructs a new Simulation object
//  */
// Simulation::Simulation(CellLattice& lattice, unsigned int seed)
// : m_lattice(lattice), m_seed(seed)
// {
//     m_fileName = generateFileName(m_numHunters, m_numPrey, m_numObstacles, 
//                                  m_preyNoise, m_hunterNoise, 
//                                  m_hunterSearchRadius, m_preySearchRadius);
    
//     clearTrajectoryData();
// }



namespace fs = std::filesystem;

// Simulation.cpp
Simulation::Simulation(CellLattice& lattice, unsigned int seed,
                       const std::string& path_out, const std::string& directory_name,
                       const std::string& base_name)
    : m_lattice(lattice), m_seed(seed), m_baseName(base_name)
{
    // Constrói o caminho completo
    m_outputPath = fs::path(path_out) / directory_name;
    
    // Cria o diretório se não existir
    if (!fs::exists(m_outputPath)) {
        if (fs::create_directories(m_outputPath)) {
            std::cout << "Diretório criado: " << m_outputPath << std::endl;
        } else {
            std::cerr << "Erro ao criar diretório: " << m_outputPath << std::endl;
        }
    }
    
    // CRIA OS ARQUIVOS VAZIOS OU COM CABEÇALHO
    createEmptyOutputFiles();
    
    clearTrajectoryData();
}

void Simulation::createEmptyOutputFiles()
{
    // Cria arquivo de chasers com cabeçalho
    std::string chaserFile = getFilePath("chasers.csv");
    std::ofstream chaserOut(chaserFile);
    if (chaserOut.is_open()) {
        chaserOut << "x,y,id\n";
        chaserOut.close();
        std::cout << "Arquivo criado: " << chaserFile << std::endl;
    }
    
    // Cria arquivo de escapers com cabeçalho
    std::string escaperFile = getFilePath("escapers.csv");
    std::ofstream escaperOut(escaperFile);
    if (escaperOut.is_open()) {
        escaperOut << "x,y,id\n";
        escaperOut.close();
        std::cout << "Arquivo criado: " << escaperFile << std::endl;
    }
    
    // Cria arquivo de seed
    std::string seedFile = getFilePath("seed.txt");
    std::ofstream seedOut(seedFile);
    if (seedOut.is_open()) {
        seedOut << "Seed: " << m_seed << "\n";
        seedOut.close();
        std::cout << "Arquivo criado: " << seedFile << std::endl;
    }
}


std::string Simulation::getFilePath(const std::string& filename) const
{
    return m_outputPath + "/" + m_baseName + "_" + filename;
}

void Simulation::saveChasersPositions()
{
    std::string filepath = getFilePath("chasers.csv");
    std::ofstream file(filepath);
    
    if (!file.is_open()) {
        std::cerr << "Erro ao criar arquivo: " << filepath << std::endl;
        return;
    }
    
    // Escreve cabeçalho
    file << "x,y,id\n";
    
    // Escreve dados dos chasers
    for (const auto& chaser : m_chasers) {
        file << chaser.getPositionX() << ","
             << chaser.getPositionY() << ","
             << chaser.getId() << "\n";
    }
    
    file.close();
    std::cout << "Chasers saved to: " << filepath << std::endl;
}

void Simulation::saveEscapersPositions()
{
    std::string filepath = getFilePath("escapers.csv");
    std::ofstream file(filepath);
    
    if (!file.is_open()) {
        std::cerr << "Erro ao criar arquivo: " << filepath << std::endl;
        return;
    }
    
    // Escreve cabeçalho
    file << "x,y,id\n";
    
    // Escreve dados dos escapers
    for (const auto& escaper : m_escapers) {
        file << escaper.getPositionX() << ","
             << escaper.getPositionY() << ","
             << escaper.getId() << "\n";
    }
    
    file.close();
    std::cout << "Escapers saved to: " << filepath << std::endl;
}

void Simulation::saveSeed()
{
    std::string filepath = getFilePath("seed.txt");
    std::ofstream file(filepath);
    
    if (!file.is_open()) {
        std::cerr << "Erro ao criar arquivo: " << filepath << std::endl;
        return;
    }
    
    file << "Seed: " << m_seed << "\n";
    file << "Timestamp: " << time(nullptr) << "\n";
    
    file.close();
    std::cout << "Seed saved to: " << filepath << std::endl;
}

void Simulation::saveSimulationData()
{
    saveChasersPositions();
    saveEscapersPositions();
    saveSeed();
    std::cout << "All simulation data saved to: " << m_outputPath << std::endl;
}























/**
 * @brief Saves current positions to trajectory data
 */
void Simulation::saveCurrentPositions(double time, const std::vector<Cell>& prey, 
    const std::vector<Cell>& hunters, const std::vector<temp_obs>& t_obs) 
{
    // Save timestep
    m_trajectoryData.timesteps.push_back(time);
    
    // Save prey positions
    std::vector<std::pair<int, int>> currentPreyPositions;
    for (const auto& p : prey) {
        currentPreyPositions.emplace_back(p.getPositionX(), p.getPositionY());
    }
    m_trajectoryData.preyPositions.push_back(currentPreyPositions);
    
    // Save hunter positions
    std::vector<std::pair<int, int>> currentHunterPositions;
    for (const auto& h : hunters) {
        currentHunterPositions.emplace_back(h.getPositionX(), h.getPositionY());
    }
    m_trajectoryData.hunterPositions.push_back(currentHunterPositions);

    // Save temporary_obstacles positions
    std::vector<std::pair<int, int>> current_temp_obs_Positions;
    for (const auto& temp : t_obs) {
        current_temp_obs_Positions.emplace_back(temp.getPositionX(), temp.getPositionY());
    }
    m_trajectoryData.temp_obst_Positions.push_back(current_temp_obs_Positions);
}

/**
 * @brief Saves trajectory data to TrajPy format files
 */
void Simulation::saveTrajectoryData(int run) const 
{
    // Save prey trajectories
    std::ofstream preyFile(m_fileName + "_run_" + std::to_string(run) + "_prey_trajectories.csv");
    if (preyFile.is_open()) {
        preyFile << "timestep,cell_id,x,y\n";
        for (size_t t = 0; t < m_trajectoryData.timesteps.size(); ++t) {
            for (size_t c = 0; c < m_trajectoryData.preyPositions[t].size(); ++c) {
                preyFile << m_trajectoryData.timesteps[t] << ","
                         << c << ","
                         << m_trajectoryData.preyPositions[t][c].first << ","
                         << m_trajectoryData.preyPositions[t][c].second << "\n";
            }
        }
        preyFile.close();
    }
    
    // Save hunter trajectories
    std::ofstream hunterFile(m_fileName + "_run_" + std::to_string(run) + "_hunter_trajectories.csv");
    if (hunterFile.is_open()) {
        hunterFile << "timestep,cell_id,x,y\n";
        for (size_t t = 0; t < m_trajectoryData.timesteps.size(); ++t) {
            for (size_t c = 0; c < m_trajectoryData.hunterPositions[t].size(); ++c) {
                hunterFile << m_trajectoryData.timesteps[t] << ","
                           << c << ","
                           << m_trajectoryData.hunterPositions[t][c].first << ","
                           << m_trajectoryData.hunterPositions[t][c].second << "\n";
            }
        }
        hunterFile.close();
    }

        // Save temporary obstacels positoins corrigir aqui
    std::ofstream temp_obs_File(m_fileName + "_run_" + std::to_string(run) + "_temp_obs_trajectories.csv");
     if (temp_obs_File.is_open()) {
         temp_obs_File << "timestep,cell_id,x,y\n";
         for (size_t t = 0; t < m_trajectoryData.timesteps.size(); ++t) {
             for (size_t c = 0; c < m_trajectoryData.temp_obst_Positions[t].size(); ++c) {
                 temp_obs_File << m_trajectoryData.timesteps[t] << ","
                            << c << ","
                            << m_trajectoryData.temp_obst_Positions[t][c].first << ","
                            << m_trajectoryData.temp_obst_Positions[t][c].second << "\n";
             }
         }
         temp_obs_File.close();
     }
}

/**
 * @brief Runs a single simulation run
 */
// SimulationResult Simulation::runSingle(int run, std::mt19937& rng) 
// {
//     // Clear previous trajectory data
//     clearTrajectoryData();
    
//     const int gridSize = m_lattice.getWidth();

//     std::vector<Cell> localHunters, localPrey;
       
//     std::uniform_int_distribution<int> distX(0, gridSize - 1);
//     std::uniform_int_distribution<int> distY(0, gridSize - 1);

//     double time = 0.0;
//     const double recordingInterval = 1.0;
//     double nextRecordingTime = recordingInterval;
//     bool checkPrey;


//     std::vector<temp_obs> tempObstacles; // creating the vector to the temp_obstacles
//     int value = 10; // Max life for a temp_obs

//     saveCurrentPositions(time, localPrey, localHunters, tempObstacles);

//     // Evolution file for prey count
//     std::ofstream evolutionFile(m_fileName + "_run_" + std::to_string(run) + "_prey_per_step.csv");
//     if (!evolutionFile.is_open()) {
//         logError("Error creating evolution file for run " + std::to_string(run));
//         return {0.0, 0};
//     }

//     evolutionFile << "step,living_prey\n";
//     evolutionFile << time << "," << localPrey.size() << "\n";

//     std::ofstream captureFile(m_fileName + "_run_" + std::to_string(run) + "_captures.csv");
//     if (!captureFile.is_open()) 
//     {
//         logError("Error creating capture log file for run " + std::to_string(run));
//         return {0.0, 0};
//     }
//     captureFile << "timestep,hunter_id,prey_id\n";

//     // Main simulation loop
//     while (time < 1.0e5) {
//         // Stop condition: all prey are captured or inaccessible

//         //Here he will go through the entire vector, add a life unit, if the lige is greater than velue, the element is eresed
//         if (!tempObstacles.empty()) {
//             for (auto it = tempObstacles.begin(); it != tempObstacles.end(); ) {
//                 // Soma uma unidade ao life
//                 it->addLife();
                
//                 // Verifica se life > value
//                 if (it->getLife() > value) {
//                     // Apaga o elemento e atualiza o iterador
//                     it = tempObstacles.erase(it);
//                 } else {
//                     // Avança para o próximo elemento
//                     ++it;
//                 }
//             }
//         }


//         // Process gridSize*gridSize movements
//         for (int i = 0; i < gridSize * gridSize; ++i) {
//             int randomX = distX(rng);
//             int randomY = distY(rng);
//             std::string gridValue = m_lattice.getGridValue(randomX, randomY);
//             bool found = false;

//             // Try to move hunter cell
//             for (auto& cell : localHunters) 
//             {
//                 if (cell.getPositionX() == randomX && cell.getPositionY() == randomY) {
//                     checkPrey = false;
//                     int capturedPreyId = m_lattice.moveNormalCell(cell, localHunters, localPrey,
//                         localObstacles, rng, checkPrey,
//                         m_hunterSearchRadius,tempObstacles);

//                     if (capturedPreyId >= 0) 
//                     {
//                         int preyX = cell.getPositionX();  // posição do hunter após mover = posição da presa
//                         int preyY = cell.getPositionY();
//                         logCapture(captureFile, time, cell.getId(), capturedPreyId);
//                     }
//                     found = true;
//                     break;
//                 }
//             }

//             // If no hunter found, try to move prey cell
//             if (!found) {
//                 for (auto& cell : localPrey) {
//                     if (cell.getPositionX() == randomX && cell.getPositionY() == randomY) {
//                         checkPrey = true;
//                         m_lattice.moveCancerCell(cell, localHunters, localPrey, localObstacles, 
//                                                rng, checkPrey, m_preySearchRadius, tempObstacles);
//                         break;
//                     }
//                 }
//             }
//         }

//         // Record state at each interval
//         if (time >= nextRecordingTime) {
//             evolutionFile << time << "," << localPrey.size() << "\n";
//             //  Save positions at recording interval
//             saveCurrentPositions(time, localPrey, localHunters,tempObstacles);
//             nextRecordingTime += recordingInterval;
//         }

//         time += 1.0;
//     }

//     // Save final positions
//    // saveCurrentPositions(time, localPrey, localHunters);
    
//     evolutionFile.close();
    
//     // Save trajectory data to files
//     saveTrajectoryData(run);
//     captureFile.close();
    
//     return {time, static_cast<int>(localPrey.size())};
// }

// void Simulation::logCapture(std::ofstream& captureFile, double timestep,
//     int hunterId, int preyId) const
// {
// captureFile << timestep << ","
// << hunterId << ","
// << preyId <<"\n";
// }
