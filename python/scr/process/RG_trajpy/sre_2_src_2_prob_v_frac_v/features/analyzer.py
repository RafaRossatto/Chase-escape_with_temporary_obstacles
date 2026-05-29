import logging
from pathlib import Path

from features.config import Config
from features.ensemble_processor import EnsembleProcessor
from features.result_saver import ResultSaver

logger = logging.getLogger(__name__)

class SimulationAnalyzer:
    """Orquestrador principal da análise de simulações"""
    
    def __init__(self, config: Config):
        self.config = config
        self.ensemble_processor = EnsembleProcessor(
            L=self.config.L,
            base_data_path=self.config.base_data_path,
            num_runs=self.config.num_runs,
            sre=self.config.sre_fixo,
            start_time= self.config.start_time
        )
        self.result_saver = ResultSaver(self.config.base_output_path)

    def analyze_single_configuration(self, frac: int, prob: float) -> None:
        output_dir = Path(self.config.base_output_path) / f"frac_{frac}" / f"obsprob_{prob:.2f}"
        logger.info(f"{'='*60}")
        logger.info(f"Analisando: frac = {frac}%, prob = {prob:.2f}")
        logger.info(f"{'='*60}")
        ensemble_result = self.ensemble_processor.process_all_runs(frac, prob, output_dir)
        self.result_saver.save_ensemble_result(ensemble_result, output_dir)
        logger.info(f"✓ Configuração completa: frac={frac}%, prob={prob:.2f}")

    def analyze_all(self) -> dict:
        total_combinations = len(self.config.frac_list) * len(self.config.prob_list)
        logger.info(f"{'='*60}")
        logger.info(f"INICIANDO ANÁLISE COMPLETA")
        logger.info(f"Frações: {self.config.frac_list}%")
        logger.info(f"Probabilidades: {len(self.config.prob_list)} valores (0.00 a 1.00)")
        logger.info(f"Total de combinações: {total_combinations}")
        logger.info(f"{'='*60}")
        
        completed = 0
        failed = 0
        
        for frac in self.config.frac_list:
            logger.info(f"\n{'#'*60}")
            logger.info(f"# Processando Fração: {frac}%")
            logger.info(f"{'#'*60}")
            for prob in self.config.prob_list:
                try:
                    self.analyze_single_configuration(frac, prob)
                    completed += 1
                except Exception as e:
                    import traceback
                    logger.error(f"Falha em frac={frac}%, prob={prob:.2f}: {str(e)}")
                    logger.error(f"Traceback completo:\n{traceback.format_exc()}")
                    failed += 1
                finally:
                    logger.info(f"Progresso: {completed + failed}/{total_combinations} combinações")
        
        return {'completed': completed, 'failed': failed}
