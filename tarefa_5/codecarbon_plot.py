import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl

EMISSIONS_SCALE = 1000    # kg → g
ENERGY_SCALE    = 1000    # kWh → Wh

mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = ['DejaVu Sans']

def analyze_codecarbon_data():
    folder_path = "pegada_de_carbono/"
    print(f"Analisando dados em: {os.path.abspath(folder_path)}")
    
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    if not csv_files:
        print("Nenhum CSV encontrado em:", os.path.abspath(folder_path))
        return

    all_data, labels = [], []
    for file_path in csv_files:
        try:
            name = os.path.basename(file_path).replace('.csv', '')
            labels.append(name)
            df = pd.read_csv(file_path)
            metrics = {
                'emissions': df['emissions'].sum(),
                'energy_consumed': df['energy_consumed'].sum(),
                'duration': df['duration'].sum(),
                'cpu_power': df['cpu_power'].mean(),
                'ram_power': df['ram_power'].mean() if 'ram_power' in df.columns else 0
            }
            all_data.append(metrics)
            print(f"Processado: {name}")
        except Exception as e:
            print(f"Erro ao processar {file_path}: {e}")

    comparison_df = pd.DataFrame(all_data, index=labels)
    # Remove “None” como nome de índice
    comparison_df.index.name = ''
    plot_comparisons(comparison_df)

def annotate_bars(ax, fmt="{:.2f}", pad=3, scale=1.10):
    # seleciona apenas barras com altura > 0
    bars = [b for b in ax.patches if b.get_height() > 0]
    if not bars:
        return
    heights = [b.get_height() for b in bars]
    ax.set_ylim(0, max(heights) * scale)
    for bar in bars:
        h = bar.get_height()
        ax.annotate(
            fmt.format(h),
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, pad), textcoords='offset points',
            ha='center', va='bottom'
        )

def plot_comparisons(df):
    # cria colunas escaladas
    df['emissions_g'] = df['emissions'] * EMISSIONS_SCALE
    df['energy_Wh']   = df['energy_consumed'] * ENERGY_SCALE

    sns.set(style="whitegrid")
    fig, axs = plt.subplots(2, 2, figsize=(14, 12), gridspec_kw={'hspace': 0.5})
    fig.suptitle('Comparativo de Emissão de Carbono e Consumo de Energia', fontsize=16)

    # 1. Emissões de Carbono (g CO₂eq)
    sns.barplot(x=df.index, y='emissions_g', data=df, palette='viridis', ax=axs[0,0])
    axs[0,0].set_title('Emissões de Carbono (g CO2)')
    axs[0,0].set_ylabel('Emissões (g CO2)')
    axs[0,0].set_xlabel('')
    annotate_bars(axs[0,0])

    # 2. Consumo de Energia (Wh)
    sns.barplot(x=df.index, y='energy_Wh', data=df, palette='viridis', ax=axs[0,1])
    axs[0,1].set_title('Consumo de Energia (Wh)')
    axs[0,1].set_ylabel('Energia (Wh)')
    axs[0,1].set_xlabel('')
    annotate_bars(axs[0,1])

    # 3. Duração da Execução (s)
    sns.barplot(x=df.index, y='duration', data=df, palette='viridis', ax=axs[1,0])
    axs[1,0].set_title('Duração da Execução (s)')
    axs[1,0].set_ylabel('Duração (s)')
    axs[1,0].set_xlabel('')
    annotate_bars(axs[1,0])

    # 4. Consumo de Potência por Componente (sem zeros)
    power_data = (
        df[['cpu_power','ram_power']]
        .melt(ignore_index=False, var_name='Componente', value_name='Potência (W)')
        .reset_index().rename(columns={'index': ''})
    )
    # Filtra para remover quaisquer valores zero
    power_data = power_data[power_data['Potência (W)'] > 0]

    sns.barplot(x='', y='Potência (W)', hue='Componente', data=power_data, ax=axs[1,1])
    axs[1,1].set_title('Consumo de Potência por Componente (W)')
    axs[1,1].set_ylabel('Potência (W)')
    axs[1,1].set_xlabel('')
    axs[1,1].legend(title='Componente')
    annotate_bars(axs[1,1])

    plt.tight_layout()
    plt.subplots_adjust(top=0.90)
    plt.show()


analyze_codecarbon_data()