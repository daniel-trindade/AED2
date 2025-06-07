# projeto_dijkstra_min_heap/main.py

import osmnx as ox
import networkx as nx 
from functions import (
    carregar_destinos,
    dividir_destinos_em_clusters,
    encontrar_ponto_mais_distante,
    otimizar_tour_cluster,
    calcular_distancia_rota,
    plotar_mapa_com_rotas
)

# NOVO: Importar o Tracker do CodeCarbon
from codecarbon import EmissionsTracker
import logging # Opcional: para controlar o log do CodeCarbon

# Opcional: Configurar o nível de log do CodeCarbon para ser menos verboso
# logging.getLogger('codecarbon').setLevel(logging.WARNING)


if __name__ == "__main__":
    # NOVO: Iniciar o rastreador de emissões para este projeto
    tracker = EmissionsTracker(
        project_name='Rotas_Dijkstra_MinHeap', # Nome do seu projeto
        output_dir='./', # Onde o arquivo de saída será salvo (na pasta do projeto)
        output_file='emissions_dijkstra_minheap.csv', # Nome do arquivo de saída
        log_level='warning', # Reduzir logs verbosos no terminal
        measure_power_secs=5 # Frequência da medição em segundos
    )
    tracker.start()

    try: # NOVO: Envolva seu código principal em um try-finally para garantir que o tracker pare
        # 1. Carregar dados
        destinos = carregar_destinos('db.json')
        czoonoses = (-5.753216, -35.262167)
        
        # 2. Obter o grafo de Natal
        place_name = "Natal, Rio Grande do Norte, Brasil"
        print(f"Baixando dados para '{place_name}'...")
        G_completo = ox.graph_from_place(place_name, network_type='drive', simplify=False)
        print(f"Grafo inicial criado com {len(G_completo.nodes)} nós.")

        print("Analisando a conectividade do grafo...")
        componentes = nx.weakly_connected_components(G_completo)
        maior_componente_nos = max(componentes, key=len)
        G = G_completo.subgraph(maior_componente_nos).copy()
        print(f"Trabalhando com o maior componente conectado do grafo, com {len(G.nodes)} nós.")

        # 3. Mapear coordenadas para os nós do grafo
        print("\nMapeando coordenadas...")
        no_czo = ox.distance.nearest_nodes(G, czoonoses[1], czoonoses[0])
        nos_destinos = {nome: ox.distance.nearest_nodes(G, lon, lat) for nome, (lon, lat) in destinos.items()}
        
        # 4. Dividir em clusters e agrupar pontos
        labels_clusters = dividir_destinos_em_clusters(destinos)
        pontos_por_cluster = {i: {} for i in range(10)}
        for nome, cluster_id in labels_clusters.items():
            pontos_por_cluster[cluster_id][nome] = nos_destinos[nome]

        # 5. Calcular a rota completa para cada cluster
        print("\n--- CALCULANDO ROTAS COM ALGORITMOS OTIMIZADOS ---")
        rotas_completas = {}
        distancia_total_geral = 0

        for cluster_id, cluster_pontos in pontos_por_cluster.items():
            if not cluster_pontos: continue

            ponto_distante, dist_ida = encontrar_ponto_mais_distante(G, no_czo, cluster_pontos)
            
            if ponto_distante is None:
                print(f"ALERTA: Cluster {cluster_id + 1} é inalcançável. Pulando.")
                continue

            outros_pontos = [item for item in cluster_pontos.items() if item[0] != ponto_distante[0]]
            tour_otimizado = otimizar_tour_cluster(G, ponto_distante, outros_pontos)
            
            distancia_tour_interno = 0
            rota_tour_nos = []
            if len(tour_otimizado) > 1:
                for i in range(len(tour_otimizado) - 1):
                    origem, destino = tour_otimizado[i][1], tour_otimizado[i+1][1]
                    distancia_segmento = calcular_distancia_rota(G, origem, destino)
                    
                    if distancia_segmento != float('inf'):
                        distancia_tour_interno += distancia_segmento
                        # USANDO NX.SHORTEST_PATH (DIJKSTRA OTIMIZADO COM MIN-HEAP)
                        path_segmento = nx.shortest_path(G, origem, destino, weight='length')
                        if not rota_tour_nos:
                            rota_tour_nos.extend(path_segmento)
                        else:
                            rota_tour_nos.extend(path_segmento[1:])

            ultimo_ponto = tour_otimizado[-1]
            dist_volta = calcular_distancia_rota(G, ultimo_ponto[1], no_czo)
            distancia_total_cluster = dist_ida + distancia_tour_interno + dist_volta
            distancia_total_geral += distancia_total_cluster
            
            # USANDO NX.SHORTEST_PATH (DIJKSTRA OTIMIZADO COM MIN-HEAP)
            rota_ida_nos = nx.shortest_path(G, no_czo, ponto_distante[1], weight='length')
            # USANDO NX.SHORTEST_PATH (DIJKSTRA OTIMIZADO COM MIN-HEAP)
            rota_volta_nos = nx.shortest_path(G, ultimo_ponto[1], no_czo, weight='length')
            
            if rota_tour_nos and rota_ida_nos and rota_volta_nos:
                rota_completa_final = rota_ida_nos[:-1] + rota_tour_nos + rota_volta_nos[1:]
            elif rota_ida_nos and rota_volta_nos:
                rota_completa_final = rota_ida_nos + rota_volta_nos[1:]
            else:
                rota_completa_final = []


            if rota_completa_final:
                rotas_completas[cluster_id] = {
                    "ordem_visita": [p[0] for p in tour_otimizado],
                    "distancia_total": distancia_total_cluster,
                    "rota_completa_nos": rota_completa_final
                }

        print("\n\n--- OPÇÃO 1: RESUMO DAS ROTAS EM TEXTO ---")
        for cluster_id, dados in sorted(rotas_completas.items()):
            print(f"========== TRABALHADOR DO CLUSTER {cluster_id + 1} ==========")
            print(f"   - Ordem de visitação: {dados['ordem_visita']}")
            print(f"   - DISTÂNCIA TOTAL: {dados['distancia_total']/1000:.2f} km\n")
        print(f"DISTÂNCIA TOTAL GERAL: {distancia_total_geral/1000:.2f} km\n")
        
        if rotas_completas:
            print("\n\n--- OPÇÃO 2: GERANDO MAPA COM TODAS AS ROTAS VISUAIS ---")
            plotar_mapa_com_rotas(G, destinos, czoonoses, rotas_completas, labels_clusters)
        else:
            print("\nNenhuma rota pôde ser calculada para ser exibida no mapa.")

    finally: # NOVO: Garantir que o rastreador pare mesmo se houver erro
        # NOVO: Parar o rastreador de emissões e obter os resultados
        emissions: float = tracker.stop()
        print(f"\nEmissões de carbono da execução: {emissions:.4f} kg CO2e")