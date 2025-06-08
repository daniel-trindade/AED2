import random
import heapq
from aux_functions import (
    a_star,
    encontrar_no_mais_proximo
)

# Função para traçar a rota usando o algoritmo a_star
def tracar_rota_cluster_tsp_a_star(cluster_alvo_id, destinos, labels_clusters, czoonoses_coords, graph, node_coords):
    """
    Traça uma rota otimizada (usando a heurística do vizinho mais próximo) que começa
    no Centro de Zoonoses, visita todos os pontos de um cluster específico e retorna ao CZO.
    """
    print(f"\nIniciando o planejamento da rota para o Cluster {cluster_alvo_id + 1}...")

    # 1. Identificar os destinos específicos deste cluster
    destinos_do_cluster = {
        nome: destinos[nome] for nome, cluster_id in labels_clusters.items() 
        if cluster_id == cluster_alvo_id
    }
    
    if not destinos_do_cluster:
        print(f"Cluster {cluster_alvo_id + 1} não possui destinos. Rota não gerada.")
        return [], 0

    print(f"Destinos do cluster: {list(destinos_do_cluster.keys())}")

    # Encontrar o nó do CZO
    no_czoonoses = encontrar_no_mais_proximo(node_coords, czoonoses_coords[0], czoonoses_coords[1])
    
    # 2. Mapear cada destino para seu nó mais próximo e verificar conectividade
    destinos_para_nos = {}
    destinos_inalcancaveis = []
    
    for nome, (lon, lat) in destinos_do_cluster.items():
        no_destino = encontrar_no_mais_proximo(node_coords, lat, lon)
        
        # Verificar se o nó tem conexões (não está isolado)
        if no_destino and no_destino in graph and len(graph[no_destino]) > 0:
            # Testar conectividade fazendo uma busca rápida
            caminho_teste, dist_teste = a_star(graph, no_czoonoses, no_destino, node_coords)
            if caminho_teste:  # Se conseguiu encontrar um caminho
                destinos_para_nos[nome] = no_destino
            else:
                destinos_inalcancaveis.append(nome)
                print(f"AVISO: '{nome}' não é alcançável pela rede viária disponível.")
        else:
            destinos_inalcancaveis.append(nome)
            print(f"AVISO: '{nome}' está mapeado para um nó isolado ou inexistente.")
    
    if not destinos_para_nos:
        print(f"Nenhum destino do Cluster {cluster_alvo_id + 1} é alcançável. Rota não gerada.")
        return [], 0

    # 3. Implementar o algoritmo do vizinho mais próximo usando os destinos alcançáveis
    rota_completa = [no_czoonoses]
    distancia_total = 0
    ponto_atual = no_czoonoses
    destinos_restantes = destinos_para_nos.copy()

    while destinos_restantes:
        distancia_minima = float('inf')
        destino_mais_proximo = None
        melhor_caminho = []

        # Encontrar o destino mais próximo do ponto atual
        for nome_destino, no_destino in destinos_restantes.items():
            caminho, distancia = a_star(graph, ponto_atual, no_destino, node_coords)
            if caminho and distancia < distancia_minima:
                distancia_minima = distancia
                destino_mais_proximo = nome_destino
                melhor_caminho = caminho
        
        if destino_mais_proximo:
            print(f"  - Visitando '{destino_mais_proximo}' (Distância: {distancia_minima:.2f} m)")
            
            # Adicionar o caminho à rota (excluindo o primeiro nó para evitar duplicatas)
            rota_completa.extend(melhor_caminho[1:])
            distancia_total += distancia_minima
            
            # Atualizar posição atual e remover o destino visitado
            ponto_atual = destinos_para_nos[destino_mais_proximo]
            del destinos_restantes[destino_mais_proximo]
        else:
            print("ERRO: Não foi possível encontrar caminho para os destinos restantes.")
            break

    # 4. Retornar ao Centro de Zoonoses
    print("  - Todos os pontos alcançáveis visitados. Retornando ao CZO...")
    caminho_final, distancia_final = a_star(graph, ponto_atual, no_czoonoses, node_coords)
    
    if caminho_final:
        rota_completa.extend(caminho_final[1:])
        distancia_total += distancia_final
        print(f"  - Retorno ao CZO (Distância: {distancia_final:.2f} m)")
    else:
        print("AVISO: Não foi possível traçar a rota de volta para o CZO.")

    # Relatório final
    print(f"Rota para o Cluster {cluster_alvo_id + 1} finalizada.")
    print(f"Destinos visitados: {len(destinos_do_cluster) - len(destinos_inalcancaveis)}/{len(destinos_do_cluster)}")
    if destinos_inalcancaveis:
        print(f"Destinos não alcançáveis: {destinos_inalcancaveis}")
    print(f"Distância total estimada: {distancia_total / 1000:.2f} km")
    
    return rota_completa, distancia_total


def planejar_rotas_para_todos_os_clusters_a_star(destinos, labels_clusters, czoonoses_coords, graph, node_coords):
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
        rota, distancia = tracar_rota_cluster_tsp_a_star(
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

def extrair_subgrafo_por_cluster(cluster_nodes, node_coords, graph, margem=0.005):
    """
    Extrai de 'graph' apenas os nós e arestas que caem no bbox que envolve
    cluster_nodes (lat/lon em node_coords) com uma pequena margem.
    """
    # calcula bbox
    lats = [node_coords[n][0] for n in cluster_nodes]
    lons = [node_coords[n][1] for n in cluster_nodes]
    min_lat, max_lat = min(lats)-margem, max(lats)+margem
    min_lon, max_lon = min(lons)-margem, max(lons)+margem

    # filtra nós no bbox
    nodes_ok = {
        n for n,(lat,lon) in node_coords.items()
        if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon
    }

    # monta subgrafo
    sub = {}
    for n in nodes_ok:
        sub[n] = [(v,w,s) for (v,w,s) in graph[n] if v in nodes_ok]
    return sub


def dijkstra_tradicional_distancias(graph, source):
    """
    Roda o seu Dijkstra tradicional (sem heap) a partir de 'source'
    e retorna dois dicts: dist[n] e pred[n].
    """
    dist = {n: float('inf') for n in graph}
    dist[source] = 0
    pred = {n: None for n in graph}
    visitados = set()

    while True:
        u, best = None, float('inf')
        for n, d in dist.items():
            if n not in visitados and d < best:
                u, best = n, d
        if u is None:
            break
        visitados.add(u)
        for v, w, _ in graph[u]:
            if v not in visitados and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u

    return dist, pred


def tracar_rota_cluster_tsp_dijkstra_trad(
    cluster_alvo_id,
    destinos,
    labels_clusters,
    czoonoses_coords,
    graph,
    node_coords
):
    """
    Traça rota NN+retorno para o cluster usando Dijkstra tradicional
    em subgrafo reduzido.
    """
    # 1) mapeia nós do CZO e destinos do cluster
    start = encontrar_no_mais_proximo(node_coords, *czoonoses_coords)
    nomes = [n for n,c in labels_clusters.items() if c==cluster_alvo_id]
    destinos_nodes = [
        encontrar_no_mais_proximo(node_coords, lat, lon)
        for n in nomes for (lon,lat) in [destinos[n]]
    ]
    cluster_nodes = [start] + destinos_nodes

    # 2) extrai subgrafo restrito
    sub_graph = extrair_subgrafo_por_cluster(cluster_nodes, node_coords, graph)

    # 3) inicializa rota e estado
    rota = [start]
    atual = start
    total = 0.0
    restantes = set(destinos_nodes)

    # 4) Nearest-Neighbor usando Dijkstra one-to-all
    while restantes:
        dist_map, pred_map = dijkstra_tradicional_distancias(sub_graph, atual)
        vizinho = min(restantes, key=lambda n: dist_map.get(n, float('inf')))
        dmin = dist_map[vizinho]

        # reconstrói caminho
        caminho = []
        cur = vizinho
        while cur is not None:
            caminho.append(cur)
            cur = pred_map[cur]
        caminho.reverse()

        # anexa e atualiza
        rota.extend(caminho[1:])
        total += dmin
        atual = vizinho
        restantes.remove(vizinho)

    # 5) volta ao CZO
    dist_map, pred_map = dijkstra_tradicional_distancias(sub_graph, atual)
    retorno = []
    cur = start
    # reconstrói de atual → start
    path_back = []
    node = atual
    while node is not None:
        path_back.append(node)
        node = pred_map[node]
    path_back.reverse()

    rota.extend(path_back[1:])
    total += dist_map[start]

    print(f"Cluster {cluster_alvo_id+1}: {len(rota)} nós, {total/1000:.2f} km")
    return rota, total


def planejar_rotas_para_todos_os_clusters_dijkstra_trad(destinos, labels_clusters, czoonoses_coords, graph, node_coords):
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
        rota, distancia = tracar_rota_cluster_tsp_dijkstra_trad(
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

def dijkstra_min_heap(graph, source):
    """
    Dijkstra com min-heap (O(E + V log V)),
    retornando (dist, pred) para todo nó.
    """
    dist = {n: float('inf') for n in graph}
    dist[source] = 0
    pred = {n: None for n in graph}
    visited = set()
    heap = [(0, source)]

    while heap:
        d_u, u = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)
        for v, w, _ in graph[u]:
            nd = d_u + w
            if nd < dist[v]:
                dist[v] = nd
                pred[v] = u
                heapq.heappush(heap, (nd, v))
    return dist, pred

def tracar_rota_cluster_tsp_dijkstra_min_heap(cluster_alvo_id, destinos, labels_clusters, czoonoses_coords, graph, node_coords):
    """
    Traça rota NN+retorno para o cluster usando Dijkstra com min-heap
    em subgrafo reduzido com margem dinâmica e fallback.
    """
    # 1) nó do depósito e destinos do cluster
    start = encontrar_no_mais_proximo(node_coords, *czoonoses_coords)
    nomes = [n for n, c in labels_clusters.items() if c == cluster_alvo_id]
    dest_nodes = [
        encontrar_no_mais_proximo(node_coords, lat, lon)
        for n in nomes for (lon, lat) in [destinos[n]]
    ]
    cluster_nodes = [start] + dest_nodes

    # 2) margem dinâmica
    lats = [node_coords[n][0] for n in cluster_nodes]
    lons = [node_coords[n][1] for n in cluster_nodes]
    span_lat = max(lats) - min(lats)
    span_lon = max(lons) - min(lons)
    margem = max(span_lat, span_lon) * 0.5 + 0.005

    # 3) extrai sub-grafo
    subg = extrair_subgrafo_por_cluster(cluster_nodes, node_coords, graph, margem)

    # 4) Nearest-Neighbor usando Dijkstra min-heap one-to-all
    rota = [start]
    atual = start
    total = 0.0
    restantes = set(dest_nodes)

    while restantes:
        dist_map, pred_map = dijkstra_min_heap(subg, atual)
        viz = min(restantes, key=lambda n: dist_map.get(n, float('inf')))
        dmin = dist_map[viz]

        # reconstrói caminho até viz
        caminho = []
        cur = viz
        while cur is not None:
            caminho.append(cur)
            cur = pred_map[cur]
        caminho.reverse()

        rota.extend(caminho[1:])
        total += dmin
        atual = viz
        restantes.remove(viz)

    # 5) volta ao depósito
    dist_map, pred_map = dijkstra_min_heap(subg, atual)
    if dist_map.get(start, float('inf')) == float('inf'):
        # fallback no grafo completo
        full_dist, full_pred = dijkstra_min_heap(graph, atual)
        d_back = full_dist[start]
        caminho_back = []
        cur = start
        while cur is not None:
            caminho_back.append(cur)
            cur = full_pred[cur]
        caminho_back.reverse()
    else:
        d_back = dist_map[start]
        caminho_back = []
        cur = start
        while cur is not None:
            caminho_back.append(cur)
            cur = pred_map[cur]
        caminho_back.reverse()

    rota.extend(caminho_back[1:])
    total += d_back

    print(f"Cluster {cluster_alvo_id+1}: {len(rota)} nós, {total/1000:.2f} km")
    return rota, total

def planejar_rotas_para_todos_os_clusters_min_heap(destinos, labels_clusters, czoonoses_coords, graph, node_coords):
    """
    Itera sobre todos os clusters e chama
    tracar_rota_cluster_tsp_dijkstra_min_heap para cada um.
    """
    print("\n=== INICIANDO PLANEJAMENTO DE ROTAS (min-heap) ===")
    rotas = {}
    for cid in sorted(set(labels_clusters.values())):
        rota, dist = tracar_rota_cluster_tsp_dijkstra_min_heap(
            cluster_alvo_id=cid,
            destinos=destinos,
            labels_clusters=labels_clusters,
            czoonoses_coords=czoonoses_coords,
            graph=graph,
            node_coords=node_coords
        )
        if rota:
            rotas[cid] = (rota, dist)
    print("=== PLANEJAMENTO CONCLUÍDO ===")
    return rotas


def gerar_rotas_aleatorias_a_star(
    destinos, czoonoses_coords, graph, node_coords,
    num_operadores=10, seed=42
):
    random.seed(seed)
    nomes = list(destinos.keys())
    random.shuffle(nomes)

    grupos = [[] for _ in range(num_operadores)]
    for i,nome in enumerate(nomes):
        grupos[i % num_operadores].append(nome)

    resultado = {}
    start = encontrar_no_mais_proximo(node_coords, *czoonoses_coords)

    for op_id, grupo in enumerate(grupos, 1):
        rota = [start]
        total = 0.0
        atual = start
        for nome in grupo:
            lon, lat = destinos[nome]
            dest_node = encontrar_no_mais_proximo(node_coords, lat, lon)
            path, dist = a_star(graph, atual, dest_node, node_coords)
            if not path:
                print(f"[Op{op_id}] falha em {nome}")
                continue
            rota.extend(path[1:])
            total += dist
            atual = dest_node
        back, dback = a_star(graph, atual, start, node_coords)
        if back:
            rota.extend(back[1:])
            total += dback

        resultado[op_id] = {
            'rota_nodes': rota,
            'dist_m': total,
            'destinos': grupo
        }
    return resultado