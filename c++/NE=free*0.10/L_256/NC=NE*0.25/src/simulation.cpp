#include "simulation.h"
#include "utils.h"
#include <iomanip>
#include <fstream>
#include "temp_obs.h"
#include "cell_lattice.h"
#include <filesystem>
#include "globals.hpp"

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
        seedOut << "Seed: " << static_cast<unsigned int>(m_seed) << "\n";
        // Ou use:
        // seedOut << "Seed: " << (unsigned int)m_seed << "\n";
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
    // const double TRAIL_PROBABILITY = 0.5;
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
      
    int m_totalSteps = 1e6;

    std::cout << "\n=== Starting Simulation - Run " << run << " ===" << std::endl;
    std::cout << "Total steps: " << m_totalSteps << std::endl;
    std::cout << "Initial chasers: " << m_chasers.size() << std::endl;
    std::cout << "Initial escapers: " << m_escapers.size() << std::endl;
    std::cout << "Progress: " << std::flush;
    
    // Loop principal
    for (int step = 0; step < m_totalSteps; ++step) {
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
        //const int EXPORT_INTERVAL = 500;
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