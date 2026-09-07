import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import glob

# Valores de frac (5 a 100, passo 5)
frac_values = np.arange(5, 101, 5)

# Diretórios base
base_data = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/NE_x_t"
output_dir_NE_t = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/plot/NE_x_t"
output_dir_NE_P = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/plot/NE_x_P"
output_dir_NE_norm = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/plot/NE_normalized"

# Criar diretórios de saída se não existirem
os.makedirs(output_dir_NE_t, exist_ok=True)
os.makedirs(output_dir_NE_P, exist_ok=True)
os.makedirs(output_dir_NE_norm, exist_ok=True)

# Dicionário para armazenar todos os dados finais para o gráfico combinado
dados_combinados = []
dados_normalizados = []

# Processar cada fração
for frac in frac_values:
    print(f"\n{'='*80}")
    print(f"PROCESSANDO FRAC = {frac}")
    print(f"{'='*80}")
    
    # Caminho para o diretório de dados desta fração
    base_dir = f"{base_data}/frac_{frac}"
    
    # Verificar se o diretório existe
    if not os.path.exists(base_dir):
        print(f"  ✗ Diretório não encontrado: {base_dir}")
        continue
    
    # Encontrar todos os arquivos CSV (exceto metadados e config)
    arquivos_NE = glob.glob(os.path.join(base_dir, "NE_vs_time_prob_*.csv"))
    
    if not arquivos_NE:
        print(f"  ✗ Nenhum arquivo encontrado em: {base_dir}")
        continue
    
    print(f"  Encontrados {len(arquivos_NE)} arquivos")
    
    # Verificar se o arquivo de metadados existe
    metadata_path = os.path.join(base_dir, "metadata_NE.csv")
    if not os.path.exists(metadata_path):
        print(f"  ✗ Metadados não encontrados: {metadata_path}")
        continue
    
    # === PLOT 1: Todas as curvas juntas (NE original) ===
    plt.figure(figsize=(12, 8))
    cores = plt.cm.viridis(np.linspace(0, 1, len(arquivos_NE)))
    
    for idx, arquivo in enumerate(sorted(arquivos_NE)):
        df = pd.read_csv(arquivo)
        prob = float(arquivo.split('prob_')[1].replace('.csv', ''))
        
        plt.plot(df['time'], df['NE_mean'], 
                label=f'prob = {prob:.2f}',
                color=cores[idx],
                linewidth=2)
        
        if 'NE_mean_minus_std' in df.columns and 'NE_mean_plus_std' in df.columns:
            plt.fill_between(df['time'], 
                           df['NE_mean_minus_std'], 
                           df['NE_mean_plus_std'], 
                           alpha=0.2, 
                           color=cores[idx])
    
    plt.xlabel('Steps', fontsize=12)
    plt.ylabel('N_E', fontsize=12)
    plt.title(f'NE vs Time - frac = {frac}%', fontsize=14, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    output_path_1 = os.path.join(output_dir_NE_t, f"NE_vs_time_all_probabilities_frac_{frac}.png")
    plt.savefig(output_path_1, dpi=300, bbox_inches='tight')
    print(f"  ✓ Plot NE original salvo em NE_x_t: {output_path_1}")
    plt.close()
    
    # === PLOT 2: NE / NE_inicial (normalizado) ===
    print("  Criando plots normalizados...")
    
    plt.figure(figsize=(12, 8))
    cores_norm = plt.cm.plasma(np.linspace(0, 1, len(arquivos_NE)))
    
    # Dicionário para armazenar dados normalizados desta fração
    dados_norm_frac = []
    
    for idx, arquivo in enumerate(sorted(arquivos_NE)):
        df = pd.read_csv(arquivo)
        prob = float(arquivo.split('prob_')[1].replace('.csv', ''))
        
        # Calcular NE / NE_inicial (primeiro valor)
        NE_inicial = df['NE_mean'].iloc[0]
        NE_normalizado = df['NE_mean'] / NE_inicial
        std_normalizado = df['NE_std'] / NE_inicial
        
        # Plotar
        plt.plot(df['time'], NE_normalizado, 
                label=f'prob = {prob:.2f}',
                color=cores_norm[idx],
                linewidth=2)
        
        # Banda de desvio padrão normalizada
        plt.fill_between(df['time'], 
                       NE_normalizado - std_normalizado, 
                       NE_normalizado + std_normalizado, 
                       alpha=0.2, 
                       color=cores_norm[idx])
        
        # Armazenar dados normalizados
        dados_norm_frac.append({
            'frac': frac,
            'prob': prob,
            'NE_inicial': NE_inicial,
            'NE_final': df['NE_mean'].iloc[-1],
            'NE_final_normalizado': df['NE_mean'].iloc[-1] / NE_inicial,
            'NE_final_normalizado_std': df['NE_std'].iloc[-1] / NE_inicial
        })
    
    plt.xlabel('Steps', fontsize=12)
    plt.ylabel('N_E / N_E(0)', fontsize=12)
    plt.title(f'NE Normalizado (NE/NE_inicial) vs Time - frac = {frac}%', fontsize=14, fontweight='bold')
    plt.axhline(y=1, color='black', linestyle='--', alpha=0.5, label='Valor inicial')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    output_path_norm = os.path.join(output_dir_NE_norm, f"NE_normalized_vs_time_frac_{frac}.png")
    plt.savefig(output_path_norm, dpi=300, bbox_inches='tight')
    print(f"  ✓ Plot normalizado salvo em: {output_path_norm}")
    plt.close()
    
    # === PLOT 3: NE final em função da probabilidade (com dados) ===
    df_metadata = pd.read_csv(metadata_path)
    
    # Extrair dados para os gráficos combinados
    for _, row in df_metadata.iterrows():
        dados_combinados.append({
            'frac': frac,
            'probabilidade': row['probabilidade'],
            'media_final': row['media_final'],
            'desvio_padrao_final': row['desvio_padrao_final'],
            'num_runs': row['num_runs_processados']
        })
    
    # Adicionar dados normalizados ao dicionário geral
    for item in dados_norm_frac:
        dados_normalizados.append(item)
    
    # Plot original NE final vs probabilidade
    plt.figure(figsize=(10, 6))
    
    plt.errorbar(df_metadata['probabilidade'], 
                df_metadata['media_final'], 
                yerr=df_metadata['desvio_padrao_final'],
                fmt='o-', 
                capsize=5,
                capthick=2,
                elinewidth=2,
                markersize=8,
                color='red',
                ecolor='gray',
                label='N_E final')
    
    plt.xlabel('Probabilidade', fontsize=12)
    plt.ylabel('N_E Final (média ± std)', fontsize=12)
    plt.title(f'Valor final de N_E em função da probabilidade (frac={frac}%)', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.xticks(df_metadata['probabilidade'])
    plt.legend()
    plt.tight_layout()
    
    output_path_2 = os.path.join(output_dir_NE_P, f"NE_final_vs_probability_frac_{frac}.png")
    plt.savefig(output_path_2, dpi=300, bbox_inches='tight')
    print(f"  ✓ Plot NE final vs probabilidade salvo em NE_x_P: {output_path_2}")
    plt.close()
    
    # === PLOT 3.5: NE médio em função da probabilidade (curva única por fração) ===
    print("  Criando gráfico NE médio vs probabilidade (curvas por fração)...")
    
    plt.figure(figsize=(12, 8))
    
    df_metadata = df_metadata.sort_values('probabilidade')
    
    plt.errorbar(df_metadata['probabilidade'], 
                df_metadata['media_final'], 
                yerr=df_metadata['desvio_padrao_final'],
                marker='o', 
                markersize=8,
                capsize=5,
                capthick=2,
                elinewidth=2,
                label=f'frac = {frac}%',
                linewidth=2.5,
                color=plt.cm.plasma(frac/100))
    
    plt.xlabel(r'$\rho$ (probabilidade de obstáculo)', fontsize=14)
    plt.ylabel(r'$\langle N_E \rangle$', fontsize=14)
    plt.title(f'Média de N_E vs Probabilidade de Obstáculo (frac={frac}%)', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.xticks(df_metadata['probabilidade'])
    plt.legend(loc='best', fontsize=12)
    plt.tight_layout()
    
    output_path_medio = os.path.join(output_dir_NE_P, f"NE_medio_vs_prob_frac_{frac}.png")
    plt.savefig(output_path_medio, dpi=300, bbox_inches='tight')
    print(f"  ✓ NE médio vs probabilidade salvo em: {output_path_medio}")
    plt.close()
    
    # === PLOT 4: Valor final normalizado em função da probabilidade ===
    df_norm_frac = pd.DataFrame(dados_norm_frac)
    
    plt.figure(figsize=(10, 6))
    
    plt.errorbar(df_norm_frac['prob'], 
                df_norm_frac['NE_final_normalizado'], 
                yerr=df_norm_frac['NE_final_normalizado_std'],
                fmt='o-', 
                capsize=5,
                capthick=2,
                elinewidth=2,
                markersize=8,
                color='blue',
                ecolor='gray',
                label='NE_final / NE_inicial')
    
    plt.xlabel('Probabilidade', fontsize=12)
    plt.ylabel('NE_final / NE_inicial', fontsize=12)
    plt.title(f'NE Final Normalizado vs Probabilidade (frac={frac}%)', fontsize=14, fontweight='bold')
    plt.axhline(y=1, color='black', linestyle='--', alpha=0.5, label='Valor inicial')
    plt.grid(True, alpha=0.3)
    plt.xticks(df_norm_frac['prob'])
    plt.legend()
    plt.tight_layout()
    
    output_path_norm_final = os.path.join(output_dir_NE_norm, f"NE_final_normalized_vs_prob_frac_{frac}.png")
    plt.savefig(output_path_norm_final, dpi=300, bbox_inches='tight')
    print(f"  ✓ Plot final normalizado salvo em: {output_path_norm_final}")
    plt.close()
    
    print(f"  ✓ Processamento completo para frac = {frac}")

# === PLOTS COMBINADOS ===
if dados_combinados:
    print(f"\n{'='*80}")
    print("CRIANDO GRÁFICOS COMBINADOS")
    print(f"{'='*80}")
    
    # Converter para DataFrame
    df_combinado = pd.DataFrame(dados_combinados)
    df_norm_combinado = pd.DataFrame(dados_normalizados)
    
    # === PLOT 5: Heatmap (original) ===
    print("  Criando heatmap (original)...")
    pivot_media = df_combinado.pivot(index='frac', columns='probabilidade', values='media_final')
    
    plt.figure(figsize=(14, 10))
    im = plt.imshow(pivot_media.values, 
                   aspect='auto', 
                   cmap='viridis',
                   interpolation='nearest',
                   origin='lower')
    
    plt.colorbar(im, label='N_E final')
    plt.xticks(np.arange(len(pivot_media.columns)), 
               [f'{x:.1f}' for x in pivot_media.columns], 
               rotation=45)
    plt.yticks(np.arange(len(pivot_media.index)), 
               [f'{x}%' for x in pivot_media.index])
    
    plt.xlabel('Probabilidade', fontsize=12)
    plt.ylabel('Fração (frac)', fontsize=12)
    plt.title('N_E Final em função de frac e probabilidade (Heatmap)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output_path_3 = os.path.join(output_dir_NE_P, "NE_final_heatmap_all_frac.png")
    plt.savefig(output_path_3, dpi=300, bbox_inches='tight')
    print(f"  ✓ Heatmap salvo em: {output_path_3}")
    plt.close()
    
    # === PLOT 6: Heatmap (normalizado) ===
    print("  Criando heatmap (normalizado)...")
    pivot_norm = df_norm_combinado.pivot(index='frac', columns='prob', values='NE_final_normalizado')
    
    plt.figure(figsize=(14, 10))
    im = plt.imshow(pivot_norm.values, 
                   aspect='auto', 
                   cmap='coolwarm',
                   interpolation='nearest',
                   origin='lower',
                   vmin=0, vmax=1.2)
    
    plt.colorbar(im, label='NE_final / NE_inicial')
    plt.xticks(np.arange(len(pivot_norm.columns)), 
               [f'{x:.1f}' for x in pivot_norm.columns], 
               rotation=45)
    plt.yticks(np.arange(len(pivot_norm.index)), 
               [f'{x}%' for x in pivot_norm.index])
    
    plt.xlabel('Probabilidade', fontsize=12)
    plt.ylabel('Fração (frac)', fontsize=12)
    plt.title('NE Final Normalizado (NE/NE_inicial) - Heatmap', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output_path_norm_heatmap = os.path.join(output_dir_NE_norm, "NE_final_normalized_heatmap_all_frac.png")
    plt.savefig(output_path_norm_heatmap, dpi=300, bbox_inches='tight')
    print(f"  ✓ Heatmap normalizado salvo em: {output_path_norm_heatmap}")
    plt.close()
    
    # === PLOT 7: NE final em função da probabilidade (todas as frações juntas) ===
    print("  Criando gráfico NE final vs probabilidade para todas as frações...")
    plt.figure(figsize=(12, 8))
    
    # Cores para diferentes frações
    fracs_unicas = sorted(df_combinado['frac'].unique())
    cores_frac = plt.cm.viridis(np.linspace(0, 1, len(fracs_unicas)))
    
    for i, frac in enumerate(fracs_unicas):
        dados_frac = df_combinado[df_combinado['frac'] == frac].sort_values('probabilidade')
        plt.errorbar(dados_frac['probabilidade'], 
                    dados_frac['media_final'],
                    yerr=dados_frac['desvio_padrao_final'],
                    marker='o',
                    capsize=3,
                    capthick=1,
                    elinewidth=1,
                    label=f'frac = {frac}%',
                    color=cores_frac[i],
                    linewidth=1.5,
                    markersize=4)
    
    plt.xlabel('Probabilidade', fontsize=12)
    plt.ylabel('N_E Final', fontsize=12)
    plt.title('N_E Final vs Probabilidade para todas as frações', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    plt.tight_layout()
    
    output_path_prob = os.path.join(output_dir_NE_P, "NE_final_vs_probability_all_frac.png")
    plt.savefig(output_path_prob, dpi=300, bbox_inches='tight')
    print(f"  ✓ NE final vs probabilidade salvo em: {output_path_prob}")
    plt.close()
    
    # === PLOT 8: NE médio vs probabilidade (TODAS as frações juntas - com barras de erro) ===
    print("  Criando gráfico NE médio vs probabilidade para todas as frações...")
    
    plt.figure(figsize=(14, 10))
    
    cores_frac = plt.cm.plasma(np.linspace(0.1, 0.9, len(fracs_unicas)))
    
    for i, frac in enumerate(fracs_unicas):
        dados_frac = df_combinado[df_combinado['frac'] == frac].sort_values('probabilidade')
        if len(dados_frac) > 1:
            plt.errorbar(dados_frac['probabilidade'], 
                        dados_frac['media_final'],
                        yerr=dados_frac['desvio_padrao_final'],
                        marker='o',
                        markersize=5,
                        capsize=3,
                        capthick=1.5,
                        elinewidth=1.5,
                        label=f'frac = {frac}%',
                        color=cores_frac[i],
                        linewidth=2,
                        alpha=0.8)
    
    plt.xlabel(r'$\rho$ (probabilidade de obstáculo)', fontsize=16)
    plt.ylabel(r'$\langle N_E \rangle$ (média final)', fontsize=16)
    plt.title(r'$\langle N_E \rangle$ vs Probabilidade de Obstáculo para todas as frações', 
              fontsize=16, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    plt.tight_layout()
    
    output_path_medio_all = os.path.join(output_dir_NE_P, "NE_medio_vs_prob_all_frac.png")
    plt.savefig(output_path_medio_all, dpi=300, bbox_inches='tight')
    print(f"  ✓ NE médio vs probabilidade (todas frações) salvo em: {output_path_medio_all}")
    plt.close()
    
    # === PLOT 8.5: NE médio vs probabilidade (TODAS as frações - sem barras de erro) ===
    print("  Criando gráfico NE médio vs probabilidade (sem barras de erro)...")
    
    plt.figure(figsize=(14, 10))
    
    for i, frac in enumerate(fracs_unicas):
        dados_frac = df_combinado[df_combinado['frac'] == frac].sort_values('probabilidade')
        if len(dados_frac) > 1:
            plt.plot(dados_frac['probabilidade'], 
                    dados_frac['media_final'],
                    marker='o',
                    markersize=6,
                    label=f'frac = {frac}%',
                    color=cores_frac[i],
                    linewidth=2.5,
                    alpha=0.8)
    
    plt.xlabel(r'$\rho$ (probabilidade de obstáculo)', fontsize=16)
    plt.ylabel(r'$\langle N_E \rangle$ (média final)', fontsize=16)
    plt.title(r'$\langle N_E \rangle$ vs Probabilidade de Obstáculo para todas as frações', 
              fontsize=16, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    plt.tight_layout()
    
    output_path_medio_all_noerr = os.path.join(output_dir_NE_P, "NE_medio_vs_prob_all_frac_no_error.png")
    plt.savefig(output_path_medio_all_noerr, dpi=300, bbox_inches='tight')
    print(f"  ✓ NE médio vs probabilidade (sem barras) salvo em: {output_path_medio_all_noerr}")
    plt.close()
    
    # === PLOT 9: Curvas frac vs NE_final (original) ===
    print("  Criando curvas frac vs NE final...")
    plt.figure(figsize=(12, 8))
    
    probs = sorted(df_combinado['probabilidade'].unique())
    cores_prob = plt.cm.plasma(np.linspace(0, 1, len(probs)))
    
    for i, prob in enumerate(probs):
        dados_prob = df_combinado[df_combinado['probabilidade'] == prob].sort_values('frac')
        if len(dados_prob) > 1:
            plt.plot(dados_prob['frac'], 
                    dados_prob['media_final'], 
                    marker='o',
                    label=f'prob = {prob:.2f}',
                    color=cores_prob[i],
                    linewidth=2,
                    markersize=6)
    
    plt.xlabel('Fração (frac)', fontsize=12)
    plt.ylabel('N_E Final', fontsize=12)
    plt.title('N_E Final vs Fração para diferentes probabilidades', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    plt.tight_layout()
    
    output_path_frac = os.path.join(output_dir_NE_P, "NE_final_vs_frac_all_prob.png")
    plt.savefig(output_path_frac, dpi=300, bbox_inches='tight')
    print(f"  ✓ NE final vs frac salvo em: {output_path_frac}")
    plt.close()
    
    # === PLOT 10: Curvas frac vs NE_final normalizado ===
    print("  Criando curvas frac vs NE normalizado...")
    plt.figure(figsize=(12, 8))
    
    probs_norm = sorted(df_norm_combinado['prob'].unique())
    cores_prob_norm = plt.cm.plasma(np.linspace(0, 1, len(probs_norm)))
    
    for i, prob in enumerate(probs_norm):
        dados_prob = df_norm_combinado[df_norm_combinado['prob'] == prob].sort_values('frac')
        if len(dados_prob) > 1:
            plt.plot(dados_prob['frac'], 
                    dados_prob['NE_final_normalizado'], 
                    marker='o',
                    label=f'prob = {prob:.2f}',
                    color=cores_prob_norm[i],
                    linewidth=2,
                    markersize=6)
    
    plt.xlabel('Fração (frac)', fontsize=12)
    plt.ylabel('NE_final / NE_inicial', fontsize=12)
    plt.title('NE Final Normalizado vs Fração para diferentes probabilidades', fontsize=14, fontweight='bold')
    plt.axhline(y=1, color='black', linestyle='--', alpha=0.5, label='Valor inicial')
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    plt.tight_layout()
    
    output_path_norm_frac = os.path.join(output_dir_NE_norm, "NE_final_normalized_vs_frac_all_prob.png")
    plt.savefig(output_path_norm_frac, dpi=300, bbox_inches='tight')
    print(f"  ✓ Curvas normalizadas salvas em: {output_path_norm_frac}")
    plt.close()
    
    # === PLOT 11: NE final normalizado vs probabilidade (todas as frações) ===
    print("  Criando gráfico NE normalizado vs probabilidade...")
    plt.figure(figsize=(12, 8))
    
    fracs_unicas_norm = sorted(df_norm_combinado['frac'].unique())
    cores_frac_norm = plt.cm.viridis(np.linspace(0, 1, len(fracs_unicas_norm)))
    
    for i, frac in enumerate(fracs_unicas_norm):
        dados_frac = df_norm_combinado[df_norm_combinado['frac'] == frac].sort_values('prob')
        plt.errorbar(dados_frac['prob'], 
                    dados_frac['NE_final_normalizado'],
                    yerr=dados_frac['NE_final_normalizado_std'],
                    marker='o',
                    capsize=3,
                    capthick=1,
                    elinewidth=1,
                    label=f'frac = {frac}%',
                    color=cores_frac_norm[i],
                    linewidth=1.5,
                    markersize=4)
    
    plt.xlabel('Probabilidade', fontsize=12)
    plt.ylabel('NE_final / NE_inicial', fontsize=12)
    plt.title('NE Final Normalizado vs Probabilidade para todas as frações', fontsize=14, fontweight='bold')
    plt.axhline(y=1, color='black', linestyle='--', alpha=0.5, label='Valor inicial')
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    plt.tight_layout()
    
    output_path_norm_prob = os.path.join(output_dir_NE_norm, "NE_final_normalized_vs_probability_all_frac.png")
    plt.savefig(output_path_norm_prob, dpi=300, bbox_inches='tight')
    print(f"  ✓ NE normalizado vs probabilidade salvo em: {output_path_norm_prob}")
    plt.close()
    
    # Salvar dados combinados em CSV
    output_csv_norm = os.path.join(output_dir_NE_norm, "dados_normalizados_todas_frac.csv")
    df_norm_combinado.to_csv(output_csv_norm, index=False)
    print(f"  ✓ Dados normalizados salvos em: {output_csv_norm}")
    
    output_csv = os.path.join(output_dir_NE_P, "dados_combinados_todas_frac.csv")
    df_combinado.to_csv(output_csv, index=False)
    print(f"  ✓ Dados combinados salvos em: {output_csv}")
    
    print(f"\n✓ Todos os plots combinados foram criados!")
else:
    print("\n⚠ Nenhum dado foi processado!")

print(f"\n{'='*80}")
print("PROCESSAMENTO CONCLUÍDO!")
print(f"{'='*80}")
print(f"\nResumo dos diretórios de saída:")
print(f"  - NE_x_t (original): {output_dir_NE_t}")
print(f"  - NE_x_P (original): {output_dir_NE_P}")
print(f"  - NE_normalized: {output_dir_NE_norm}")