""""
PARA EXECUÇÃO DESSE PROGRAMA SERÁ NECESSÁRIO A INSTALAÇÃO DE ALGUMAS BIBLIOTECAS:
 - matplotlib
 - codecarbon
 - pandas
Você pode instalar direto em sua maquina ou usar um ambiente virtual.
Caso opte por um ambiente virtual, execute os seguintes comandos:
python -m venv venv
venv/Scripts/activate
pip install requirements.txt
"""

import requests
import math
import matplotlib.pyplot as plt
from collections import defaultdict
import time
from codecarbon import EmissionsTracker
import heapq

# Iniciando o rastreador de emissões do code carbon
tracker = EmissionsTracker()
tracker.start()

#########################
### DEFININDO FUNÇÕES ###
#########################

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



# Carregar destinos do arquivo JSON
destinos = carregar_destinos('db.json')

# Coordenadas do centro de zoonoses
czoonoses = (-5.7532189, -35.2621815)

# Definir limites para extrair dados do OpenStreetMap (bounding box para Natal-RN)
min_lat = -5.87
min_lon = -35.28
max_lat = -5.73
max_lon = -35.19
bounds = (min_lat, min_lon, max_lat, max_lon)

print("Baixando dados do OpenStreetMap...")
data = obter_dados_estradas(bounds)

print("Criando grafo da rede viária...")
graph, node_coords = criar_grafo(data)

print(f"Grafo criado com {len(graph)} nós.")

# Encontrar o nó mais próximo ao centro de zoonoses
no_czoonoses = encontrar_no_mais_proximo(node_coords, czoonoses[0], czoonoses[1])
print(f"Nó mais próximo ao centro de zoonoses: {no_czoonoses}")




######## A PARTIR DAQUI O CÓDIGO PRECISA SER ########
######## AJUSTADO DE ACORDO COM A ESTRATÉGIA ########
######## QUE IREMOS ADOTAR PARA O PROBLEMA   ########




# Cores para as rotas
cores = ['red', 'blue', 'green', 'orange', 'purple']

# Calcular rotas, distâncias e tempos estimados usando A*
rotas = []
print("\nCalculando rotas com A*, distâncias e tempos estimados:")
for i, (bairro, coords) in enumerate(destinos.items()):
    # Encontrar o nó mais próximo ao ponto
    no_destino = encontrar_no_mais_proximo(node_coords, coords[0], coords[1])
    print(f"Nó mais próximo para {bairro}: {no_destino}")
    
    # Verificar se ambos os nós (origem e destino) existem no grafo
    if no_czoonoses not in graph:
        print(f"ERRO: Nó do hospital {no_czoonoses} não está no grafo!")
        continue
    if no_destino not in graph:
        print(f"ERRO: Nó do destino {no_destino} para {bairro} não está no grafo!")
        continue
    
    # Calcular a rota usando A*
    print(f"Calculando rota para {bairro} com A*...")
    inicio = time.time()
    path, distancia = a_star(graph, no_czoonoses, no_destino, node_coords)
    fim = time.time()
    
    # Verificar se uma rota válida foi encontrada
    if len(path) > 0:
        # Estimar tempo de deslocamento
        tempo_min = estimar_tempo(graph, path)
        print(f"{bairro}: {distancia:.2f} metros, tempo estimado = {tempo_min:.2f} minutos")
        print(f"Tempo de cálculo A*: {(fim - inicio):.4f} segundos, Nós na rota: {len(path)}")
    else:
        print(f"AVISO: A* não conseguiu encontrar uma rota para {bairro}")
    
    # Adicionar rota à lista (mesmo que vazia)
    rotas.append(path)
    print()

# Plotar todas as rotas no mesmo mapa
print("Plotando rotas calculadas com A*...")
plotar_grafo_e_rotas(graph, node_coords, rotas, cores)

# Parar o rastreador e exibir as emissões
emissions = tracker.stop()
print(f"\nEmissões de CO2 estimadas: {emissions:.6f} kg")