from dataclasses import dataclass
from typing import List, Optional
import numpy as np
import pandas as pd

@dataclass
class RunResult:
    """Resultado do processo de um único run"""
    run: int
    frac: int
    prob: float
    times: List[float]
    msd: np.ndarray
    success: bool = True
    error: Optional[str] = None

    def __post_init__(self):
        if not self.success and self.error is None:
            self.error = "Unknown error"  # ← Corrigido: Unknown

@dataclass
class EnsembleResult:
    """Resultado do ensemble de runs para uma configuração"""
    frac: int
    prob: float
    times: List[float]
    mean_msd: np.ndarray  # ← CORRIGIDO: mean_msd (não mean_std)
    std_msd: np.ndarray
    successful_runs: int
    total_runs: int
    individual_runs_msd: List[np.ndarray]

    def to_dataframe(self) -> pd.DataFrame:
        """Converter para DataFrame (estatísticas do ensemble)"""
        return pd.DataFrame({
            'time': self.times,
            'msd_mean': self.mean_msd,  # ← AGORA mean_msd existe
            'msd_std': self.std_msd
        })