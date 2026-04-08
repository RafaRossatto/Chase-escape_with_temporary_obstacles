import pandas as pd
import numpy as np
import os
import glob

def encontrar_tempo_convergencia(valores, tempo, tolerancia=0.01):
    """
    Encontra o primeiro tempo em que o valor estabiliza no final.
    
    Parâmetros:
    - valores: array com os valores da série temporal
    - tempo: array com os tempos correspondentes
    - tolerancia: tolerância relativa para considerar que atingiu o valor final
    
    Retorna:
    - tempo_convergencia: primeiro tempo em que atinge o valor final
    """
    valor_final = valores[-1]
    
    # Procurar do início ao fim
    for i in range(len(valores)):
        # Se o valor está dentro da tolerância do valor final
        if abs(valores[i] - valor_final) <= tolerancia * abs(valor_final):
            return tempo[i]
    
    # Se não encontrar, retorna o último tempo
    return tempo[-1]

def processar_tempos_convergencia(base_path, frac, prob_values, num_runs, tipo='NE'):
    """
    Processa os tempos de convergência para cada probabilidade.
    
    Parâmetros:
    - base_path: caminho base dos dados
    - frac: valor de frac
    - prob_values: lista de probabilidades
    - num_runs: número de runs
    - tipo: 'NE' para escapers ou 'NO' para observadores
    
    Retorna:
    - dicionário com resultados
    """
    resultados = {}
    
    for prob in prob_values:
        tempos_convergencia = []
        
        print(f"  Processando prob = {prob:.2f}...")
        
        for run in range(1, num_runs + 1):
            try:
                if tipo == 'NE':
                    caminho = f"{base_path}simulation_frac_{frac}run{run}obsprob{prob:.2f}/results_N_escapers_run{run}.csv"
                    coluna_dados = 'NE'  # Ajuste conforme necessário
                else:  # NO
                    caminho = f"{base_path}simulation_frac_{frac}run{run}obsprob{prob:.2f}/results_N_obs{run}.csv"
                    coluna_dados = 'TO'  # Ajuste conforme necessário
                
                df = pd.read_csv(caminho)
                
                # Pular primeira linha se necessário
                df_cortado = df.iloc[1:].reset_index(drop=True)
                
                # Identificar coluna de dados
                col_dados = [col for col in df_cortado.columns if col != 'time'][0]
                valores = df_cortado[col_dados].values
                tempo = df_cortado['time'].values
                
                # Encontrar tempo de convergência
                tempo_conv = encontrar_tempo_convergencia(valores, tempo, tolerancia=0.01)
                tempos_convergencia.append(tempo_conv)
                
            except FileNotFoundError:
                continue
            except Exception as e:
                continue
        
        if tempos_convergencia:
            resultados[prob] = {
                'tempo_medio': np.mean(tempos_convergencia),
                'tempo_std': np.std(tempos_convergencia),
                'tempo_mediana': np.median(tempos_convergencia),
                'tempo_min': np.min(tempos_convergencia),
                'tempo_max': np.max(tempos_convergencia),
                'num_runs': len(tempos_convergencia),
                'todos_tempos': tempos_convergencia
            }
            print(f"    ✓ prob {prob:.2f}: tempo médio = {resultados[prob]['tempo_medio']:.2f} ± {resultados[prob]['tempo_std']:.2f}")
        else:
            print(f"    ✗ prob {prob:.2f}: nenhum dado encontrado")
    
    return resultados

# Configurações
frac = 100
base_path = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_raw/"
output_dir = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data_processed/tempos_convergencia"

# Criar diretório de saída
os.makedirs(output_dir, exist_ok=True)

# Valores de probabilidade
prob_values = np.arange(0.00, 1.01, 0.10)
num_runs = 100

print("="*70)
print("CALCULANDO TEMPOS DE CONVERGÊNCIA - N_E (Escapers)")
print("="*70)
resultados_NE = processar_tempos_convergencia(base_path, frac, prob_values, num_runs, tipo='NE')

print("\n" + "="*70)
print("CALCULANDO TEMPOS DE CONVERGÊNCIA - N_O (Observadores)")
print("="*70)
resultados_NO = processar_tempos_convergencia(base_path, frac, prob_values, num_runs, tipo='NO')

# Salvar resultados
for tipo, resultados in [('NE', resultados_NE), ('NO', resultados_NO)]:
    if resultados:
        # Criar DataFrame com resumo
        df_resumo = pd.DataFrame([{
            'probabilidade': prob,
            'tempo_medio': stats['tempo_medio'],
            'tempo_std': stats['tempo_std'],
            'tempo_mediana': stats['tempo_mediana'],
            'tempo_min': stats['tempo_min'],
            'tempo_max': stats['tempo_max'],
            'num_runs': stats['num_runs']
        } for prob, stats in resultados.items()])
        
        # Salvar resumo
        caminho_resumo = os.path.join(output_dir, f"tempos_convergencia_{tipo}_frac_{frac}.csv")
        df_resumo.to_csv(caminho_resumo, index=False)
        print(f"\n✓ Resumo salvo: {caminho_resumo}")
        
        # Salvar todos os tempos individuais
        dados_individuais = {'probabilidade': []}
        for prob, stats in resultados.items():
            for i, tempo in enumerate(stats['todos_tempos']):
                dados_individuais['probabilidade'].append(prob)
                dados_individuais[f'run_{i+1}'] = dados_individuais.get(f'run_{i+1}', []) + [tempo]
        
        # Salvar dados individuais (formato alternativo)
        df_individuais = pd.DataFrame([{
            'probabilidade': prob,
            'tempos_individuais': str(stats['todos_tempos'])  # Salva como string
        } for prob, stats in resultados.items()])
        
        caminho_individuais = os.path.join(output_dir, f"tempos_individuais_{tipo}_frac_{frac}.csv")
        df_individuais.to_csv(caminho_individuais, index=False)
        print(f"✓ Tempos individuais salvos: {caminho_individuais}")

# Mostrar tabela de resultados
print("\n" + "="*70)
print("RESUMO DOS TEMPOS DE CONVERGÊNCIA - N_E")
print("="*70)
if resultados_NE:
    df_NE = pd.DataFrame([{
        'prob': prob,
        'tempo_médio': f"{stats['tempo_medio']:.2f} ± {stats['tempo_std']:.2f}",
        'mediana': f"{stats['tempo_mediana']:.2f}",
        'n_runs': stats['num_runs']
    } for prob, stats in resultados_NE.items()])
    print(df_NE.to_string(index=False))

print("\n" + "="*70)
print("RESUMO DOS TEMPOS DE CONVERGÊNCIA - N_O")
print("="*70)
if resultados_NO:
    df_NO = pd.DataFrame([{
        'prob': prob,
        'tempo_médio': f"{stats['tempo_medio']:.2f} ± {stats['tempo_std']:.2f}",
        'mediana': f"{stats['tempo_mediana']:.2f}",
        'n_runs': stats['num_runs']
    } for prob, stats in resultados_NO.items()])
    print(df_NO.to_string(index=False))

print("\n" + "="*70)
print("PROCESSAMENTO CONCLUÍDO!")