import logging
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
import traceback
from pathlib import Path

from features.run_processor import RunProcessor
from features.models import EnsembleResult

logger = logging.getLogger(__name__)

class EnsembleProcessor:
    """Processa ensemble de runs para uma configuração (frac, prob)"""

    def __init__(self, L: int, base_data_path: str, num_runs: int, sre: int, start_time: int = 0):
        self.run_processor = RunProcessor(L, base_data_path, start_time)
        self.num_runs = num_runs
        self.sre = sre
    
    def process_all_runs(self, frac: int, prob: float, result_saver=None) -> EnsembleResult:
        """
        Processa todos os runs em paralelo (fail-fast em qualquer erro)

        Args:
            frac: fração
            prob: probabilidade
            result_saver: opcional, para acumular resultados

        Returns: 
            EnsembleResult com estatísticas e runs individuais

        Raises:
            RuntimeError: Se qualquer run falhar
        """
        logger.info(f"Processando frac={frac}%, prob={prob:.2f} - {self.num_runs} runs")

        # Processar run 1 (síncrono para garantir que funciona)
        logger.debug(f"Processando run 1 de referência...")
        ref_result = self.run_processor.process(frac, prob, self.sre, 1)
        
        # Acumular resultado do run 1
        if result_saver:
            result_saver.accumulate_run(ref_result)

        all_runs_rg_squared = [ref_result.rg_squared]

        # Processar runs restantes em paralelo
        if self.num_runs > 1:
            logger.info(f"Processando runs 2..{self.num_runs} em paralelo (usando {mp.cpu_count()} cores)")

            with ProcessPoolExecutor(max_workers=mp.cpu_count()-2) as executor:
                futures = {
                    executor.submit(self.run_processor.process, frac, prob, self.sre, run): run
                    for run in range(2, self.num_runs + 1)
                }
                completed = 1
                
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        all_runs_rg_squared.append(result.rg_squared)
                        completed += 1
                        
                        # Acumular resultado
                        if result_saver:
                            result_saver.accumulate_run(result)
                        
                        if completed % 10 == 0 or completed == self.num_runs:
                            logger.info(f"Progresso: {completed}/{self.num_runs} runs processados")
                    
                    except Exception as e:
                        error_msg = f"Falha crítica ao processar ensemble (frac={frac}, prob={prob:.2f}): {str(e)}\n{traceback.format_exc()}"
                        logger.error(error_msg)
                        raise RuntimeError(error_msg) from e
        
        all_runs_rg_squared_array = np.array(all_runs_rg_squared)
        mean_rg_squared = np.mean(all_runs_rg_squared_array, axis=0)
        std_rg_squared = np.std(all_runs_rg_squared_array, axis=0)
        
        logger.info(f"Ensemble completo: {self.num_runs}/{self.num_runs} runs processados com sucesso")

        return EnsembleResult(
            frac=frac,
            prob=prob,
            mean_rg_squared=mean_rg_squared,
            std_rg_squared=std_rg_squared,
            successful_runs=self.num_runs,
            total_runs=self.num_runs,
            individual_runs_rg_squared=all_runs_rg_squared
        )
