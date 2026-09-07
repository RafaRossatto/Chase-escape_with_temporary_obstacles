import logging
from pathlib import Path
import pandas as pd

from features.config import Config
from features.ensemble_processor import EnsembleProcessor
from features.result_saver import ResultSaver

logger = logging.getLogger(__name__)

class SimulationAnalyzer:
    """Orquestrador principal da análise de simulações"""
    
    def __init__(self, config: Config):
        self.config = config
        self.result_saver = ResultSaver(self.config.base_output_path)
        self.current_frac = None
        self.ensemble_results_for_frac = []  # Acumular resultados para salvar ensemble no final
    
    def analyze_single_configuration(self, frac: int, prob: float) -> None:
        """Analisa uma única configuração (frac, prob)"""
        
        self.current_frac = frac
        
        # Criar ensemble_processor com o start_time correto
        config = Config.from_file(frac, prob)
        
        ensemble_processor = EnsembleProcessor(
            L=self.config.L,
            base_data_path=self.config.base_data_path,
            num_runs=self.config.num_runs,
            sre=self.config.sre_fixo,
            start_time=config.start_time
        )
        
        logger.info(f"{'='*60}")
        logger.info(f"Analisando: frac = {frac}%, prob = {prob:.2f}, start_time = {config.start_time}")
        logger.info(f"{'='*60}")
        
        # Processar runs e acumular dados
        ensemble_result = ensemble_processor.process_all_runs(frac, prob, result_saver=self.result_saver)
        
        # Guardar resultado do ensemble para salvar depois
        self.ensemble_results_for_frac.append(ensemble_result)
    
    def _save_frac_ensembles(self):
        """Salva todos os ensembles de uma fração em um único arquivo"""
        if not self.ensemble_results_for_frac:
            return
        
        frac = self.ensemble_results_for_frac[0].frac
        output_dir = Path(self.config.base_output_path) / f"frac_{frac}"

        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Combinar todos os resultados da fração
        all_means = []
        all_stds = []
        all_probs = []
        
        for result in self.ensemble_results_for_frac:
            all_means.append(result.mean_rg_squared)
            all_stds.append(result.std_rg_squared)
            all_probs.append(result.prob)
        
        # Criar DataFrame com todas as probabilidades
        n_particles = len(all_means[0])
        data = []
        for prob, mean, std in zip(all_probs, all_means, all_stds):
            for p_id in range(n_particles):
                data.append({
                    'prob': prob,
                    'particle_id': p_id + 1,
                    'rg_squared_mean': mean[p_id],
                    'rg_squared_std': std[p_id]
                })
        
        df_all_ensembles = pd.DataFrame(data)
        csv_path = output_dir / f"all_ensembles_frac_{frac}.csv"
        df_all_ensembles.to_csv(csv_path, index=False)
        logger.info(f"Todos os ensembles salvos em: {csv_path}")
        
        # Os runs individuais já foram acumulados, salvar agora
        self.result_saver.flush_all(output_dir)
        
        # Limpar
        self.ensemble_results_for_frac = []

    def analyze_all(self) -> dict:
        """Executa análise para todas as combinações"""
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
            self.current_frac = frac
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
            
            # Salvar dados da fração completa (ensembles e runs) - SOMENTE AQUI
            self._save_frac_ensembles()
        
        return {'completed': completed, 'failed': failed}