from dataclasses import dataclass
from typing import List
import numpy as np
import pandas as pd
from pathlib import Path

@dataclass
class Config:
    """Configuração centralizada"""
    prob_list: List[float]
    sre_fixo: int
    num_runs: int
    frac_list: List[int]
    base_data_path: str
    base_output_path: str
    L: int
    start_time: int
    
    @classmethod
    def from_file(cls, frac: int = 5, prob: float = 0.0):
        """Cria configuração lendo start_time do arquivo baseado na fração e probabilidade"""
        
        # Caminho do arquivo de configuração
        config_file = Path("/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/512/RG_sre_2_src_2_prob_v_frac_v/config.csv")
       
        start_time = 5450000  # valor padrão
        
        if config_file.exists():
            try:
                df_config = pd.read_csv(config_file)
                # Filtrar pela fração e probabilidade
                mask = (df_config['frac'] == frac) & (abs(df_config['obsprob'] - prob) < 0.0001)
                if mask.any():
                    start_time = int(df_config.loc[mask, 'primeiro_x'].iloc[0])
                    print(f"  ✓ start_time encontrado: {start_time}")
                else:
                    print(f"  ⚠ start_time NÃO encontrado para frac={frac}, prob={prob} -> usando padrão {start_time}")
            except Exception as e:
                print(f"  ✗ Erro ao ler arquivo: {e} -> usando padrão {start_time}")
        else:
            print(f"  ✗ Arquivo não encontrado: {config_file} -> usando padrão {start_time}")
        
        return cls(
            prob_list=[round(p, 2) for p in np.arange(0.00, 1.01, 0.10)],
            #prob_list=[0.00,0.10],
            sre_fixo=2,
            num_runs=100,
            #frac_list= [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100],
            #frac_list=[80, 85, 90, 95, 100],
            frac_list=[100],
            base_data_path="/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_raw/512/sre_2_src_2_prob_v_frac_v/",
            base_output_path="/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/512/RG_sre_2_src_2_prob_v_frac_v/",
            L=512,
            start_time=start_time
        )
    
    @classmethod
    def default(cls):
        """Configuração padrão (fallback)"""
        return cls.from_file(5, 0.0)
