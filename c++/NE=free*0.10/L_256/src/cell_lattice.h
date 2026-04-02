#pragma once
#ifndef CELL_LATTICE_H
#define CELL_LATTICE_H

#include "cell_lattice.h"
#include "utils.h" // for fileExists, logError
#include "cell.h"
#include <fstream>
#include <sstream>
#include <iostream>
#include <vector>
#include <algorithm> 
#include <random>            // for std::mt19937
#include "obstacle.h"        // for Obstacle class
#include "temp_obs.h"

class Cell;

/**
 * @class CellLattice
 * @brief Represents a 2D grid environment for cell simulation
 * 
 * This class manages a grid-based environment where cells and obstacles
 * are placed and interact. It handles movement, collision detection,
 * and spatial queries.
 */
class CellLattice 
{
    private:
    int m_width;                                /**< Width of the grid */
    int m_height;                               /**< Height of the grid */
    std::vector<std::vector<std::string>> m_grid; /**< 2D grid storing cell types */

    
    public:
    /**
     * @brief Constructs a new CellLattice object
     * 
     * @param width Width of the grid
     * @param height Height of the grid
     */
    CellLattice(int width, int height);
    
    /**
     * @brief Calculates Manhattan distance with toroidal wrapping
     * 
     * @param x1 First point X coordinate
     * @param y1 First point Y coordinate
     * @param x2 Second point X coordinate
     * @param y2 Second point Y coordinate
     * @return double Manhattan distance
     */


    /**
     * @brief Places objects (chasers, escapers) on the grid
     * @param chasers Vector of chasers
     * @param escapers Vector of chasers
     */
    void placeObjects(std::vector<Cell>& chasers,
        std::vector<Cell>& escapers);

    /**
     * @brief Verify if the objects positoned are in the same quantitie as define
     * @param chasers Vector of chasers
     * @param escapers Vector of chasers
     */

    bool verifyPlacement(const std::vector<Cell>& chasers, 
                                   const std::vector<Cell>& escapers) const;


    /**
     * @brief Verify if the objects are be sobreposition for another
     * @param chasers Vector of chasers
     * @param escapers Vector of chasers
     * @param width Size of the grid
     * @param width Size of the grid
     */
    bool checkDuplicates(const std::vector<Cell>& chasers, const std::vector<Cell>& escapers, int width, int height);

    
    double calculateDistance(int x1, int y1, int x2, int y2) const;
    
    /**
     * @brief Prints the grid to console
     */
    void printGrid() const;

    //GETTERS
    /**
     * @brief Sets a value in the grid
     * 
     * @param x X coordinate
     * @param y Y coordinate
     * @param value Value to set
     */

    /**
     * @brief Gets a value from the grid
     * 
     * @param x X coordinate
     * @param y Y coordinate
     * @return std::string Value at position
     */
    std::string getGridValue(int x, int y) const;

    /**
     * @brief Gets the grid width
     * @return int Grid width
     */
    int getWidth() const { return m_width; }
    
    /**
     * @brief Gets the grid height
     * @return int Grid height
     */
    int getHeight() const { return m_height; }
    
    //SETTERS
    /**
     * @brief Sets a value in the grid
     * 
     * @param x X coordinate
     * @param y Y coordinate
     * @param value Value to set
     */
    void setGridValue(int x, int y, const std::string& value);

    
        /**
     * @brief Places objects (obstacles, normal cells, cancer cells) on the grid
     * 
     * @param obstacles Vector of obstacles
     * @param normalCells Vector of normal cells
     * @param cancerCells Vector of cancer cells
     * @param numObstacles Number of obstacles
     * @param numNormal Number of normal cells
     * @param numCancer Number of cancer cells
     * @param rng Random number generator
     * @param searchRadiusNormal Search radius for normal cells
     * @param searchRadiusCancer Search radius for cancer cells
     * @param run Current run identifier
     * @return true if placement successful
     * @return false if placement failed
     */
    bool placeObjects(std::vector<Obstacle>& obstacles,
        std::vector<Cell>& normalCells,
        std::vector<Cell>& cancerCells,
        int numObstacles, int numNormal, int numCancer,
        std::mt19937& rng,
        int searchRadiusNormal, int searchRadiusCancer, int run);
    
    
    
    /**
     * @brief Counts targets around a position
     * 
     * @param x X coordinate
     * @param y Y coordinate
     * @param agents Vector of agents to check
     * @param types Types of agents to count
     * @param searchRadius Search radius
     * @return int Number of targets found
     */
    int countTargetsAround(int x, int y,
        const std::vector<std::string>& types,
        int searchRadius = 2) const;
                     
    /**
     * @brief Moves a normal cell (good cell) according to its behavior
     * 
     * @param cell Cell to move
     * @param normalCells Vector of normal cells
     * @param cancerCells Vector of cancer cells
     * @param obstacles Vector of obstacles
     * @param rng Random number generator
     * @param checkCancer Whether to check cancer cells
     * @param searchRadius Search radius
     */
    void moveNormalCell(Cell& cell,
        std::vector<Cell>& normalCells, std::vector<Cell>& cancerCells,
        std::mt19937& rng, bool checkCancer, std::vector<temp_obs>& tempObstacles);

    void moveCancerCell(Cell& cell,
    std::vector<Cell>& normalCells, std::vector<Cell>& cancerCells,
    std::mt19937& rng, bool checkCancer,std::vector<temp_obs>& tempObstacles);

};

#endif // CELL_LATTICE_H