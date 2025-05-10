import osmnx as ox
import networkx as nx
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

# Baixar o grafo da cidade
place = "Natal, Rio Grande do Norte, Brazil"
G = ox.graph_from_place(place, network_type="drive")

# Encontrar o nó mais próximo ao hospital
nó_hospital = ox.distance.nearest_nodes(G, X=hospital[1], Y=hospital[0])

# Listas para armazenar rotas e distâncias
rotas = []
cores = ['red', 'blue', 'green', 'orange', 'purple']

# Função para estimar tempo com base em maxspeed
def estimar_tempo(G, rota, velocidade_padrao=40):
    tempo_total = 0
    for u, v in zip(rota[:-1], rota[1:]):
        dados = G.get_edge_data(u, v, 0)
        comprimento = dados.get("length", 0)
        velocidade = dados.get("maxspeed", velocidade_padrao)
        
        # Caso maxspeed seja lista ou string
        if isinstance(velocidade, list):
            velocidade = velocidade[0]
        if isinstance(velocidade, str):
            velocidade = velocidade.split()[0]  # Remove ' km/h' se houver
        try:
            velocidade = float(velocidade)
        except:
            velocidade = velocidade_padrao

        # Calcular tempo em minutos
        tempo = (comprimento / 1000) / velocidade * 60
        tempo_total += tempo
    return tempo_total

# Calcular rotas, distâncias e tempos
for i, (bairro, coords) in enumerate(destinos.items()):
    nó_destino = ox.distance.nearest_nodes(G, X=coords[1], Y=coords[0])
    rota = nx.shortest_path(G, nó_hospital, nó_destino, weight="length")
    rotas.append(rota)

    # GeoDataFrame da rota para somar a distância
    gdf_rota = ox.routing.route_to_gdf(G, rota)
    distancia = gdf_rota["length"].sum()

    # Estimar tempo de deslocamento
    tempo_min = estimar_tempo(G, rota)

    print(f"{bairro}: {distancia:.2f} metros, tempo estimado = {tempo_min:.2f} minutos")

# Plotar todas as rotas no mesmo mapa
fig, ax = ox.plot_graph_routes(G, rotas, route_colors=cores, route_linewidth=1, node_size=2)

# Parar o rastreador e exibir as emissões
emissions = tracker.stop()
print(f"\nEmissões de CO2 estimadas: {emissions:.6f} kg")