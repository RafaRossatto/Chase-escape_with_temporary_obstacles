import pandas as pd
from pathlib import Path
from features.models import RunResult, EnsembleResult
import logging

logger = logging.getLogger(__name__)

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

        # Para Rg, rg_squared é um array por partícula (shape: n_particles)
        # Cada partícula tem UM valor de Rg² para o run inteiro
        df_run = pd.DataFrame({
            'particle_id': list(range(1, len(result.rg_squared) + 1)),
            'rg_squared': result.rg_squared  # Valor escalar por partícula
        })
        run_filename = runs_dir / f"run_{result.run:03d}_rg.csv"
        df_run.to_csv(run_filename, index=False)
        logger.debug(f"Run {result.run} salvo: {len(result.rg_squared)} partículas")
    
    def save_ensemble_result(self, ensemble_result: EnsembleResult, output_dir: Path) -> None:
        """Salva resultados do ensemble (média e std do Rg² sobre partículas)"""
        self.ensure_directory(output_dir)

        # Salvar estatísticas do ensemble
        df_ensemble = ensemble_result.to_dataframe()
        csv_path = output_dir / f"rg_ensemble_frac_{ensemble_result.frac}_obsprob_{ensemble_result.prob:.2f}.csv"
        df_ensemble.to_csv(csv_path, index=False)
        logger.info(f"Ensemble salvo: {csv_path}")
        
        # Salvar runs individuais (cada run com seus Rg² por partícula)
        runs_dir = output_dir / "individual_runs"
        self.ensure_directory(runs_dir)
        
        for i, rg_squared_per_particle in enumerate(ensemble_result.individual_runs_rg_squared):
            df_run = pd.DataFrame({
                'particle_id': list(range(1, len(rg_squared_per_particle) + 1)),
                'rg_squared': rg_squared_per_particle
            })
            run_filename = runs_dir / f"run_{i+1:03d}_rg.csv"
            df_run.to_csv(run_filename, index=False)
        
        logger.info(f"Ensemble salvo: {ensemble_result.successful_runs}/{ensemble_result.total_runs} runs")