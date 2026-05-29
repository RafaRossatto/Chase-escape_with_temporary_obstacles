# main.py
import logging
from pathlib import Path
import numpy as np

from features.config import Config
from features.analyzer import SimulationAnalyzer  # ← CORRIGIDO: SimulationAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    """Função principal"""
    
    config = Config.default()
    
    # Criar diretório de saída
    Path(config.base_output_path).mkdir(parents=True, exist_ok=True)
    
    # Criar analisador e executar
    analyzer = SimulationAnalyzer(config)  # ← CORRIGIDO: SimulationAnalyzer
    stats = analyzer.analyze_all()
    
    # Relatório final
    logger.info(f"\n{'='*60}")
    logger.info("PROCESSAMENTO CONCLUÍDO!")
    logger.info(f"Completos: {stats['completed']}")
    logger.info(f"Falhas: {stats['failed']}")
    logger.info(f"{'='*60}")

if __name__ == "__main__":
    main()