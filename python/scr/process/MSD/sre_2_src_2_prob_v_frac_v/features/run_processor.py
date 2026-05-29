# run_processor.py
from features.data_loader import DataLoader
from features.msd_calculator import MSDCalculator
from features.models import RunResult

class RunProcessor:
    """Processa um único run(cálculo do MSD)"""
    def __init__(self,L:int,base_data_path:str):
        self.data_loader= DataLoader(L)
        self.msd_calculator = MSDCalculator()
        self.base_data_path = base_data_path
        self.L = L
    
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
        times = sorted(df_all["time"].unique())
        
        # Extrair posições em formato 3D
        positions_3d = self.data_loader.extract_positions_3d(df_all,times)

        msd = self.msd_calculator.calculate_from_positions(positions_3d)
        
        return RunResult(
            run=run,
            frac=frac,
            prob=prob,
            times=times,
            msd= msd,
            success= True
        )