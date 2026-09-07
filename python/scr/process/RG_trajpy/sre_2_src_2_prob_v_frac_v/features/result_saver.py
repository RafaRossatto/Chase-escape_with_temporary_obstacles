import pandas as pd
from pathlib import Path
from features.models import RunResult, EnsembleResult
import logging

logger = logging.getLogger(__name__)

class ResultSaver:
    """Salva resultados em disco"""
    
    def __init__(self, base_output_path: str):
        self.base_output_path = Path(base_output_path)
        self.all_runs_data = {}  # Acumular dados para cada fração
    
    def ensure_directory(self, path: Path) -> None:
        """Cria um diretório se não existir"""
        path.mkdir(parents=True, exist_ok=True)
    
    def accumulate_run(self, result: RunResult) -> None:
        """Acumula um run para salvar depois (não salva ainda)"""
        frac = result.frac
        prob = result.prob
        
        if frac not in self.all_runs_data:
            self.all_runs_data[frac] = []
        
        for particle_id, rg_sq in enumerate(result.rg_squared, start=1):
            self.all_runs_data[frac].append({
                'frac': frac,
                'prob': prob,
                'run': result.run,
                'particle_id': particle_id,
                'rg_squared': rg_sq
            })
        
        logger.debug(f"Run {result.run} acumulado: {len(result.rg_squared)} partículas")
    
    def save_ensemble_result(self, ensemble_result: EnsembleResult, output_dir: Path) -> None:
        """Salva resultados do ensemble e todos os runs acumulados"""
        self.ensure_directory(output_dir)
        
        frac = ensemble_result.frac
        
        # 1. Salvar estatísticas do ensemble (média e std por partícula)
        n_particles = len(ensemble_result.mean_rg_squared)
        df_ensemble = pd.DataFrame({
            'particle_id': list(range(1, n_particles + 1)),
            'rg_squared_mean': ensemble_result.mean_rg_squared,
            'rg_squared_std': ensemble_result.std_rg_squared
        })
        csv_path = output_dir / f"rg_ensemble_frac_{frac}.csv"
        df_ensemble.to_csv(csv_path, index=False)
        logger.info(f"Ensemble salvo: {csv_path}")
        
        # 2. Salvar TODOS os runs acumulados em um único arquivo
        if frac in self.all_runs_data and self.all_runs_data[frac]:
            df_all_runs = pd.DataFrame(self.all_runs_data[frac])
            csv_path = output_dir / f"all_runs_frac_{frac}.csv"
            df_all_runs.to_csv(csv_path, index=False)
            logger.info(f"Todos os runs salvos em: {csv_path} ({len(df_all_runs)} linhas, {len(df_all_runs['run'].unique())} runs, {len(df_all_runs['prob'].unique())} probabilidades)")
            
            # Limpar dados acumulados desta fração
            del self.all_runs_data[frac]
        else:
            logger.warning(f"Nenhum dado acumulado para fração {frac}")
    
    def flush_all(self, output_dir: Path) -> None:
        """Salva qualquer dado restante (útil no final do processamento)"""
        self.ensure_directory(output_dir)
        for frac in list(self.all_runs_data.keys()):
            if self.all_runs_data[frac]:
                df_all_runs = pd.DataFrame(self.all_runs_data[frac])
                csv_path = output_dir / f"all_runs_frac_{frac}.csv"
                df_all_runs.to_csv(csv_path, index=False)
                logger.info(f"Dados restantes salvos em: {csv_path}")
                del self.all_runs_data[frac]