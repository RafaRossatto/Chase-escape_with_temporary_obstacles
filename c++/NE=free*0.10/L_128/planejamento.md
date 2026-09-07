# Planejento para introdução dos obstaculos temporários:

## No obstacle.cpp

Aqui é necessário criar a classe temp_obs, onde ele vai herdar a classe obstacle e adiconar um atributo chamamo life, onde ao ser criado ele vai ser life = 0
Feito

## No simulation.cpp

Ele vai criar um vetor t_obs que vai receber objetos temp_obs.
Agora dento do loop principal while (time < 1.0e5)
    Vai percorrer todo o vetor t_obs se não for vazio
    Se ele entrar ele vai adicionar uma unidade ao atributo life
    Se life > valor: ele apaga o mesmo.

    Ainda dentro do loop principal, manda o vetor t_obs tanto para o método moveGoodCell e moveCancerCell

## No celllattice.cpp

Dentro do moveCancelCell:
    mandar o t_obs para o isOccupied 
    Se ele se mover cria um temp_obs

Dentro do moveGoodCell
    mandar o t_obs para o isOccupied

Dentro do isOccupied:
    fazer a verificação do t_obs