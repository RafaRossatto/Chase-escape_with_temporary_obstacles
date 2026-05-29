import numpy as np
from trajpy.trajpy import Trajectory

class MSDCalculator:
    """
    Calcula MSD(Mean Square) a partir de trajetórias
    """
    @staticmethod
    def calculate_from_positions(positions_3d:np.ndarray) -> np.ndarray:
        """
        Calcula MSD ensemble-averaged

        Args:
            positions_3d: Array de shape (n_particles, n_times,2)
        
        Returns:
            Array com MSD para cada tempo
        """
        # Transpor para (n_times, n_particles,2) conforme esperado pelo trajpy
        return Trajectory.msd_ensemble_averaged_(positions_3d.transpose(1,0,2))