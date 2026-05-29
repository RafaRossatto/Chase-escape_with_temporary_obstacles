import pandas as pd
from pathlib import Path
from typing import List
from .trajectory import TrajectoryUnwrapper
import numpy as np

class DataLoader:
    """Carrega e processa dados de un run"""
    def __init__(self,L:int):
        self.L = L
        self.unwrapper= TrajectoryUnwrapper()

    def load_run(self, frac: int, prob: float, sre: int, run: int, base_data_path: str)-> pd.DataFrame:
        """
        Carrega dados de um específico

        Returns:
            DataFrame com colunas 'id', 'time', 'x_unwrapped', 'y_unwrapped'
        
        Reises:
            FileNotFoundError: Se arquivo não existir
            Execption: Para outros erros de processamento
        """
        prob_str = f"{prob:.2f}"
        file_path = Path(base_data_path) / f"simulation_frac_{frac}_run_{run}_obsprob_{prob_str}_SRC_2_SRE_{sre}/results_chasers_run{run}.csv"

        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")  # ✅ Classe correta
        
        df = pd.read_csv(file_path)

        df_unwrapped_list = []
        for pid, group in df.groupby("id"):
            df_unwrapped =  self.unwrapper.unwrap_dataframe(group,self.L)
            df_unwrapped_list.append(df_unwrapped)
                # ← ADICIONAR ESTA LINHA: criar df_all
        df_all = pd.concat(df_unwrapped_list, ignore_index=True)
        
        return df_all  # ← AGORA df_all existe!
    
    def extract_positions_3d(self, df_all: pd.DataFrame, times: List[float]) -> np.ndarray:  
        """
        Extrai posições em formato 3D para cálculo do MSD

        Args:
            df_all: DataFrame com colunas
            times: Lista de tempo únicos ordenados
        
        Returns:
            Array de shape (n_particles,n_times,2)
        """
        particle_ids = df_all["id"].unique()
        n_particles = len(particle_ids)
        n_times = len(times)

        positions_3d = np.zeros((n_particles,n_times,2))
        for i,pid in enumerate(particle_ids):
            df_particles = df_all[df_all["id"]==pid].sort_values("time")
            for j,t in enumerate(times):
                pos = df_particles[df_particles["time"]== t][["x_unwrapped", "y_unwrapped"]].values
                if len(pos) > 0:
                    positions_3d[i,j] = pos[0]
                elif j> 0:
                    # Manter a última posição conheçida
                    positions_3d[i,j] = positions_3d[i,j-1]
        return positions_3d