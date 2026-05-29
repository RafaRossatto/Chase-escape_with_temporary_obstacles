import pandas as pd
from pathlib import Path
from features.models import RunResult, EnsembleResult

class ResultSaver:
    """Salva resultados em disco"""
    
    def __init__(self, base_output_path: str):
        self.base_output_path = Path(base_output_path)
    
    def ensure_directory(self, path: Path) -> None:
        """Cria um diretório se não existir"""
        path.mkdir(parents=True, exist_ok=True)
    
    def save_run_results(self, result: RunResult, output_dir: Path) -> None:
        """Salva resultado de um único run"""
        runs_dir = output_dir / "individual_runs"
        self.ensure_directory(runs_dir)

        df_run = pd.DataFrame({
            'time': result.times,  # ← CORRIGIDO: times (plural)
            'msd': result.msd
        })
        run_filename = runs_dir / f"run_{result.run:03d}_msd.csv"
        df_run.to_csv(run_filename, index=False)
    
    def save_ensemble_result(self, ensemble_result: EnsembleResult, output_dir: Path) -> None:
        """Salva resultados do ensemble (média e std)"""
        self.ensure_directory(output_dir)

        # Salvar estatísticas do ensemble
        df_ensemble = ensemble_result.to_dataframe()
        csv_path = output_dir / f"msd_ensemble_frac_{ensemble_result.frac}_obsprob_{ensemble_result.prob:.2f}.csv"  # ← CORRIGIDO: ensemble_result
        df_ensemble.to_csv(csv_path, index=False)
        
        # Salvar runs individuais
        runs_dir = output_dir / "individual_runs"
        self.ensure_directory(runs_dir)
        
        for i, msd in enumerate(ensemble_result.individual_runs_msd):
            df_run = pd.DataFrame({
                'time': ensemble_result.times,
                'msd': msd
            })
            run_filename = runs_dir / f"run_{i+1:03d}_msd.csv"
            df_run.to_csv(run_filename, index=False)