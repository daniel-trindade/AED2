import requests
import math
import matplotlib.pyplot as plt
from collections import defaultdict
import time

# Coordenadas dos bairros
hospital = (-5.8098114, -35.2028957)  # Hospital Walfredo Gurgel
destinos = {
    "Lagoa Nova": (-5.8258482, -35.2351506),
    "Tirol": (-5.799086, -35.2204163),
    "Capim Macio": (-5.8565295, -35.2184822),
    "Alecrim": (-5.7970756, -35.2287974),
    "Potengi": (-5.7521007, -35.2674567),
}

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

# Encontrar o nó com menor distância que ainda não foi visitado
def encontrar_no_menor_distancia(distances, visitados):
    # Inicializa com valor infinito e None
    menor_distancia = float('infinity')
    no_menor_distancia = None
    
    # Procura linearmente entre todos os nós
    for no, distancia in distances.items():
        if distancia < menor_distancia and no not in visitados:
            menor_distancia = distancia
            no_menor_distancia = no
    
    # Se não encontrou nenhum nó com distância finita e não visitado
    if menor_distancia == float('infinity'):
        return None
        
    return no_menor_distancia

# Implementação do algoritmo de Dijkstra sem usar min-heap
def dijkstra_tradicional(graph, start_node, end_node):
    # Inicialização
    distances = {node: float('infinity') for node in graph}
    distances[start_node] = 0
    predecessors = {node: None for node in graph}
    visitados = set()
    
    # Verificar caso trivial: início e fim são o mesmo nó
    if start_node == end_node:
        return [start_node], 0
    
    # Enquanto houver nós não visitados com distância finita
    continuar = True
    while continuar:
        # Encontrar o nó não visitado com a menor distância
        atual = encontrar_no_menor_distancia(distances, visitados)
        
        # Se não há mais nós acessíveis ou chegamos ao destino
        if atual is None:
            break
            
        # Se chegamos ao destino, podemos parar
        if atual == end_node:
            break
        
        # Marcar o nó atual como visitado
        visitados.add(atual)
        
        # Atualizar distâncias dos vizinhos
        for vizinho, peso, _ in graph[atual]:
            if vizinho not in visitados:
                distancia_via_atual = distances[atual] + peso
                if distancia_via_atual < distances[vizinho]:
                    distances[vizinho] = distancia_via_atual
                    predecessors[vizinho] = atual
    
    # Verificar se um caminho foi encontrado
    if end_node not in visitados and predecessors[end_node] is None:
        print(f"Não foi possível encontrar um caminho para {end_node}")
        return [], float('infinity')  # Não há caminho para o destino
        
    # Reconstruir o caminho
    path = []
    atual = end_node
    while atual is not None:
        path.append(atual)
        atual = predecessors[atual]
    
    # Reverter o caminho para começar no nó inicial
    path.reverse()
    
    print(f"Caminho encontrado com {len(path)} nós, distância: {distances[end_node]:.2f} metros")
    
    return path, distances[end_node]

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
    
    # Plotar o hospital
    plt.plot(hospital[1], hospital[0], 'ro', markersize=10, label='Hospital')
    
    # Plotar destinos
    for bairro, (lat, lon) in destinos.items():
        plt.plot(lon, lat, 'go', markersize=8)
        plt.text(lon, lat, bairro, fontsize=12)
    
    plt.title("Rotas do Hospital Walfredo Gurgel para diferentes bairros de Natal")
    plt.legend()
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

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

# Encontrar o nó mais próximo ao hospital
no_hospital = encontrar_no_mais_proximo(node_coords, hospital[0], hospital[1])
print(f"Nó mais próximo ao hospital: {no_hospital}")

# Cores para as rotas
cores = ['red', 'blue', 'green', 'orange', 'purple']

# Calcular rotas, distâncias e tempos estimados
rotas = []
print("\nCalculando rotas, distâncias e tempos estimados:")
for i, (bairro, coords) in enumerate(destinos.items()):
    # Encontrar o nó mais próximo ao destino
    no_destino = encontrar_no_mais_proximo(node_coords, coords[0], coords[1])
    print(f"Nó mais próximo para {bairro}: {no_destino}")
    
    # Verificar se ambos os nós (origem e destino) existem no grafo
    if no_hospital not in graph:
        print(f"ERRO: Nó do hospital {no_hospital} não está no grafo!")
        continue
    if no_destino not in graph:
        print(f"ERRO: Nó do destino {no_destino} para {bairro} não está no grafo!")
        continue
    
    # Calcular a rota usando Dijkstra tradicional (sem min-heap)
    print(f"Calculando rota para {bairro}...")
    inicio = time.time()
    path, distancia = dijkstra_tradicional(graph, no_hospital, no_destino)
    fim = time.time()
    
    # Verificar se uma rota válida foi encontrada
    if len(path) > 0:
        # Estimar tempo de deslocamento
        tempo_min = estimar_tempo(graph, path)
        print(f"{bairro}: {distancia:.2f} metros, tempo estimado = {tempo_min:.2f} minutos")
        print(f"Tempo de cálculo: {(fim - inicio):.2f} segundos, Nós na rota: {len(path)}")
    else:
        print(f"AVISO: Não foi possível encontrar uma rota para {bairro}")
    
    # Adicionar rota à lista (mesmo que vazia)
    rotas.append(path)

# Plotar todas as rotas no mesmo mapa
print("\nPlotando rotas...")
plotar_grafo_e_rotas(graph, node_coords, rotas, cores)