import requests
import math
import heapq
import matplotlib.pyplot as plt
from collections import defaultdict
import time
from codecarbon import EmissionsTracker

# Iniciar o rastreador de emissões
tracker = EmissionsTracker()
tracker.start()

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

# Implementação do algoritmo de Dijkstra usando min-heap explicitamente
def dijkstra_min_heap(graph, start_node, end_node):
    # Inicialização
    distances = {node: float('infinity') for node in graph}
    distances[start_node] = 0
    predecessors = {node: None for node in graph}
    
    # Min-heap (fila de prioridade) para nós a serem explorados
    # Formato: (distância, node_id)
    min_heap = [(0, start_node)]
    
    # Conjunto para rastrear nós processados
    processed = set()
    
    while min_heap:
        # Extrair nó com menor distância do min-heap (operação O(log n))
        current_distance, current_node = heapq.heappop(min_heap)
        
        # Se já alcançamos o nó de destino, terminamos
        if current_node == end_node:
            break
        
        # Se o nó já foi processado, pule
        if current_node in processed:
            continue
        
        # Marcar o nó como processado
        processed.add(current_node)
        
        # Relaxamento: Atualizar distâncias para todos os vizinhos
        for neighbor, edge_weight, _ in graph[current_node]:
            # Se o vizinho já foi processado completamente, pule
            if neighbor in processed:
                continue
                
            # Calcular nova distância potencial
            new_distance = current_distance + edge_weight
            
            # Se encontramos um caminho mais curto
            if new_distance < distances[neighbor]:
                # Atualizar distância
                distances[neighbor] = new_distance
                # Atualizar predecessor
                predecessors[neighbor] = current_node
                # Adicionar ao min-heap (não removemos entradas antigas, apenas adicionamos a nova)
                heapq.heappush(min_heap, (new_distance, neighbor))
    
    # Reconstruir o caminho do final para o início
    path = []
    current = end_node
    
    # Se não há caminho para o destino
    if predecessors[end_node] is None and end_node != start_node:
        return [], float('infinity')
    
    # Construir o caminho seguindo os predecessores
    while current is not None:
        path.append(current)
        current = predecessors[current]
    
    # Reverter o caminho para que comece no nó inicial
    path.reverse()
    
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
    
    # Plotar arestas
    for node in graph:
        x1, y1 = node_coords[node][1], node_coords[node][0]  # lon, lat
        for neighbor, _, _ in graph[node]:
            x2, y2 = node_coords[neighbor][1], node_coords[neighbor][0]  # lon, lat
            plt.plot([x1, x2], [y1, y2], 'k-', linewidth=0.2, alpha=0.3)
    
    # Plotar rotas
    for i, (rota, cor) in enumerate(zip(rotas, cores)):
        x_coords = [node_coords[node][1] for node in rota]  # lon
        y_coords = [node_coords[node][0] for node in rota]  # lat
        plt.plot(x_coords, y_coords, color=cor, linewidth=2, label=list(destinos.keys())[i])
    
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
    
    # Calcular a rota usando Dijkstra min-heap
    print(f"Calculando rota para {bairro}...")
    inicio = time.time()
    path, distancia = dijkstra_min_heap(graph, no_hospital, no_destino)
    fim = time.time()
    
    # Estimar tempo de deslocamento
    tempo_min = estimar_tempo(graph, path)
    
    print(f"{bairro}: {distancia:.2f} metros, tempo estimado = {tempo_min:.2f} minutos")
    print(f"Tempo de cálculo: {(fim - inicio):.2f} segundos, Nós na rota: {len(path)}")
    
    rotas.append(path)

# Plotar todas as rotas no mesmo mapa
print("\nPlotando rotas...")
plotar_grafo_e_rotas(graph, node_coords, rotas, cores)

# Parar o rastreador e exibir as emissões
emissions = tracker.stop()
print(f"\nEmissões de CO2 estimadas: {emissions:.6f} kg")