import math
import time
import json
import heapq
import requests
import osmnx as ox
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from collections import defaultdict

# Função para carregar destinos do arquivo JSON
def carregar_destinos(arquivo_json):
    """
    Carrega os destinos do arquivo db.json mantendo todas as ocorrências
    Formato: "Neighborhood_ID": (Lon, Lat) ou usando lista de coordenadas por bairro
    """
    try:
        with open(arquivo_json, 'r', encoding='utf-8') as file:
            dados = json.load(file)

        destinos_dict = {}
        contador_bairros = {}
        
        for entrada in dados:
            neighborhood = entrada['Neighborhood']
            lon = entrada['Lon']
            lat = entrada['Lat']
            
            # Contar ocorrências do bairro
            if neighborhood not in contador_bairros:
                contador_bairros[neighborhood] = 0
            contador_bairros[neighborhood] += 1
            
            # Criar chave única para cada ocorrência
            if contador_bairros[neighborhood] == 1:
                # Primeira ocorrência mantém o nome original
                chave = neighborhood
            else:
                # Demais ocorrências recebem sufixo
                chave = f"{neighborhood}_{contador_bairros[neighborhood]}"
            
            destinos_dict[chave] = (lon, lat)
        
        print(f"Carregados {len(destinos_dict)} destinos do arquivo {arquivo_json}")
        print(f"Distribuição por bairro:")
        for bairro, count in contador_bairros.items():
            if count > 1:
                print(f"  {bairro}: {count} ocorrências")
        
        return destinos_dict
        
    except FileNotFoundError:
        print(f"Erro: Arquivo {arquivo_json} não encontrado!")
        return {}
    except json.JSONDecodeError:
        print(f"Erro: Arquivo {arquivo_json} contém JSON inválido!")
        return {}
    except Exception as e:
        print(f"Erro ao carregar destinos: {e}")
        return {}
    
# Função para obter dados de ruas de uma área usando Overpass API
def obter_dados_estradas(bounds):
    min_lat, min_lon, max_lat, max_lon = bounds
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    way[highway][!area]
        ({min_lat},{min_lon},{max_lat},{max_lon});
    (._;>;);
    out body;
    """
    response = requests.get(overpass_url, params={"data": overpass_query})
    return response.json()

# Função para criar um grafo a partir dos dados do OpenStreetMap
def criar_grafo(data):
    nodes = {}
    graph = defaultdict(list)
    node_coords = {}
    
    # Extrair nós
    for element in data["elements"]:
        if element["type"] == "node":
            node_id = element["id"]
            lat = element["lat"]
            lon = element["lon"]
            nodes[node_id] = (lat, lon)
            node_coords[node_id] = (lat, lon)
            graph[node_id] = []
    
    # Extrair vias e conectar nós
    for element in data["elements"]:
        if element["type"] == "way" and "highway" in element["tags"]:
            # Verificar se a via é acessível para carros
            highway_type = element["tags"]["highway"]
            if highway_type in ["motorway", "trunk", "primary", "secondary", "tertiary", 
                               "unclassified", "residential", "service"]:
                
                # Obter velocidade máxima (padrão por tipo de via se não disponível)
                if "maxspeed" in element["tags"]:
                    try:
                        speed = float(element["tags"]["maxspeed"].split()[0])
                    except:
                        speed = get_default_speed(highway_type)
                else:
                    speed = get_default_speed(highway_type)
                
                nodes_list = element["nodes"]
                for i in range(len(nodes_list) - 1):
                    n1 = nodes_list[i]
                    n2 = nodes_list[i + 1]
                    
                    if n1 in nodes and n2 in nodes:
                        # Calcular distância entre os nós
                        lat1, lon1 = nodes[n1]
                        lat2, lon2 = nodes[n2]
                        distance = haversine(lat1, lon1, lat2, lon2)
                        
                        # Verificar sentido único
                        oneway = element["tags"].get("oneway", "no")
                        
                        # Adicionar arestas
                        graph[n1].append((n2, distance, speed))
                        if oneway != "yes":
                            graph[n2].append((n1, distance, speed))
    
    return graph, node_coords

# Função para dividir os destinos em clusters (subgrafos)
def dividir_destinos_em_clusters(destinos, n_clusters=10, plotar=True):
    """
    Divide os destinos em clusters usando K-Means.

    Parâmetros:
    - destinos: dicionário {nome: (lon, lat)}
    - n_clusters: número de clusters desejado
    - plotar: se True, exibe um gráfico dos clusters
    
    Retorna:
    - labels_clusters: dicionário {nome: cluster_id}
    """
    # Preparar os dados em formato adequado
    coords = []
    nomes = []
    for nome, (lon, lat) in destinos.items():
        # Usar lon, lat diretamente (atenção: para clustering mais preciso, ideal seria converter para UTM)
        coords.append([lon, lat])
        nomes.append(nome)
    
    coords = np.array(coords)

    # Rodar o K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(coords)
    labels = kmeans.labels_

    # Construir dicionário de resultado
    labels_clusters = {nome: label for nome, label in zip(nomes, labels)}

    # Plotar se desejado
    if plotar:
        plt.figure(figsize=(10, 8))
        cores = plt.cm.tab10(np.linspace(0, 1, n_clusters))
        for i in range(n_clusters):
            cluster_coords = coords[labels == i]
            plt.scatter(cluster_coords[:,0], cluster_coords[:,1], 
                        color=cores[i], label=f'Cluster {i+1}', s=80, edgecolor='k')
        
        plt.title(f"Clusters dos Destinos (K-Means, k={n_clusters})", fontsize=14)
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    
    return labels_clusters


# Função para calcular a distância haversine entre dois pontos em lat/long
def haversine(lat1, lon1, lat2, lon2):
    # Raio da Terra em metros
    R = 6371000
    # Converter coordenadas de graus para radianos
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    # Diferença de latitude e longitude
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    # Fórmula haversine
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    # Distância em metros
    distance = R * c
    return distance

# Função heurística para o A* (distância euclidiana estimada)
# Calcula a heurística entre dois nós usando a fórmula haversine
def heuristica(node1, node2, node_coords):
    if node1 not in node_coords or node2 not in node_coords:
        return 0
    
    lat1, lon1 = node_coords[node1]
    lat2, lon2 = node_coords[node2]
    return haversine(lat1, lon1, lat2, lon2)

# Função para definir velocidade padrão por tipo de via
def get_default_speed(highway_type):
    speed_dict = {
        "motorway": 100,
        "trunk": 80,
        "primary": 60,
        "secondary": 50,
        "tertiary": 40,
        "unclassified": 30,
        "residential": 30,
        "service": 20
    }
    return speed_dict.get(highway_type, 40)  # Padrão para vias não especificadas

# Implementação do algoritmo A* para encontrar o caminho mais curto
# entre dois nós usando uma heurística baseada na distância euclidiana
def a_star(graph, start_node, end_node, node_coords):

    # Verificar caso trivial: início e fim são o mesmo nó
    if start_node == end_node:
        return [start_node], 0
    
    # Verificar se os nós existem no grafo
    if start_node not in graph or end_node not in graph:
        print(f"Erro: Nó inicial ({start_node}) ou final ({end_node}) não existe no grafo")
        return [], float('infinity')
    
    # Inicialização
    # g_score: custo real desde o início até o nó
    g_score = defaultdict(lambda: float('infinity'))
    g_score[start_node] = 0
    
    # f_score: g_score + heurística (estimativa do custo total)
    f_score = defaultdict(lambda: float('infinity'))
    f_score[start_node] = heuristica(start_node, end_node, node_coords)
    
    # Predecessores para reconstruir o caminho
    predecessors = {}
    
    # Conjunto de nós já avaliados
    closed_set = set()
    
    # Fila de prioridade (min-heap) com os nós a serem avaliados
    # Formato: (f_score, node_id)
    open_heap = [(f_score[start_node], start_node)]
    open_set = {start_node}  # Para verificação rápida de pertencimento
    
    nodes_explored = 0
    
    while open_heap:
        # Obter o nó com menor f_score
        current_f, current = heapq.heappop(open_heap)
        
        # Remover da lista de nós abertos
        if current not in open_set:
            continue  # Este nó já foi processado

        open_set.remove(current)
        
        # Se chegamos ao destino, reconstruir o caminho
        if current == end_node:
            path = []
            total_distance = g_score[end_node]
            
            # Reconstruir o caminho
            while current in predecessors:
                path.append(current)
                current = predecessors[current]
            path.append(start_node)
            path.reverse()
            
            print(f"A* encontrou caminho com {len(path)} nós, distância: {total_distance:.2f} metros")
            print(f"Nós explorados: {nodes_explored}")
            return path, total_distance
        
        # Marcar como visitado
        closed_set.add(current)
        nodes_explored += 1
        
        # Avaliar todos os vizinhos
        for neighbor, distance, speed in graph[current]:
            # Ignorar vizinhos já avaliados
            if neighbor in closed_set:
                continue
            
            # Calcular o novo g_score para este vizinho
            tentative_g_score = g_score[current] + distance
            
            # Se este vizinho não está na lista aberta, adicioná-lo
            if neighbor not in open_set:
                open_set.add(neighbor)
            # Se já encontramos um caminho melhor para este vizinho, ignorar
            elif tentative_g_score >= g_score[neighbor]:
                continue
            
            # Este é o melhor caminho até agora para este vizinho
            predecessors[neighbor] = current
            g_score[neighbor] = tentative_g_score
            f_score[neighbor] = tentative_g_score + heuristica(neighbor, end_node, node_coords)
            
            # Adicionar/atualizar na fila de prioridade
            heapq.heappush(open_heap, (f_score[neighbor], neighbor))
    
    # Não foi encontrado caminho
    print(f"A* não encontrou caminho para o destino. Nós explorados: {nodes_explored}")
    return [], float('infinity')

# Estimar tempo de percurso
def estimar_tempo(graph, path, velocidade_padrao=40):
    tempo_total = 0
    
    for i in range(len(path) - 1):
        n1 = path[i]
        n2 = path[i + 1]
        
        # Encontrar a aresta entre n1 e n2
        for neighbor, distance, speed in graph[n1]:
            if neighbor == n2:
                # Calcular tempo em minutos
                # velocidade em km/h, distância em metros
                tempo = (distance / 1000) / speed * 60
                tempo_total += tempo
                break
    
    return tempo_total

# Função para encontrar o nó mais próximo às coordenadas dadas
def encontrar_no_mais_proximo(node_coords, lat, lon):
    min_dist = float('infinity')
    closest_node = None
    
    for node_id, (node_lat, node_lon) in node_coords.items():
        dist = haversine(lat, lon, node_lat, node_lon)
        if dist < min_dist:
            min_dist = dist
            closest_node = node_id
    
    return closest_node


# Função para dividir os destinos em clusters (subgrafos)
def dividir_destinos_em_clusters(destinos, n_clusters=10, plotar=True):
    """
    Divide os destinos em clusters usando K-Means.

    Parâmetros:
    - destinos: dicionário {nome: (lon, lat)}
    - n_clusters: número de clusters desejado
    - plotar: se True, exibe um gráfico dos clusters
    
    Retorna:
    - labels_clusters: dicionário {nome: cluster_id}
    """
    # Preparar os dados em formato adequado
    coords = []
    nomes = []
    for nome, (lon, lat) in destinos.items():
        # Usar lon, lat diretamente (atenção: para clustering mais preciso, ideal seria converter para UTM)
        coords.append([lon, lat])
        nomes.append(nome)
    
    coords = np.array(coords)

    # Rodar o K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(coords)
    labels = kmeans.labels_

    # Construir dicionário de resultado
    labels_clusters = {nome: label for nome, label in zip(nomes, labels)}

    # Plotar se desejado
    if plotar:
        plt.figure(figsize=(10, 8))
        cores = plt.cm.tab10(np.linspace(0, 1, n_clusters))
        for i in range(n_clusters):
            cluster_coords = coords[labels == i]
            plt.scatter(cluster_coords[:,0], cluster_coords[:,1], 
                        color=cores[i], label=f'Cluster {i+1}', s=80, edgecolor='k')
        
        plt.title(f"Clusters dos Destinos (K-Means, k={n_clusters})", fontsize=14)
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    
    return labels_clusters

def encontrar_pontos_mais_distantes_por_cluster(destinos, labels_clusters, czoonoses):
    """
    Para cada cluster existente, encontra o ponto mais distante do centro de zoonoses.

    Parâmetros:
    - destinos: dicionário {nome: (lon, lat)}
    - labels_clusters: dicionário {nome: cluster_id}
    - czoonoses: tupla (lat, lon)

    Retorna:
    - dicionário {cluster_id: (nome_destino_mais_distante, distancia_em_metros)}
    """
    resultados = {}

    # Obter todos os cluster_ids únicos
    cluster_ids = set(labels_clusters.values())

    for cluster_id in sorted(cluster_ids):
        max_dist = -1
        destino_mais_distante = None

        lat_cz, lon_cz = czoonoses

        for nome, cluster in labels_clusters.items():
            if cluster == cluster_id:
                lon, lat = destinos[nome]
                dist = haversine(lat_cz, lon_cz, lat, lon)
                if dist > max_dist:
                    max_dist = dist
                    destino_mais_distante = nome

        resultados[cluster_id] = (destino_mais_distante, max_dist)

    return resultados

######################################################################################
############################### TESTE DE FUNÇÕES AQUI ################################
######################################################################################

def encontrar_ponto_mais_distante_no_cluster(destinos, labels_clusters, czoonoses, cluster_alvo_id):
    """
    Encontra o ponto mais distante do centro de zoonoses dentro de um único cluster específico.

    Parâmetros:
    - destinos: dicionário {nome: (lon, lat)}
    - labels_clusters: dicionário {nome: cluster_id}
    - czoonoses: tupla (lat, lon) do ponto de origem
    - cluster_alvo_id: O ID do cluster a ser analisado.

    Retorna:
    - Uma tupla (nome_destino_mais_distante, distancia_em_metros).
    - Retorna (None, -1) se o cluster especificado não contiver nenhum destino.
    """
    max_dist = -1
    destino_mais_distante = None

    # Coordenadas do ponto de origem (Centro de Zoonoses)
    lat_cz, lon_cz = czoonoses

    # Itera sobre os destinos para encontrar aqueles que pertencem ao cluster alvo
    for nome_destino, id_cluster_atual in labels_clusters.items():
        if id_cluster_atual == cluster_alvo_id:
            # Obtém as coordenadas do destino (lon, lat) e desempacota corretamente
            lon_destino, lat_destino = destinos[nome_destino]
            
            # Calcula a distância Haversine
            dist = haversine(lat_cz, lon_cz, lat_destino, lon_destino)
            
            # Verifica se é a maior distância encontrada até agora neste cluster
            if dist > max_dist:
                max_dist = dist
                destino_mais_distante = nome_destino

    # Retorna o resultado para o cluster específico
    if destino_mais_distante is not None:
        return (destino_mais_distante, max_dist)
    else:
        # Caso o cluster esteja vazio ou não seja encontrado
        return (None, -1)

def tracar_rota_cluster_tsp_a_star(cluster_alvo_id, destinos, labels_clusters, czoonoses_coords, graph, node_coords):
    """
    Traça uma rota otimizada (usando a heurística do vizinho mais próximo) que começa
    no Centro de Zoonoses, visita todos os pontos de um cluster específico e retorna ao CZO.
    """
    print(f"\nIniciando o planejamento da rota para o Cluster {cluster_alvo_id + 1}...")

    # 1. Identificar os destinos específicos deste cluster
    destinos_do_cluster = {
        nome: destinos[nome] for nome, cluster_id in labels_clusters.items() 
        if cluster_id == cluster_alvo_id
    }
    
    if not destinos_do_cluster:
        print(f"Cluster {cluster_alvo_id + 1} não possui destinos. Rota não gerada.")
        return [], 0

    print(f"Destinos do cluster: {list(destinos_do_cluster.keys())}")

    # Encontrar o nó do CZO
    no_czoonoses = encontrar_no_mais_proximo(node_coords, czoonoses_coords[0], czoonoses_coords[1])
    
    # 2. Mapear cada destino para seu nó mais próximo e verificar conectividade
    destinos_para_nos = {}
    destinos_inalcancaveis = []
    
    for nome, (lon, lat) in destinos_do_cluster.items():
        no_destino = encontrar_no_mais_proximo(node_coords, lat, lon)
        
        # Verificar se o nó tem conexões (não está isolado)
        if no_destino and no_destino in graph and len(graph[no_destino]) > 0:
            # Testar conectividade fazendo uma busca rápida
            caminho_teste, dist_teste = a_star(graph, no_czoonoses, no_destino, node_coords)
            if caminho_teste:  # Se conseguiu encontrar um caminho
                destinos_para_nos[nome] = no_destino
            else:
                destinos_inalcancaveis.append(nome)
                print(f"AVISO: '{nome}' não é alcançável pela rede viária disponível.")
        else:
            destinos_inalcancaveis.append(nome)
            print(f"AVISO: '{nome}' está mapeado para um nó isolado ou inexistente.")
    
    if not destinos_para_nos:
        print(f"Nenhum destino do Cluster {cluster_alvo_id + 1} é alcançável. Rota não gerada.")
        return [], 0

    # 3. Implementar o algoritmo do vizinho mais próximo usando os destinos alcançáveis
    rota_completa = [no_czoonoses]
    distancia_total = 0
    ponto_atual = no_czoonoses
    destinos_restantes = destinos_para_nos.copy()

    while destinos_restantes:
        distancia_minima = float('inf')
        destino_mais_proximo = None
        melhor_caminho = []

        # Encontrar o destino mais próximo do ponto atual
        for nome_destino, no_destino in destinos_restantes.items():
            caminho, distancia = a_star(graph, ponto_atual, no_destino, node_coords)
            if caminho and distancia < distancia_minima:
                distancia_minima = distancia
                destino_mais_proximo = nome_destino
                melhor_caminho = caminho
        
        if destino_mais_proximo:
            print(f"  - Visitando '{destino_mais_proximo}' (Distância: {distancia_minima:.2f} m)")
            
            # Adicionar o caminho à rota (excluindo o primeiro nó para evitar duplicatas)
            rota_completa.extend(melhor_caminho[1:])
            distancia_total += distancia_minima
            
            # Atualizar posição atual e remover o destino visitado
            ponto_atual = destinos_para_nos[destino_mais_proximo]
            del destinos_restantes[destino_mais_proximo]
        else:
            print("ERRO: Não foi possível encontrar caminho para os destinos restantes.")
            break

    # 4. Retornar ao Centro de Zoonoses
    print("  - Todos os pontos alcançáveis visitados. Retornando ao CZO...")
    caminho_final, distancia_final = a_star(graph, ponto_atual, no_czoonoses, node_coords)
    
    if caminho_final:
        rota_completa.extend(caminho_final[1:])
        distancia_total += distancia_final
        print(f"  - Retorno ao CZO (Distância: {distancia_final:.2f} m)")
    else:
        print("AVISO: Não foi possível traçar a rota de volta para o CZO.")

    # Relatório final
    print(f"Rota para o Cluster {cluster_alvo_id + 1} finalizada.")
    print(f"Destinos visitados: {len(destinos_do_cluster) - len(destinos_inalcancaveis)}/{len(destinos_do_cluster)}")
    if destinos_inalcancaveis:
        print(f"Destinos não alcançáveis: {destinos_inalcancaveis}")
    print(f"Distância total estimada: {distancia_total / 1000:.2f} km")
    
    return rota_completa, distancia_total

def planejar_rotas_para_todos_os_clusters_a_star(destinos, labels_clusters, czoonoses_coords, graph, node_coords):
    """
    Itera sobre todos os clusters, traça uma rota para cada um usando a função
    tracar_rota_cluster_tsp e salva todas as rotas geradas.

    Parâmetros:
    - Todos os parâmetros necessários para a função tracar_rota_cluster_tsp.

    Retorna:
    - Um dicionário onde as chaves são os IDs dos clusters e os valores são
      tuplas contendo (rota_completa, distancia_total_metros) para aquele cluster.
      Ex: {0: (rota_cluster_0, dist_0), 1: (rota_cluster_1, dist_1), ...}
    """
    print("\n\n=== INICIANDO PLANEJAMENTO DE ROTAS PARA TODOS OS CLUSTERS ===")
    
    todas_as_rotas = {}
    
    # Encontra todos os IDs de cluster únicos e os ordena
    ids_clusters_unicos = sorted(set(labels_clusters.values()))
    
    # Itera sobre cada cluster para planejar sua rota
    for cluster_id in ids_clusters_unicos:
        rota, distancia = tracar_rota_cluster_tsp_a_star(
            cluster_alvo_id=cluster_id,
            destinos=destinos,
            labels_clusters=labels_clusters,
            czoonoses_coords=czoonoses_coords,
            graph=graph,
            node_coords=node_coords
        )
        
        # Salva a rota e a distância no dicionário se a rota foi gerada com sucesso
        if rota:
            todas_as_rotas[cluster_id] = (rota, distancia)
            
    print("\n=== PLANEJAMENTO DE TODAS AS ROTAS CONCLUÍDO ===")
    return todas_as_rotas

def extrair_subgrafo_por_cluster(cluster_nodes, node_coords, graph, margem=0.005):
    """
    Extrai de 'graph' apenas os nós e arestas que caem no bbox que envolve
    cluster_nodes (lat/lon em node_coords) com uma pequena margem.
    """
    # calcula bbox
    lats = [node_coords[n][0] for n in cluster_nodes]
    lons = [node_coords[n][1] for n in cluster_nodes]
    min_lat, max_lat = min(lats)-margem, max(lats)+margem
    min_lon, max_lon = min(lons)-margem, max(lons)+margem

    # filtra nós no bbox
    nodes_ok = {
        n for n,(lat,lon) in node_coords.items()
        if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon
    }

    # monta subgrafo
    sub = {}
    for n in nodes_ok:
        sub[n] = [(v,w,s) for (v,w,s) in graph[n] if v in nodes_ok]
    return sub


def dijkstra_tradicional_distancias(graph, source):
    """
    Roda o seu Dijkstra tradicional (sem heap) a partir de 'source'
    e retorna dois dicts: dist[n] e pred[n].
    """
    dist = {n: float('inf') for n in graph}
    dist[source] = 0
    pred = {n: None for n in graph}
    visitados = set()

    while True:
        u, best = None, float('inf')
        for n, d in dist.items():
            if n not in visitados and d < best:
                u, best = n, d
        if u is None:
            break
        visitados.add(u)
        for v, w, _ in graph[u]:
            if v not in visitados and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u

    return dist, pred


def tracar_rota_cluster_tsp_dijkstra_trad(
    cluster_alvo_id,
    destinos,
    labels_clusters,
    czoonoses_coords,
    graph,
    node_coords
):
    """
    Traça rota NN+retorno para o cluster usando Dijkstra tradicional
    em subgrafo reduzido.
    """
    # 1) mapeia nós do CZO e destinos do cluster
    start = encontrar_no_mais_proximo(node_coords, *czoonoses_coords)
    nomes = [n for n,c in labels_clusters.items() if c==cluster_alvo_id]
    destinos_nodes = [
        encontrar_no_mais_proximo(node_coords, lat, lon)
        for n in nomes for (lon,lat) in [destinos[n]]
    ]
    cluster_nodes = [start] + destinos_nodes

    # 2) extrai subgrafo restrito
    sub_graph = extrair_subgrafo_por_cluster(cluster_nodes, node_coords, graph)

    # 3) inicializa rota e estado
    rota = [start]
    atual = start
    total = 0.0
    restantes = set(destinos_nodes)

    # 4) Nearest-Neighbor usando Dijkstra one-to-all
    while restantes:
        dist_map, pred_map = dijkstra_tradicional_distancias(sub_graph, atual)
        vizinho = min(restantes, key=lambda n: dist_map.get(n, float('inf')))
        dmin = dist_map[vizinho]

        # reconstrói caminho
        caminho = []
        cur = vizinho
        while cur is not None:
            caminho.append(cur)
            cur = pred_map[cur]
        caminho.reverse()

        # anexa e atualiza
        rota.extend(caminho[1:])
        total += dmin
        atual = vizinho
        restantes.remove(vizinho)

    # 5) volta ao CZO
    dist_map, pred_map = dijkstra_tradicional_distancias(sub_graph, atual)
    retorno = []
    cur = start
    # reconstrói de atual → start
    path_back = []
    node = atual
    while node is not None:
        path_back.append(node)
        node = pred_map[node]
    path_back.reverse()

    rota.extend(path_back[1:])
    total += dist_map[start]

    print(f"Cluster {cluster_alvo_id+1}: {len(rota)} nós, {total/1000:.2f} km")
    return rota, total


def planejar_rotas_para_todos_os_clusters_dijkstra_trad(destinos, labels_clusters, czoonoses_coords, graph, node_coords):
    """
    Itera sobre todos os clusters, traça uma rota para cada um usando a função
    tracar_rota_cluster_tsp e salva todas as rotas geradas.

    Parâmetros:
    - Todos os parâmetros necessários para a função tracar_rota_cluster_tsp.

    Retorna:
    - Um dicionário onde as chaves são os IDs dos clusters e os valores são
      tuplas contendo (rota_completa, distancia_total_metros) para aquele cluster.
      Ex: {0: (rota_cluster_0, dist_0), 1: (rota_cluster_1, dist_1), ...}
    """
    print("\n\n=== INICIANDO PLANEJAMENTO DE ROTAS PARA TODOS OS CLUSTERS ===")
    
    todas_as_rotas = {}
    
    # Encontra todos os IDs de cluster únicos e os ordena
    ids_clusters_unicos = sorted(set(labels_clusters.values()))
    
    # Itera sobre cada cluster para planejar sua rota
    for cluster_id in ids_clusters_unicos:
        rota, distancia = tracar_rota_cluster_tsp_dijkstra_trad(
            cluster_alvo_id=cluster_id,
            destinos=destinos,
            labels_clusters=labels_clusters,
            czoonoses_coords=czoonoses_coords,
            graph=graph,
            node_coords=node_coords
        )
        
        # Salva a rota e a distância no dicionário se a rota foi gerada com sucesso
        if rota:
            todas_as_rotas[cluster_id] = (rota, distancia)
            
    print("\n=== PLANEJAMENTO DE TODAS AS ROTAS CONCLUÍDO ===")
    return todas_as_rotas

def dijkstra_min_heap(graph, source):
    """
    Dijkstra com min-heap (O(E + V log V)),
    retornando (dist, pred) para todo nó.
    """
    dist = {n: float('inf') for n in graph}
    dist[source] = 0
    pred = {n: None for n in graph}
    visited = set()
    heap = [(0, source)]

    while heap:
        d_u, u = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)
        for v, w, _ in graph[u]:
            nd = d_u + w
            if nd < dist[v]:
                dist[v] = nd
                pred[v] = u
                heapq.heappush(heap, (nd, v))
    return dist, pred

def tracar_rota_cluster_tsp_dijkstra_min_heap(
    cluster_alvo_id,
    destinos,
    labels_clusters,
    czoonoses_coords,
    graph,
    node_coords
):
    """
    Traça rota NN+retorno para o cluster usando Dijkstra com min-heap
    em subgrafo reduzido com margem dinâmica e fallback.
    """
    # 1) nó do depósito e destinos do cluster
    start = encontrar_no_mais_proximo(node_coords, *czoonoses_coords)
    nomes = [n for n, c in labels_clusters.items() if c == cluster_alvo_id]
    dest_nodes = [
        encontrar_no_mais_proximo(node_coords, lat, lon)
        for n in nomes for (lon, lat) in [destinos[n]]
    ]
    cluster_nodes = [start] + dest_nodes

    # 2) margem dinâmica
    lats = [node_coords[n][0] for n in cluster_nodes]
    lons = [node_coords[n][1] for n in cluster_nodes]
    span_lat = max(lats) - min(lats)
    span_lon = max(lons) - min(lons)
    margem = max(span_lat, span_lon) * 0.5 + 0.005

    # 3) extrai sub-grafo
    subg = extrair_subgrafo_por_cluster(cluster_nodes, node_coords, graph, margem)

    # 4) Nearest-Neighbor usando Dijkstra min-heap one-to-all
    rota = [start]
    atual = start
    total = 0.0
    restantes = set(dest_nodes)

    while restantes:
        dist_map, pred_map = dijkstra_min_heap(subg, atual)
        viz = min(restantes, key=lambda n: dist_map.get(n, float('inf')))
        dmin = dist_map[viz]

        # reconstrói caminho até viz
        caminho = []
        cur = viz
        while cur is not None:
            caminho.append(cur)
            cur = pred_map[cur]
        caminho.reverse()

        rota.extend(caminho[1:])
        total += dmin
        atual = viz
        restantes.remove(viz)

    # 5) volta ao depósito
    dist_map, pred_map = dijkstra_min_heap(subg, atual)
    if dist_map.get(start, float('inf')) == float('inf'):
        # fallback no grafo completo
        full_dist, full_pred = dijkstra_min_heap(graph, atual)
        d_back = full_dist[start]
        caminho_back = []
        cur = start
        while cur is not None:
            caminho_back.append(cur)
            cur = full_pred[cur]
        caminho_back.reverse()
    else:
        d_back = dist_map[start]
        caminho_back = []
        cur = start
        while cur is not None:
            caminho_back.append(cur)
            cur = pred_map[cur]
        caminho_back.reverse()

    rota.extend(caminho_back[1:])
    total += d_back

    print(f"Cluster {cluster_alvo_id+1}: {len(rota)} nós, {total/1000:.2f} km")
    return rota, total

def planejar_rotas_para_todos_os_clusters_min_heap(
    destinos,
    labels_clusters,
    czoonoses_coords,
    graph,
    node_coords
):
    """
    Itera sobre todos os clusters e chama
    tracar_rota_cluster_tsp_dijkstra_min_heap para cada um.
    """
    print("\n=== INICIANDO PLANEJAMENTO DE ROTAS (min-heap) ===")
    rotas = {}
    for cid in sorted(set(labels_clusters.values())):
        rota, dist = tracar_rota_cluster_tsp_dijkstra_min_heap(
            cluster_alvo_id=cid,
            destinos=destinos,
            labels_clusters=labels_clusters,
            czoonoses_coords=czoonoses_coords,
            graph=graph,
            node_coords=node_coords
        )
        if rota:
            rotas[cid] = (rota, dist)
    print("=== PLANEJAMENTO CONCLUÍDO ===")
    return rotas

def imprimir_resumo_detalhado(rotas_salvas, destinos, node_coords, labels_clusters):
    """
    Imprime um resumo detalhado de cada rota planejada.
    
    CORREÇÃO: Agora mapeia corretamente os nós visitados para os destinos específicos
    de cada cluster, evitando que um mesmo ponto apareça em múltiplas rotas.
    """
    print("\n\n--- RESUMO DETALHADO DAS ROTAS GERADAS ---")

    if not rotas_salvas:
        print("Nenhuma rota para exibir.")
        return

    # Para cada cluster, identificar quais destinos deveriam ser visitados
    for cluster_id, (rota, distancia) in sorted(rotas_salvas.items()):
        print(f"\n-----------------------------------------")
        print(f"| Rota para o Cluster {cluster_id + 1}                  |")
        print(f"-----------------------------------------")
        print(f"  -> Distância Total: {distancia / 1000:.2f} km")
        print(f"  -> Número de nós na rota: {len(rota)}")

        # Identificar quais destinos pertencem a este cluster específico
        destinos_do_cluster = []
        for nome, cluster_destino in labels_clusters.items():
            if cluster_destino == cluster_id:
                destinos_do_cluster.append(nome)

        # Para cada destino do cluster, verificar se seu nó está na rota
        destinos_visitados = []
        destinos_nao_visitados = []
        
        for nome_destino in destinos_do_cluster:
            lon, lat = destinos[nome_destino]
            no_destino = encontrar_no_mais_proximo(node_coords, lat, lon)
            
            if no_destino in rota:
                destinos_visitados.append(nome_destino)
            else:
                destinos_nao_visitados.append(nome_destino)
        
        print(f"  -> Destinos Visitados ({len(destinos_visitados)}):")
        for i, nome in enumerate(destinos_visitados, 1):
            print(f"     {i}. {nome}")
        
        if destinos_nao_visitados:
            print(f"  -> Destinos Não Visitados ({len(destinos_nao_visitados)}):")
            for nome in destinos_nao_visitados:
                print(f"     - {nome} (possivelmente isolado na rede viária)")
    
    print("\n-----------------------------------------")
    print("--- Fim do Resumo ---")


def diagnosticar_conectividade_grafo(graph, node_coords, destinos, czoonoses_coords):
    """
    Nova função para diagnosticar problemas de conectividade no grafo.
    Ajuda a identificar destinos que não podem ser alcançados.
    """
    print("\n=== DIAGNÓSTICO DE CONECTIVIDADE ===")
    
    no_czoonoses = encontrar_no_mais_proximo(node_coords, czoonoses_coords[0], czoonoses_coords[1])
    print(f"Nó do Centro de Zoonoses: {no_czoonoses}")
    print(f"Conexões do CZO: {len(graph.get(no_czoonoses, []))}")
    
    destinos_problematicos = []
    destinos_ok = []
    
    for nome, (lon, lat) in destinos.items():
        no_destino = encontrar_no_mais_proximo(node_coords, lat, lon)
        
        # Verificar se o nó existe e tem conexões
        if no_destino not in graph:
            destinos_problematicos.append((nome, "Nó não existe no grafo"))
            continue
            
        if len(graph[no_destino]) == 0:
            destinos_problematicos.append((nome, "Nó isolado (sem conexões)"))
            continue
        
        # Testar conectividade com o CZO
        caminho, distancia = a_star(graph, no_czoonoses, no_destino, node_coords)
        if not caminho:
            destinos_problematicos.append((nome, "Sem caminho para o CZO"))
        else:
            destinos_ok.append((nome, distancia))
    
    print(f"\nDestinos alcançáveis: {len(destinos_ok)}")
    print(f"Destinos problemáticos: {len(destinos_problematicos)}")
    
    if destinos_problematicos:
        print("\nDestinos com problemas:")
        for nome, problema in destinos_problematicos:
            print(f"  - {nome}: {problema}")
    
    return destinos_ok, destinos_problematicos

