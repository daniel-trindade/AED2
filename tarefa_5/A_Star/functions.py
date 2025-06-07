# projeto_astar/functions.py

import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import osmnx as ox
import networkx as nx
from math import sqrt 

# MANTENHA A FUNÇÃO HEURÍSTICA AQUI, MAS COM G COMO PRIMEIRO ARGUMENTO
def heuristic(G, u, v):
    """Calcula a distância euclidiana entre dois nós (u e v) no grafo G."""
    x1, y1 = G.nodes[u]["x"], G.nodes[u]["y"]
    x2, y2 = G.nodes[v]["x"], G.nodes[v]["y"]
    return sqrt((x1 - x2)**2 + (y1 - y2)**2)

def carregar_destinos(arquivo_json):
    """Carrega os destinos, assumindo que o db.json está com Lat e Lon corretos."""
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
    """Divide os destinos em clusters usando K-Means."""
    coords = np.array([list(coord) for coord in destinos.values()])
    nomes = list(destinos.keys())
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10).fit(coords)
    return {nome: label for nome, label in zip(nomes, kmeans.labels_)}

# AGORA, calcular_distancia_rota TAMBÉM RECEBE O GRAFO G
def calcular_distancia_rota(G, no_origem, no_destino):
    """Calcula a distância da rota mais curta usando A* e retorna a distância."""
    try:
        # AQUI USAMOS UMA FUNÇÃO LAMBDA PARA ENCAPSULAR G E PASSAR PARA A HEURÍSTICA
        return nx.astar_path_length(G, no_origem, no_destino, heuristic=lambda u, v: heuristic(G, u, v), weight='length')
    except nx.NetworkXNoPath:
        return float('inf')
    except Exception as e:
        if "No path between" in str(e): 
             return float('inf')
        print(f"   --> Erro inesperado ao calcular rota de {no_origem} para {no_destino}: {e}")
        return float('inf')

# encontrar_ponto_mais_distante e otimizar_tour_cluster já recebem G, então não precisam de mudanças
def encontrar_ponto_mais_distante(G, no_inicial, pontos_cluster):
    """Encontra o ponto do cluster com a maior distância de rota a partir de um nó inicial."""
    ponto_distante = None
    max_distancia = -1
    for nome, no_ponto in pontos_cluster.items():
        distancia = calcular_distancia_rota(G, no_inicial, no_ponto) # Aqui G já é passado
        if distancia != float('inf') and distancia > max_distancia:
            max_distancia = distancia
            ponto_distante = (nome, no_ponto)
    return ponto_distante, max_distancia

def otimizar_tour_cluster(G, ponto_partida, outros_pontos):
    """Cria uma rota otimizada (vizinho mais próximo) para visitar os pontos do cluster."""
    pontos_a_visitar = outros_pontos.copy()
    tour_ordenado = [ponto_partida]
    ponto_atual = ponto_partida
    while pontos_a_visitar:
        proximo_ponto = min(pontos_a_visitar, key=lambda p: calcular_distancia_rota(G, ponto_atual[1], p[1])) # Aqui G já é passado
        tour_ordenado.append(proximo_ponto)
        pontos_a_visitar.remove(proximo_ponto)
        ponto_atual = proximo_ponto
    return tour_ordenado

# plotar_mapa_com_rotas não precisa de alteração, pois as rotas já vêm prontas do main
def plotar_mapa_com_rotas(graph_osmnx, destinos, czoonoses, rotas_completas, labels_clusters):
    """
    Versão final que desenha o mapa de ruas e sobrepõe as rotas coloridas,
    agora com uma legenda detalhada dos clusters e seus bairros.
    """
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
        
        # CORREÇÃO DEFINITIVA AQUI: ox.routing.route_to_gdf
        route_gdf = ox.routing.route_to_gdf(graph_osmnx, route_nodes, weight="length")
        
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