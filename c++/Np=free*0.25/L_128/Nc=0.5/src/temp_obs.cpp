#include "temp_obs.h"

/**
 * @brief Construtor da classe temp_obs
 * Inicializa a parte Obstacle e define m_life como 0
 */
temp_obs::temp_obs(const std::string& type, int id, int positionX, int positionY)
    : Obstacle(type, id, positionX, positionY), m_life(0)
{}

/**
 * @brief Soma uma unidade ao life
 */
void temp_obs::addLife()
{
    m_life++;
}

/**
 * @brief Retorna o valor atual do life
 * @return int Valor do life
 */
int temp_obs::getLife() const
{
    return m_life;
}