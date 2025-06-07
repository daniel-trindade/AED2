""""
PARA EXECUÇÃO DESSE PROGRAMA SERÁ NECESSÁRIO A INSTALAÇÃO DE ALGUMAS BIBLIOTECAS:
Você pode instalar direto em sua maquina ou usar um ambiente virtual.
Caso opte por um ambiente virtual, execute os seguintes comandos:
estando dentro da pasta do projeto:
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
"""

from functions import (
  carregar_destinos,
  obter_dados_estradas,
  criar_grafo,
  encontrar_no_mais_proximo,
  plotar_mapa_natal_com_destinos,
  dividir_destinos_em_clusters,
  plotar_mapa_com_clusters,
  encontrar_pontos_mais_distantes_por_cluster
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

# Encontrar o nó mais próximo ao centro de zoonoses
no_czoonoses = encontrar_no_mais_proximo(node_coords, czoonoses[0], czoonoses[1])
print(f"Nó mais próximo ao centro de zoonoses: {no_czoonoses}")

# Plot do mapa com os pontos de destino e o centro de zoonoses
# Desomente essa parte para plotar mapa com todos os pontos de interesse
""" 
print("Plotando mapa natal com destinos...")
plotar_mapa_natal_com_destinos(graph, node_coords, destinos, czoonoses, bounds)
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

########### Encontra ponto mais distante de cada Cluster #############

# Encontrar o ponto mais distante do CZO em cada cluster
resultados = encontrar_pontos_mais_distantes_por_cluster(destinos, labels_clusters, czoonoses)

# Imprimir resultados
print("\n=== Pontos mais distantes por cluster ===")
for cluster_id, (nome_destino, distancia) in resultados.items():
    print(f"Cluster {cluster_id + 1}: '{nome_destino}' a {distancia:.2f} metros")


# Finalizando reastreador de emissões de carbono
# Precisa descomentar para calcular pegada de carbono
""" 
emissions = tracker.stop()
print(f"\nEmissões de CO2 estimadas: {emissions:.6f} kg")
"""