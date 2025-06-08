""""
PARA EXECUÇÃO DESSE PROGRAMA SERÁ NECESSÁRIO A INSTALAÇÃO DE ALGUMAS BIBLIOTECAS:
Você pode instalar direto em sua maquina ou usar um ambiente virtual.
Caso opte por um ambiente virtual, execute os seguintes comandos:
estando dentro da pasta do projeto:
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
"""

from aux_functions import (
  carregar_destinos,
  obter_dados_estradas,
  criar_grafo,
  dividir_destinos_em_clusters,
  imprimir_resumo_detalhado,
  diagnosticar_conectividade_grafo
)

from plot_functions import(
  plotar_mapa_com_clusters,
  plotar_mapa_natal_com_destinos,
  plotar_mapa_com_rotas,
  plotar_mapa_rotas_operadores
)

from routes_functions import(
planejar_rotas_para_todos_os_clusters_dijkstra_trad,
  planejar_rotas_para_todos_os_clusters_min_heap,
  planejar_rotas_para_todos_os_clusters_a_star,
  gerar_rotas_aleatorias_a_star
)

from codecarbon import EmissionsTracker

# Iniciando o rastreador de emissões do code carbon
# Descomente o bloco a seguir e o último bloco do código para calcular a pegada de corbono
""" 
tracker = EmissionsTracker()       
tracker.start()  
"""            

# Carregar destinos do arquivo JSON
destinos = carregar_destinos('db.json')

# Define as coordenadas do centro de zoonoses
czoonoses = (-5.7532189, -35.2621815)

# Define os limites para extrair dados do OpenStreetMap (bounding box para Natal-RN)
min_lat = -5.8850
min_lon = -35.3150
max_lat = -5.7000
max_lon = -35.1700
bounds = (min_lat, min_lon, max_lat, max_lon)
 
print("Baixando dados do OpenStreetMap...")
data = obter_dados_estradas(bounds)

print("Criando grafo da rede viária...")
graph, node_coords = criar_grafo(data)
print(f"Grafo criado com {len(graph)} nós.")

# Plot do mapa com os pontos de destino e o centro de zoonoses
# Descomente esse bloco para plotar mapa com todos os pontos de interesse

"""
print("Plotando mapa natal com destinos...")
plotar_mapa_natal_com_destinos(graph, node_coords, destinos, czoonoses, bounds=None)
"""

################### Diagnosticar Conectividade entra nós ###################
# Descomente esse bloco para plotar mapa com todos os pontos de interesse

""" 
destinos_ok, destinos_problematicos = diagnosticar_conectividade_grafo(
    graph, node_coords, destinos, czoonoses
) 
"""

################### Dividir os destinos em clusters ###################

print("Dividindo destinos em 10 clusters...")
labels_clusters = dividir_destinos_em_clusters(destinos, n_clusters=10, plotar=False)

# Exemplo: imprimir quais destinos ficaram em cada cluster
clusters = {}
for nome, cluster_id in labels_clusters.items():
    clusters.setdefault(cluster_id, []).append(nome)

for cluster_id, nomes in clusters.items():
    print(f"\nCluster {cluster_id+1} ({len(nomes)} pontos):")
    for nome in nomes:
        print(f"  - {nome}")


###################### Plota mapa com clusters ######################
# Descomente esse bloco para plotar o mapa com os pontos clusterizados

""" 
print("\nPlotando mapa com destinos coloridos por cluster...")
mapa_cores, estatisticas_clusters = plotar_mapa_com_clusters(
    graph=graph, 
    node_coords=node_coords, 
    destinos=destinos, 
    labels_clusters=labels_clusters, 
    czoonoses=czoonoses, 
    bounds=bounds
)

print("\nCores utilizadas para cada cluster:")
for cluster_id, cor in mapa_cores.items():
    print(f"Cluster {cluster_id + 1}: RGB{tuple(cor[:3])}")

print("\nEstatísticas finais:")
print(f"Total de clusters: {len(mapa_cores)}")
print(f"Total de destinos plotados: {sum(estatisticas_clusters.values())}") 
"""


######## Planejar e Salvar Rotas para Todos os Clusters usado A* ######## 
# Chama a função principal que gerencia o planejamento para todos os clusters

""" 
rotas_salvas = planejar_rotas_para_todos_os_clusters_a_star(
    destinos=destinos,
    labels_clusters=labels_clusters,
    czoonoses_coords=czoonoses,
    graph=graph,
    node_coords=node_coords
)  
"""

######## Planejar e Salvar Rotas para Todos os Clusters usado Dijkstra ######## 
"""
rotas_salvas = planejar_rotas_para_todos_os_clusters_dijkstra_trad(
    destinos=destinos,
    labels_clusters=labels_clusters,
    czoonoses_coords=czoonoses,
    graph=graph,
    node_coords=node_coords
)
"""

######## Planejar e Salvar Rotas para Todos os Clusters usado Dijkstra Min-Heap ######## 
"""
rotas_salvas = planejar_rotas_para_todos_os_clusters_min_heap(
    destinos=destinos,
    labels_clusters=labels_clusters,
    czoonoses_coords=czoonoses,
    graph=graph,
    node_coords=node_coords
)
"""

"""
# Chama a nova função dedicada a imprimir os resultados de forma organizada
imprimir_resumo_detalhado(
    rotas_salvas=rotas_salvas,
    destinos=destinos,
    node_coords=node_coords,
    labels_clusters=labels_clusters
)

if rotas_salvas:
    plotar_mapa_com_rotas(
        rotas_salvas=rotas_salvas,
        node_coords=node_coords,
        destinos=destinos,
        labels_clusters=labels_clusters,
        czoonoses_coords=czoonoses
    )
"""


""" 
######## Planejar e Salvar Rotas para os operadores usado A* sem clustering ######## 
# Gera as 10 rotas
rotas_por_operador = gerar_rotas_aleatorias_a_star(
    destinos=destinos,
    czoonoses_coords=czoonoses,
    graph=graph,
    node_coords=node_coords,
    num_operadores=10,
    seed=123
)

# --- Resumo detalhado por Operador, com total geral ---
print("\n=== Resumo detalhado por Operador ===")
dist_total = 0.0

for op_id, info in rotas_por_operador.items():
    rota = info['rota_nodes']
    distancia = info['dist_m']
    destinos_vis = info['destinos']
    
    dist_total += distancia
    
    print("\n" + "-"*41)
    print(f"| Rota para o Operador {op_id:<2}               |")
    print("-"*41)
    print(f"  -> Distância Total: {distancia/1000:.2f} km")
    print(f"  -> Número de nós na rota: {len(rota)}")
    print(f"  -> Destinos Visitados ({len(destinos_vis)}):")
    for i, nome in enumerate(destinos_vis, start=1):
        print(f"     {i:2d}. {nome}")

# Depois de listar todos, imprime o total
print("\n" + "="*41)
print(f"Distância TOTAL percorrida por todos os operadores: {dist_total/1000:.2f} km")
print("="*41 + "\n")


# Plota o mapa
plotar_mapa_rotas_operadores(
    rotas_por_operador,
    node_coords=node_coords,
    destinos=destinos,
    czoonoses_coords=czoonoses
)
""" 
 
# Finalizando reastreador de emissões de carbono
# Precisa descomentar para calcular pegada de carbono
""" 
emissions = tracker.stop()
print(f"\nEmissões de CO2 estimadas: {emissions:.6f} kg")
""" 