#include "cell.h"
#include "cell_lattice.h"
#include <algorithm>

Cell::Cell(const std::string& type, int id, int positionX, int positionY, int searchRadius)
    : m_type(type), m_id(id), m_positionX(positionX), m_positionY(positionY), m_searchRadius(0)
{}

std::vector<Cell> Cell::loadFromCSV(const std::string& filename, 
                                     const std::string& type,
                                     int defaultSearchRadius) {
    std::vector<Cell> cells;
    std::ifstream file(filename);
    
    if (!file.is_open()) {
        std::cerr << "Erro ao abrir arquivo: " << filename << std::endl;
        return cells;
    }
    
    std::string line;
    bool isFirstLine = true;
    int lineCount = 0;
    
    while (std::getline(file, line)) {
        lineCount++;
        
        if (isFirstLine) {
            isFirstLine = false;
            continue;
        }
        
        line.erase(0, line.find_first_not_of(" \t\r\n"));
        line.erase(line.find_last_not_of(" \t\r\n") + 1);
        
        if (line.empty()) continue;
        
        std::stringstream ss(line);
        std::string x_str, y_str, id_str;
        
        if (std::getline(ss, x_str, ',') && 
            std::getline(ss, y_str, ',') && 
            std::getline(ss, id_str, ',')) {
            
            try {
                int x = std::stoi(x_str);
                int y = std::stoi(y_str);
                int id = std::stoi(id_str);
                
                // Usar o construtor com searchRadius
                Cell cell(type, id, x, y, defaultSearchRadius);
                cells.push_back(cell);
                
                std::cout << "Carregada célula ID=" << id 
                          << " Tipo=" << type 
                          << " Pos=(" << x << "," << y << ")"
                          << " Raio=" << defaultSearchRadius << "\n";
                          
            } catch (const std::exception& e) {
                std::cerr << "Erro na linha " << lineCount << ": " << e.what() << std::endl;
            }
        }
    }
    
    file.close();
    std::cout << "Total carregado: " << cells.size() << " células do tipo " << type << std::endl;
    return cells;
}

void Cell::changePosition(int newX, int newY) 
{
    if (newX < 0 || newX >= HEIGHT || newY < 0 || newY >= WIDTH) 
    {
        logError("CRITICAL ERROR: Attempted to move cell " + std::to_string(m_id) +
         " to an invalid position (" + std::to_string(newX) + "," + std::to_string(newY) + ")\n" +
         "Current position: (" + std::to_string(m_positionX) + "," + std::to_string(m_positionY) + ")\n" +
         "Stack trace:");
        
        // Force correction using modulo arithmetic
        newX = (newX % HEIGHT + HEIGHT) % HEIGHT;
        newY = (newY % WIDTH + WIDTH) % WIDTH;
        
        std::cin.get();
    }
    m_positionX = newX;
    m_positionY = newY;
}

void Cell::randomWalk(int& x, int& y, Direction move) 
{
    int originalX = x, originalY = y; // Store original position
    WIDTH = 128;
    HEIGHT = WIDTH;
    switch (move) {
        case SOUTH:
            y = (y - 1 + HEIGHT) % HEIGHT;
            break;
        case NORTH:
            y = (y + 1) % HEIGHT;
            break;
        case EAST:
            x = (x + 1) % WIDTH;
            break;
        case WEST:
            x = (x - 1 + WIDTH) % WIDTH;
            break;
    }

    // Validate movement and correct if necessary
    if (x < 0 || y < 0) 
    {
        logError("Failed to move cell from position: " + 
                 std::to_string(originalX) + "," + std::to_string(originalY));
        logError("Direction: " + std::to_string(move));
        logError("Attempted position: " + std::to_string(x) + "," + std::to_string(y));

        // Immediate correction using modulo arithmetic
        x = (x + WIDTH) % WIDTH;
        y = (y + HEIGHT) % HEIGHT;
        
        std::cin.get();
    }
}

std::string Cell::getType() const 
{
    return m_type;
}

int Cell::getId() const 
{
    return m_id;
}

int Cell::getPositionX() const 
{
    return m_positionX;
}

int Cell::getPositionY() const 
{
    return m_positionY;
}

int Cell::getSearchRadius() const 
{
    return m_searchRadius;
}

void Cell::setSearchRadius(int searchRadius) 
{
    m_searchRadius = searchRadius;
}
