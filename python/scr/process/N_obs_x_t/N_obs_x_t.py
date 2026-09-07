import pandas as pd
import numpy as np
import os
import re
from pathlib import Path
from multiprocessing import Pool
from tqdm import tqdm
from collections import defaultdict
import time

# Caminhos
input_dir = "/media/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_raw/sre_2_src_2_prob_v_frac_v"
output_dir = "/media/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/no_x_t"

os.makedirs(output_dir, exist_ok=True)

pattern_dir = r"simulation_frac_(\d+)_run_(\d+)_obsprob_([\d.]+)_SRC_\d+_SRE_\d+"

def processar_diretorio(diretorio):
    """
    Processa um diretório e retorna os dados com tempo
    """
    try:
        match = re.search(pattern_dir, diretorio)
        if not match:
            return None
        
        frac = int(match.group(1))
        run = int(match.group(2))
        obsprob = float(match.group(3))
        
        caminho_dir = os.path.join(input_dir, diretorio)
        
        # Procurar arquivos results_N_obs*.csv
        arquivos_csv = [f for f in os.listdir(caminho_dir) 
                       if f.startswith("results_N_obs") and f.endswith(".csv")]
        
        if not arquivos_csv:
            return None
        
        # Para cada arquivo, pegar time e NO
        dados = []
        for arquivo_csv in arquivos_csv:
            caminho_csv = os.path.join(caminho_dir, arquivo_csv)
            df = pd.read_csv(caminho_csv)
            dados.append(df)
        
        # Concatenar todos os dados
        df_combinado = pd.concat(dados, ignore_index=True)
        
        return {
            'frac': frac,
            'run': run,
            'obsprob': obsprob,
            'df': df_combinado  # DataFrame com time e NO
        }
        
    except Exception as e:
        return None

def main():
    print("=" * 70)
    print("PROCESSAMENTO - NO em função do TEMPO")
    print("=" * 70)
    
    start_time = time.time()
    
    # Listar diretórios
    print("\n📂 Listando diretórios...")
    diretorios = [d for d in os.listdir(input_dir) 
                  if os.path.isdir(os.path.join(input_dir, d)) and d.startswith("simulation_")]
    
    print(f"Total de diretórios: {len(diretorios)}")
    
    # Processar em paralelo
    print(f"\n⚡ Processando com 20 núcleos...")
    
    num_cores = 20
    resultados = []
    
    with Pool(processes=num_cores) as pool:
        with tqdm(total=len(diretorios), desc="Processando", unit="dir") as pbar:
            for resultado in pool.imap_unordered(processar_diretorio, diretorios, chunksize=10):
                if resultado is not None:
                    resultados.append(resultado)
                pbar.update(1)
    
    print(f"\n✓ Processados {len(resultados)} diretórios")
    
    # Agrupar por configuração (frac, obsprob)
    print("\n🔄 Agrupando por configuração...")
    configs = defaultdict(list)
    
    for r in tqdm(resultados, desc="Agrupando"):
        chave = (r['frac'], r['obsprob'])
        configs[chave].append(r)
    
    print(f"Total de configurações: {len(configs)}")
    
    # Para cada configuração, calcular média e std do NO em função do tempo
    print("\n🧮 Calculando NO em função do tempo para cada configuração...")
    print("=" * 70)
    
    # Dicionário para armazenar os resultados por configuração
    resultados_por_tempo = {}
    
    for (frac, obsprob), runs in tqdm(sorted(configs.items()), desc="Processando configurações"):
        print(f"\nConfiguração: frac={frac}, obsprob={obsprob:.2f}")
        print(f"  Runs: {len(runs)}")
        
        # Coletar todos os DataFrames
        dfs = [r['df'] for r in runs]
        
        # Verificar se todos têm o mesmo comprimento
        comprimentos = [len(df) for df in dfs]
        if len(set(comprimentos)) > 1:
            print(f"  ⚠️ Runs com comprimentos diferentes: {set(comprimentos)}")
            # Usar o comprimento mínimo
            min_len = min(comprimentos)
            dfs = [df.iloc[:min_len] for df in dfs]
        
        # Criar DataFrame com todos os runs
        # Cada coluna será um run
        n_points = len(dfs[0])
        n_runs = len(dfs)
        
        # Matriz: n_runs x n_points
        matriz_NO = np.array([df['NO'].values for df in dfs])
        matriz_time = dfs[0]['time'].values  # Assumindo que o tempo é o mesmo para todos
        
        # Calcular média e std para cada ponto de tempo
        media_NO = np.mean(matriz_NO, axis=0)
        std_NO = np.std(matriz_NO, axis=0)
        
        # Salvar resultados
        chave = (frac, obsprob)
        resultados_por_tempo[chave] = {
            'time': matriz_time,
            'NO_mean': media_NO,
            'NO_std': std_NO,
            'n_runs': n_runs,
            'n_points': n_points
        }
        
        print(f"  ✓ Pontos de tempo: {n_points}")
        print(f"  ✓ NO médio (primeiros 5): {media_NO[:5]}")
        print(f"  ✓ NO std (primeiros 5): {std_NO[:5]}")
    
    print("=" * 70)
    
    # Salvar resultados em arquivos separados para cada configuração
    print("\n💾 Salvando arquivos...")
    
    # Opção 1: Um arquivo por configuração
    for (frac, obsprob), dados in resultados_por_tempo.items():
        # Criar DataFrame com time, NO_mean, NO_std
        df_resultado = pd.DataFrame({
            'time': dados['time'],
            'NO_mean': dados['NO_mean'],
            'NO_std': dados['NO_std']
        })
        
        # Nome do arquivo: no_x_t_frac_{frac}_obsprob_{obsprob}.csv
        nome_arquivo = f"no_x_t_frac_{frac}_obsprob_{obsprob:.2f}.csv"
        caminho_saida = os.path.join(output_dir, nome_arquivo)
        df_resultado.to_csv(caminho_saida, index=False)
    
    # Opção 2: Um único arquivo com todas as configurações
    print("\n📊 Criando arquivo consolidado...")
    
    dados_consolidados = []
    for (frac, obsprob), dados in sorted(resultados_por_tempo.items()):
        for i in range(len(dados['time'])):
            dados_consolidados.append({
                'frac': frac,
                'obsprob': round(obsprob, 2),
                'time': dados['time'][i],
                'NO_mean': dados['NO_mean'][i],
                'NO_std': dados['NO_std'][i],
                'n_runs': dados['n_runs']
            })
    
    df_consolidado = pd.DataFrame(dados_consolidados)
    caminho_consolidado = os.path.join(output_dir, 'no_x_t_consolidado.csv')
    df_consolidado.to_csv(caminho_consolidado, index=False)
    
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 70)
    print("RESULTADO FINAL")
    print("=" * 70)
    print(f"✓ Arquivos salvos em: {output_dir}")
    print(f"✓ Total de configurações processadas: {len(resultados_por_tempo)}")
    print(f"✓ Arquivo consolidado: {caminho_consolidado}")
    print(f"✓ Tempo total: {elapsed_time:.2f} segundos")
    
    # Mostrar resumo das configurações
    print(f"\n📋 Configurações processadas:")
    fracoes = sorted(set([k[0] for k in resultados_por_tempo.keys()]))
    obsprobs = sorted(set([k[1] for k in resultados_por_tempo.keys()]))
    print(f"  - Frações: {fracoes}")
    print(f"  - ObsProbs: {[round(o,2) for o in obsprobs]}")
    print(f"  - Total de combinações: {len(resultados_por_tempo)}")
    
    return resultados_por_tempo

if __name__ == "__main__":
    resultados = main()