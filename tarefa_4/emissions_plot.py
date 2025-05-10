import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_codecarbon_data(csv_path='emissions/emissions_osmnx.csv'):
    """
    Plota gráficos para visualizar os dados de recursos capturados pelo codecarbon.
    
    Parâmetros:
    csv_path (str): Caminho para o arquivo CSV gerado pelo codecarbon
    """
    # Verificar se o arquivo existe
    if not os.path.exists(csv_path):
        print(f"Arquivo {csv_path} não encontrado!")
        return
    
    # Carregar os dados do CSV
    try:
        df = pd.read_csv(csv_path)
        print(f"Dados carregados com sucesso! Colunas disponíveis: {', '.join(df.columns.tolist())}")
    except Exception as e:
        print(f"Erro ao carregar o arquivo CSV: {e}")
        return
    
    # Configurar o estilo dos gráficos
    sns.set_style("whitegrid")
    plt.figure(figsize=(15, 12))
    
    # 1. Gráfico das emissões totais
    plt.subplot(2, 2, 1)
    plt.bar(['Emissões de CO2'], [df['emissions'].sum()], color='darkgreen')
    plt.title('Emissões Totais de CO2 (kg)', fontsize=14)
    plt.ylabel('CO2 (kg)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # 2. Gráfico de consumo de energia
    plt.subplot(2, 2, 2)
    energia_cols = [col for col in df.columns if 'energy' in col.lower()]
    if energia_cols:
        df[energia_cols].sum().plot(kind='bar', color='orange')
        plt.title('Consumo de Energia por Fonte (kWh)', fontsize=14)
        plt.ylabel('Energia (kWh)')
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
    else:
        plt.text(0.5, 0.5, 'Dados de energia não disponíveis', 
                 horizontalalignment='center', verticalalignment='center')
        plt.title('Consumo de Energia', fontsize=14)
    
    # 3. Gráfico de uso da CPU ao longo do tempo (se houver dados temporais)
    plt.subplot(2, 2, 3)
    if 'timestamp' in df.columns and 'cpu_power' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        sns.lineplot(data=df, x='timestamp', y='cpu_power', color='blue')
        plt.title('Uso de Energia da CPU ao Longo do Tempo', fontsize=14)
        plt.xlabel('Tempo')
        plt.ylabel('Energia CPU (W)')
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.7)
    else:
        # Se não houver dados temporais, plotar CPU vs RAM
        cpu_cols = [col for col in df.columns if 'cpu' in col.lower()]
        if cpu_cols:
            df[cpu_cols].sum().plot(kind='bar', color='blue')
            plt.title('Uso de Recursos da CPU', fontsize=14)
            plt.xticks(rotation=45)
            plt.grid(axis='y', linestyle='--', alpha=0.7)
        else:
            plt.text(0.5, 0.5, 'Dados de CPU não disponíveis', 
                     horizontalalignment='center', verticalalignment='center')
            plt.title('Uso da CPU', fontsize=14)
    
    # 4. Breakdown de emissões por componente (se disponível)
    plt.subplot(2, 2, 4)
    emission_breakdown = ['cpu_energy', 'gpu_energy', 'ram_energy']
    emission_data = []
    emission_labels = []
    
    for col in emission_breakdown:
        if col in df.columns:
            emission_data.append(df[col].sum())
            emission_labels.append(col.replace('_energy', '').upper())
    
    if emission_data:
        plt.pie(emission_data, labels=emission_labels, autopct='%1.1f%%', 
                startangle=90, shadow=True, explode=[0.05]*len(emission_data))
        plt.title('Distribuição de Energia por Componente', fontsize=14)
    else:
        plt.text(0.5, 0.5, 'Dados detalhados de energia não disponíveis', 
                 horizontalalignment='center', verticalalignment='center')
        plt.title('Distribuição de Energia', fontsize=14)
    
    # Ajustar layout e mostrar os gráficos
    plt.tight_layout()
    plt.savefig('codecarbon_resources.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Gráficos salvos como 'codecarbon_resources.png'")
    
    # Gerar estatísticas resumidas
    print("\nEstatísticas resumidas dos recursos monitorados:")
    if len(df) > 0:
        # Calcular duração em minutos
        if 'duration' in df.columns:
            print(f"Duração total: {df['duration'].sum():.2f} segundos")
        
        # Emissões totais
        if 'emissions' in df.columns:
            print(f"Emissões totais: {df['emissions'].sum():.6f} kg de CO2")
        
        # Energia total
        energy_cols = [col for col in df.columns if 'energy' in col.lower()]
        if energy_cols:
            total_energy = df[energy_cols].sum().sum()
            print(f"Energia total consumida: {total_energy:.6f} kWh")
    else:
        print("Não há dados suficientes para gerar estatísticas.")


if __name__ == "__main__":
    # Executar o plot com o caminho padrão do arquivo emissions.csv
    plot_codecarbon_data()
