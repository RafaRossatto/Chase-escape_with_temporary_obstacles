#include <map>
#include "cell_lattice.h"
#include <iomanip>
#include <algorithm> 
#include <array> 
#include <optional>
#include "temp_obs.h"

/**
 * @brief Constructs a new CellLattice object
 * 
 * @param width Width of the grid
 * @param height Height of the grid
 */
CellLattice::CellLattice(int width, int height) : m_width(width), m_height(height) {
    m_grid.resize(height, std::vector<std::string>(width, "L")); // Initialize with "L" for free
}

// bool CellLattice::loadObstacles(std::vector<Obstacle>& obstacles, int numObstacles, std::string& line) const
// {
//     if (numObstacles == 0) 
//     {
//         return true; // nothing to do
//     }

//     std::string filename = "obstacules_" + std::to_string(numObstacles) + ".txt";
//     if (!fileExists(filename)) 
//     {
//         logError("Error: File " + filename + " does not exist.");
//         std::cin.get();
//         return false;
//     }

//     std::ifstream inputFile(filename);
//     if (!inputFile.is_open()) 
//     {
//         logError("Error opening file: " + filename);
//         std::cin.get();
//         return false;
//     }

//     int idCounter = 1;
//     int x, y;

//     while (std::getline(inputFile, line)) 
//     {
//         std::istringstream lineStream(line);
//         if (lineStream >> x >> y) 
//         {
//             Obstacle newObstacle("C", idCounter++, x, y);
//             obstacles.push_back(newObstacle);
//         }
//     }

//     inputFile.close();
//     return true;
// }

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
 * @brief Places objects on the grid from files
 */
void CellLattice::placeObjects(std::vector<Cell>& chasers, std::vector<Cell>& escapers)
{
    // Posiciona células normais (chasers)
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
    
    // Posiciona células cancerígenas (escapers)
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



bool CellLattice:: checkDuplicates(const std::vector<Cell>& chasers, const std::vector<Cell>& escapers, int width, int height) {
    std::cout << "\n=== VERIFICAÇÃO DE POSIÇÕES ===\n";
    bool isValid = true;  // Assume que está válido
    
    // 1. Verificar se alguma posição está fora do grid
    std::cout << "\n1. Verificando posições fora do grid (" << width << "x" << height << "):\n";
    bool hasOutOfBounds = false;
    
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
    
    // 2. Verificar posições duplicadas entre chasers e escapers
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
    
    // 3. Verificar duplicatas dentro da mesma lista
    std::cout << "\n3. Verificando duplicatas dentro da mesma lista:\n";
    
    // Verificar duplicatas nos chasers
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
    
    // Verificar duplicatas nos escapers
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
    
    // 4. Estatísticas gerais
    std::cout << "\n4. Estatísticas:\n";
    std::cout << "  Total de Chasers: " << chasers.size() << "\n";
    std::cout << "  Total de Escapers: " << escapers.size() << "\n";
    std::cout << "  Posições únicas ocupadas: " 
              << (chaserPositions.size() + escaperPositionsList.size()) << "\n";
    
    if (isValid) {
        std::cout << "\n✓ VERIFICAÇÃO PASSADA - Todos os dados estão corretos!\n";
    } else {
        std::cout << "\n✗ VERIFICAÇÃO FALHOU - Existem erros nos dados!\n";
    }
    
    return isValid;
}



/*
Verifica se o numero de posicionado é o mesmo que o definido
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
 * @brief Sets a value in the grid
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
 * @brief Gets a value from the grid
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
 * @brief Prints the grid to console
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
