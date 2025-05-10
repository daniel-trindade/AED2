import osmnx as ox
import networkx as nx

# 1. Defina as coordenadas centrais dos bairros
destino = (-5.8678, -35.2075)
origem = 5244548621

# 2. Baixe o grafo cobrindo a região (ex.: raio de 2 km)
centro = (
    (destino[0] + origem[0]) / 2,
    (destino[1] + origem[1]) / 2,
)
G = ox.graph_from_point(centro, dist=2000, network_type="drive")

# 3. Encontre os nós mais próximos a cada bairro
orig = ox.distance.nearest_nodes(
    G, X=destino[1], Y=destino[0]
)
dest = ox.distance.nearest_nodes(
    G, X=origem[1], Y=origem[0]
)

# 4. Calcule a rota mais curta (peso = comprimento em metros)
route = ox.shortest_path(G, orig, dest, weight="length")  # :contentReference[oaicite:0]{index=0}

# 5. Converta a rota para GeoDataFrame e some os comprimentos
route_gdf = ox.routing.route_to_gdf(G, route, weight="length")  # :contentReference[oaicite:1]{index=1}
distancia_total = route_gdf["length"].sum()

print(f"Distância entre Neópolis e Mirassol: {distancia_total:.2f} metros")

# 6. Opcional: plote a rota
fig, ax = ox.plot_graph_route(
    G, route, route_color="y", route_linewidth=4, node_size=0
)
