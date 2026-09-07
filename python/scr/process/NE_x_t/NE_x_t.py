import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Caminho base
base_path = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_raw/sre_2_src_2_prob_v_frac_v"
base_out_base = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/NE_x_t"

# Valores de frac (5 a 100, passo 5)
frac_values = np.arange(5, 101, 5)

# Lista de valores de prob (0.00 a 1.00 com passo 0.10)
prob_values = np.arange(0.00, 1.01, 0.10)

# Número de runs
num_runs = 100

# Dicionário para armazenar todos os resultados
todos_resultados = {}

for frac in frac_values:
    print(f"\n{'='*80}")
    print(f"PROCESSANDO FRAC = {frac}")
    print(f"{'='*80}")
    
    base_out = f"{base_out_base}/frac_{frac}"
    os.makedirs(base_out, exist_ok=True)
    
    resultados_frac = {}  # Dicionário para armazenar os resultados desta fração
    
    for idx, prob in enumerate(prob_values):
        todos_dados_NE = []
        
        print(f"  Processando prob = {prob:.2f}...")
        
        # Ler todos os runs para esta probabilidade
        for run in range(1, num_runs + 1):
            try:
                caminho = f"{base_path}/simulation_frac_{frac}_run_{run}_obsprob_{prob:.2f}_SRC_2_SRE_2/results_N_escapers_run{run}.csv"
                
                # DEBUG: Mostrar apenas para prob=0.00
                if prob == 0.00:
                    print(f"    📖 Lendo: {caminho}")
                
                df = pd.read_csv(caminho)
                
                # DEBUG: Verificar estrutura para prob=0.00
                if prob == 0.00:
                    print(f"       Shape: {df.shape}")
                    print(f"       Colunas: {df.columns.tolist()}")
                    print(f"       Primeiras 3 linhas:")
                    print(df.head(3))
                
                # Verificar se o DataFrame tem dados
                if df.empty:
                    if prob == 0.00:
                        print(f"       ⚠️  DataFrame está vazio!")
                    continue
                
                # CORREÇÃO: Não pular a primeira linha se não houver dados depois
                # Tentar pular a primeira linha
                df_cortado = df.iloc[1:].reset_index(drop=True)
                
                # Se o DataFrame cortado estiver vazio, usar o original
                if df_cortado.empty:
                    if prob == 0.00:
                        print(f"       ⚠️  DataFrame cortado vazio! Usando original.")
                    df_cortado = df
                
                # Identificar a coluna de dados (exceto 'time')
                colunas_sem_time = [col for col in df_cortado.columns if col != 'time']
                
                # DEBUG para prob=0.00
                if prob == 0.00:
                    print(f"       Colunas sem 'time': {colunas_sem_time}")
                
                if not colunas_sem_time:
                    if prob == 0.00:
                        print(f"       ❌ Nenhuma coluna encontrada exceto 'time'!")
                    continue
                
                col_NE = colunas_sem_time[0]
                
                # DEBUG para prob=0.00
                if prob == 0.00:
                    print(f"       Coluna de dados: '{col_NE}'")
                    print(f"       Primeiros 5 valores: {df_cortado[col_NE].head(5).tolist()}")
                    print(f"       Total de valores: {len(df_cortado[col_NE].values)}")
                
                # Guardar os valores
                valores = df_cortado[col_NE].values
                todos_dados_NE.append(valores)
                
                if prob == 0.00:
                    print(f"       ✅ Run {run}: {len(valores)} valores lidos")
                
            except FileNotFoundError:
                if prob == 0.00:
                    print(f"      ❌ Run {run}: Arquivo não encontrado")
                continue
            except Exception as e:
                if prob == 0.00:
                    print(f"      ❌ Run {run}: ERRO - {e}")
                continue
        
        # DEBUG: Mostrar total de runs carregados para prob=0.00
        if prob == 0.00:
            print(f"  📊 Total de runs carregados para prob=0.00: {len(todos_dados_NE)}")
        
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
            resultados_frac[prob] = {
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
            
            # DEFINIR caminho_saida AQUI (dentro do if)
            nome_arquivo = f"NE_vs_time_prob_{prob:.2f}.csv"
            caminho_saida = os.path.join(base_out, nome_arquivo)
            df_saida.to_csv(caminho_saida, index=False)
            
            print(f"      ✓ Dados salvos: {caminho_saida}")
            print(f"      ✓ prob = {prob:.2f}: média final = {ultimo_valor:.2f} ± {desvio_padrao[-1]:.2f} ({resultados_frac[prob]['num_runs']} runs)")
        else:
            print(f"      ✗ prob = {prob:.2f}: nenhum dado encontrado")
        
    # Salvar metadados para esta fração
    if resultados_frac:
        df_metadata = pd.DataFrame([{
            'frac': frac,
            'probabilidade': prob,
            'media_final': resultados_frac[prob]['media_final'],
            'desvio_padrao_final': resultados_frac[prob]['std_final'],
            'num_runs_processados': resultados_frac[prob]['num_runs'],
            'comprimento_temporal': resultados_frac[prob]['comprimento_tempo']
        } for prob in sorted(resultados_frac.keys())])
        
        caminho_metadata = os.path.join(base_out, 'metadata_NE.csv')
        df_metadata.to_csv(caminho_metadata, index=False)
        print(f"  ✓ Metadados salvos em: {caminho_metadata}")
        
        # Salvar configuração para esta fração
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
        print(f"  ✓ Configurações salvas em: {caminho_config}")
        
        # Mostrar resumo desta fração
        print(f"\n  RESUMO - FRAC = {frac}")
        print(f"  {'Probabilidade':<12} | {'Média Final':<12} | {'Desvio Padrão':<12} | {'Runs':<6}")
        print(f"  {'-'*12}+{'-'*14}+{'-'*14}+{'-'*8}")
        for prob in sorted(resultados_frac.keys()):
            stats = resultados_frac[prob]
            print(f"  {prob:.2f}          | {stats['media_final']:>10.2f} | {stats['std_final']:>11.2f} | {stats['num_runs']:>4}")
        
        # Armazenar resultados desta fração no dicionário geral
        todos_resultados[frac] = resultados_frac

# Salvar um arquivo de resumo global com todos os resultados
print(f"\n{'='*80}")
print("CRIANDO RESUMO GLOBAL")
print(f"{'='*80}")

# Criar DataFrame com todos os resultados
dados_global = []
for frac in sorted(todos_resultados.keys()):
    for prob in sorted(todos_resultados[frac].keys()):
        stats = todos_resultados[frac][prob]
        dados_global.append({
            'frac': frac,
            'probabilidade': prob,
            'media_final': stats['media_final'],
            'desvio_padrao_final': stats['std_final'],
            'num_runs': stats['num_runs'],
            'comprimento_tempo': stats['comprimento_tempo']
        })

if dados_global:
    df_global = pd.DataFrame(dados_global)
    caminho_global = os.path.join(base_out_base, 'resumo_global_todos_frac.csv')
    df_global.to_csv(caminho_global, index=False)
    print(f"✓ Resumo global salvo em: {caminho_global}")
    
    # Também salvar em formato pivot para facilitar visualização
    pivot_media = df_global.pivot(index='frac', columns='probabilidade', values='media_final')
    pivot_std = df_global.pivot(index='frac', columns='probabilidade', values='desvio_padrao_final')
    
    caminho_pivot_media = os.path.join(base_out_base, 'pivot_medias_por_frac_prob.csv')
    caminho_pivot_std = os.path.join(base_out_base, 'pivot_desvios_por_frac_prob.csv')
    
    pivot_media.to_csv(caminho_pivot_media)
    pivot_std.to_csv(caminho_pivot_std)
    
    print(f"✓ Pivot de médias salvo em: {caminho_pivot_media}")
    print(f"✓ Pivot de desvios salvo em: {caminho_pivot_std}")
    
    # Mostrar resumo global no console
    print(f"\n{'='*80}")
    print("RESUMO GLOBAL - Todas as frações")
    print(f"{'='*80}")
    print(f"\nFrações processadas: {sorted(todos_resultados.keys())}")
    print(f"Total de combinações frac × prob: {len(df_global)}")
    
    # Mostrar estatísticas básicas
    print(f"\nEstatísticas globais:")
    print(f"  Média final - Mínimo: {df_global['media_final'].min():.2f}")
    print(f"  Média final - Máximo: {df_global['media_final'].max():.2f}")
    print(f"  Média final - Média geral: {df_global['media_final'].mean():.2f}")
    print(f"  Desvio padrão final - Média: {df_global['desvio_padrao_final'].mean():.2f}")
    
    print(f"\n✓ Processamento completo para todas as frações!")
else:
    print("⚠ Nenhum dado foi processado!")