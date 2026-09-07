#pragma once
#ifndef CELL_LATTICE_H
#define CELL_LATTICE_H

#include <fstream>
#include <sstream>
#include <iostream>
#include <vector>
#include <algorithm> 
#include <random>            // for std::mt19937
#include "cell_lattice.h"
#include "utils.h" 
#include "cell.h"
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
    CellLattice(int width, int height);

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
    void placeObjects(std::vector<Cell>& chasers,
    std::vector<Cell>& escapers);

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
    bool verifyPlacement(const std::vector<Cell>& chasers, 
                                   const std::vector<Cell>& escapers) const;


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
    bool checkDuplicates(const std::vector<Cell>& chasers, const std::vector<Cell>& escapers, int width, int height);

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
    void printGrid() const;

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
    void setGridValue(int x, int y, const std::string& value);

    /**
     * @brief Counts the number of target cells around a specific position.
     * 
     * This method analyzes neighboring cells within a square radius around the
     * position (x, y), considering toroidal wrapping (edges that connect to each other).
     * Only cells whose type is present in the provided list are counted.
     * The center cell (original position) is ignored in the count.
     * 
     * @param x X-coordinate of the center cell (0 to m_width-1).
     * @param y Y-coordinate of the center cell (0 to m_height-1).
     * @param types Vector of cell type strings to search for (target types).
     * @param searchRadius Radius of the square neighborhood to search (non-negative).
     * 
     * @return Number of neighboring cells whose type matches any of the target types.
     * 
     * @note The search area is a square of size (2*searchRadius+1) x (2*searchRadius+1),
     *       excluding the center cell.
     * @note Toroidal wrapping ensures that cells on the edges wrap around to the
     *       opposite side of the grid.
     * 
     * @pre m_width and m_height must be properly initialized.
     * @pre x must be in range [0, m_width-1].
     * @pre y must be in range [0, m_height-1].
     * @pre searchRadius must be >= 0.
     */
    int countTargetsAround(int x, int y,
        const std::vector<std::string>& types,
        int searchRadius = 2) const;
                     
    /**
     * @brief Moves a normal cell (chaser/hunter) with intelligent hunting behavior.
     * 
     * This method implements a multi-layered hunting strategy for normal cells:
     * 1. If a prey (cancer cell 'O') is adjacent (distance 1), the chaser captures it
     *    immediately and moves into its position.
     * 2. If no adjacent prey but prey exist within searchRadius (2), the chaser moves
     *    toward the direction with the highest prey density.
     * 3. If no prey are detected within the radius, the chaser moves randomly.
     * 
     * The method maintains internal static counters for performance tracking:
     * total calls, prey found, capture success/failure, and moves made.
     * 
     * @param cell Reference to the normal cell (chaser) being moved.
     * @param normalCells Vector of all normal cells (unused, kept for interface consistency).
     * @param cancerCells Vector of cancer cells (prey) - the chaser removes prey from this list.
     * @param rng Random number generator used for shuffling directions and random movement.
     * @param checkCancer Boolean flag to enable cancer checking (unused).
     * @param tempObstacles Vector of temporary obstacles (unused, kept for interface consistency).
     * 
     * @note The method performs toroidal wrapping when calculating adjacent positions.
     * @note When a prey is captured, it is erased from the cancerCells vector and its
     *       grid cell is set to empty ('L') before the chaser moves into it.
     * @note The method validates that the source cell contains a normal cell ('N')
     *       before moving.
     * @note If capture fails (prey moved before capture), the chaser may still move
     *       to the target position if it becomes empty.
     * 
     * @pre The grid dimensions (m_width, m_height) must be properly initialized.
     * @pre The cell position must be valid within the grid bounds.
     * 
     * @warning The method uses commented-out debug output that can be enabled for
     *          troubleshooting by uncommenting the std::cout and std::cin.get() lines.
     * @warning Static counters accumulate across all calls and are not reset - this
     *          is intentional for tracking total simulation statistics.
     * 
     * @see countTargetsAround() For prey density calculation.
     * @see Cell::randomWalk() For position calculation based on direction.
     */
    void moveNormalCell(Cell& cell,
        std::vector<Cell>& normalCells, std::vector<Cell>& cancerCells,
        std::mt19937& rng, bool checkCancer, std::vector<temp_obs>& tempObstacles);

    
     /**
     * @brief Moves a cancer cell (escaper) with intelligent fleeing behavior.
     * 
     * This method implements a multi-layered movement strategy for cancer cells:
     * 1. If a hunter cell is adjacent (distance 1), the cancer cell flees in the
     *    opposite direction.
     * 2. If no adjacent hunter but hunters exist within searchRadius (2), the cell
     *    moves toward the direction with the lowest hunter density.
     * 3. If no hunters are detected within the radius, the cell moves randomly.
     * 
     * When fleeing from an adjacent hunter, there's a chance (TRAIL_PROBABILITY)
     * to leave a temporary obstacle trail at the previous position.
     * 
     * @param cell Reference to the cancer cell being moved.
     * @param normalCells Vector of normal cells (unused, kept for interface consistency).
     * @param cancerCells Vector of all cancer cells (unused, kept for interface consistency).
     * @param rng Random number generator used for shuffling directions and probability rolls.
     * @param checkCancer Boolean flag to enable cancer checking (unused).
     * @param tempObstacles Vector of temporary obstacles where trails will be added.
     * 
     * @note The method performs toroidal wrapping when calculating adjacent positions.
     * @note Movement only occurs if the target cell is empty ('L').
     * @note The method validates that the source cell contains a cancer cell ('O')
     *       and the target cell is empty before moving.
     * 
     * @pre The grid dimensions (m_width, m_height) must be properly initialized.
     * @pre The cell position must be valid within the grid bounds.
     * @pre TRAIL_PROBABILITY must be defined (typically 0.5) for trail creation.
     * 
     * @warning The method uses commented-out debug output that can be enabled for
     *          troubleshooting by uncommenting the std::cout and std::cin.get() lines.
     * 
     * @see countTargetsAround() For hunter density calculation.
     * @see Cell::randomWalk() For position calculation based on direction.
     */
    void moveCancerCell(Cell& cell,
    std::vector<Cell>& normalCells, std::vector<Cell>& cancerCells,
    std::mt19937& rng, bool checkCancer,std::vector<temp_obs>& tempObstacles);

};

#endif // CELL_LATTICE_H