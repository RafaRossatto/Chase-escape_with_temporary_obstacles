#include "temp_obs.h"

temp_obs::temp_obs(const std::string& type, int id, int positionX, int positionY)
    : Obstacle(type, id, positionX, positionY), m_life(0)
{}