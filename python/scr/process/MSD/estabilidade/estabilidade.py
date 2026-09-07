import pandas as pd
import numpy as np
import os
from scipy import stats
from pathlib import Path

def analisar_por_residuos(arquivo_csv, tolerancia_percentual=5.0, min_pontos=10):
    """
    Analisa o ajuste da curva calculando o erro percentual entre o fit e os dados reais.
    
    Parâmetros:
    - arquivo_csv: caminho do arquivo
    - tolerancia_percentual: erro máximo aceitável em % (ex: 5.0 = 5%)
    - min_pontos: número mínimo de pontos para começar
    
    Retorna:
    - ponto_otimo: dicionário com informações do melhor ponto de corte
    - df_filtrado: DataFrame com os pontos selecionados
    - inclinacao_final: inclinação do fit final
    """
    
    try:
        df = pd.read_csv(arquivo_csv)
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return None, None, None
    
    # Verificar colunas
    if 'time' not in df.columns or 'msd_mean' not in df.columns:
        return None, None, None
    
    # Remover valores não positivos
    df = df[(df['time'] > 0) & (df['msd_mean'] > 0)].reset_index(drop=True)
    
    if len(df) < min_pontos:
        return None, None, None
    
    resultados = []
    
    # Testar diferentes pontos de corte (do final para o começo)
    for corte in range(len(df) - min_pontos, -1, -1):
        # Pega os dados do corte até o final
        x_data = df['time'].iloc[corte:].values
        y_data = df['msd_mean'].iloc[corte:].values
        
        # Fit em escala log
        log_x = np.log10(x_data)
        log_y = np.log10(y_data)
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_x, log_y)
        
        # Predição do fit
        log_y_pred = intercept + slope * log_x
        y_pred = 10**log_y_pred
        
        # Calcula erro percentual para cada ponto
        erro_percentual = np.abs((y_data - y_pred) / y_data) * 100
        
        # Métricas
        erro_medio = np.mean(erro_percentual)
        erro_maximo = np.max(erro_percentual)
        erro_std = np.std(erro_percentual)
        
        resultados.append({
            'corte': corte,
            'n_pontos': len(x_data),
            'primeiro_x': x_data[0],
            'ultimo_x': x_data[-1],
            'inclinacao': slope,
            'r2': r_value**2,
            'erro_medio': erro_medio,
            'erro_maximo': erro_maximo,
            'erro_std': erro_std,
            'dentro_tolerancia': erro_maximo <= tolerancia_percentual
        })
    
    resultados_df = pd.DataFrame(resultados)
    resultados_ok = resultados_df[resultados_df['dentro_tolerancia'] == True]
    
    if len(resultados_ok) == 0:
        # Se nenhum atende, pega o que tem menor erro máximo
        ponto_otimo = resultados_df.loc[resultados_df['erro_maximo'].idxmin()].to_dict()
        ponto_otimo['atingiu_tolerancia'] = False
    else:
        # Pega o que tem mais pontos (menor corte)
        ponto_otimo = resultados_ok.loc[resultados_ok['corte'].idxmin()].to_dict()
        ponto_otimo['atingiu_tolerancia'] = True
    
    return ponto_otimo, df, ponto_otimo['inclinacao']


def main():
    # ==================== CONFIGURAÇÕES ====================
    tolerancia_percentual = 2.0  # 5% de erro máximo aceitável
    min_pontos = 5              # Mínimo de pontos para análise
    tamanho_janela = 10          # (não usado, mas mantido para compatibilidade)
    
    # Listas de parâmetros
    #frac_values = list(range(5, 105, 5))  # 5, 10, 15, ..., 100
    frac_values = [5,50,100]
    obs_values = [round(i/10, 2) for i in range(0, 11)]  # 0.00, 0.10, ..., 1.00
    
    # Lista para armazenar todos os resultados
    resultados = []
    
    # Path base
    base_path = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/512/MSD_sre_2_src_2_prob_v_frac_v/"
    
    print("="*80)
    print("ANÁLISE POR RESÍDUOS - PROCESSANDO TODAS COMBINAÇÕES")
    print(f"Tolerância: {tolerancia_percentual}% de erro máximo")
    print("="*80)
    
    # Percorrer todas as combinações
    total_combinacoes = len(frac_values) * len(obs_values)
    processados = 0
    
    for frac in frac_values:
        for obs in obs_values:
            processados += 1
            print(f"\n[{processados}/{total_combinacoes}] Processando: frac = {frac}, obsprob = {obs:.2f}")
            
            # Construir caminho do arquivo
            arquivo_csv = os.path.join(
                base_path,
                f"frac_{frac}",
                f"obsprob_{obs:.2f}",
                f"msd_ensemble_frac_{frac}_obsprob_{obs:.2f}.csv"
            )
            
            # Verificar se arquivo existe
            if not os.path.exists(arquivo_csv):
                print(f"  ⚠️ Arquivo não encontrado")
                resultados.append({
                    'frac': frac,
                    'obsprob': obs,
                    'status': 'arquivo_nao_encontrado',
                    'atingiu_tolerancia': False,
                    'inclinacao': None,
                    'primeiro_x': None,
                    'ultimo_x': None,
                    'n_pontos': None,
                    'r2': None,
                    'erro_maximo': None,
                    'erro_medio': None,
                    'erro_std': None
                })
                continue
            
            # Analisar
            ponto_otimo, df_full, inclinacao = analisar_por_residuos(arquivo_csv, tolerancia_percentual, min_pontos)
            
            if ponto_otimo is not None:
                # Salvar resultados
                resultado = {
                    'frac': frac,
                    'obsprob': obs,
                    'primeiro_x': round(ponto_otimo['primeiro_x'], 2),
                    'n_pontos': ponto_otimo['n_pontos'],
                    'r2': round(ponto_otimo['r2'], 4),
                    'corte': ponto_otimo['corte']
                }
                resultados.append(resultado)
                
                if ponto_otimo['atingiu_tolerancia']:
                    print(f"  ✓ OK - α={ponto_otimo['inclinacao']:.4f}, pontos={ponto_otimo['n_pontos']}, erro_max={ponto_otimo['erro_maximo']:.2f}%")
                else:
                    print(f"  ⚠️ Não atingiu tolerância - α={ponto_otimo['inclinacao']:.4f}, pontos={ponto_otimo['n_pontos']}, erro_max={ponto_otimo['erro_maximo']:.2f}%")
                
                # Salvar arquivo individual dos pontos filtrados (opcional)
                output_dir = f"resultados_residuos_frac_{frac}_obs_{obs:.2f}"
                os.makedirs(output_dir, exist_ok=True)
                
                # Filtrar os dados originais pelo ponto de corte
                df_filtrado = df_full.iloc[ponto_otimo['corte']:].copy()
                df_filtrado[['time', 'msd_mean']].to_csv(
                    f"{output_dir}/resultado_filtrado.csv", 
                    index=False
                )
                
            else:
                print(f"  ✗ Falha ao processar")
                resultados.append({
                    'frac': frac,
                    'obsprob': obs,
                    'status': 'erro_processamento',
                    'atingiu_tolerancia': False,
                    'inclinacao': None,
                    'primeiro_x': None,
                    'n_pontos': None,
                    'r2': None,
                    'erro_maximo': None,
                    'erro_medio': None,
                    'erro_std': None
                })
    
    # Salvar todos os resultados em um único arquivo CSV
    df_resultados = pd.DataFrame(resultados)
    
    # Salvar com formatação
    df_resultados.to_csv('todos_resultados_residuos.csv', index=False, float_format='%.4f')
    
    print("\n" + "="*80)
    print("PROCESSAMENTO CONCLUÍDO!")
    print("="*80)
    print(f"Total de combinações processadas: {len(resultados)}")
    print(f"Arquivo 'todos_resultados_residuos.csv' salvo com todos os resultados")
    
    # Estatísticas finais
    df_ok = df_resultados[df_resultados['status'] == 'ok']
    
    return df_resultados


if __name__ == "__main__":
    resultados = main()