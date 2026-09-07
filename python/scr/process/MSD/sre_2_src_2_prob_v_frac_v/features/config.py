from dataclasses import dataclass
from typing import List
import numpy as np

@dataclass
class Config:
    """Configuração centralizada"""
    prob_list : List[float]
    sre_fixo: int
    num_runs: int
    frac_list: List[int]      # ← ADICIONAR ESTA LINHA
    base_data_path: str
    base_output_path: str
    L: int 
    @classmethod
    def default(cls):
        """Configuração padrão"""
        return cls(
                prob_list=[round(p, 2) for p in np.arange(0.00, 1.01, 0.10)],
                sre_fixo=2,
                num_runs=100,
                #frac_list=[5],  # ← MUDAR AQUI para [5] em vez da lista completa
                #frac_list = [5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100],
                frac_list = [5,50,100],
                base_data_path="/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_raw/128/sre_2_src_2_prob_v_frac_v/",
                base_output_path="/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/128/MSD_sre_2_src_2_prob_v_frac_v",
                L=128
            )
