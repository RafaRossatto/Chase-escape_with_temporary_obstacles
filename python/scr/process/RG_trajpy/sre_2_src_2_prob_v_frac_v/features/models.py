from dataclasses import dataclass
from typing import List, Optional
import numpy as np
import pandas as pd

@dataclass
class RunResult:
    """Resultado do processo de um único run (Raio de giro)"""
    run: int
    frac: int
    prob: float
    times: List[float]
    rg_squared: np.ndarray
    eigenvalues: List[np.ndarray] 
    success: bool = True
    error: Optional[str] = None

    def __post_init__(self):
        if not self.success and self.error is None:
            self.error = "Unknown error"

@dataclass
class EnsembleResult:
    """Resultado do ensemble de runs para uma configuração"""
    frac: int
    prob: float
    mean_rg_squared: np.ndarray  
    std_rg_squared: np.ndarray
    successful_runs: int
    total_runs: int
    individual_runs_rg_squared: List[np.ndarray]
    times: List[float] = None

    def to_dataframe(self) -> pd.DataFrame:
        """Converter para DataFrame (estatísticas do ensemble)"""
        n_particles = len(self.mean_rg_squared)
        return pd.DataFrame({
            'particle_id': list(range(1, n_particles + 1)),
            'rg_squared_mean': self.mean_rg_squared,
            'rg_squared_std': self.std_rg_squared
        })