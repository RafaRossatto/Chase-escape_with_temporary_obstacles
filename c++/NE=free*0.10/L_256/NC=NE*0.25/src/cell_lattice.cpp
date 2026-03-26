#include <map>
#include "cell_lattice.h"
#include <iomanip>
#include <algorithm> 
#include <array> 
#include <optional>
#include "temp_obs.h"

/**
 * @brief Constructs a new CellLattice object with the specified dimensions
 * 
 * Initializes a toroidal grid of size width x height. All cells are initially
 * set to "L" (free/empty) state. The grid is implemented as a 2D vector where
 * the first dimension represents rows (y-coordinate) and the second dimension
 * represents columns (x-coordinate).
 * 
 * @param width Number of columns in the grid (x-direction)
 * @param height Number of rows in the grid (y-direction)
 * 
 * @note The grid uses toroidal (wrapping) boundaries, meaning that moving
 *       beyond the left edge wraps to the right edge, and similarly for
 *       top/bottom edges.
 * 
 * @warning Grid dimensions must be positive integers. No validation is
 *          performed on the input parameters.
 * 
 * @see m_grid
 * @see getGridValue()
 * @see setGridValue()
 * 
 * @example
 * @code
 * // Create a 256x256 grid
 * CellLattice lattice(256, 256);
 * 
 * // All cells are initially free
 * std::string value = lattice.getGridValue(100, 100);  // Returns "L"
 * @endcode
 */
CellLattice::CellLattice(int width, int height) : m_width(width), m_height(height) {
    m_grid.resize(height, std::vector<std::string>(width, "L")); // Initialize with "L" for free
}

/**
 * @brief Places chaser and escaper cells onto the grid
 * 
 * This function takes vectors of chaser (normal) and escaper (cancer) cells
 * and positions them on the grid by setting the corresponding grid values.
 * 
 * - Chaser cells are marked as "N" on the grid
 * - Escaper cells are marked as "O" on the grid
 * 
 * The function performs boundary validation for each cell position.
 * If a position is outside the grid boundaries, an error message is printed
 * to std::cerr and the cell is not placed.
 * 
 * @param chasers Vector of chaser cells (type "N") to be placed on the grid
 * @param escapers Vector of escaper cells (type "O") to be placed on the grid
 * 
 * @note This function assumes that there are no position conflicts between
 *       chasers and escapers. Position validation should be performed
 *       before calling this function.
 * 
 * @warning Cells with positions outside the grid boundaries will be skipped
 *          and will not be placed. Check the error output for invalid positions.
 * 
 * @see setGridValue()
 * @see getGridValue()
 */
void CellLattice::placeObjects(std::vector<Cell>& chasers, std::vector<Cell>& escapers)
{
    // Place chaser cells
    for (auto& cell : chasers) 
    {
        int x = cell.getPositionX();
        int y = cell.getPositionY();
        
        if (x >= 0 && x < m_width && y >= 0 && y < m_height) 
        {
            setGridValue(x, y, "N");
        }
        else 
        {
            std::cerr << "Invalid position for normal cell ID " << cell.getId() 
                      << ": (" << x << ", " << y << ")\n";
        }
    }
    
    // Place escaper cells)
    for (auto& cell : escapers) 
    {
        int x = cell.getPositionX();
        int y = cell.getPositionY();
        
        if (x >= 0 && x < m_width && y >= 0 && y < m_height) 
        {
            setGridValue(x, y, "O");
        }
        else 
        {
            std::cerr << "Invalid position for cancer cell ID " << cell.getId() 
                      << ": (" << x << ", " << y << ")\n";
        }
    }
}


/**
 * @brief Validates positions of chaser and escaper cells for conflicts and boundaries
 * 
 * This function performs comprehensive validation of cell positions to ensure
 * data integrity before simulation. It checks for:
 * - Positions outside the grid boundaries
 * - Overlap between chasers and escapers (same position)
 * - Duplicate positions within the same cell type
 * 
 * @param chasers Vector of chaser cells to validate
 * @param escapers Vector of escaper cells to validate
 * @param width Grid width (number of columns)
 * @param height Grid height (number of rows)
 * 
 * @return true if all validations pass (no errors found)
 * @return false if any validation fails (out of bounds, overlaps, or duplicates)
 * 
 * @note This function is non-const as it only reads data and does not modify
 *       the grid or cell vectors.
 * 
 * @warning This function outputs detailed validation results to std::cout.
 *          It should be called before placing cells on the grid to ensure
 *          valid initial configuration.
 * 
 * @see placeObjects()
 * @see verifyPlacement()
 * 
 * @example
 * @code
 * std::vector<Cell> chasers = Cell::loadFromCSV("chasers.csv", "N");
 * std::vector<Cell> escapers = Cell::loadFromCSV("escapers.csv", "O");
 * 
 * if (lattice.checkDuplicates(chasers, escapers, 256, 256)) {
 *     lattice.placeObjects(chasers, escapers);
 *     std::cout << "Simulation ready to start\n";
 * } else {
 *     std::cerr << "Cannot start simulation due to invalid data\n";
 * }
 * @endcode
 */

bool CellLattice:: checkDuplicates(const std::vector<Cell>& chasers, const std::vector<Cell>& escapers, int width, int height) {
    std::cout << "\n=== VERIFICAÇÃO DE POSIÇÕES ===\n";
    bool isValid = true;  // Assume que está válido
    
     // 1. Check for positions outside grid boundaries
    std::cout << "\n1. Verificando posições fora do grid (" << width << "x" << height << "):\n";
    bool hasOutOfBounds = false;
    
    // Check chasers
    for (const auto& cell : chasers) {
        int x = cell.getPositionX();
        int y = cell.getPositionY();
        if (x < 0 || x >= width || y < 0 || y >= height) {
            std::cout << "  CHASER ID=" << cell.getId() 
                      << " fora do grid: (" << x << "," << y << ")\n";
            hasOutOfBounds = true;
            isValid = false;
        }
    }
    
    // Check escapers
    for (const auto& cell : escapers) {
        int x = cell.getPositionX();
        int y = cell.getPositionY();
        if (x < 0 || x >= width || y < 0 || y >= height) {
            std::cout << "  ESCAPER ID=" << cell.getId() 
                      << " fora do grid: (" << x << "," << y << ")\n";
            hasOutOfBounds = true;
            isValid = false;
        }
    }
    
    if (!hasOutOfBounds) {
        std::cout << "  Todas as posições estão dentro do grid!\n";
    }
    
    // 2. Check for overlaps between chasers and escapers
    std::cout << "\n2. Verificando posições duplicadas entre CHASERS e ESCAPERS:\n";
    
    std::map<std::pair<int,int>, int> escaperPositions;
    for (const auto& cell : escapers) {
        escaperPositions[{cell.getPositionX(), cell.getPositionY()}] = cell.getId();
    }
    
    bool hasDuplicates = false;
    for (const auto& cell : chasers) {
        auto pos = std::make_pair(cell.getPositionX(), cell.getPositionY());
        auto it = escaperPositions.find(pos);
        if (it != escaperPositions.end()) {
            std::cout << "  DUPLICATA: Chaser ID=" << cell.getId() 
                      << " e Escaper ID=" << it->second 
                      << " na posição (" << pos.first << "," << pos.second << ")\n";
            hasDuplicates = true;
            isValid = false;
        }
    }
    
    if (!hasDuplicates) {
        std::cout << "  Nenhuma posição duplicada entre chasers e escapers!\n";
    }
    
    // 3. Check for duplicates within the same list
    std::cout << "\n3. Verificando duplicatas dentro da mesma lista:\n";
    
    // Check for duplicate chasers
    std::map<std::pair<int,int>, std::vector<int>> chaserPositions;
    for (const auto& cell : chasers) {
        chaserPositions[{cell.getPositionX(), cell.getPositionY()}].push_back(cell.getId());
    }
    
    bool hasChaserDuplicates = false;
    for (const auto& [pos, ids] : chaserPositions) {
        if (ids.size() > 1) {
            std::cout << "  CHASERS duplicados na posição (" << pos.first << "," << pos.second 
                      << "): IDs = ";
            for (size_t i = 0; i < ids.size(); i++) {
                if (i > 0) std::cout << ", ";
                std::cout << ids[i];
            }
            std::cout << "\n";
            hasChaserDuplicates = true;
            isValid = false;
        }
    }
    
    // Check for duplicate escapers
    std::map<std::pair<int,int>, std::vector<int>> escaperPositionsList;
    for (const auto& cell : escapers) {
        escaperPositionsList[{cell.getPositionX(), cell.getPositionY()}].push_back(cell.getId());
    }
    
    bool hasEscaperDuplicates = false;
    for (const auto& [pos, ids] : escaperPositionsList) {
        if (ids.size() > 1) {
            std::cout << "  ESCAPERS duplicados na posição (" << pos.first << "," << pos.second 
                      << "): IDs = ";
            for (size_t i = 0; i < ids.size(); i++) {
                if (i > 0) std::cout << ", ";
                std::cout << ids[i];
            }
            std::cout << "\n";
            hasEscaperDuplicates = true;
            isValid = false;
        }
    }
    
    if (!hasChaserDuplicates && !hasEscaperDuplicates) {
        std::cout << "  Nenhuma duplicata dentro das listas!\n";
    }
    
    // 4. Output statistics
    std::cout << "\n4. Estatísticas:\n";
    std::cout << "  Total de Chasers: " << chasers.size() << "\n";
    std::cout << "  Total de Escapers: " << escapers.size() << "\n";
    std::cout << "  Posições únicas ocupadas: " 
              << (chaserPositions.size() + escaperPositionsList.size()) << "\n";
    
    // Final verdict
    if (isValid) {
        std::cout << "\n✓ VERIFICAÇÃO PASSADA - Todos os dados estão corretos!\n";
    } else {
        std::cout << "\n✗ VERIFICAÇÃO FALHOU - Existem erros nos dados!\n";
    }
    
    return isValid;
}

/**
 * @brief Verifies that the number of cells placed on the grid matches the input vectors
 * 
 * This function counts all 'N' (chaser) and 'O' (escaper) cells currently
 * present on the grid and compares these counts against the sizes of the
 * input vectors. This ensures that all cells from the vectors were
 * successfully placed during the placement phase.
 * 
 * @param chasers Vector of chaser cells that should be on the grid
 * @param escapers Vector of escaper cells that should be on the grid
 * 
 * @return true if the number of 'N' cells equals chasers.size() AND
 *         the number of 'O' cells equals escapers.size()
 * @return false otherwise
 * 
 * @note This function only verifies counts, not individual positions.
 *       Use checkDuplicates() for position-specific validation.
 * 
 * @warning This function does not verify that the cells are in the correct
 *          positions, only that the total counts match. A cell placed in
 *          the wrong position would still satisfy this check.
 * 
 * @see placeObjects()
 * @see checkDuplicates()
 * 
 * @example
 * @code
 * std::vector<Cell> chasers = Cell::loadFromCSV("chasers.csv", "N");
 * std::vector<Cell> escapers = Cell::loadFromCSV("escapers.csv", "O");
 * 
 * lattice.placeObjects(chasers, escapers);
 * 
 * if (lattice.verifyPlacement(chasers, escapers)) {
 *     std::cout << "All cells successfully placed on grid\n";
 * } else {
 *     std::cerr << "Placement failed - some cells not placed\n";
 * }
 * @endcode
 */
bool CellLattice::verifyPlacement(const std::vector<Cell>& chasers, 
                                   const std::vector<Cell>& escapers) const
{
    int countN = 0;
    int countO = 0;
    
    // Conta elementos no grid
    for (int y = 0; y < m_height; ++y) {
        for (int x = 0; x < m_width; ++x) {
            if (m_grid[y][x] == "N") countN++;
            else if (m_grid[y][x] == "O") countO++;
        }
    }
    
    // Verifica se os números correspondem
    bool correct = (countN == static_cast<int>(chasers.size())) &&
                   (countO == static_cast<int>(escapers.size()));
    
    if (!correct) {
        std::cerr << "Placement verification failed!\n";
        std::cerr << "  Grid: N=" << countN << ", O=" << countO << "\n";
        std::cerr << "  Vectors: N=" << chasers.size() << ", O=" << escapers.size() << "\n";
    }
    
    return correct;
}


/**
 * @brief Sets the value of a cell at the specified grid coordinates
 * 
 * Updates the grid cell at position (x, y) with the given value.
 * The method performs bounds checking and reports errors for invalid
 * coordinates without modifying the grid.
 * 
 * @param x X-coordinate (column) of the cell to modify (0 to width-1)
 * @param y Y-coordinate (row) of the cell to modify (0 to height-1)
 * @param value The string value to assign to the grid cell
 * 
 * @note Common grid values used in the simulation:
 *       - "L": Free/empty cell
 *       - "N": Normal cell (chaser)
 *       - "O": Cancer cell (escaper)
 *       - "C": Permanent obstacle
 *       - "T": Temporary obstacle
 * 
 * @warning This function does not validate that the new value is one of the
 *          expected types. Any string can be assigned, which may lead to
 *          unexpected behavior in other parts of the code.
 * 
 * @see getGridValue()
 * @see isOccupied()
 * @see placeObjects()
 * 
 * @example
 * @code
 * // Mark a cell as free
 * lattice.setGridValue(10, 20, "L");
 * 
 * // Place a chaser at position (5, 5)
 * lattice.setGridValue(5, 5, "N");
 * 
 * // Place a temporary obstacle
 * lattice.setGridValue(15, 30, "T");
 * @endcode
 */
void CellLattice::setGridValue(int x, int y, const std::string& value) 
{
    if (x >= 0 && x < m_width && y >= 0 && y < m_height) 
    {
        m_grid[y][x] = value;
    } else 
    {
        std::cerr << "[ERROR] Grid access out of bounds in setGridValue: (" << x << "," << y << ")\n";
    }
}

/**
 * @brief Retrieves the value of a cell at the specified grid coordinates
 * 
 * Returns the current value stored at position (x, y) in the grid.
 * The method performs bounds checking and returns an error indicator
 * for invalid coordinates.
 * 
 * @param x X-coordinate (column) of the cell to read (0 to width-1)
 * @param y Y-coordinate (row) of the cell to read (0 to height-1)
 * @return std::string The value at the specified grid cell, or "!" if
 *         coordinates are out of bounds
 * 
 * @note Common return values:
 *       - "L": Free/empty cell
 *       - "N": Normal cell (chaser)
 *       - "O": Cancer cell (escaper)
 *       - "C": Permanent obstacle
 *       - "T": Temporary obstacle
 *       - "!": Error indicator (out of bounds)
 * 
 * @warning The function returns "!" for out-of-bounds accesses, which
 *          is not a valid grid state. Always check coordinates before
 *          calling this function if you need to distinguish between
 *          valid "!" values and errors.
 * 
 * @see setGridValue()
 * @see isOccupied()
 * 
 * @example
 * @code
 * // Safe access with bounds checking
 * std::string cellType = lattice.getGridValue(10, 20);
 * if (cellType == "N") {
 *     std::cout << "Found a chaser at (10, 20)\n";
 * } else if (cellType == "!") {
 *     std::cerr << "Invalid coordinates\n";
 * }
 * 
 * // Check if cell is free
 * if (lattice.getGridValue(x, y) == "L") {
 *     // Cell is empty, can place agent
 * }
 * @endcode
 */
std::string CellLattice::getGridValue(int x, int y) const {
    if (x >= 0 && x < m_width && y >= 0 && y < m_height) {
        return m_grid[y][x];
    } else {
        std::cerr << "[ERROR] Grid access out of bounds in getGridValue: (" << x << "," << y << ")\n";
        return "!";
    }
}

/**
 * @brief Prints the current grid state to the console
 * 
 * Outputs the entire grid to standard output with each cell represented
 * by its value string. The grid is printed row by row, with cells
 * separated by spaces. A separator line is printed after the grid.
 * 
 * **Grid representation:**
 * - "L": Free/empty cell
 * - "N": Normal cell (chaser)
 * - "O": Cancer cell (escaper)
 * - "C": Permanent obstacle
 * - "T": Temporary obstacle
 * 
 * @note This function is useful for debugging and visualizing the
 *       simulation state. For large grids (e.g., 256x256), this output
 *       can be very verbose and may slow down execution.
 * 
 * @warning This function prints to std::cout and cannot be redirected
 *          without modifying the function. Consider using a logger or
 *          file output for large-scale simulations.
 * 
 * @see getGridValue()
 * @see saveGridToFile()
 * 
 * @example
 * @code
 * // Print small grid for debugging
 * CellLattice lattice(10, 10);
 * lattice.placeObjects(chasers, escapers);
 * lattice.printGrid();
 * 
 * // Output example:
 * // L L L L N L O L L L
 * // L L L L L L L L L L
 * // L N L L L L L L L L
 * // L L L O L L L L L L
 * // ---------------------------
 * @endcode
 */
void CellLattice::printGrid() const 
{
    for (int y = 0; y < m_height; ++y) 
    {
        for (int x = 0; x < m_width; ++x) 
        {
            std::cout << m_grid[y][x] << " ";
        }
        std::cout << "\n";
    }
    std::cout << "---------------------------\n";
}























/**
 * @brief Calculates Manhattan distance with toroidal wrapping
 */
double CellLattice::calculateDistance(int x1, int y1, int x2, int y2) const
{
    int dx = std::abs(x2 - x1);
    if (dx > m_width / 2) dx = m_width - dx;

    int dy = std::abs(y2 - y1);
    if (dy > m_height / 2) dy = m_height - dy;

    return dx + dy;
}



/**
 * @brief Checks if a position is occupied
 */
bool CellLattice::isOccupied(int x, int y,
    const std::vector<Cell>& normalCells,
    const std::vector<Cell>& cancerCells,
    const std::vector<Obstacle>& obstacles,
    bool checkCancer, std::vector<temp_obs>& tempObstacles) const
{
    for (const auto& cell : normalCells) 
    {
    if (cell.getPositionX() == x && cell.getPositionY() == y) 
    {
        return true;
    }
    }

    if (checkCancer) 
    {
        for (const auto& cancer : cancerCells) 
        {
            if (cancer.getPositionX() == x && cancer.getPositionY() == y) 
            {
                return true;
            }
        }
    }

    // for (const auto& obs : obstacles) 
    // {
    //     if (obs.getPositionX() == x && obs.getPositionY() == y) 
    //     {
    //         return true;
    //     }
    // }


    for (const auto& t_obs : tempObstacles) 
    {
        if (t_obs.getPositionX() == x && t_obs.getPositionY() == y) 
        {
            return true;
        }
    }
    return false;
}


/**
 * @brief Counts targets around a position
 */
int CellLattice::countTargetsAround(int x, int y,
    const std::vector<Cell>& agents,
    const std::vector<std::string>& types,
    int searchRadius) const
{
    int count = 0;
    for (const auto& agent : agents) 
    {
        if (std::find(types.begin(), types.end(), agent.getType()) == types.end())
            continue;

        double distance = calculateDistance(x, y, agent.getPositionX(), agent.getPositionY());
        if (distance <= searchRadius + 1e-6)
            ++count;
    }
    return count;
}

void CellLattice::moveCancerCell(Cell& cell,
    std::vector<Cell>& normalCells, std::vector<Cell>& cancerCells,
    std::vector<Obstacle>& obstacles,
    std::mt19937& rng, bool checkCancer, int searchRadius, std::vector<temp_obs>& tempObstacles)
{
    int x = cell.getPositionX();
    int y = cell.getPositionY();
    
    // Variável para armazenar a nova posição apenas quando realmente for mover
    std::optional<std::pair<int, int>> newPosition = std::nullopt;

    const std::array<Direction, 4> directions = {NORTH, EAST, SOUTH, WEST};
    std::array<Direction, 4> shuffledDirections = directions;
    std::shuffle(shuffledDirections.begin(), shuffledDirections.end(), rng);

    // 1. Collect all adjacent hunters
    std::vector<std::pair<int, int>> adjacentHunters;
    for (Direction dir : shuffledDirections)
    {
        int adjX = x, adjY = y;
        cell.randomWalk(adjX, adjY, dir);
        for (const auto& hunter : normalCells)
        {
            if (hunter.getPositionX() == adjX && hunter.getPositionY() == adjY)
            {
                adjacentHunters.emplace_back(adjX, adjY);
                break;
            }
        }
    }

    // 2. If there are adjacent hunters → choose random one and flee to free position
    if (!adjacentHunters.empty())
    {
        std::shuffle(adjacentHunters.begin(), adjacentHunters.end(), rng);
        
        std::vector<Direction> freeDirections;
        for (Direction dir : shuffledDirections)
        {
            int tempX = x, tempY = y;
            cell.randomWalk(tempX, tempY, dir);

            if (!isOccupied(tempX, tempY, normalCells, cancerCells, obstacles, checkCancer,tempObstacles))
                freeDirections.push_back(dir);
        }

        if (!freeDirections.empty())
        {
            std::shuffle(freeDirections.begin(), freeDirections.end(), rng);
            Direction fleeDirection = freeDirections.front();
            
            int newX = x, newY = y;
            cell.randomWalk(newX, newY, fleeDirection);
            newPosition = std::make_pair(newX, newY);
        }
    }   
    // 3. If no adjacent hunter → density strategy
    else
    {
        std::vector<Cell> allCells;
        allCells.insert(allCells.end(), normalCells.begin(), normalCells.end());
        allCells.insert(allCells.end(), cancerCells.begin(), cancerCells.end());

        int currentDensity = countTargetsAround(x, y, allCells, {"N"}, searchRadius);
        int minDensity = currentDensity;
        std::vector<Direction> bestDirections;

        for (Direction dir : shuffledDirections)
        {
            int tempX = x, tempY = y;
            cell.randomWalk(tempX, tempY, dir);
            if (isOccupied(tempX, tempY, normalCells, cancerCells, obstacles, checkCancer,tempObstacles))
                continue;

            int neighborDensity = countTargetsAround(tempX, tempY, allCells, {"N"}, searchRadius);
            if (neighborDensity < minDensity)
            {
                minDensity = neighborDensity;
                bestDirections.clear();
                bestDirections.push_back(dir);
            }
            else if (neighborDensity == minDensity)
            {
                bestDirections.push_back(dir);
            }
        }

        if (!bestDirections.empty())
        {
            std::shuffle(bestDirections.begin(), bestDirections.end(), rng);
            Direction bestDir = bestDirections.front();
            
            int newX = x, newY = y;
            cell.randomWalk(newX, newY, bestDir);
            newPosition = std::make_pair(newX, newY);
        }
        else
        {
            std::uniform_int_distribution<int> dirDist(0, 3);
            Direction randomDir = static_cast<Direction>(dirDist(rng));
            
            int newX = x, newY = y;
            cell.randomWalk(newX, newY, randomDir);
            
            if (!isOccupied(newX, newY, normalCells, cancerCells, obstacles, checkCancer,tempObstacles))
                newPosition = std::make_pair(newX, newY);
        }
    }

    // Move apenas se tivermos uma nova posição válida
    if (newPosition.has_value())
    {
        auto [newX, newY] = newPosition.value();
        setGridValue(x, y, "L");
        cell.changePosition(newX, newY);
        setGridValue(newX, newY, "O");

            tempObstacles.emplace_back("T", 
                               tempObstacles.size() + 1,
                               x, 
                               y);
        setGridValue(newX, newY, "T");
    }
}

int CellLattice::moveNormalCell(Cell& cell,
    std::vector<Cell>& normalCells, std::vector<Cell>& cancerCells,
    std::vector<Obstacle>& obstacles,
    std::mt19937& rng, bool checkCancer, int searchRadius, std::vector<temp_obs>& tempObstacles)
{
    int capturedId = -1;
    int x = cell.getPositionX();
    int y = cell.getPositionY();
    
    // Usar optional para representar se houve movimento e para onde
    std::optional<std::pair<int, int>> newPosition = std::nullopt;
    
    // Probability for intelligent movement
    const double CT_PROBABILITY = 1.0;
    std::bernoulli_distribution dist(CT_PROBABILITY);
    bool intelligentMovement = dist(rng);

    const std::array<Direction, 4> directions = {NORTH, EAST, SOUTH, WEST};
    std::array<Direction, 4> shuffledDirections = directions;
    std::shuffle(shuffledDirections.begin(), shuffledDirections.end(), rng);

    if (intelligentMovement)
    {
        // 1. Check for adjacent prey
        std::vector<Direction> adjacentPrey;
        for (Direction dir : shuffledDirections)
        {
            int tempX = x, tempY = y;
            cell.randomWalk(tempX, tempY, dir);
            for (const auto& prey : cancerCells)
            {
                if (prey.getPositionX() == tempX && prey.getPositionY() == tempY)
                {
                    adjacentPrey.push_back(dir);
                    break;
                }
            }
        }

        // 2. If there's adjacent prey → capture random one
        if (!adjacentPrey.empty())
        {
            std::shuffle(adjacentPrey.begin(), adjacentPrey.end(), rng);
            Direction dir = adjacentPrey.front();
            
            int captureX = x, captureY = y;
            cell.randomWalk(captureX, captureY, dir);
            newPosition = std::make_pair(captureX, captureY);

            // Capture prey at that position
            for (auto it = cancerCells.begin(); it != cancerCells.end(); )
            {
                if (it->getPositionX() == captureX && it->getPositionY() == captureY)
                {
                    capturedId = it->getId(); 
                    setGridValue(it->getPositionX(), it->getPositionY(), "L");    
                    it = cancerCells.erase(it);
                }
                else
                {
                    ++it;
                }
            }
            
            // Como removemos a presa, a posição está livre - podemos mover
            setGridValue(x, y, "L");
            cell.changePosition(captureX, captureY);
            setGridValue(captureX, captureY, "N");
            return capturedId;
        }

        // 3. If no adjacent prey → follow density strategy
        std::vector<Cell> allCells;
        allCells.insert(allCells.end(), normalCells.begin(), normalCells.end());
        allCells.insert(allCells.end(), cancerCells.begin(), cancerCells.end());

        int currentDensity = countTargetsAround(x, y, allCells, {"O"}, searchRadius);
        int maxDensity = currentDensity;
        std::vector<Direction> bestDirections;

        for (Direction dir : shuffledDirections)
        {
            int tempX = x, tempY = y;
            cell.randomWalk(tempX, tempY, dir);
            if (isOccupied(tempX, tempY, normalCells, cancerCells, obstacles, checkCancer,tempObstacles))
                continue;

            int neighborDensity = countTargetsAround(tempX, tempY, allCells, {"O"}, searchRadius);
            if (neighborDensity > maxDensity)
            {
                maxDensity = neighborDensity;
                bestDirections.clear();
                bestDirections.push_back(dir);
            }
            else if (neighborDensity == maxDensity)
            {
                bestDirections.push_back(dir);
            }
        }

        if (!bestDirections.empty())
        {
            std::shuffle(bestDirections.begin(), bestDirections.end(), rng);
            Direction bestDir = bestDirections.front();
            
            int moveX = x, moveY = y;
            cell.randomWalk(moveX, moveY, bestDir);
            newPosition = std::make_pair(moveX, moveY);
        }
        else
        {
            std::uniform_int_distribution<int> dirDist(0, 3);
            Direction randomDir = static_cast<Direction>(dirDist(rng));
            
            int moveX = x, moveY = y;
            cell.randomWalk(moveX, moveY, randomDir);
            
            // Verifica se a posição aleatória está livre
            if (!isOccupied(moveX, moveY, normalCells, cancerCells, obstacles, checkCancer,tempObstacles))
                newPosition = std::make_pair(moveX, moveY);
        }
    }
    else
    {
        // Completely random movement
        std::uniform_int_distribution<int> dirDist(0, 3);
        Direction randomDir = static_cast<Direction>(dirDist(rng));
        
        int moveX = x, moveY = y;
        cell.randomWalk(moveX, moveY, randomDir);
        
        if (!isOccupied(moveX, moveY, normalCells, cancerCells, obstacles, checkCancer,tempObstacles))
            newPosition = std::make_pair(moveX, moveY);
    }

    // Move apenas se tivermos uma nova posição válida
    if (newPosition.has_value())
    {
        auto [newX, newY] = newPosition.value();
        setGridValue(x, y, "L");
        cell.changePosition(newX, newY);
        setGridValue(newX, newY, "N");
    }
    
    return capturedId;
}
