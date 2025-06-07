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

def plotar_mapa_natal_com_destinos(graph, node_coords, destinos, czoonoses, bounds=None):
    """
    Plota um mapa da cidade de Natal mostrando a rede viária e os pontos de destino.
    
    Parâmetros:
    - graph: grafo da rede viária
    - node_coords: coordenadas dos nós do grafo
    - destinos: dicionário com destinos carregados do JSON
    - czoonoses: coordenadas do centro de zoonoses (lat, lon)
    - bounds: limites da área (min_lat, min_lon, max_lat, max_lon) - opcional
    """

    plt.figure(figsize=(16, 12))
    
    # Definir ou calcular limites para a área do mapa
    if bounds is None or bounds == (0, 0, 0, 0):
        # Calcular limites automaticamente baseado nos destinos e centro de zoonoses
        print("Calculando limites automaticamente...")
        
        lats = [czoonoses[0]]  # lat do centro de zoonoses
        lons = [czoonoses[1]]  # lon do centro de zoonoses
        
        # Adicionar coordenadas dos destinos
        for lon, lat in destinos.values():
            lats.append(lat)
            lons.append(lon)
        
        # Adicionar coordenadas dos nós do grafo se disponíveis
        if node_coords:
            for lat, lon in node_coords.values():
                lats.append(lat)
                lons.append(lon)
        
        # Calcular limites com margem
        margem = 0.01  # ~1km aproximadamente
        min_lat = min(lats) - margem
        max_lat = max(lats) + margem
        min_lon = min(lons) - margem
        max_lon = max(lons) + margem
        
        print(f"Limites calculados: lat({min_lat:.4f}, {max_lat:.4f}), lon({min_lon:.4f}, {max_lon:.4f})")
    else:
        min_lat, min_lon, max_lat, max_lon = bounds
        print(f"Usando limites fornecidos: lat({min_lat:.4f}, {max_lat:.4f}), lon({min_lon:.4f}, {max_lon:.4f})")
    
    print("Plotando rede viária de Natal...")
    
    # Plotar arestas do grafo (rede viária)
    edges_plotted = 0
    for node in graph:
        if node in node_coords:
            lat1, lon1 = node_coords[node]  # lat, lon
            x1, y1 = lon1, lat1  # converter para x, y (lon, lat)
            
            for neighbor, distance, speed in graph[node]:
                if neighbor in node_coords:
                    lat2, lon2 = node_coords[neighbor]
                    x2, y2 = lon2, lat2
                    
                    # Plotar apenas se as coordenadas estão dentro dos limites
                    if (min_lat <= lat1 <= max_lat and min_lon <= lon1 <= max_lon and
                        min_lat <= lat2 <= max_lat and min_lon <= lon2 <= max_lon):
                        plt.plot([x1, x2], [y1, y2], 'gray', linewidth=0.6, alpha=0.9)
                        edges_plotted += 1
    
    print(f"Plotadas {edges_plotted} arestas da rede viária")
    
    # Plotar o centro de zoonoses
    lat_czoonoses, lon_czoonoses = czoonoses
    plt.plot(lon_czoonoses, lat_czoonoses, 'ro', markersize=12, 
             label='Centro de Zoonoses', markeredgecolor='darkred', markeredgewidth=2)
    
    # Plotar destinos por bairro
    print("Plotando destinos...")
    destinos_plotados = 0
    
    if not destinos:
        print("AVISO: Nenhum destino foi carregado!")
    else:
        print(f"Destinos disponíveis: {len(destinos)}")
        
    cores_bairros = plt.cm.Set3(np.linspace(0, 1, max(12, len(destinos))))
    bairros_unicos = {}
    
    for i, (nome_destino, coordenadas) in enumerate(destinos.items()):
        # Verificar formato das coordenadas (lon, lat) ou (lat, lon)
        if len(coordenadas) == 2:
            # Assumir que está no formato (lon, lat) baseado no código original
            lon, lat = coordenadas
            
            # Verificar se as coordenadas fazem sentido para Natal-RN
            # Natal: aproximadamente lat -5.7 a -5.8, lon -35.2 a -35.3
            if not (-6.0 <= lat <= -5.0 and -36.0 <= lon <= -34.0):
                print(f"AVISO: Coordenadas suspeitas para {nome_destino}: {coordenadas}")
                # Tentar trocar lat/lon
                lat, lon = coordenadas
                
        else:
            print(f"ERRO: Formato de coordenadas inválido para {nome_destino}: {coordenadas}")
            continue
            
        # Extrair nome do bairro (remover sufixo numérico se existir)
        nome_bairro = nome_destino.split('_')[0]
        
        # Atribuir cor única por bairro
        if nome_bairro not in bairros_unicos:
            bairros_unicos[nome_bairro] = len(bairros_unicos)
        
        cor_idx = bairros_unicos[nome_bairro] % len(cores_bairros)
        cor = cores_bairros[cor_idx]
        
        # Plotar ponto
        plt.plot(lon, lat, 'o', color=cor, markersize=8, 
                markeredgecolor='black', markeredgewidth=1, alpha=0.8)
        
        # Adicionar rótulo com nome do destino
        plt.text(lon, lat, nome_destino, fontsize=8, 
                ha='center', va='bottom', weight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))
        
        destinos_plotados += 1
        print(f"Plotado: {nome_destino} em ({lon:.4f}, {lat:.4f})")
    
    print(f"Plotados {destinos_plotados} destinos")
    
    # Criar legenda para bairros únicos
    handles_legenda = []
    for bairro, idx in bairros_unicos.items():
        cor_idx = idx % len(cores_bairros)
        cor = cores_bairros[cor_idx]
        handles_legenda.append(plt.Line2D([0], [0], marker='o', color='w', 
                                        markerfacecolor=cor, markersize=8, 
                                        label=bairro, markeredgecolor='black'))
    
    # Adicionar centro de zoonoses à legenda
    handles_legenda.insert(0, plt.Line2D([0], [0], marker='o', color='w', 
                                       markerfacecolor='red', markersize=10, 
                                       label='Centro de Zoonoses', markeredgecolor='darkred'))
    
    # Configurar o plot
    plt.title("Mapa de Natal - RN\nRede Viária e Pontos de Destino", 
              fontsize=16, weight='bold', pad=20)
    plt.xlabel("Longitude", fontsize=12, weight='bold')
    plt.ylabel("Latitude", fontsize=12, weight='bold')
    
    # Definir limites do plot baseado nos dados reais
    if destinos_plotados > 0 or node_coords:
        plt.xlim(min_lon - 0.005, max_lon + 0.005)
        plt.ylim(min_lat - 0.005, max_lat + 0.005)
    else:
        # Limites padrão para Natal-RN se não houver dados
        plt.xlim(-35.3, -35.1)
        plt.ylim(-5.9, -5.7)
    
    # Adicionar grade
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Adicionar legenda
    plt.legend(handles=handles_legenda, loc='upper left', bbox_to_anchor=(1.05, 1), 
              fontsize=10, title="Locais", title_fontsize=12)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Adicionar informações sobre a área
    info_text = f"Área: {abs(max_lat - min_lat):.4f}° × {abs(max_lon - min_lon):.4f}°\n"
    info_text += f"Nós no grafo: {len(node_coords)}\n"
    info_text += f"Destinos plotados: {destinos_plotados}"
    
    plt.text(0.02, 0.98, info_text, transform=plt.gca().transAxes, 
             fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8))
    
    print("Mapa plotado com sucesso!")
    plt.show()

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

def plotar_mapa_com_clusters(graph, node_coords, destinos, labels_clusters, czoonoses, bounds=None):
    """
    Plota um mapa da cidade de Natal mostrando a rede viária e os pontos de destino
    coloridos por cluster.
    
    Parâmetros:
    - graph: grafo da rede viária
    - node_coords: coordenadas dos nós do grafo
    - destinos: dicionário com destinos carregados do JSON {nome: (lon, lat)}
    - labels_clusters: dicionário com os clusters {nome: cluster_id}
    - czoonoses: coordenadas do centro de zoonoses (lat, lon)
    - bounds: limites da área (min_lat, min_lon, max_lat, max_lon) - opcional
    """
    import matplotlib.pyplot as plt
    import numpy as np

    plt.figure(figsize=(16, 12))
    
    # Definir ou calcular limites para a área do mapa
    if bounds is None or bounds == (0, 0, 0, 0):
        print("Calculando limites automaticamente...")
        
        lats = [czoonoses[0]]  # lat do centro de zoonoses
        lons = [czoonoses[1]]  # lon do centro de zoonoses
        
        # Adicionar coordenadas dos destinos
        for lon, lat in destinos.values():
            lats.append(lat)
            lons.append(lon)
        
        # Adicionar coordenadas dos nós do grafo se disponíveis
        if node_coords:
            for lat, lon in node_coords.values():
                lats.append(lat)
                lons.append(lon)
        
        # Calcular limites com margem
        margem = 0.01  # ~1km aproximadamente
        min_lat = min(lats) - margem
        max_lat = max(lats) + margem
        min_lon = min(lons) - margem
        max_lon = max(lons) + margem
        
        print(f"Limites calculados: lat({min_lat:.4f}, {max_lat:.4f}), lon({min_lon:.4f}, {max_lon:.4f})")
    else:
        min_lat, min_lon, max_lat, max_lon = bounds
        print(f"Usando limites fornecidos: lat({min_lat:.4f}, {max_lat:.4f}), lon({min_lon:.4f}, {max_lon:.4f})")
    
    print("Plotando rede viária de Natal...")
    
    # Plotar arestas do grafo (rede viária)
    edges_plotted = 0
    for node in graph:
        if node in node_coords:
            lat1, lon1 = node_coords[node]  # lat, lon
            x1, y1 = lon1, lat1  # converter para x, y (lon, lat)
            
            for neighbor, distance, speed in graph[node]:
                if neighbor in node_coords:
                    lat2, lon2 = node_coords[neighbor]
                    x2, y2 = lon2, lat2
                    
                    # Plotar apenas se as coordenadas estão dentro dos limites
                    if (min_lat <= lat1 <= max_lat and min_lon <= lon1 <= max_lon and
                        min_lat <= lat2 <= max_lat and min_lon <= lon2 <= max_lon):
                        plt.plot([x1, x2], [y1, y2], 'gray', linewidth=0.6, alpha=0.9)
                        edges_plotted += 1
    
    print(f"Plotadas {edges_plotted} arestas da rede viária")
    
    # Plotar o centro de zoonoses
    lat_czoonoses, lon_czoonoses = czoonoses
    plt.plot(lon_czoonoses, lat_czoonoses, 'ro', markersize=12, 
             label='Centro de Zoonoses', markeredgecolor='darkred', markeredgewidth=2)
    
    # Plotar destinos coloridos por cluster
    print("Plotando destinos coloridos por cluster...")
    destinos_plotados = 0
    
    if not destinos:
        print("AVISO: Nenhum destino foi carregado!")
    else:
        print(f"Destinos disponíveis: {len(destinos)}")
        
    # Determinar número de clusters únicos
    clusters_unicos = set(labels_clusters.values())
    n_clusters = len(clusters_unicos)
    print(f"Número de clusters encontrados: {n_clusters}")
    
    # Gerar cores para cada cluster usando uma paleta de cores distinta
    cores_clusters = plt.cm.tab10(np.linspace(0, 1, min(10, n_clusters)))
    if n_clusters > 10:
        # Se tiver mais de 10 clusters, usar paletas adicionais
        cores_extra = plt.cm.Set3(np.linspace(0, 1, n_clusters - 10))
        cores_clusters = np.vstack([cores_clusters, cores_extra])
    
    # Mapear cada cluster_id para uma cor
    cluster_ids_ordenados = sorted(clusters_unicos)
    mapa_cores = {cluster_id: cores_clusters[i % len(cores_clusters)] 
                  for i, cluster_id in enumerate(cluster_ids_ordenados)}
    
    # Agrupar destinos por cluster para estatísticas
    destinos_por_cluster = {}
    
    for nome_destino, coordenadas in destinos.items():
        # Verificar formato das coordenadas (lon, lat)
        if len(coordenadas) == 2:
            lon, lat = coordenadas
            
            # Verificar se as coordenadas fazem sentido para Natal-RN
            if not (-6.0 <= lat <= -5.0 and -36.0 <= lon <= -34.0):
                print(f"AVISO: Coordenadas suspeitas para {nome_destino}: {coordenadas}")
                # Tentar trocar lat/lon
                lat, lon = coordenadas
                
        else:
            print(f"ERRO: Formato de coordenadas inválido para {nome_destino}: {coordenadas}")
            continue
        
        # Obter cluster do destino
        if nome_destino in labels_clusters:
            cluster_id = labels_clusters[nome_destino]
            cor = mapa_cores[cluster_id]
            
            # Contar destinos por cluster
            if cluster_id not in destinos_por_cluster:
                destinos_por_cluster[cluster_id] = 0
            destinos_por_cluster[cluster_id] += 1
            
            # Plotar ponto com cor do cluster
            plt.plot(lon, lat, 'o', color=cor, markersize=8, 
                    markeredgecolor='black', markeredgewidth=1, alpha=0.8)
            
            # Adicionar rótulo com nome do destino
            #plt.text(lon, lat, nome_destino, fontsize=8, 
            #        ha='center', va='bottom', weight='bold',
            #        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))
            
            destinos_plotados += 1
            print(f"Plotado: {nome_destino} (Cluster {cluster_id + 1}) em ({lon:.4f}, {lat:.4f})")
        else:
            print(f"AVISO: Destino {nome_destino} não encontrado nos clusters!")
    
    print(f"Plotados {destinos_plotados} destinos")
    
    # Criar legenda para clusters
    handles_legenda = []
    
    # Adicionar centro de zoonoses à legenda
    handles_legenda.append(plt.Line2D([0], [0], marker='o', color='w', 
                                    markerfacecolor='red', markersize=10, 
                                    label='Centro de Zoonoses', markeredgecolor='darkred'))
    
    # Adicionar clusters à legenda (ordenados)
    for cluster_id in cluster_ids_ordenados:
        cor = mapa_cores[cluster_id]
        count = destinos_por_cluster.get(cluster_id, 0)
        handles_legenda.append(plt.Line2D([0], [0], marker='o', color='w', 
                                        markerfacecolor=cor, markersize=8, 
                                        label=f'Cluster {cluster_id + 1} ({count} destinos)', 
                                        markeredgecolor='black'))
    
    # Configurar o plot
    plt.title("Mapa de Natal - RN\nRede Viária e Destinos Agrupados por Clusters", 
              fontsize=16, weight='bold', pad=20)
    plt.xlabel("Longitude", fontsize=12, weight='bold')
    plt.ylabel("Latitude", fontsize=12, weight='bold')
    
    # Definir limites do plot baseado nos dados reais
    if destinos_plotados > 0 or node_coords:
        plt.xlim(min_lon - 0.005, max_lon + 0.005)
        plt.ylim(min_lat - 0.005, max_lat + 0.005)
    else:
        # Limites padrão para Natal-RN se não houver dados
        plt.xlim(-35.3, -35.1)
        plt.ylim(-5.9, -5.7)
    
    # Adicionar grade
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Adicionar legenda
    plt.legend(handles=handles_legenda, loc='upper left', bbox_to_anchor=(1.05, 1), 
              fontsize=10, title="Clusters", title_fontsize=12)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Adicionar informações sobre a área e clusters
    info_text = f"Área: {abs(max_lat - min_lat):.4f}° × {abs(max_lon - min_lon):.4f}°\n"
    info_text += f"Nós no grafo: {len(node_coords)}\n"
    info_text += f"Destinos plotados: {destinos_plotados}\n"
    info_text += f"Clusters: {n_clusters}"
    
    plt.text(0.02, 0.98, info_text, transform=plt.gca().transAxes, 
             fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8))
    
    # Imprimir estatísticas dos clusters
    print("\n=== ESTATÍSTICAS DOS CLUSTERS ===")
    for cluster_id in cluster_ids_ordenados:
        count = destinos_por_cluster.get(cluster_id, 0)
        print(f"Cluster {cluster_id + 1}: {count} destinos")
    
    print("Mapa com clusters plotado com sucesso!")
    plt.show()
    
    return mapa_cores, destinos_por_cluster


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
                lat, lon = destinos[nome]
                dist = haversine(lat_cz, lon_cz, lat, lon)
                if dist > max_dist:
                    max_dist = dist
                    destino_mais_distante = nome

        resultados[cluster_id] = (destino_mais_distante, max_dist)

    return resultados


######################################################################################
######### NÃO SEI SE ESSA FUNÇÃO É NECESSÁRIA, MAS ESTÁ AQUI PARA REFERÊNCIA #########
######################################################################################

""" 
# Função para plotar o grafo e as rotas
def plotar_grafo_e_rotas(graph, node_coords, rotas, cores):
    plt.figure(figsize=(15, 15))
    
    # Plotar arestas do grafo (fundo)
    print("Plotando arestas do grafo...")
    edges_plotted = 0
    for node in graph:
        if node in node_coords:  # Garantir que o nó tem coordenadas
            x1, y1 = node_coords[node][1], node_coords[node][0]  # lon, lat
            for neighbor, _, _ in graph[node]:
                if neighbor in node_coords:  # Garantir que o vizinho tem coordenadas
                    x2, y2 = node_coords[neighbor][1], node_coords[neighbor][0]  # lon, lat
                    plt.plot([x1, x2], [y1, y2], 'k-', linewidth=0.2, alpha=0.5)
                    edges_plotted += 1
    print(f"Plotadas {edges_plotted} arestas do grafo")
    
    # Plotar rotas
    print("Plotando rotas...")
    rotas_validas = 0
    for i, (rota, cor) in enumerate(zip(rotas, cores)):
        # Verificar se a rota é válida (não vazia)
        if len(rota) > 1:
            x_coords = []
            y_coords = []
            for node in rota:
                if node in node_coords:  # Garantir que o nó tem coordenadas
                    x_coords.append(node_coords[node][1])  # lon
                    y_coords.append(node_coords[node][0])  # lat
            
            if len(x_coords) > 1:  # Só plotar se tiver pelo menos dois pontos
                bairro_nome = list(destinos.keys())[i]
                plt.plot(x_coords, y_coords, color=cor, linewidth=2.5, label=bairro_nome)
                print(f"Rota para {bairro_nome} plotada com {len(x_coords)} pontos")
                rotas_validas += 1
        else:
            print(f"Rota para {list(destinos.keys())[i]} é inválida (vazia)")
    
    print(f"Plotadas {rotas_validas} rotas válidas")
    
    # Plotar o centro de zoonoses
    plt.plot(czoonoses[1], czoonoses[0], 'ro', markersize=10, label='czoonoses')
    
    # Plotar destinos
    for bairro, (lat, lon) in destinos.items():
        plt.plot(lon, lat, 'go', markersize=8)
        plt.text(lon, lat, bairro, fontsize=12)
    
    plt.title("Rotas do Hospital Walfredo Gurgel para diferentes bairros de Natal (A*)")
    plt.legend()
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)
    plt.tight_layout()
    plt.show() 

"""