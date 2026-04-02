#pragma once

#include <string>
#include "cell_lattice.h"
#include <limits>
#include <vector>
class CellLattice;


/**
 * @enum Direction
 * @brief Represents the possible movement directions
 */
enum Direction 
{ 
    NORTH = 1,  /**< North direction */
    EAST = 0,   /**< East direction */
    SOUTH = 2,  /**< South direction */
    WEST = 3    /**< West direction */
};

/**
 * @class Cell
 * @brief Represents a cell in the simulation environment
 * 
 * This class manages cell properties, position, and movement behavior
 * within a bounded lattice environment.
 */
class Cell 
{
    private:
        std::string m_type;           /**< Type of the cell */
        int m_id;                     /**< Unique identifier of the cell */
        int m_positionX;              /**< X coordinate position */
        int m_positionY;              /**< Y coordinate position */
        int m_searchRadius;           /**< Search radius for cell operations */

    public:
    
    /**
    * @brief Constructs a new Cell object
    * 
    * @param type Type of the cell
    * @param id Unique identifier
    * @param positionX Initial X coordinate
    * @param positionY Initial Y coordinate
    */
    Cell(const std::string& type, int id, int positionX, int positionY, int searchRadius);

    /**
     * @brief Updates coordinates based on a movement direction with toroidal wrapping.
     * 
     * This method modifies the given x and y coordinates by moving one step in the
     * specified direction. The movement wraps around the grid boundaries using
     * modulo arithmetic (toroidal topology). NORTH increases Y, SOUTH decreases Y,
     * EAST increases X, WEST decreases X.
     * 
     * The method validates that the resulting coordinates are non-negative and
     * corrects them if necessary. Note that due to the modulo operations, coordinates
     * should always be within [0, WIDTH-1] and [0, HEIGHT-1] after movement.
     * 
     * @param x Reference to the X coordinate (row index). Modified in place.
     * @param y Reference to the Y coordinate (column index). Modified in place.
     * @param move The direction to move: NORTH, SOUTH, EAST, or WEST.
     * 
     * @note WIDTH and HEIGHT are hardcoded to 256 within this method, overriding any
     *       member variables or external definitions. This is a potential bug if the
     *       grid size differs elsewhere in the codebase.
     * @note Direction mapping:
     *       - NORTH: Y increases (moves down in typical matrix indexing)
     *       - SOUTH: Y decreases (moves up in typical matrix indexing)
     *       - EAST:  X increases (moves right)
     *       - WEST:  X decreases (moves left)
     * @note The modulo formula for negative numbers: (y - 1 + HEIGHT) % HEIGHT ensures
     *       proper wrapping for SOUTH direction.
     * 
     * @warning This method contains a critical issue: WIDTH and HEIGHT are locally
     *          set to 256, ignoring any member variables with the same names. The
     *          method should use member variables or passed parameters instead.
     * @warning The correction block checks `if (x < 0 || y < 0)` which should never
     *          be true due to the modulo operations. However, integer overflow or
     *          unexpected input could trigger this.
     * @warning The method calls `std::cin.get()` when an error occurs, pausing
     *          execution and waiting for user input.
     * 
     * @bug WIDTH and HEIGHT are hardcoded to 256 inside the method, overriding any
     *      member variables. Use `this->WIDTH` and `this->HEIGHT` or remove these lines.
     * 
     * @see Cell::changePosition() For updating cell position with validation.
     */
    void randomWalk(int& x, int& y, Direction move);

    /**
     * @brief Loads cell data from a CSV file and creates Cell objects.
     * 
     * This static method reads cell configuration data from a CSV file and creates
     * Cell objects of the specified type. The CSV file is expected to have a header
     * line followed by data lines in the format: x,y,id
     * 
     * The method automatically skips empty lines and handles whitespace trimming.
     * 
     * @param filename Path to the CSV file to read.
     * @param type The type identifier for all cells loaded from this file
     *            (e.g., "N" for normal cells, "O" for cancer cells).
     * @param defaultSearchRadius The search radius to assign to each loaded cell.
     * 
     * @return std::vector<Cell> A vector containing all successfully created Cell objects.
     *         Returns an empty vector if the file cannot be opened.
     * 
     * @note The first line of the CSV file is treated as a header and is skipped.
     * @note Each data line must contain exactly three comma-separated values: x, y, id.
     * @note Lines that are empty or contain only whitespace are ignored.
     * @note Error messages are printed to std::cerr for:
     *       - File open failures
     *       - Parsing errors (invalid integer conversion)
     * @note Success messages are printed to std::cout for each loaded cell and a summary.
     * 
     * @warning The method does not validate that x and y coordinates are within
     *          any specific grid bounds - this should be handled by the caller.
     * 
     * @see Cell::Cell() The constructor called with the provided parameters.
     * 
     * @example Expected CSV format:
     *          # Optional header (any content, will be skipped)
     *          10,20,101
     *          15,25,102
     *          30,35,103
     */
    static std::vector<Cell> loadFromCSV(const std::string& filename, 
                                         const std::string& type,
                                         int defaultSearchRadius = 0);  // valor padrão é 0

    /**
     * @brief Changes the cell's position with boundary validation and auto-correction.
     * 
     * This method updates the cell's coordinates after validating that the new position
     * is within the grid bounds. If the provided coordinates are out of bounds, the
     * method logs an error message and automatically corrects the position using
     * modulo arithmetic (toroidal wrapping) before updating.
     * 
     * The validation uses HEIGHT for X coordinates and WIDTH for Y coordinates.
     * Note the parameter order: newX is validated against HEIGHT, newY against WIDTH.
     * 
     * @param newX New X coordinate (row index) to move the cell to.
     * @param newY New Y coordinate (column index) to move the cell to.
     * 
     * @note The method uses HEIGHT for X-axis bounds checking and WIDTH for Y-axis
     *       bounds checking. Ensure these constants are correctly defined.
     * @note When coordinates are out of bounds, the correction formula uses:
     *       `(coord % bound + bound) % bound` which handles negative values correctly.
     * @note Error logging includes the cell ID, requested invalid position, and
     *       current position before correction.
     * 
     * @warning The method calls `std::cin.get()` after logging an error, which will
     *          pause execution waiting for user input. This may be undesirable in
     *          batch/automated simulations.
     * @warning The error message mentions a "stack trace" but no stack trace is
     *          actually printed - only the message text is logged.
     * @warning The parameter order (newX, newY) but validation uses (HEIGHT, WIDTH)
     *          suggests X corresponds to rows (height) and Y to columns (width).
     *          Ensure consistency throughout the codebase.
     * 
     * @see Cell::getPositionX() To retrieve the current X coordinate.
     * @see Cell::getPositionY() To retrieve the current Y coordinate.
     */
        void changePosition(int newX, int newY);
        
        // Getters
        /**
         * @brief Gets the cell type
         * @return std::string Type of the cell
         */
        std::string getType() const;

        /**
         * @brief Gets the cell unique identifier
         * @return int Unique ID
         */
        int getId() const;

        /**
         * @brief Gets the X coordinate position
         * @return int X coordinate
         */
        int getPositionX() const;
        
        /**
         * @brief Gets the Y coordinate position
         * @return int Y coordinate
         */
        int getPositionY() const; 

        /**
         * @brief Gets the current search radius
         * @return int Search radius value
         */
        int getSearchRadius() const;

        // Setters
        /**
         * @brief Sets the search radius for the cell
         * @param searchRadius New search radius value
         */
        void setSearchRadius(int searchRadius);
};