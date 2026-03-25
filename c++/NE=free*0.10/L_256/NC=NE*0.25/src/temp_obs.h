#ifndef TEMP_OBS_H
#define TEMP_OBS_H

#include "obstacle.h"
#include <string>

/**
 * @brief Classe que herda de Obstacle e adiciona atributo life
 */
class temp_obs : public Obstacle {
public:
    /**
     * @brief Construtor da classe temp_obs
     * @param type Tipo do obstáculo
     * @param id Identificador único
     * @param positionX Posição X
     * @param positionY Posição Y
     */
    temp_obs(const std::string& type, int id, int positionX, int positionY);
    
    /**
     * @brief Soma uma unidade ao life
     */
    void addLife();
    
    /**
     * @brief Retorna o valor atual do life
     * @return int Valor do life
     */
    int getLife() const;

private:
    int m_life;  // Atributo life sempre começa com 0
};

#endif // TEMP_OBS_H