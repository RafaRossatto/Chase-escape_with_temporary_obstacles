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
Simulation::Simulation(CellLattice& lattice, unsigned int seed,
                       const std::string& path_out, const std::string& directory_name,
                       const std::string& base_name)
    : m_lattice(lattice), m_seed(seed), m_baseName(base_name)
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
    clearTrajectoryData();
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
void Simulation::runSingle(int run) 
{
    const int gridSize = m_lattice.getWidth();

    // Initialize random number generator with simulation seed
    //std::mt19937 rng(m_seed);
    
    
    // Define uniform distributions for random coordinate generation
    std::uniform_int_distribution<int> distX(0, gridSize - 1);
    std::uniform_int_distribution<int> distY(0, gridSize - 1);
    
    std::cout << "\n=== Selecionando pontos aleatórios no grid " << gridSize << "x" << gridSize << " ===" << std::endl;
    std::cout << "Run: " << run << std::endl;
    
    // // Generate and display 20 random points on the grid
    // for (int i = 0; i < 20; ++i) {
    //     int randomX = distX(rng);
    //     int randomY = distY(rng);
        
    //     std::string cellValue = m_lattice.getGridValue(randomX, randomY);
        
    //     // Display point coordinates and grid value
    //     std::cout << "Ponto " << i+1 << ": (" << randomX << ", " << randomY << ") -> " << cellValue;
        
    //     // Interpret grid value as agent type
    //     if (cellValue == "N") {
    //         std::cout << " (CHASER)";
    //     } else if (cellValue == "O") {
    //         std::cout << " (ESCAPER)";
    //     } else if (cellValue == "C") {
    //         std::cout << " (OBSTACLE)";
    //     } else if (cellValue == "T") {
    //         std::cout << " (TEMP_OBSTACLE)";
    //     } else if (cellValue == "L") {
    //         std::cout << " (FREE)";
    //     } else {
    //         std::cout << " (UNKNOWN)";
    //     }
        
    //     std::cout << std::endl;
    // }
    
    // std::cout << "=== Fim da seleção ===" << std::endl;



        // Gerador de números aleatórios
    //std::mt19937 rng(m_seed);
// Gerador de números aleatórios
    std::mt19937 rng(m_seed);
    std::uniform_int_distribution<int> distPos(0, gridSize - 1);
    std::uniform_int_distribution<int> distId(1, 1000);
    
    // Criar arquivos de saída
    std::string chaserFile = getFilePath("chasers_run" + std::to_string(run) + ".csv");
    std::string escaperFile = getFilePath("escapers_run" + std::to_string(run) + ".csv");
    std::string seedFile = getFilePath("seed_run" + std::to_string(run) + ".txt");
    
    std::ofstream chaserOut(chaserFile);
    std::ofstream escaperOut(escaperFile);
    std::ofstream seedOut(seedFile);
    
    if (!chaserOut.is_open() || !escaperOut.is_open() || !seedOut.is_open()) {
        std::cerr << "[ERROR] Failed to create output files!" << std::endl;
        return;
    }
    
    // Escrever cabeçalhos COM TEMPO
    chaserOut << "time,x,y,id\n";
    escaperOut << "time,x,y,id\n";
    
    // Salvar seed com informações
    seedOut << "Simulation Seed: " << m_seed << "\n";

    // Para teste, vamos gerar dados em diferentes tempos
    // Isso simula diferentes passos da simulação
    
    double currentTime = 0.0;
    const double timeStep = 1.0;
    const int numSteps = 5;  // Gerar 5 passos de tempo
    
    int numChasersPerStep = 10;  // 10 chasers por passo
    int numEscapersPerStep = 20;  // 20 escapers por passo
    
    for (int step = 0; step < numSteps; ++step) {
        currentTime = step * timeStep;
        
        // Gerar posições para chasers neste tempo
        for (int i = 0; i < numChasersPerStep; ++i) {
            int x = distPos(rng);
            int y = distPos(rng);
            int id = distId(rng);
            chaserOut << currentTime << "," << x << "," << y << "," << id << "\n";
        }
        
        // Gerar posições para escapers neste tempo
        for (int i = 0; i < numEscapersPerStep; ++i) {
            int x = distPos(rng);
            int y = distPos(rng);
            int id = distId(rng);
            escaperOut << currentTime << "," << x << "," << y << "," << id << "\n";
        }
    }
    
    // Fechar arquivos
    chaserOut.close();
    escaperOut.close();
    seedOut.close();
    
    // Mostrar informações
    std::cout << "\n=== Teste de Exportação - Run " << run << " ===" << std::endl;
    std::cout << "Seed: " << m_seed << std::endl;
    std::cout << "Grid size: " << gridSize << "x" << gridSize << std::endl;
    std::cout << "Time steps gerados: " << numSteps << " (0 a " << (numSteps-1)*timeStep << ")" << std::endl;
    std::cout << "Chasers por passo: " << numChasersPerStep << " (total: " << numSteps * numChasersPerStep << ")" << std::endl;
    std::cout << "Escapers por passo: " << numEscapersPerStep << " (total: " << numSteps * numEscapersPerStep << ")" << std::endl;
    std::cout << "\nArquivos criados:" << std::endl;
    std::cout << "  - " << chaserFile << std::endl;
    std::cout << "  - " << escaperFile << std::endl;
    std::cout << "  - " << seedFile << std::endl;
    std::cout << "=== Fim do Teste ===" << std::endl;
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