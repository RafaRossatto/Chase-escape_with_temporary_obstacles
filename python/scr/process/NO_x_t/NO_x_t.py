import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

frac = 100
# Caminho base
base_path = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_raw/"
base_out = f"/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data_processed/NO_x_t/frac_{frac}"

# Lista de valores de prob (0.10 a 1.00 com passo 0.10)
prob_values = np.arange(0.10, 1.01, 0.10)

# Número de runs
num_runs = 100

# Criar o diretório de saída se não existir
os.makedirs(base_out, exist_ok=True)

# Dicionário para armazenar resultados
resultados = {}

# Para cada probabilidade
for idx, prob in enumerate(prob_values):
    todos_dados_TO = []
    tempos = []
    
    print(f"Processando prob = {prob:.2f}...")
    
    # Ler todos os runs para esta probabilidade
    for run in range(1, num_runs + 1):
        try:
            caminho = f"{base_path}simulation_frac_{frac}run{run}obsprob{prob:.2f}/results_N_obs{run}.csv"
            df = pd.read_csv(caminho)
            
            # Começar a partir da segunda linha
            df_cortado = df.iloc[1:].reset_index(drop=True)
            
            # Identificar a coluna de dados (exceto 'time')
            col_TO = [col for col in df_cortado.columns if col != 'time'][0]
            
            # Guardar os valores e o tempo
            valores = df_cortado[col_TO].values
            tempo = df_cortado['time'].values
            
            todos_dados_TO.append(valores)
            tempos.append(tempo)
            
        except FileNotFoundError:
            continue
        except Exception as e:
            continue
    
    if todos_dados_TO:
        # Encontrar o menor comprimento entre todos os arrays
        min_len = min(len(arr) for arr in todos_dados_TO)
        
        # Cortar todos os arrays para o mesmo comprimento
        todos_dados_TO_cortados = [arr[:min_len] for arr in todos_dados_TO]
        
        # Converter para array numpy
        todos_dados_TO_array = np.array(todos_dados_TO_cortados)
        
        # Usar o tempo do primeiro array (cortado)
        tempo = tempos[0][:min_len]
        
        # Calcular média e desvio padrão
        media = np.mean(todos_dados_TO_array, axis=0)
        desvio_padrao = np.std(todos_dados_TO_array, axis=0)
        
        # Último valor da média
        ultimo_valor = media[-1]
        
        # Armazenar resultado
        resultados[prob] = {
            'media_final': ultimo_valor,
            'std_final': desvio_padrao[-1],
            'num_runs': len(todos_dados_TO),
            'min_len': min_len
        }
        
        # Criar DataFrame com tempo, média e desvio padrão
        df_saida = pd.DataFrame({
            'time': tempo,
            'TO_mean': media,
            'TO_std': desvio_padrao,
            'TO_mean_minus_std': media - desvio_padrao,
            'TO_mean_plus_std': media + desvio_padrao
        })
        
        # Salvar arquivo CSV
        nome_arquivo = f"TO_vs_time_prob_{prob:.2f}.csv"
        caminho_saida = os.path.join(base_out, nome_arquivo)
        df_saida.to_csv(caminho_saida, index=False)
        
        print(f"  ✓ Dados salvos: {caminho_saida}")
        print(f"  ✓ prob = {prob:.2f}: média final = {ultimo_valor:.2f} ± {desvio_padrao[-1]:.2f} ({resultados[prob]['num_runs']} runs, comprimento={min_len})")
    else:
        print(f"  ✗ prob = {prob:.2f}: nenhum dado encontrado")

# Salvar também um arquivo de metadados com resumo dos resultados
df_metadata = pd.DataFrame([{
    'probabilidade': prob,
    'media_final': resultados[prob]['media_final'],
    'desvio_padrao_final': resultados[prob]['std_final'],
    'num_runs': resultados[prob]['num_runs'],
    'comprimento_tempo': resultados[prob]['min_len']
} for prob in sorted(resultados.keys())])

caminho_metadata = os.path.join(base_out, 'metadata_TO.csv')
df_metadata.to_csv(caminho_metadata, index=False)
print(f"\n✓ Metadados salvos em: {caminho_metadata}")

# Mostrar tabela de resultados no console
print("\n" + "="*70)
print("RESUMO DOS RESULTADOS - OBSERVADORES (TO)")
print("="*70)
print(f"{'Probabilidade':<12} | {'Média Final':<12} | {'Desvio Padrão':<12} | {'Runs':<6} | {'Tamanho':<8}")
print("-"*70)
for prob in sorted(resultados.keys()):
    stats = resultados[prob]
    print(f"{prob:.2f}          | {stats['media_final']:>10.2f} | {stats['std_final']:>11.2f} | {stats['num_runs']:>4} | {stats['min_len']:>8}")
print("="*70)

print("\nProcessamento concluído!")