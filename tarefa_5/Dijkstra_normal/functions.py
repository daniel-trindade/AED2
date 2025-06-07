# projeto_dijkstra_basico/functions.py

import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import osmnx as ox
import networkx as nx

# Reimplementação básica de Dijkstra (O(V^2) sem min-heap)
def dijkstra_basico_manual(G, source, target, weight='length'):
    """
    Implementação manual básica do algoritmo de Dijkstra (O(V^2)).
    Calcula o caminho mais curto e a distância.
    """
    distances = {node: float('inf') for node in G.nodes()}
    distances[source] = 0
    previous_nodes = {node: None for node in G.nodes()}
    
    # Use uma lista para simular nós não visitados (sem otimização de min-heap)
    unvisited_nodes = list(G.nodes()) 
    
    # Dicionário auxiliar para acesso rápido ao peso das arestas em MultiDiGraph
    edge_weights_cache = {} 
    
    while unvisited_nodes:
        # Encontrar o nó não visitado com a menor distância (O(V) operação em cada iteração)
        current_node = None
        min_distance = float('inf')
        
        # Otimização: removemos o nó visitado da lista para reduzir a busca
        # Isso ainda é O(V) mas evita iterar sobre nós já processados.
        # A verdadeira lentidão está na busca linear pelo "próximo nó"
        # que seria otimizada por uma min-heap.
        
        # Encontra o nó com a menor distância entre os não visitados
        for node in unvisited_nodes:
            if distances[node] < min_distance:
                min_distance = distances[node]
                current_node = node
        
        # Se não há mais nós alcançáveis ou o destino foi encontrado
        if current_node is None:
            break
        
        # Se o destino foi alcançado, podemos parar
        if current_node == target:
            break
            
        unvisited_nodes.remove(current_node) # Remove para não processar novamente

        # Atualizar distâncias dos vizinhos
        for neighbor in G.neighbors(current_node): # Itera por vizinhos (out-edges)
            
            # Pega o peso da aresta (lidando com MultiDiGraph)
            # Otimização: Cache para evitar recalcular pesos de arestas
            if (current_node, neighbor) not in edge_weights_cache:
                edge_data = G.get_edge_data(current_node, neighbor)
                edge_weight = float('inf')
                if edge_data is None:
                    continue # Não há aresta no sentido correto
                
                if isinstance(edge_data, dict) and '0' in edge_data: # MultiDiGraph
                    edge_weight = min(d.get(weight, float('inf')) for k, d in edge_data.items() if isinstance(d, dict))
                else: # DiGraph ou edge_data é o próprio dicionário
                    edge_weight = edge_data.get(weight, float('inf'))
                edge_weights_cache[(current_node, neighbor)] = edge_weight
            else:
                edge_weight = edge_weights_cache[(current_node, neighbor)]

            if edge_weight == float('inf'): # Aresta não tem o peso ou é inválida
                continue

            new_distance = distances[current_node] + edge_weight
            
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous_nodes[neighbor] = current_node
    
    # Reconstruir o caminho
    path = []
    current = target
    
    # Verifica se o target foi alcançado
    if distances[target] == float('inf'):
        return float('inf'), []

    while current is not None and current in previous_nodes and previous_nodes[current] is not None:
        path.insert(0, current)
        current = previous_nodes[current]
    
    if current == source: # Adiciona o nó de origem se o caminho foi reconstruído corretamente
        path.insert(0, source)
    else: # Caminho incompleto ou inalcançável
        return float('inf'), []
        
    return distances[target], path

def carregar_destinos(arquivo_json):
    try:
        with open(arquivo_json, 'r', encoding='utf-8') as file:
            dados = json.load(file)
        destinos_dict = {}
        contador_bairros = {}
        for entrada in dados:
            neighborhood = entrada['Neighborhood']
            lon = entrada['Lon']
            lat = entrada['Lat']
            if neighborhood not in contador_bairros:
                contador_bairros[neighborhood] = 0
            contador_bairros[neighborhood] += 1
            if contador_bairros[neighborhood] == 1:
                chave = neighborhood
            else:
                chave = f"{neighborhood}_{contador_bairros[neighborhood]}"
            destinos_dict[chave] = (lon, lat)
        print(f"Carregados {len(destinos_dict)} destinos do arquivo {arquivo_json}")
        return destinos_dict
    except Exception as e:
        print(f"Erro ao carregar destinos: {e}")
        return {}

def dividir_destinos_em_clusters(destinos, n_clusters=10):
    coords = np.array([list(coord) for coord in destinos.values()])
    nomes = list(destinos.keys())
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10).fit(coords)
    return {nome: label for nome, label in zip(nomes, kmeans.labels_)}

# Usa o Dijkstra básico manual para calcular a distância
def calcular_distancia_rota(G, no_origem, no_destino):
    """Calcula a distância da rota mais curta usando Dijkstra manual e retorna a distância."""
    try:
        distancia, _ = dijkstra_basico_manual(G, no_origem, no_destino, weight='length')
        return distancia
    except Exception as e:
        print(f"   --> Erro inesperado ao calcular rota de {no_origem} para {no_destino}: {e}")
        return float('inf')

# Retorna o caminho para plotagem, também usando o Dijkstra básico manual
def obter_caminho_rota(G, no_origem, no_destino):
    """Obtém a sequência de nós do caminho mais curto usando Dijkstra manual."""
    try:
        _, path = dijkstra_basico_manual(G, no_origem, no_destino, weight='length')
        return path
    except Exception as e:
        print(f"   --> Erro inesperado ao obter caminho de {no_origem} para {no_destino}: {e}")
        return []

def encontrar_ponto_mais_distante(G, no_inicial, pontos_cluster):
    ponto_distante = None
    max_distancia = -1
    for nome, no_ponto in pontos_cluster.items():
        distancia = calcular_distancia_rota(G, no_inicial, no_ponto)
        if distancia != float('inf') and distancia > max_distancia:
            max_distancia = distancia
            ponto_distante = (nome, no_ponto)
    return ponto_distante, max_distancia

def otimizar_tour_cluster(G, ponto_partida, outros_pontos):
    pontos_a_visitar = outros_pontos.copy()
    tour_ordenado = [ponto_partida]
    ponto_atual = ponto_partida
    while pontos_a_visitar:
        proximo_ponto = min(pontos_a_visitar, key=lambda p: calcular_distancia_rota(G, ponto_atual[1], p[1]))
        tour_ordenado.append(proximo_ponto)
        pontos_a_visitar.remove(proximo_ponto)
        ponto_atual = proximo_ponto
    return tour_ordenado

def plotar_mapa_com_rotas(graph_osmnx, destinos, czoonoses, rotas_completas, labels_clusters):
    print("Iniciando a plotagem em camadas: mapa de fundo e rotas por cima...")
    
    fig, ax = plt.subplots(figsize=(16, 12)) 

    ox.plot_graph(
        graph_osmnx,
        ax=ax, 
        show=False,
        close=False,
        bgcolor='#FFFFFF',
        edge_color='lightgray',
        edge_linewidth=0.5,
        node_size=0
    )
    
    lista_de_rotas_nos = [dados['rota_completa_nos'] for dados in rotas_completas.values()]
    num_clusters = len(lista_de_rotas_nos) 
    cmap = plt.cm.get_cmap('tab10', num_clusters)
    cores_rotas = [cmap(i) for i in range(num_clusters)]

    bairros_por_cluster = {i: set() for i in range(num_clusters)}
    for nome_destino, cluster_id in labels_clusters.items():
        bairro_limpo = nome_destino.split('_')[0]
        if cluster_id < num_clusters:
            bairros_por_cluster[cluster_id].add(bairro_limpo)

    legend_handles = []
    for i, route_data in rotas_completas.items(): 
        route_nodes = route_data['rota_completa_nos']
        
        route_gdf = ox.utils_graph.route_to_gdf(graph_osmnx, route_nodes, weight="length")
        
        for _, row in route_gdf.iterrows():
            if 'geometry' in row and row['geometry'] is not None:
                if row['geometry'].geom_type == 'LineString':
                    xs, ys = row['geometry'].xy
                    ax.plot(xs, ys, color=cores_rotas[i], linewidth=2, alpha=0.8, solid_capstyle='round', zorder=3)
            else:
                u, v = row['u'], row['v']
                if u in graph_osmnx.nodes and v in graph_osmnx.nodes:
                    x1, y1 = graph_osmnx.nodes[u]['x'], graph_osmnx.nodes[u]['y']
                    x2, y2 = graph_osmnx.nodes[v]['x'], graph_osmnx.nodes[v]['y']
                    ax.plot([x1, x2], [y1, y2], color=cores_rotas[i], linewidth=2, alpha=0.8, solid_capstyle='round', zorder=3)
        
        bairros_str = ", ".join(sorted(list(bairros_por_cluster[i])))
        legend_label = f"Cluster {i+1}: {bairros_str}"
        legend_handles.append(plt.Line2D([0], [0], color=cores_rotas[i], lw=3, label=legend_label))

    lon_czoonoses, lat_czoonoses = czoonoses[1], czoonoses[0] 
    ax.plot(lon_czoonoses, lat_czoonoses, '*', color='yellow', markersize=20, markeredgecolor='black', markeredgewidth=1.5, zorder=5, label='Centro de Zoonoses')
    
    czo_handle = plt.Line2D([0], [0], marker='*', color='yellow', markersize=10, linestyle='None',
                            markeredgecolor='black', markeredgewidth=1.5, label='Centro de Zoonoses')
    legend_handles.insert(0, czo_handle) 

    for nome, (lon, lat) in destinos.items():
        ax.plot(lon, lat, 'o', color='black', markersize=5, alpha=0.5, zorder=4)

    ax.set_title("Rotas Otimizadas Sobre a Rede Viária de Natal", fontsize=20, weight='bold', pad=20)
    
    ax.legend(handles=legend_handles, loc='upper left', bbox_to_anchor=(1.02, 1), 
              title="Clusters e Bairros", borderaxespad=0., fontsize='small') 
    
    plt.tight_layout()
    
    print("Mapa com rotas sobrepostas finalizado. Exibindo...")
    plt.show()