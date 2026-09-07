import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from tqdm import tqdm

# Caminhos
input_dir = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/no_x_t"
output_dir = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/plot/no_x_t"

os.makedirs(output_dir, exist_ok=True)

L2 = 256*256

def main():
    print("=" * 70)
    print("CRIANDO GRÁFICOS - NO/L² vs TEMPO E NO/L² MÉDIO vs OBSTÁCULOS")
    print("=" * 70)
    
    # Ler todos os arquivos processados
    print("\n📂 Lendo arquivos...")
    arquivos = [f for f in os.listdir(input_dir) 
                if f.startswith("no_x_t_frac_") and f.endswith(".csv")]
    
    print(f"Total de arquivos encontrados: {len(arquivos)}")
    
    # Organizar dados por fração 
    dados_todas_frac = {}
    
    for arquivo in tqdm(arquivos, desc="Carregando"):
        partes = arquivo.replace('no_x_t_', '').replace('.csv', '').split('_')
        frac = int(partes[1])
        obsprob = float(partes[3])
        
        caminho = os.path.join(input_dir, arquivo)
        df = pd.read_csv(caminho)
        
        if frac not in dados_todas_frac:
            dados_todas_frac[frac] = {}
        dados_todas_frac[frac][obsprob] = df
    
    print(f"\n✓ Dados carregados:")
    print(f"  - Frações: {sorted(dados_todas_frac.keys())}")
    print(f"  - Total de combinações: {sum(len(d) for d in dados_todas_frac.values())}")
    
    # ============================================
    # GRÁFICO 1: NO/L² vs TEMPO (passos)
    # ============================================
    print("\n" + "=" * 70)
    print("📊 GRÁFICO 1: NO/L² vs PASSOS (um por fração)")
    print("=" * 70)

    cores = plt.cm.viridis(np.linspace(0, 1, 11))
    
    for frac in tqdm(sorted(dados_todas_frac.keys()), desc="Gerando gráficos vs tempo"):
        dados_frac = dados_todas_frac[frac]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        obsprobs = sorted(dados_frac.keys())
        
        for i, obsprob in enumerate(obsprobs):
            df = dados_frac[obsprob]
            
            # Converter para numpy arrays
            time = np.array(df['time'].values, dtype=float)
            NO_mean = np.array(df['NO_mean'].values, dtype=float)
            
            # Calcular NO/L²
            NO_norm = NO_mean / L2
            
            # Plotar apenas a linha (sem banda de erro)
            ax.plot(time, NO_norm, 
                   label=f'$N^{{C}}$= {obsprob:.2f}$N^{{E}}_{{0}}$',
                   linewidth=2.5)
        
        ax.set_xlabel('steps', fontsize=14)
        ax.set_ylabel(r'$\rho$', fontsize=14)
        ax.legend(loc='best', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)
        
        plt.tight_layout()
        
        nome_arquivo = f'NO_L2_vs_tempo_frac_{frac}.pdf'
        caminho_salvar = os.path.join(output_dir, nome_arquivo)
        plt.savefig(caminho_salvar, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ {nome_arquivo}")



    # ============================================
# DEBUG: MOSTRAR VALORES LIDOS
# ============================================
    print("\n" + "=" * 70)
    print("🔍 DEBUG: Valores carregados para cada fração")
    print("=" * 70)

    for frac in sorted(dados_todas_frac.keys()):
        print(f"\n📊 frac = {frac}")
        dados_frac = dados_todas_frac[frac]
        obsprobs = sorted(dados_frac.keys())
        
        print(f"   Número de obsprob: {len(obsprobs)}")
        print(f"   Valores de obsprob: {[f'{x:.3f}' for x in obsprobs]}")
        
        # Mostrar primeiras linhas de cada DataFrame
        for obsprob in obsprobs[:3]:  # Mostra só os 3 primeiros para não poluir
            df = dados_frac[obsprob]
            print(f"\n   obsprob = {obsprob:.3f}:")
            print(f"      - shape: {df.shape}")
            print(f"      - time: {df['time'].min():.0f} a {df['time'].max():.0f}")
            print(f"      - NO_mean: {df['NO_mean'].min():.3f} a {df['NO_mean'].max():.3f}")
            print(f"      - Primeiras 3 linhas:")
            print(df[['time', 'NO_mean']].head(3).to_string(index=False))
        
        if len(obsprobs) > 3:
            print(f"\n   ... e mais {len(obsprobs) - 3} valores de obsprob")

    print("\n" + "=" * 70)
    print("✅ Fim do debug")
    print("=" * 70)

   # ============================================
    # GRÁFICO 2: NO/L² MÉDIO vs PROBABILIDADE DE OBSTÁCULO (rho)
    # ============================================
    print("\n" + "=" * 70)
    print("📊 GRÁFICO 2: NO/L² MÉDIO vs PROBABILIDADE DE OBSTÁCULOS")
    print("=" * 70)

    # Calcular médias temporais (IGNORANDO DATAFRAMES VAZIOS)
    medias_por_frac = {}

    for frac in sorted(dados_todas_frac.keys()):
        dados_frac = dados_todas_frac[frac]
        obsprobs = sorted(dados_frac.keys())
        medias = []
        erros = []
        obsprobs_validos = []  # Lista para guardar apenas os válidos
        
        for obsprob in obsprobs:
            df = dados_frac[obsprob]
            
            # VERIFICAR SE O DATAFRAME NÃO ESTÁ VAZIO
            if df.empty:
                print(f"⚠️  frac = {frac}, obsprob = {obsprob:.3f}: DataFrame vazio, pulando...")
                continue
            
            NO_mean = np.array(df['NO_mean'].values, dtype=float)
            NO_norm = NO_mean / L2
            media_temporal = np.mean(NO_norm)
            std_temporal = np.std(NO_norm)
            
            medias.append(media_temporal)
            erros.append(std_temporal)
            obsprobs_validos.append(obsprob)
        
        # Só guardar se tiver dados válidos
        if obsprobs_validos:
            medias_por_frac[frac] = {
                'obsprob': obsprobs_validos,
                'medias': medias,
                'erros': erros
            }
        else:
            print(f"⚠️  frac = {frac}: Nenhum dado válido encontrado!")

    # Criar gráfico
    fig, ax = plt.subplots(figsize=(12, 8))

    fracs = sorted(medias_por_frac.keys())
    cores_frac = plt.cm.plasma(np.linspace(0.2, 0.9, len(fracs)))

    for i, frac in enumerate(fracs):
        dados = medias_por_frac[frac]
        ax.errorbar(dados['obsprob'], dados['medias'], 
                yerr=dados['erros'],
                marker='o', markersize=10, linewidth=2.5,
                capsize=5, capthick=2,
                label=f'$N^{{C}} = {frac}N^{{E}}$',
                color=cores_frac[i],
                elinewidth=1.5)

    ax.set_xlabel(r'$\rho$', fontsize=14)
    ax.set_ylabel(r'$\langle \rho_{NO} \rangle$', fontsize=14)
    ax.legend(loc='best', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-0.08, 1.01)
    ax.set_ylim(bottom=0)
        
    plt.tight_layout()

    nome_arquivo = 'NO_L2_medio_vs_rho.pdf'
    caminho_salvar = os.path.join(output_dir, nome_arquivo)
    plt.savefig(caminho_salvar, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  ✓ {nome_arquivo}")
        
    # ============================================
    # SALVAR DADOS EM CSV
    # ============================================
    print("\n" + "=" * 70)
    print("💾 Salvando dados em CSV...")
    
    df_medias = pd.DataFrame()
    for frac in fracs:
        dados = medias_por_frac[frac]
        temp_df = pd.DataFrame({
            'frac': frac,
            'obsprob': dados['obsprob'],
            'NO_L2_medio': dados['medias'],
            'NO_L2_std': dados['erros']
        })
        df_medias = pd.concat([df_medias, temp_df], ignore_index=True)
    
    df_medias.to_csv(os.path.join(output_dir, 'NO_L2_medio_vs_obsprob.csv'), index=False)
    print(f"  ✓ Dados médios salvos em: NO_L2_medio_vs_obsprob.csv")
    
    # ============================================
    # RESUMO FINAL
    # ============================================
    print("\n" + "=" * 70)
    print("✅ RESULTADOS FINAIS")
    print("=" * 70)
    print(f"📁 Pasta de saída: {output_dir}")
    print(f"\n📊 Gráficos gerados:")
    print(f"  - {len(dados_todas_frac)} gráficos de NO/L² vs tempo (um por fração)")
    print(f"  - 1 gráfico de NO/L² médio vs obsprob")
    print(f"  - 1 arquivo CSV com dados médios")
    print(f"\n📈 Total: {len(dados_todas_frac) + 2} arquivos")
    print("=" * 70)

if __name__ == "__main__":
    main()