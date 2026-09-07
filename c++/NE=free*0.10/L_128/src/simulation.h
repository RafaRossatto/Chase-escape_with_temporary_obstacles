#pragma once
#ifndef SIMULATION_H
#define SIMULATION_H

#include "cell_lattice.h"
#include "obstacle.h"
#include "config.h"
#include <string>
#include <vector>
#include <random>
#include <fstream>
#include <utility> // para std::pair

/**
 * @struct TrajectoryData
 * @brief Stores trajectory data for all cells across timesteps
 */
struct TrajectoryData 
{
    std::vector<double> timesteps;
    std::vector<std::vector<std::pair<int, int>>> preyPositions;   // [timestep][cell](x,y)
    std::vector<std::vector<std::pair<int, int>>> hunterPositions; // [timestep][cell](x,y)
    std::vector<std::vector<std::pair<int, int>>> temp_obst_Positions; // [timestep][cell](x,y)
};

/**
 * @struct SimulationResult
 * @brief Stores the results of a simulation run
 */
struct SimulationResult 
{
    double steps;        /**< Number of steps executed */
    int remainingPrey;   /**< Number of remaining prey cells at the end */
};

/**
 * @class Simulation
 * @brief Manages and executes the cell simulation
 * 
 * This class handles the main simulation loop, movement of cells,
 * and collection of results for statistical analysis.
 */
class Simulation 
{
private:
    CellLattice& m_lattice;          /**< Reference to the cell lattice environment */
    int m_numHunters;                /**< Number of hunter (normal) cells */
    int m_numPrey;                   /**< Number of prey (cancer) cells */
    //int m_tempObstacles;              /**< Number of obstacles */
    double m_hunterNoise;            /**< Noise parameter for hunter movement */
    double m_preyNoise;              /**< Noise parameter for prey movement */
    std::string m_fileName;          /**< Base filename for output files */
    std::vector<Obstacle> m_obstacles;  // Vetor de obstáculos fixos

    int m_hunterSearchRadius;        /**< Search radius for hunter cells */
    int m_preySearchRadius;          /**< Search radius for prey cells */
    int m_seed;             /**< Random seed for reproducibility */
    std::string m_outputPath;      // ADICIONE ESTA LINHA
    std::string m_pathOut;
    std::string m_directoryName;
    std::string m_baseName;
    std::vector<temp_obs> m_tempObstacles;
    

    std::vector<Cell> m_chasers;
    std::vector<Cell> m_escapers;
    /**
     * @brief Constructs a complete file path by combining output directory, base name, and filename.
     * 
     * This helper method builds a full file path using the simulation's output directory,
     * base filename prefix, and the provided filename. The resulting path follows the format:
     * `{outputPath}/{baseName}_{filename}`
     * 
     * For example, if:
     * - m_outputPath = "./results/run_001"
     * - m_baseName = "simulation"
     * - filename = "chasers.csv"
     * The returned path would be: "./results/run_001/simulation_chasers.csv"
     * 
     * @param filename The specific filename to append (e.g., "chasers.csv", "escapers.csv").
     * @return std::string The complete file path as a string.
     * 
     * @note The method uses a forward slash ('/') as the path separator, which works on
     *       Unix-like systems (Linux, macOS). For Windows compatibility, consider using
     *       `std::filesystem::path::preferred_separator` or `fs::path` concatenation.
     * @note The base name is automatically prepended with an underscore to the filename,
     *       which helps organize multiple output files from the same simulation run.
     * @note This method is typically called by other output-related methods like
     *       `createEmptyOutputFiles()` and logging functions.
     * 
     * @warning No validation is performed to ensure the resulting path is valid or that
     *          the directory exists. The caller should handle any filesystem errors.
     * @warning The hardcoded '/' separator may cause issues on Windows systems. Consider
     *          using `fs::path(m_outputPath) / (m_baseName + "_" + filename)` instead.
     * 
     * @see Simulation::createEmptyOutputFiles() For usage example.
     * @see Simulation::m_outputPath The member variable containing the output directory.
     * @see Simulation::m_baseName The member variable containing the filename prefix.
     */
    std::string getFilePath(const std::string& filename) const;
    
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
    void createEmptyOutputFiles();  // Método para criar arquivos vazios
    

    // /**
    //  * @brief Saves current positions to trajectory data
    //  * @param time Current simulation time
    //  * @param prey Vector of prey cells
    //  * @param hunters Vector of hunter cells
    //  */
    // void saveCurrentPositions(double time, const std::vector<Cell>& prey, 
    //     const std::vector<Cell>& hunters, const std::vector<temp_obs>& t_obs);

public:
    /**
     * @brief Constructs a Simulation object and initializes the output directory.
     * 
     * This constructor initializes a simulation with the given lattice, cell populations,
     * random seed, and output configuration. It automatically creates the output
     * directory structure if it doesn't already exist.
     * 
     * The output path is constructed by joining the base path (`path_out`) with the
     * subdirectory name (`directory_name`). For example, if `path_out` is "./results"
     * and `directory_name` is "run_001", the full output path becomes "./results/run_001".
     * 
     * @param lattice Reference to the CellLattice grid where the simulation runs.
     * @param chasers Vector of normal cells (chasers/hunters) participating in the simulation.
     * @param escapers Vector of cancer cells (escapers/prey) participating in the simulation.
     * @param seed Random seed for deterministic simulation reproducibility.
     * @param path_out Base directory path where simulation outputs will be stored.
     * @param directory_name Subdirectory name for this specific simulation run.
     * @param base_name Base filename prefix for output files (e.g., "simulation").
     * 
     * @note The constructor uses `std::filesystem` (C++17) for path manipulation
     *       and directory creation.
     * @note If the output directory already exists, a message is printed but no
     *       files are overwritten automatically.
     * @note If directory creation fails, an error message is printed to std::cerr
     *       but the simulation continues (no exception is thrown).
     * 
     * @warning The commented code suggests intended functionality that is not
     *          implemented in this constructor:
     *          - `createEmptyOutputFiles()` - intended to initialize output files with headers
     *          - `clearTrajectoryData()` - intended to reset trajectory tracking
     *          These methods should be called elsewhere or uncommented if needed.
     * 
     * @see Simulation::run() The main simulation loop (not shown here).
     * @see fs::path std::filesystem::path for path operations.
     */
    Simulation(CellLattice& lattice, 
                        std::vector<Cell>& chasers,
                        std::vector<Cell>& escapers,
                        unsigned int seed,
                        const std::string& path_out, 
                        const std::string& directory_name,
                        const std::string& base_name);
    

    /**
     * @brief Runs a single simulation run
     * 
     * @param run Run identifier number
     * @param rng Random number generator
     * @return SimulationResult Results of the simulation run
     */
    void runSingle(int run);
    
    // Getters
    int getNumHunters() const { return m_numHunters; }
    int getNumPrey() const { return m_numPrey; }
    //int getNumObstacles() const { return m_numObstacles; }
    std::string getFileName() const { return m_fileName; }
    unsigned int getSeed() const { return m_seed; }
    const std::vector<Cell>& getChasers() const { return m_chasers; }
    const std::vector<Cell>& getEscapers() const { return m_escapers; }
    std::string getOutputPath() const { return m_outputPath; }
};

#endif // SIMULATION_H