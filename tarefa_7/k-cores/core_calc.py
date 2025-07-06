import networkx as nx
import argparse
import os

def calcular_kcore_e_exportar(arquivo_entrada, arquivo_saida=None):
    """
    Calcula o k-core de um grafo e adiciona o atributo 'core' a cada nó.
    
    Args:
        arquivo_entrada (str): Caminho para o arquivo .gexf de entrada
        arquivo_saida (str): Caminho para o arquivo .gexf de saída (opcional)
    """
    
    try:
        # Carrega o grafo do arquivo GEXF
        print(f"Carregando grafo de: {arquivo_entrada}")
        G = nx.read_gexf(arquivo_entrada)
        
        print(f"Grafo carregado com {G.number_of_nodes()} nós e {G.number_of_edges()} arestas")
        
        # Verifica se é um multigrafo e converte para grafo simples se necessário
        if G.is_multigraph():
            print("Detectado multigrafo. Convertendo para grafo simples...")
            # Preserva os atributos dos nós
            G_simple = nx.Graph()
            G_simple.add_nodes_from(G.nodes(data=True))
            
            # Adiciona arestas (remove duplicatas automaticamente)
            for u, v, data in G.edges(data=True):
                if not G_simple.has_edge(u, v):
                    G_simple.add_edge(u, v, **data)
                # Se a aresta já existe, podemos somar pesos ou manter o primeiro
                elif 'weight' in data and 'weight' in G_simple[u][v]:
                    G_simple[u][v]['weight'] += data.get('weight', 1)
            
            G = G_simple
            print(f"Grafo convertido: {G.number_of_nodes()} nós e {G.number_of_edges()} arestas")
        
        # Calcula o k-core de cada nó
        print("Calculando k-core...")
        core_numbers = nx.core_number(G)
        
        # Adiciona o atributo 'core' a cada nó
        nx.set_node_attributes(G, core_numbers, 'core')
        
        # Estatísticas do k-core
        max_core = max(core_numbers.values())
        min_core = min(core_numbers.values())
        print(f"K-core calculado: mínimo = {min_core}, máximo = {max_core}")
        
        # Conta quantos nós estão em cada core
        core_distribution = {}
        for core_value in core_numbers.values():
            core_distribution[core_value] = core_distribution.get(core_value, 0) + 1
        
        print("Distribuição dos cores:")
        for core, count in sorted(core_distribution.items()):
            print(f"  Core {core}: {count} nós")
        
        # Define o arquivo de saída
        if arquivo_saida is None:
            nome_base = os.path.splitext(arquivo_entrada)[0]
            arquivo_saida = f"{nome_base}_kcore.gexf"
        
        # Exporta o grafo modificado
        print(f"Exportando grafo modificado para: {arquivo_saida}")
        nx.write_gexf(G, arquivo_saida)
        
        print("Processo concluído com sucesso!")
        return G
        
    except FileNotFoundError:
        print(f"Erro: Arquivo '{arquivo_entrada}' não encontrado.")
        return None
    except Exception as e:
        print(f"Erro durante o processamento: {e}")
        return None

def main():
    """Função principal com interface de linha de comando"""
    
    parser = argparse.ArgumentParser(
        description='Calcula k-core de um grafo GEXF e adiciona atributo core aos nós'
    )
    parser.add_argument(
        'arquivo_entrada', 
        help='Caminho para o arquivo .gexf de entrada'
    )
    parser.add_argument(
        '-o', '--output', 
        help='Caminho para o arquivo .gexf de saída (opcional)'
    )
    
    args = parser.parse_args()
    
    # Executa o processamento
    calcular_kcore_e_exportar(args.arquivo_entrada, args.output)

if __name__ == "__main__":
    main()