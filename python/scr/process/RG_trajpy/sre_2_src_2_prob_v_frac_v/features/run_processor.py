# run_processor.py
from features.data_loader import DataLoader
from features.rg_calculator import RgCalculator 
from features.models import RunResult
import numpy as np

class RunProcessor:
    """Processa um único run(cálculo do Raio de giro do trajpy)"""
    def __init__(self,L:int,base_data_path:str,start_time: int = 0):
        self.data_loader= DataLoader(L)
        self.rg_calculator = RgCalculator()  # ✅ Correto
        self.base_data_path = base_data_path
        self.L = L
        self.start_time = start_time
    
    def process(self,frac: int, prob: float, sre: int, run:int) ->RunResult:
        """
        Processa un run completo
        Returns:
            RunResult com MSD calculado

        Raises:
            Execption: Qualquer erro no processamento (fail-fast)
        """
        df_all = self.data_loader.load_run(frac,prob,sre,run,self.base_data_path)

        # Obter tempos únicos
        all_times = sorted(df_all["time"].unique())
        
        #filtrar apenas temos >= start_time
        times = [t for t in all_times if t >= self.start_time]

        if len(times) == 0:
            raise ValueError(f"Nenhum tempo enctrado para start_time={self.start_time}")
        #Filtrar dados apenas para os tempos selecionados
        df_filtered = df_all[df_all["time"].isin(times)]

        # Extrair posições em formato 3D
        positions_3d = self.data_loader.extract_positions_3d(df_filtered,times)

        # Calcular dados de raio de giro para cada partícula usando trajpy
        # Retorna lista de dicionários com tensor, autovalores, autovetores
        gyration_data_per_particle = self.rg_calculator.calculate_for_all_particles(positions_3d)

        # Extrair Rg^{2} escalar para cada partícula
        rg_squered_per_particle = np.array([
            self.rg_calculator.extract_rg_squared(data)for data in gyration_data_per_particle
        ])

        #Extrai autovalores para cada partícula
        eigenvalues_per_particle =[self.rg_calculator.extract_eigenvalues(data)for data in gyration_data_per_particle]
        
        return RunResult(
            run=run,
            frac=frac,
            prob=prob,
            times=times,
            rg_squere= rg_squered_per_particle,
            eigenvalues= eigenvalues_per_particle,
            success= True
        )