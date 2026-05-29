import logging
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
import traceback
import pandas as pd
from pathlib import Path

from features.run_processor import RunProcessor
from features.models import EnsembleResult

logger = logging.getLogger(__name__)

class EnsembleProcessor:
    """Processa ensemble de runs para uma configuração (frac, prob)"""

    def __init__(self, L: int, base_data_path: str, num_runs: int, sre: int):
        self.run_processor = RunProcessor(L, base_data_path)
        self.num_runs = num_runs
        self.sre = sre
    
    def process_all_runs(self, frac: int, prob: float, output_dir: Path = None) -> EnsembleResult:
        """
        Processa todos os runs em paralelo (fail-fast em qualquer erro)

        Returns: 
            EnsembleResult com estatísticas e runs individuais

        Raises:
            RuntimeError: Se qualquer run falhar
        """
        logger.info(f"Processando frac={frac}%, prob={prob:.2f} - {self.num_runs} runs")

        # Criar diretório para runs individuais se output_dir foi fornecido
        if output_dir:
            runs_dir = output_dir / "individual_runs"
            runs_dir.mkdir(parents=True, exist_ok=True)

        # Processar run 1 (síncrono para garantir que funciona)
        logger.debug(f"Processando run 1 de referência...")
        ref_result = self.run_processor.process(frac, prob, self.sre, 1)
        
        # Salvar run 1 individualmente
        if output_dir:
            df_run = pd.DataFrame({'time': ref_result.times, 'msd': ref_result.msd})
            df_run.to_csv(runs_dir / f"run_001_msd.csv", index=False)
            logger.debug(f"Run 1 salvo")

        all_runs_msd = [ref_result.msd]
        all_runs_results = [ref_result]
        reference_times = ref_result.times

        # Processar runs restantes em paralelo
        if self.num_runs > 1:
            logger.info(f"Processando runs 2..{self.num_runs} em paralelo (usando {mp.cpu_count()} cores)")

            with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
                futures = {
                    executor.submit(self.run_processor.process, frac, prob, self.sre, run): run
                    for run in range(2, self.num_runs + 1)
                }
                completed = 1
                
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        all_runs_msd.append(result.msd)
                        all_runs_results.append(result)
                        completed += 1
                        
                        # Salvar CADA run individualmente conforme termina
                        if output_dir:
                            df_run = pd.DataFrame({'time': result.times, 'msd': result.msd})
                            df_run.to_csv(runs_dir / f"run_{result.run:03d}_msd.csv", index=False)
                        
                        if completed % 10 == 0 or completed == self.num_runs:
                            logger.info(f"Progresso: {completed}/{self.num_runs} runs processados e salvos")
                    
                    except Exception as e:
                        error_msg = f"Falha crítica ao processar ensemble (frac={frac}, prob={prob:.2f}): {str(e)}\n{traceback.format_exc()}"
                        logger.error(error_msg)
                        raise RuntimeError(error_msg) from e
        
        all_runs_msd_array = np.array(all_runs_msd)
        mean_msd = np.mean(all_runs_msd_array, axis=0)
        std_msd = np.std(all_runs_msd_array, axis=0)
        
        logger.info(f"Ensemble completo: {self.num_runs}/{self.num_runs} runs processados com sucesso")

        return EnsembleResult(
            frac=frac,
            prob=prob,
            times=reference_times,
            mean_msd=mean_msd,
            std_msd=std_msd,
            successful_runs=self.num_runs,
            total_runs=self.num_runs,
            individual_runs_msd=all_runs_msd
        )
