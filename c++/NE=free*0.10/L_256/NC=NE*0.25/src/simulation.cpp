#include "simulation.h"
#include "utils.h"
#include <iomanip>
#include <fstream>
#include "temp_obs.h"
#include "cell_lattice.h"
#include <filesystem>

namespace fs = std::filesystem;

/**
 * @brief Constructs a Simulation object and initializes output directory
 * 
 * Creates a new simulation instance with the specified grid, seed, and
 * output configuration. The constructor automatically creates the output
 * directory structure and initializes empty output files for recording
 * simulation results.
 * 
 * @param lattice Reference to the grid lattice where simulation will run
 * @param seed Random number generator seed for reproducibility
 * @param path_out Base output directory path
 * @param directory_name Subdirectory name for this specific simulation run
 * @param base_name Base filename prefix for all output files
 * 
 * @note The constructor creates the following directory structure:
 *       path_out/directory_name/
 *       ├── base_name_chasers.csv
 *       ├── base_name_escapers.csv
 *       └── base_name_seed.txt
 * 
 * @warning The function does not validate that the output directory is
 *          writable. Ensure proper permissions before calling.
 * 
 * @see ~Simulation()
 * @see createEmptyOutputFiles()
 * @see getOutputPath()
 * 
 * @example
 * @code
 * // Create simulation with output in "output/sim_1/"
 * Simulation sim(lattice, 12345, "output", "sim_1", "results");
 * // Creates:
 * // output/sim_1/results_chasers.csv
 * // output/sim_1/results_escapers.csv
 * // output/sim_1/results_seed.txt
 * @endcode
 */
// Simulation.cpp
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
    
    // Initialize empty output files with headers
    //createEmptyOutputFiles();
    
    // Reset trajectory data structures
    //clearTrajectoryData();
}


/**
 * @brief Creates empty output files with appropriate headers for simulation data
 * 
 * Initializes all output files that will be used during simulation execution.
 * Each file is created with a header row containing column definitions.
 * Files are created in the output directory specified during construction.
 * 
 * **Files Created:**
 * - `{base_name}_chasers.csv`: Records chaser (normal cell) positions
 *   - Columns: x, y, id
 * - `{base_name}_escapers.csv`: Records escaper (cancer cell) positions
 *   - Columns: x, y, id
 * - `{base_name}_seed.txt`: Stores simulation seed for reproducibility
 *   - Content: Seed: {seed_value}
 * 
 * @note This function is called automatically by the constructor.
 *       It does not need to be called manually in normal usage.
 * 
 * @warning If file creation fails, an error is printed to std::cerr but
 *          the function continues execution. Subsequent file operations
 *          may fail if the file wasn't created.
 * 
 * @see getFilePath()
 * @see saveChasersPositions()
 * @see saveEscapersPositions()
 * 
 * @example
 * @code
 * // Called automatically by constructor:
 * Simulation sim(lattice, 12345, "output", "run_1", "results");
 * // Creates:
 * // output/run_1/results_chasers.csv
 * // output/run_1/results_escapers.csv
 * // output/run_1/results_seed.txt
 * @endcode
 */

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
        seedOut << "Seed: " << m_seed << "\n";
        seedOut.close();
        std::cout << "[INFO] Created seed file: " << seedFile << std::endl;
    } else {
        std::cerr << "[ERROR] Failed to create seed file: " << seedFile << std::endl;
    }
}

/**
 * @brief Constructs the full file path for a simulation output file
 * 
 * Combines the output directory path, base filename prefix, and the specific
 * filename to create a complete filesystem path for simulation output files.
 * 
 * **Path Format:**
 * ```
 * {m_outputPath}/{m_baseName}_{filename}
 * ```
 * 
 * @param filename The specific filename (e.g., "chasers.csv", "seed.txt")
 * @return std::string Complete file path including directory and filename
 * 
 * @note This function does not validate whether the path is valid or
 *       whether the directory exists. It simply performs string concatenation.
 * 
 * @warning The returned path uses the operating system's path separator.
 *          On Unix-like systems it uses '/', on Windows it will use '\'
 *          if the path is constructed with backslashes.
 * 
 * @see createEmptyOutputFiles()
 * @see saveChasersPositions()
 * @see saveEscapersPositions()
 * 
 * @example
 * @code
 * // With m_outputPath = "output/simulation_run_1"
 * // and m_baseName = "results"
 * 
 * std::string chaserPath = getFilePath("chasers.csv");
 * // Returns: "output/simulation_run_1/results_chasers.csv"
 * 
 * std::string seedPath = getFilePath("seed.txt");
 * // Returns: "output/simulation_run_1/results_seed.txt"
 * 
 * // Using with file operations
 * std::ofstream file(getFilePath("data.csv"));
 * @endcode
 */
std::string Simulation::getFilePath(const std::string& filename) const
{
    return m_outputPath + "/" + m_baseName + "_" + filename;
}

/**
 * @brief Runs a single simulation step for testing grid point selection
 * 
 * This method demonstrates random point selection on the grid by generating
 * and displaying random coordinates along with the cell types found at those
 * positions. It's useful for testing grid initialization and agent placement
 * before running full simulations.
 * 
 * **Functionality:**
 * - Initializes random number generator with the simulation seed
 * - Generates 20 random (x, y) coordinates within grid boundaries
 * - Retrieves and displays the cell value at each position
 * - Identifies the agent type based on grid value
 * 
 * @param run The run identifier (used for logging and output file naming)
 * 
 * @note This is a testing/debugging method that does not perform actual
 *       simulation logic. It only demonstrates grid access and random
 *       coordinate selection.
 * 
 * @warning This method uses the same seed for all runs, which may produce
 *          the same sequence of random points across multiple calls.
 *          For different sequences, call with different run parameters or
 *          modify the seed per run.
 * 
 * @see runFullSimulation()
 * @see getGridValue()
 * 
 * @example
 * @code
 * // Create simulation and test grid point selection
 * Simulation sim(lattice, 12345, "output", "test_run", "test");
 * sim.runSingle(1);
 * 
 * // Output example:
 * // === Selecionando pontos aleatórios no grid 256x256 ===
 * // Run: 1
 * // Ponto 1: (123, 45) -> N (CHASER)
 * // Ponto 2: (67, 89) -> O (ESCAPER)
 * // ...
 * // === Fim da seleção ===
 * @endcode
 */
     // std::cout << "=== Fim da seleção ===" << std::endl;


void Simulation::runSingle(int run) 
{
    const int gridSize = m_lattice.getWidth();
    
 
    
    // Gerador de números aleatórios
    std::mt19937 rng(m_seed);
    std::uniform_int_distribution<int> distPos(0, gridSize - 1);
    
    // Probabilidade para criação de rastro
    const double TRAIL_PROBABILITY = 0.5;
    std::uniform_real_distribution<double> probDist(0.0, 1.0);
    
    // Criar arquivos de saída
    std::string chaserFile = getFilePath("chasers_run" + std::to_string(run) + ".csv");
    std::string escaperFile = getFilePath("escapers_run" + std::to_string(run) + ".csv");
    std::string tempObstaclesFile = getFilePath("tempObs_run" + std::to_string(run) + ".csv");
    std::string seedFile = getFilePath("seed_run" + std::to_string(run) + ".txt");
    
    std::ofstream chaserOut(chaserFile);
    std::ofstream escaperOut(escaperFile);
    std::ofstream tempObsOut(tempObstaclesFile);
    std::ofstream seedOut(seedFile);
    
    if (!chaserOut.is_open() || !escaperOut.is_open() || !tempObsOut.is_open() || !seedOut.is_open()) {
        std::cerr << "[ERROR] Failed to create output files!" << std::endl;
        return;
    }
    
    // Escrever cabeçalhos
    chaserOut << "time,x,y,id\n";
    escaperOut << "time,x,y,id\n";
    tempObsOut << "time,x,y,id\n";
    
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
    
    // Progresso
    const int PROGRESS_INTERVAL = 10000;
    auto startTime = std::chrono::high_resolution_clock::now();
    

    int m_totalSteps = 1e6;

    std::cout << "\n=== Starting Simulation - Run " << run << " ===" << std::endl;
    std::cout << "Total steps: " << m_totalSteps << std::endl;
    std::cout << "Initial chasers: " << m_chasers.size() << std::endl;
    std::cout << "Initial escapers: " << m_escapers.size() << std::endl;
    std::cout << "Progress: " << std::flush;
    
    // Loop principal
    for (int step = 0; step < m_totalSteps; ++step) {
        currentTime = step;
        
        // Mostrar progresso
        if (step % PROGRESS_INTERVAL == 0 && step > 0) {
            double progress = (double)step / m_totalSteps * 100.0;
            auto currentTimePoint = std::chrono::high_resolution_clock::now();
            auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(currentTimePoint - startTime).count();
            
            if (elapsed > 0) {
                double stepsPerSecond = step / elapsed;
                double eta = (m_totalSteps - step) / stepsPerSecond;
                int hours = eta / 3600;
                int minutes = (eta - hours * 3600) / 60;
                int seconds = eta - hours * 3600 - minutes * 60;
                
                std::cout << "\rProgress: " << std::fixed << std::setprecision(1) << progress 
                          << "% | Step: " << step << "/" << m_totalSteps 
                          << " | " << (int)stepsPerSecond << " steps/s"
                          << " | ETA: " << hours << "h " << minutes << "m " << seconds << "s" 
                          << std::flush;
            } else {
                std::cout << "\rProgress: " << std::fixed << std::setprecision(1) << progress << "%" << std::flush;
            }
        }
        
        // ESCOLHER POSIÇÃO ALEATÓRIA
        int randomX = distPos(rng);
        int randomY = distPos(rng);
        std::string cellType = m_lattice.getGridValue(randomX, randomY);
        
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
        const int EXPORT_INTERVAL = 100;
        if (step % EXPORT_INTERVAL == 0 || step == m_totalSteps - 1) {
            // Exportar chasers
            for (const auto& chaser : m_chasers) {
                chaserBuffer.push_back(std::to_string(currentTime) + "," + 
                                       std::to_string(chaser.getPositionX()) + "," + 
                                       std::to_string(chaser.getPositionY()) + "," + 
                                       std::to_string(chaser.getId()) + "\n");
            }
            
            // Exportar escapers
            for (const auto& escaper : m_escapers) {
                escaperBuffer.push_back(std::to_string(currentTime) + "," + 
                                        std::to_string(escaper.getPositionX()) + "," + 
                                        std::to_string(escaper.getPositionY()) + "," + 
                                        std::to_string(escaper.getId()) + "\n");
            }
            
            // Exportar obstáculos temporários
            for (const auto& t_obs : m_tempObstacles) {
                tempObsBuffer.push_back(std::to_string(currentTime) + "," + 
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
    chaserOut.close();
    escaperOut.close();
    tempObsOut.close();
    seedOut.close();
    
    // Estatísticas finais
    auto endTime = std::chrono::high_resolution_clock::now();
    auto totalElapsed = std::chrono::duration_cast<std::chrono::seconds>(endTime - startTime).count();
    
    std::cout << "\n\n=== Simulation Complete - Run " << run << " ===" << std::endl;
    std::cout << "Total steps: " << m_totalSteps << std::endl;
    std::cout << "Total time: " << totalElapsed << " seconds" << std::endl;
    if (totalElapsed > 0) {
        std::cout << "Average speed: " << (m_totalSteps / totalElapsed) << " steps/second" << std::endl;
    }
    std::cout << "Final chasers: " << m_chasers.size() << std::endl;
    std::cout << "Final escapers: " << m_escapers.size() << std::endl;
    std::cout << "Final temp obstacles: " << m_tempObstacles.size() << std::endl;
    std::cout << "================================" << std::endl;
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