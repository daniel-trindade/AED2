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

def tracar_rota_cluster_tsp(cluster_alvo_id, destinos, labels_clusters, czoonoses_coords, graph, node_coords):
    """
    Traça uma rota otimizada (usando a heurística do vizinho mais próximo) que começa
    no Centro de Zoonoses, visita todos os pontos de um cluster específico e retorna ao CZO.

    Parâmetros:
    - cluster_alvo_id: O ID do cluster para o qual a rota será traçada.
    - destinos: Dicionário {nome: (lon, lat)} com todos os destinos.
    - labels_clusters: Dicionário {nome: cluster_id} que mapeia destinos a clusters.
    - czoonoses_coords: Tupla (lat, lon) com as coordenadas do CZO.
    - graph: O grafo da rede viária.
    - node_coords: Dicionário com as coordenadas de cada nó do grafo.

    Retorna:
    - Uma tupla contendo (rota_completa, distancia_total_metros), onde:
      - rota_completa: é uma lista de nós do grafo representando o caminho completo.
      - distancia_total_metros: é a distância total da rota em metros.
    """
    print(f"\nIniciando o planejamento da rota para o Cluster {cluster_alvo_id + 1}...")

    # 1. Identificar os pontos a serem visitados no cluster
    nomes_destinos_cluster = [
        nome for nome, cluster_id in labels_clusters.items() if cluster_id == cluster_alvo_id
    ]
    
    if not nomes_destinos_cluster:
        print(f"Cluster {cluster_alvo_id + 1} não possui destinos. Rota não gerada.")
        return [], 0

    # Encontrar os nós do grafo correspondentes aos pontos
    no_czoonoses = encontrar_no_mais_proximo(node_coords, czoonoses_coords[0], czoonoses_coords[1])
    
    pontos_a_visitar = set()
    for nome in nomes_destinos_cluster:
        lon, lat = destinos[nome]
        no_destino = encontrar_no_mais_proximo(node_coords, lat, lon)
        if no_destino:
            pontos_a_visitar.add(no_destino)

    # 2. Iniciar a lógica do Vizinho Mais Próximo
    rota_completa = [no_czoonoses]
    distancia_total = 0
    ponto_atual = no_czoonoses

    while pontos_a_visitar:
        distancia_minima = float('inf')
        vizinho_mais_proximo = None
        melhor_caminho = []

        # Encontra o vizinho mais próximo do ponto atual
        for ponto_destino in pontos_a_visitar:
            caminho, distancia = a_star(graph, ponto_atual, ponto_destino, node_coords)
            if distancia < distancia_minima:
                distancia_minima = distancia
                vizinho_mais_proximo = ponto_destino
                melhor_caminho = caminho
        
        if vizinho_mais_proximo:
            nome_destino_visitado = next((nome for nome, (lon, lat) in destinos.items() if encontrar_no_mais_proximo(node_coords, lat, lon) == vizinho_mais_proximo), "Desconhecido")
            print(f"  - Visitando '{nome_destino_visitado}' (Distância: {distancia_minima:.2f} m)")
            
            # Adiciona o caminho e a distância à rota total
            # Adiciona a partir do segundo elemento para não duplicar nós
            rota_completa.extend(melhor_caminho[1:])
            distancia_total += distancia_minima
            
            # Atualiza a posição atual e remove o ponto da lista de visitação
            ponto_atual = vizinho_mais_proximo
            pontos_a_visitar.remove(vizinho_mais_proximo)
        else:
            print("AVISO: Não foi possível encontrar um caminho para os pontos restantes. Interrompendo.")
            break

    # 3. Rota de volta para o Centro de Zoonoses
    print("  - Todos os pontos do cluster visitados. Retornando ao CZO...")
    caminho_final, distancia_final = a_star(graph, ponto_atual, no_czoonoses, node_coords)
    
    if caminho_final:
        rota_completa.extend(caminho_final[1:])
        distancia_total += distancia_final
        print(f"  - Retorno ao CZO (Distância: {distancia_final:.2f} m)")
    else:
        print("AVISO: Não foi possível traçar a rota de volta para o CZO.")

    print(f"Rota para o Cluster {cluster_alvo_id + 1} finalizada.")
    print(f"Distância total estimada: {distancia_total / 1000:.2f} km")
    
    return rota_completa, distancia_total

def planejar_rotas_para_todos_os_clusters(destinos, labels_clusters, czoonoses_coords, graph, node_coords):
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
        rota, distancia = tracar_rota_cluster_tsp(
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

def imprimir_resumo_detalhado(rotas_salvas, destinos, node_coords):
    """
    Imprime um resumo detalhado e amigável de cada rota que foi planejada e salva.
    A função exibe a distância total e a ordem de visitação dos pontos para cada cluster.

    Parâmetros:
    - rotas_salvas: Dicionário gerado por 'planejar_rotas_para_todos_os_clusters'.
    - destinos: Dicionário {nome: (lon, lat)} com todos os destinos.
    - node_coords: Dicionário com as coordenadas de cada nó do grafo.
    """
    print("\n\n--- RESUMO DETALHADO DAS ROTAS GERADAS ---")

    if not rotas_salvas:
        print("Nenhuma rota para exibir.")
        return

    # Para eficiência, crie um mapa reverso de nós para nomes de destinos
    mapa_no_para_nome = {}
    for nome, (lon, lat) in destinos.items():
        # A função encontrar_no_mais_proximo pode ser custosa, mas aqui é necessária
        # para garantir a correspondência correta entre o destino e o nó no grafo.
        no = encontrar_no_mais_proximo(node_coords, lat, lon)
        mapa_no_para_nome[no] = nome

    # Itera sobre cada rota salva no dicionário
    for cluster_id, (rota, distancia) in sorted(rotas_salvas.items()):
        print(f"\n-----------------------------------------")
        print(f"| Rota para o Cluster {cluster_id + 1}                  |")
        print(f"-----------------------------------------")
        print(f"  -> Distância Total: {distancia / 1000:.2f} km")

        # Encontra a sequência de visitação dos pontos nomeados
        pontos_visitados_na_ordem = []
        for no_da_rota in rota:
            if no_da_rota in mapa_no_para_nome:
                nome_do_ponto = mapa_no_para_nome[no_da_rota]
                if nome_do_ponto not in pontos_visitados_na_ordem:
                    pontos_visitados_na_ordem.append(nome_do_ponto)
        
        if pontos_visitados_na_ordem:
            print("  -> Ordem de Visitação dos Pontos:")
            for i, nome in enumerate(pontos_visitados_na_ordem):
                print(f"     {i + 1}. {nome}")
        else:
            print("  -> Nenhum ponto de destino identificado na rota.")
    
    print("\n-----------------------------------------")
    print("--- Fim do Resumo ---")

######################################################################################
############################### TESTE DE FUNÇÕES AQUI ################################
######################################################################################
