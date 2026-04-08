import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

frac = 100
# Caminho base
base_path = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_raw/"
base_out = f"/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data_processed/NE_x_t/frac_{frac}"

# Lista de valores de prob (0.10 a 1.00 com passo 0.10)
prob_values = np.arange(0.00, 1.01, 0.10)

# Número de runs
num_runs = 100

# Criar o diretório de saída se não existir
os.makedirs(base_out, exist_ok=True)

resultados = {}  # Dicionário para armazenar os resultados finais se necessário

for idx, prob in enumerate(prob_values):
    todos_dados_NE = []
    
    print(f"Processando prob = {prob:.2f}...")
    
    # Ler todos os runs para esta probabilidade
    for run in range(1, num_runs + 1):
        try:
            caminho = f"{base_path}simulation_frac_{frac}run{run}obsprob{prob:.2f}/results_N_escapers_run{run}.csv"
            df = pd.read_csv(caminho)
            
            # Começar a partir da segunda linha
            df_cortado = df.iloc[1:].reset_index(drop=True)
            
            # Identificar a coluna de dados (exceto 'time')
            col_NE = [col for col in df_cortado.columns if col != 'time'][0]
            
            # Guardar os valores
            todos_dados_NE.append(df_cortado[col_NE].values)
            
        except FileNotFoundError:
            print(f"  Aviso: Run {run} não encontrado para prob {prob:.2f}")
        except Exception as e:
            continue
    
    if todos_dados_NE:
        # Converter para array numpy
        todos_dados_NE = np.array(todos_dados_NE)
        
        # Calcular média e desvio padrão
        media = np.mean(todos_dados_NE, axis=0)
        desvio_padrao = np.std(todos_dados_NE, axis=0)
        
        # Tempo (assumindo que é o mesmo para todos)
        tempo = df_cortado['time'].values
        
        # Último valor da média
        ultimo_valor = media[-1]
        
        # Armazenar resultado
        resultados[prob] = {
            'media_final': ultimo_valor,
            'std_final': desvio_padrao[-1],
            'num_runs': len(todos_dados_NE),
            'comprimento_tempo': len(tempo)
        }
        
        # Criar DataFrame com tempo, média e desvio padrão
        df_saida = pd.DataFrame({
            'time': tempo,
            'NE_mean': media,
            'NE_std': desvio_padrao,
            'NE_mean_minus_std': media - desvio_padrao,
            'NE_mean_plus_std': media + desvio_padrao
        })
        
        # Salvar arquivo CSV
        nome_arquivo = f"NE_vs_time_prob_{prob:.2f}.csv"
        caminho_saida = os.path.join(base_out, nome_arquivo)
        df_saida.to_csv(caminho_saida, index=False)
        
        print(f"  ✓ Dados salvos: {caminho_saida}")
        print(f"  ✓ prob = {prob:.2f}: média final = {ultimo_valor:.2f} ± {desvio_padrao[-1]:.2f} ({resultados[prob]['num_runs']} runs)")
    else:
        print(f"  ✗ prob = {prob:.2f}: nenhum dado encontrado")

# Salvar metadados com resumo de todos os resultados
df_metadata = pd.DataFrame([{
    'probabilidade': prob,
    'media_final': resultados[prob]['media_final'],
    'desvio_padrao_final': resultados[prob]['std_final'],
    'num_runs_processados': resultados[prob]['num_runs'],
    'comprimento_temporal': resultados[prob]['comprimento_tempo']
} for prob in sorted(resultados.keys())])

# Adicionar informações adicionais nos metadados
caminho_metadata = os.path.join(base_out, 'metadata_NE.csv')
df_metadata.to_csv(caminho_metadata, index=False)
print(f"\n✓ Metadados salvos em: {caminho_metadata}")

# Salvar também um arquivo de configuração/parâmetros
config_info = {
    'frac': frac,
    'num_runs_total': num_runs,
    'prob_values': prob_values.tolist(),
    'prob_values_min': float(prob_values.min()),
    'prob_values_max': float(prob_values.max()),
    'prob_values_step': 0.10,
    'base_path_raw': base_path,
    'output_path': base_out
}

df_config = pd.DataFrame([config_info])
caminho_config = os.path.join(base_out, 'config.csv')
df_config.to_csv(caminho_config, index=False)
print(f"✓ Configurações salvas em: {caminho_config}")

# Mostrar tabela de resultados no console
print("\n" + "="*80)
print(f"RESUMO DOS RESULTADOS - N_E (Número de Escapers) - frac = {frac}")
print("="*80)
print(f"{'Probabilidade':<12} | {'Média Final':<12} | {'Desvio Padrão':<12} | {'Runs':<6} | {'Comprimento':<12}")
print("-"*80)
for prob in sorted(resultados.keys()):
    stats = resultados[prob]
    print(f"{prob:.2f}          | {stats['media_final']:>10.2f} | {stats['std_final']:>11.2f} | {stats['num_runs']:>4} | {stats['comprimento_tempo']:>8}")
print("="*80)

print("\nProcessamento concluído!")