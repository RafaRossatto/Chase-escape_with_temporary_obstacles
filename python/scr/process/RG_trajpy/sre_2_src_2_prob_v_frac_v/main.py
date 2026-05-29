# main.py
import logging
from pathlib import Path
import numpy as np

from features.config import Config
from features.analyzer import SimulationAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    """Função principal"""
    
    config = Config.default()
    
    # Log das configurações importantes
    logger.info(f"Configurações:")
    logger.info(f"  - Frações: {config.frac_list}")
    logger.info(f"  - Probabilidades: {len(config.prob_list)} valores")
    logger.info(f"  - Runs por configuração: {config.num_runs}")
    logger.info(f"  - Start time: {config.start_time}")  # ← ADICIONADO
    logger.info(f"  - Output dir: {config.base_output_path}")
    
    # Criar diretório de saída
    Path(config.base_output_path).mkdir(parents=True, exist_ok=True)
    
    # Criar analisador e executar
    analyzer = SimulationAnalyzer(config)
    stats = analyzer.analyze_all()
    
    # Relatório final
    logger.info(f"\n{'='*60}")
    logger.info("PROCESSAMENTO CONCLUÍDO!")
    logger.info(f"Completos: {stats['completed']}")
    logger.info(f"Falhas: {stats['failed']}")
    logger.info(f"{'='*60}")

if __name__ == "__main__":
    main()