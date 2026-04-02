#include <map>
#include "cell_lattice.h"
#include <iomanip>
#include <algorithm> 
#include <array> 
#include <optional>
#include "temp_obs.h"
#include "globals.hpp"

CellLattice::CellLattice(int width, int height) : m_width(width), m_height(height) {
    m_grid.resize(height, std::vector<std::string>(width, "L")); // Initialize with "L" for free
}

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

std::string CellLattice::getGridValue(int x, int y) const {
    if (x >= 0 && x < m_width && y >= 0 && y < m_height) {
        return m_grid[y][x];
    } else {
        std::cerr << "[ERROR] Grid access out of bounds in getGridValue: (" << x << "," << y << ")\n";
        return "!";
    }
}

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

void CellLattice::moveCancerCell(Cell& cell,
    std::vector<Cell>& normalCells, std::vector<Cell>& cancerCells,
    std::mt19937& rng, bool checkCancer, std::vector<temp_obs>& tempObstacles)
{
    int x = cell.getPositionX();
    int y = cell.getPositionY();
    
    // std::cout << "\n========================================\n";
    // std::cout << "🎯 MOVENDO ESCAPER na posição (" << x << "," << y << ")" << std::endl;
    // std::cout << "========================================\n";
    //std::cin.get();
    
    const std::array<Direction, 4> directions = {NORTH, EAST, SOUTH, WEST};
    std::array<Direction, 4> shuffledDirections = directions;
    std::shuffle(shuffledDirections.begin(), shuffledDirections.end(), rng);
    
    // 1. DETECTAR HUNTER ADJACENTE (distância 1)
    int hunterIndex = -1;
    int hunterX = -1, hunterY = -1;
    
    // std::cout << "🔍 Verificando hunters ADJACENTES (distância 1):\n";
    for (int i = 0; i < 4; i++) {
        Direction dir = shuffledDirections[i];
        int adjX = x, adjY = y;
        cell.randomWalk(adjX, adjY, dir);
        
        std::string dirName;
        switch(dir) {
            case NORTH: dirName = "NORTE"; break;
            case SOUTH: dirName = "SUL"; break;
            case EAST: dirName = "LESTE"; break;
            case WEST: dirName = "OESTE"; break;
        }
        
        std::string gridVal = getGridValue(adjX, adjY);
        // std::cout << "  " << dirName << " (" << adjX << "," << adjY << ") = '" << gridVal << "'";
        
        if (gridVal == "N") {
            hunterIndex = i;
            hunterX = adjX;
            hunterY = adjY;
            // std::cout << " <- HUNTER ENCONTRADO!" << std::endl;
            break;
        }
        // std::cout << std::endl;
    }
    //std::cin.get();
    
    std::optional<std::pair<int, int>> newPosition = std::nullopt;
    bool isFleeing = false;
    
    // 2. CASO 1: TEM HUNTER ADJACENTE → FUGE
    if (hunterIndex != -1) {
        isFleeing = true;
        // std::cout << "\n⚠️ HUNTER ADJACENTE encontrado em (" << hunterX << "," << hunterY << ")!" << std::endl;
        // std::cout << "🦁 ESCAPER VAI FUGIR na direção oposta!" << std::endl;
        //std::cin.get();
        
        Direction hunterDir = shuffledDirections[hunterIndex];
        
        Direction oppositeDir;
        std::string oppDirName;
        switch(hunterDir) {
            case NORTH: oppositeDir = SOUTH; oppDirName = "SUL"; break;
            case SOUTH: oppositeDir = NORTH; oppDirName = "NORTE"; break;
            case EAST:  oppositeDir = WEST; oppDirName = "OESTE"; break;
            case WEST:  oppositeDir = EAST; oppDirName = "LESTE"; break;
        }
        
        // std::cout << "  Direção do hunter: " << (hunterDir == NORTH ? "NORTE" : hunterDir == SOUTH ? "SUL" : hunterDir == EAST ? "LESTE" : "OESTE") << std::endl;
        // std::cout << "  Direção oposta (fuga): " << oppDirName << std::endl;
        //std::cin.get();
        
        int newX = x, newY = y;
        cell.randomWalk(newX, newY, oppositeDir);
        
        std::string targetType = getGridValue(newX, newY);
        //std::cout << "  Posição de fuga: (" << newX << "," << newY << ") = '" << targetType << "'" << std::endl;
        
        if (targetType == "L") {
            newPosition = std::make_pair(newX, newY);
            // std::cout << "  ✅ Posição LIVRE! Vai se mover para (" << newX << "," << newY << ")" << std::endl;
        } 
        // else {
        //     std::cerr << "  ❌ Posição OCUPADA! Não vai se mover." << std::endl;
        // }
        //std::cin.get();
    } 
    // 3. CASO 2: NÃO TEM HUNTER ADJACENTE → VERIFICA HUNTER NO RAIO
    else {
        // Verificar se existe hunter dentro do searchRadius (2)
        int currentDensity = countTargetsAround(x, y, {"N"}, 2);
        
        // std::cout << "\n✅ NENHUM hunter adjacente encontrado." << std::endl;
        // std::cout << "📊 Densidade de hunters no raio 2: " << currentDensity << std::endl;
        //std::cin.get();
        
        if (currentDensity > 0) {
            // Tem hunter no raio → usa estratégia de densidade
            // std::cout << "🔍 HUNTERS encontrados no raio! Usando ESTRATÉGIA DE DENSIDADE..." << std::endl;
            // std::cout << "  (Movendo para direção com MENOR densidade de hunters)" << std::endl;
            //std::cin.get();
            
            int minDensity = currentDensity;
            std::vector<Direction> bestDirections;
            
            for (Direction dir : shuffledDirections) {
                int tempX = x, tempY = y;
                cell.randomWalk(tempX, tempY, dir);
                
                std::string cellType = getGridValue(tempX, tempY);
                if (cellType != "L") {
                    continue;
                }
                
                int neighborDensity = countTargetsAround(tempX, tempY, {"N"}, 2);
                
                std::string dirName;
                switch(dir) {
                    case NORTH: dirName = "NORTE"; break;
                    case SOUTH: dirName = "SUL"; break;
                    case EAST: dirName = "LESTE"; break;
                    case WEST: dirName = "OESTE"; break;
                }
                // std::cout << "  " << dirName << ": densidade = " << neighborDensity << std::endl;
                
                if (neighborDensity < minDensity) {
                    minDensity = neighborDensity;
                    bestDirections.clear();
                    bestDirections.push_back(dir);
                } else if (neighborDensity == minDensity) {
                    bestDirections.push_back(dir);
                }
            }
            
            if (!bestDirections.empty()) {
                std::shuffle(bestDirections.begin(), bestDirections.end(), rng);
                Direction bestDir = bestDirections.front();
                
                int newX = x, newY = y;
                cell.randomWalk(newX, newY, bestDir);
                newPosition = std::make_pair(newX, newY);
                
                std::string dirName;
                switch(bestDir) {
                    case NORTH: dirName = "NORTE"; break;
                    case SOUTH: dirName = "SUL"; break;
                    case EAST: dirName = "LESTE"; break;
                    case WEST: dirName = "OESTE"; break;
                }
                // std::cout << "  ✅ Melhor direção: " << dirName << " para (" << newX << "," << newY << ")" << std::endl;
            } 
            // else {
            //     std::cerr << "  ❌ Nenhuma direção livre encontrada!" << std::endl;
            // }
            //std::cin.get();
            
        } else {
            // Não tem hunter no raio → movimento aleatório
            // std::cout << "🎲 NENHUM hunter no raio! Usando MOVIMENTO ALEATÓRIO..." << std::endl;
            //std::cin.get();
            
            std::uniform_int_distribution<int> dirDist(0, 3);
            Direction randomDir = static_cast<Direction>(dirDist(rng));
            
            int newX = x, newY = y;
            cell.randomWalk(newX, newY, randomDir);
            
            std::string targetType = getGridValue(newX, newY);
            std::string dirName;
            switch(randomDir) {
                case NORTH: dirName = "NORTE"; break;
                case SOUTH: dirName = "SUL"; break;
                case EAST: dirName = "LESTE"; break;
                case WEST: dirName = "OESTE"; break;
            }
            // std::cout << "  Direção aleatória: " << dirName << " (" << newX << "," << newY << ") = '" << targetType << "'" << std::endl;
            
            if (targetType == "L") {
                newPosition = std::make_pair(newX, newY);
                // std::cout << "  ✅ Posição LIVRE! Vai se mover." << std::endl;
            } 
            // else {
            //     std::cerr << "  ❌ Posição OCUPADA! Não vai se mover." << std::endl;
            // }
            //std::cin.get();
        }
    }
    
    // 4. APLICAR MOVIMENTO
    if (newPosition.has_value()) {
        auto [newX, newY] = newPosition.value();
        
        // std::cout << "\n🚀 APLICANDO MOVIMENTO..." << std::endl;
        
        if (getGridValue(newX, newY) != "L") {
            std::cerr << "  ❌ ERRO: Posição destino não está mais livre! Abortando." << std::endl;
            return;
        }
        
        if (getGridValue(x, y) != "O") {
            std::cerr << "  ❌ ERRO: Posição origem não tem escaper! Abortando." << std::endl;
            return;
        }
        
        // Move
        // std::cout << "  Limpando posição antiga (" << x << "," << y << ")" << std::endl;
        setGridValue(x, y, "L");
        
        // std::cout << "  Movendo escaper para (" << newX << "," << newY << ")" << std::endl;
        cell.changePosition(newX, newY);
        
        // std::cout << "  Marcando nova posição como 'O'" << std::endl;
        setGridValue(newX, newY, "O");
        
        // std::cout << "✅ ESCAPER MOVEU de (" << x << "," << y << ") para (" << newX << "," << newY << ")" << std::endl;
        
        // CRIAR RASTRO (apenas se estiver fugindo de hunter adjacente)
        //const double TRAIL_PROBABILITY = 0.5;
        std::uniform_real_distribution<double> probDist(0.0, 1.0);
        double roll = probDist(rng);
        
        // std::cout << "\n💨 CRIANDO RASTRO? isFleeing=" << isFleeing << " roll=" << roll << std::endl;
        
        if (isFleeing && roll <= TRAIL_PROBABILITY) {
            int newId = tempObstacles.size() + 1;
            tempObstacles.emplace_back("T", newId, x, y);
            setGridValue(x, y, "T");
            // std::cout << "✅ RASTRO CRIADO na posição antiga (" << x << "," << y << ") ID=" << newId << std::endl;
        } 
        // else if (isFleeing) {
        //     std::cout << "❌ NÃO CRIOU RASTRO: probabilidade falhou (" << roll << " > " << TRAIL_PROBABILITY << ")" << std::endl;
        // } else {
        //     std::cout << "❌ NÃO CRIOU RASTRO: não estava fugindo de hunter adjacente (isFleeing=false)" << std::endl;
        // }
    } 
    //else {
    //     std::cout << "\n❌ NENHUM MOVIMENTO (newPosition is null)" << std::endl;
    //     std::cout << "   O escaper ficou na posição (" << x << "," << y << ")" << std::endl;
    // }
    
    // std::cout << "\n========================================\n";
    // std::cout << "🏁 FIM DO MOVIMENTO DO ESCAPER" << std::endl;
    // std::cout << "========================================\n";
    //std::cin.get();
}

int CellLattice::countTargetsAround(int x, int y,
    const std::vector<std::string>& types,
    int searchRadius) const
{
    int count = 0;
    
    // Itera apenas sobre o quadrado ao redor da posição
    for (int dx = -searchRadius; dx <= searchRadius; dx++) {
        for (int dy = -searchRadius; dy <= searchRadius; dy++) {
            if (dx == 0 && dy == 0) continue;
            
            // Calcula posição com wrapping toroidal
            int checkX = (x + dx + m_width) % m_width;
            int checkY = (y + dy + m_height) % m_height;
            
            std::string cellType = getGridValue(checkX, checkY);
            
            // Verifica se o tipo está na lista de tipos procurados
            for (const auto& targetType : types) {
                if (cellType == targetType) {
                    count++;
                    break;
                }
            }
        }
    }
    
    return count;
}



void CellLattice::moveNormalCell(Cell& cell,
    std::vector<Cell>& normalCells, std::vector<Cell>& cancerCells,
    std::mt19937& rng, bool checkCancer, std::vector<temp_obs>& tempObstacles)
{
    static int totalCalls = 0;
    static int preyFoundCount = 0;
    static int captureSuccess = 0;
    static int captureFailed = 0;
    static int movesMade = 0;
    
    totalCalls++;
    
    int x = cell.getPositionX();
    int y = cell.getPositionY();
    
    // std::cout << "\n========================================\n";
    // std::cout << "🔫 MOVENDO CHASER na posição (" << x << "," << y << ")" << std::endl;
    // std::cout << "========================================\n";
    //std::cin.get();
    
    const std::array<Direction, 4> directions = {NORTH, EAST, SOUTH, WEST};
    std::array<Direction, 4> shuffledDirections = directions;
    std::shuffle(shuffledDirections.begin(), shuffledDirections.end(), rng);
    
    // 1. VERIFICAR PRESA ADJACENTE (escaper)
    int preyIndex = -1;
    int preyX = -1, preyY = -1;
    
    // std::cout << "🔍 Verificando presas adjacentes (escaper 'O'):\n";
    for (int i = 0; i < 4; i++) {
        Direction dir = shuffledDirections[i];
        int adjX = x, adjY = y;
        cell.randomWalk(adjX, adjY, dir);
        
        std::string dirName;
        switch(dir) {
            case NORTH: dirName = "NORTE"; break;
            case SOUTH: dirName = "SUL"; break;
            case EAST: dirName = "LESTE"; break;
            case WEST: dirName = "OESTE"; break;
        }
        
        std::string gridVal = getGridValue(adjX, adjY);
        // std::cout << "  " << dirName << " (" << adjX << "," << adjY << ") = '" << gridVal << "'";
        
        if (gridVal == "O") {
            preyIndex = i;
            preyX = adjX;
            preyY = adjY;
            preyFoundCount++;
            // std::cout << " <- PRESA ENCONTRADA!" << std::endl;
            break;
        }
        // std::cout << std::endl;
    }
    //std::cin.get();
    
    std::optional<std::pair<int, int>> newPosition = std::nullopt;
    int capturedId = -1;
    
    // 2. CASO 1: TEM PRESA ADJACENTE → CAPTURA
    if (preyIndex != -1) {
        // std::cout << "\n⚠️ PRESA ADJACENTE encontrada em (" << preyX << "," << preyY << ")!" << std::endl;
        // std::cout << "🔫 CHASER VAI CAPTURAR!" << std::endl;
        //std::cin.get();
        
        Direction preyDir = shuffledDirections[preyIndex];
        
        int captureX = preyX;
        int captureY = preyY;
        
        // std::cout << "  Posição da presa: (" << captureX << "," << captureY << ")" << std::endl;
        // std::cout << "  Verificando se escaper ainda está lá..." << std::endl;
        //std::cin.get();
        
        // Verificar se o escaper ainda existe
        bool escaperExists = false;
        for (const auto& escaper : cancerCells) {
            if (escaper.getPositionX() == captureX && escaper.getPositionY() == captureY) {
                escaperExists = true;
                break;
            }
        }
        
        std::string gridVal = getGridValue(captureX, captureY);
        // std::cout << "  Grid na posição: '" << gridVal << "'" << std::endl;
        // std::cout << "  Escaper no vetor: " << (escaperExists ? "SIM" : "NÃO") << std::endl;
        //std::cin.get();
        
        if (escaperExists && gridVal == "O") {
            // Captura a presa
            for (auto it = cancerCells.begin(); it != cancerCells.end(); ) {
                if (it->getPositionX() == captureX && it->getPositionY() == captureY) {
                    capturedId = it->getId();
                    captureSuccess++;
                    // std::cout << "\n✅ CAPTURA REALIZADA! Escaper ID=" << capturedId << " capturado!" << std::endl;
                    setGridValue(captureX, captureY, "L");
                    it = cancerCells.erase(it);
                    break;
                } else {
                    ++it;
                }
            }
            
            // Move para a posição da presa capturada
            newPosition = std::make_pair(captureX, captureY);
            
            // std::cout << "  Chaser vai se mover para (" << captureX << "," << captureY << ")" << std::endl;
            //std::cin.get();
        } else {
            captureFailed++;
            std::cerr << "\n❌ CAPTURA FALHOU! Escaper não está mais na posição!" << std::endl;
            std::cerr << "  (Pode ter sido capturado por outro chaser ou se movido)" << std::endl;
            //std::cin.get();
            
            // Ainda assim, tenta mover para a posição se estiver vazia
            if (gridVal == "L") {
                newPosition = std::make_pair(captureX, captureY);
                // std::cout << "  Posição agora está vazia. Chaser vai se mover para lá." << std::endl;
                //std::cin.get();
            }
        }
    } 
    // 3. CASO 2: NÃO TEM PRESA ADJACENTE → SEGUE MAIOR DENSIDADE DE ESCAPERS
    else {
        // std::cout << "\n✅ NENHUMA presa adjacente encontrada." << std::endl;
        
        // Verificar se existe escaper no raio
        int currentDensity = countTargetsAround(x, y, {"O"}, 2);
        // std::cout << "📊 Densidade de escapers no raio 2: " << currentDensity << std::endl;
        //std::cin.get();
        
        // if (currentDensity > 0) {
        //     std::cout << "🔍 ESCAPERS encontrados no raio! Usando ESTRATÉGIA DE DENSIDADE..." << std::endl;
        //     std::cout << "  (Movendo para direção com MAIOR densidade de escapers)" << std::endl;
        //     //std::cin.get();
        // } 
        // else {
        //     std::cout << "🎲 NENHUM escaper no raio! Usando MOVIMENTO ALEATÓRIO..." << std::endl;
        //     //std::cin.get();
        // }
        
        int maxDensity = currentDensity;
        std::vector<Direction> bestDirections;
        
        // std::cout << "\n📊 Analisando densidade em cada direção:\n";
        for (Direction dir : shuffledDirections) {
            int tempX = x, tempY = y;
            cell.randomWalk(tempX, tempY, dir);
            
            std::string cellType = getGridValue(tempX, tempY);
            
            std::string dirName;
            switch(dir) {
                case NORTH: dirName = "NORTE"; break;
                case SOUTH: dirName = "SUL"; break;
                case EAST: dirName = "LESTE"; break;
                case WEST: dirName = "OESTE"; break;
            }
            
            // std::cout << "  " << dirName << " (" << tempX << "," << tempY << ") = '" << cellType << "'";
            
            if (cellType != "L" && cellType != "O") {
                // std::cout << " -> OCUPADO, ignorando" << std::endl;
                continue;
            }
            
            int neighborDensity = countTargetsAround(tempX, tempY, {"O"}, 2);
            // std::cout << " -> densidade = " << neighborDensity;
            
            if (neighborDensity > maxDensity) {
                maxDensity = neighborDensity;
                bestDirections.clear();
                bestDirections.push_back(dir);
                // std::cout << " -> NOVO MELHOR!" << std::endl;
            } else if (neighborDensity == maxDensity) {
                bestDirections.push_back(dir);
                // std::cout << " -> EMPATE" << std::endl;
            } 
            // else {
            //     std::cout << " -> PIOR" << std::endl;
            // }
        }
        //std::cin.get();
        
        // std::cout << "\n📊 Melhores direções encontradas: " << bestDirections.size() << std::endl;
        
        if (!bestDirections.empty()) {
            std::shuffle(bestDirections.begin(), bestDirections.end(), rng);
            Direction bestDir = bestDirections.front();
            
            int newX = x, newY = y;
            cell.randomWalk(newX, newY, bestDir);
            newPosition = std::make_pair(newX, newY);
            
            std::string dirName;
            switch(bestDir) {
                case NORTH: dirName = "NORTE"; break;
                case SOUTH: dirName = "SUL"; break;
                case EAST: dirName = "LESTE"; break;
                case WEST: dirName = "OESTE"; break;
            }
            // std::cout << "  ✅ Melhor direção: " << dirName << " para (" << newX << "," << newY << ")" << std::endl;
        } 
        else {
            // std::cout << "  ❌ Nenhuma direção válida encontrada!" << std::endl;
            
            // Fallback: movimento aleatório
            // std::cout << "\n🎲 Tentando movimento aleatório como fallback..." << std::endl;
            std::uniform_int_distribution<int> dirDist(0, 3);
            Direction randomDir = static_cast<Direction>(dirDist(rng));
            
            int newX = x, newY = y;
            cell.randomWalk(newX, newY, randomDir);
            
            std::string cellType = getGridValue(newX, newY);
            std::string dirName;
            switch(randomDir) {
                case NORTH: dirName = "NORTE"; break;
                case SOUTH: dirName = "SUL"; break;
                case EAST: dirName = "LESTE"; break;
                case WEST: dirName = "OESTE"; break;
            }
            // std::cout << "  Direção aleatória: " << dirName << " (" << newX << "," << newY << ") = '" << cellType << "'" << std::endl;
            
            if (cellType == "L" || cellType == "O") {
                newPosition = std::make_pair(newX, newY);
                // std::cout << "  ✅ Posição válida! Vai se mover." << std::endl;
                
                // Se for um escaper, captura
                if (cellType == "O") {
                    // std::cout << "  🎯 Encontrou um escaper! Capturando..." << std::endl;
                    for (auto it = cancerCells.begin(); it != cancerCells.end(); ) {
                        if (it->getPositionX() == newX && it->getPositionY() == newY) {
                            capturedId = it->getId();
                            captureSuccess++;
                            // std::cout << "  ✅ CAPTURA NO FALLBACK! Escaper ID=" << capturedId << std::endl;
                            setGridValue(newX, newY, "L");
                            it = cancerCells.erase(it);
                            break;
                        } else {
                            ++it;
                        }
                    }
                }
            } 
            // else {
            //     std::cout << "  ❌ Posição ocupada! Não vai se mover." << std::endl;
            // }
        }
        //std::cin.get();
    }
    
    // 4. APLICAR MOVIMENTO
    if (newPosition.has_value()) {
        auto [newX, newY] = newPosition.value();
        
        // std::cout << "\n🚀 APLICANDO MOVIMENTO DO CHASER..." << std::endl;
        
        // Verificar se a posição ainda está livre
        std::string currentType = getGridValue(newX, newY);
        if (currentType != "L" && currentType != "O") {
            std::cerr << "  ❌ Posição destino ocupada por '" << currentType << "'! Abortando." << std::endl;
            return;
        }
        
        if (getGridValue(x, y) != "N") {
            std::cerr << "  ❌ Posição origem não tem chaser! Abortando." << std::endl;
            return;
        }
        
        // Move
        // std::cout << "  Limpando posição antiga (" << x << "," << y << ")" << std::endl;
        setGridValue(x, y, "L");
        
        // std::cout << "  Movendo chaser para (" << newX << "," << newY << ")" << std::endl;
        cell.changePosition(newX, newY);
        
        // std::cout << "  Marcando nova posição como 'N'" << std::endl;
        setGridValue(newX, newY, "N");
        
        movesMade++;
        // std::cout << "✅ CHASER MOVEU de (" << x << "," << y << ") para (" << newX << "," << newY << ")" << std::endl;
    } 
    // else {
    //     std::cout << "\n❌ NENHUM MOVIMENTO (newPosition is null)" << std::endl;
    //     std::cout << "   O chaser ficou na posição (" << x << "," << y << ")" << std::endl;
    // }
    
    // Estatísticas
    // if (totalCalls % 100 == 0) {
    //     std::cout << "\n========================================\n";
    //     std::cout << "📊 ESTATÍSTICAS DO CHASER (após " << totalCalls << " chamadas)" << std::endl;
    //     std::cout << "  Presas encontradas: " << preyFoundCount << std::endl;
    //     std::cout << "  Capturas bem sucedidas: " << captureSuccess << std::endl;
    //     std::cout << "  Capturas falhas: " << captureFailed << std::endl;
    //     std::cout << "  Movimentos realizados: " << movesMade << std::endl;
    //     std::cout << "========================================\n";
    // }
    
    // std::cout << "\n========================================\n";
    // std::cout << "🏁 FIM DO MOVIMENTO DO CHASER" << std::endl;
    // std::cout << "========================================\n";
    //std::cin.get();
}