import numpy as np
from typing import Dict,Union,List
from trajpy.trajpy import Trajectory

class RgCalculator:
    """
    Calcula o Raio de Giro usando o método gyration_radius_ do trajpy
    """

    @ staticmethod
    def calculate_gyration_tensor_for_particle(particle_trajectory: np.ndarray)->Dict[str,Union[np.ndarray,float]]:
        """
        Calcula o tensor de raio de giração para uma partícula usando trajpy

        Args:
            particle_trajectory: Array de shape(n_times, 2) ou (n_times,3)
        
        Returns:
            Dicionário com:
            -"gyration tensor": tensor de raio de giro(matriz dim x dim)
            -"eigenvalues": autovalores em ordem decresente
            -"eigenvectors": autoveroes correspondentes
        """
        return Trajectory.gyration_radius_(particle_trajectory)
    
    @staticmethod
    def calculate_for_all_particle(positons_3d: np.ndarray) -> List[Dict]:
        """
        Calcula o raio de giro para todas as partícula

        Args:
            positions_3d: Array de shape (n_particles, n_time,2)
        
        Returns:
            List de dicionários com resultados do trajpy para cada partícula
        """
        n_particle,n_times,n_dims = positons_3d.shape
        results = []

        for i in range (n_particle):
            # Trajetória da partícula i: (n_times, n_dims)
            particle_traj= positons_3d[i]

            # Calcular gyration radius usando trajpy
            gyration_data= Trajectory.gyration_radius_(particle_traj)
            results.append(gyration_data)
        return results
    
    @staticmethod
    def extract_rg_squared(gyrations_data: Dict) -> float:
        """
        Extrai o Rg^{2} do tensor (traço do tensor/dimensão)
        Rg^{2} = (\lambda_{1}^{2}+\lambda_{2}^{2}+...) = traço tensor
        """
        tensor = gyrations_data["gyration tensor"]
        rg_squared = np.trace(tensor)
        return rg_squared

    @staticmethod
    def extract_eigenvalues(gyration_data: Dict) -> np.ndarray:
        """Extrai os autovalores (raios principais)"""
        return gyration_data["eigenvalues"]
    
    @staticmethod
    def extract_eigenvectors(gyration_data: Dict) -> np.ndarray:
        """Extrai os autovetores (direções principais)"""
        return gyration_data["eigenvectors"]
    
    @staticmethod
    def extract_gyration_tensor(gyration_data: Dict) -> np.ndarray:
        """Extrai o tensor de raio de giração"""
        return gyration_data["gyration tensor"]