import matplotlib.pyplot as plt
import numpy as np



def plotar_mapa_com_clusters(graph, node_coords, destinos, labels_clusters, czoonoses, bounds=None):
    """
    Plota um mapa da cidade de Natal mostrando a rede viária e os pontos de destino
    coloridos por cluster.
    
    Parâmetros:
    - graph: grafo da rede viária
    - node_coords: coordenadas dos nós do grafo
    - destinos: dicionário com destinos carregados do JSON {nome: (lon, lat)}
    - labels_clusters: dicionário com os clusters {nome: cluster_id}
    - czoonoses: coordenadas do centro de zoonoses (lat, lon)
    - bounds: limites da área (min_lat, min_lon, max_lat, max_lon) - opcional
    """
    import matplotlib.pyplot as plt
    import numpy as np

    plt.figure(figsize=(16, 12))
    
    # Definir ou calcular limites para a área do mapa
    if bounds is None or bounds == (0, 0, 0, 0):
        print("Calculando limites automaticamente...")
        
        lats = [czoonoses[0]]  # lat do centro de zoonoses
        lons = [czoonoses[1]]  # lon do centro de zoonoses
        
        # Adicionar coordenadas dos destinos
        for lon, lat in destinos.values():
            lats.append(lat)
            lons.append(lon)
        
        # Adicionar coordenadas dos nós do grafo se disponíveis
        if node_coords:
            for lat, lon in node_coords.values():
                lats.append(lat)
                lons.append(lon)
        
        # Calcular limites com margem
        margem = 0.01  # ~1km aproximadamente
        min_lat = min(lats) - margem
        max_lat = max(lats) + margem
        min_lon = min(lons) - margem
        max_lon = max(lons) + margem
        
        print(f"Limites calculados: lat({min_lat:.4f}, {max_lat:.4f}), lon({min_lon:.4f}, {max_lon:.4f})")
    else:
        min_lat, min_lon, max_lat, max_lon = bounds
        print(f"Usando limites fornecidos: lat({min_lat:.4f}, {max_lat:.4f}), lon({min_lon:.4f}, {max_lon:.4f})")
    
    print("Plotando rede viária de Natal...")
    
    # Plotar arestas do grafo (rede viária)
    edges_plotted = 0
    for node in graph:
        if node in node_coords:
            lat1, lon1 = node_coords[node]  # lat, lon
            x1, y1 = lon1, lat1  # converter para x, y (lon, lat)
            
            for neighbor, distance, speed in graph[node]:
                if neighbor in node_coords:
                    lat2, lon2 = node_coords[neighbor]
                    x2, y2 = lon2, lat2
                    
                    # Plotar apenas se as coordenadas estão dentro dos limites
                    if (min_lat <= lat1 <= max_lat and min_lon <= lon1 <= max_lon and
                        min_lat <= lat2 <= max_lat and min_lon <= lon2 <= max_lon):
                        plt.plot([x1, x2], [y1, y2], 'gray', linewidth=0.6, alpha=0.9)
                        edges_plotted += 1
    
    print(f"Plotadas {edges_plotted} arestas da rede viária")
    
    # Plotar o centro de zoonoses
    lat_czoonoses, lon_czoonoses = czoonoses
    plt.plot(lon_czoonoses, lat_czoonoses, 'ro', markersize=12, 
             label='Centro de Zoonoses', markeredgecolor='darkred', markeredgewidth=2)
    
    # Plotar destinos coloridos por cluster
    print("Plotando destinos coloridos por cluster...")
    destinos_plotados = 0
    
    if not destinos:
        print("AVISO: Nenhum destino foi carregado!")
    else:
        print(f"Destinos disponíveis: {len(destinos)}")
        
    # Determinar número de clusters únicos
    clusters_unicos = set(labels_clusters.values())
    n_clusters = len(clusters_unicos)
    print(f"Número de clusters encontrados: {n_clusters}")
    
    # Gerar cores para cada cluster usando uma paleta de cores distinta
    cores_clusters = plt.cm.tab10(np.linspace(0, 1, min(10, n_clusters)))
    if n_clusters > 10:
        # Se tiver mais de 10 clusters, usar paletas adicionais
        cores_extra = plt.cm.Set3(np.linspace(0, 1, n_clusters - 10))
        cores_clusters = np.vstack([cores_clusters, cores_extra])
    
    # Mapear cada cluster_id para uma cor
    cluster_ids_ordenados = sorted(clusters_unicos)
    mapa_cores = {cluster_id: cores_clusters[i % len(cores_clusters)] 
                  for i, cluster_id in enumerate(cluster_ids_ordenados)}
    
    # Agrupar destinos por cluster para estatísticas
    destinos_por_cluster = {}
    
    for nome_destino, coordenadas in destinos.items():
        # Verificar formato das coordenadas (lon, lat)
        if len(coordenadas) == 2:
            lon, lat = coordenadas
            
            # Verificar se as coordenadas fazem sentido para Natal-RN
            if not (-6.0 <= lat <= -5.0 and -36.0 <= lon <= -34.0):
                print(f"AVISO: Coordenadas suspeitas para {nome_destino}: {coordenadas}")
                # Tentar trocar lat/lon
                lat, lon = coordenadas
                
        else:
            print(f"ERRO: Formato de coordenadas inválido para {nome_destino}: {coordenadas}")
            continue
        
        # Obter cluster do destino
        if nome_destino in labels_clusters:
            cluster_id = labels_clusters[nome_destino]
            cor = mapa_cores[cluster_id]
            
            # Contar destinos por cluster
            if cluster_id not in destinos_por_cluster:
                destinos_por_cluster[cluster_id] = 0
            destinos_por_cluster[cluster_id] += 1
            
            # Plotar ponto com cor do cluster
            plt.plot(lon, lat, 'o', color=cor, markersize=8, 
                    markeredgecolor='black', markeredgewidth=1, alpha=0.8)
            
            # Adicionar rótulo com nome do destino
            plt.text(lon, lat+0.003, nome_destino, fontsize=8, 
                    ha='center', va='bottom', weight='normal',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))
            
            destinos_plotados += 1
            print(f"Plotado: {nome_destino} (Cluster {cluster_id + 1}) em ({lon:.4f}, {lat:.4f})")
        else:
            print(f"AVISO: Destino {nome_destino} não encontrado nos clusters!")
    
    print(f"Plotados {destinos_plotados} destinos")
    
    # Criar legenda para clusters
    handles_legenda = []
    
    # Adicionar centro de zoonoses à legenda
    handles_legenda.append(plt.Line2D([0], [0], marker='o', color='w', 
                                    markerfacecolor='red', markersize=10, 
                                    label='Centro de Zoonoses', markeredgecolor='darkred'))
    
    # Adicionar clusters à legenda (ordenados)
    for cluster_id in cluster_ids_ordenados:
        cor = mapa_cores[cluster_id]
        count = destinos_por_cluster.get(cluster_id, 0)
        handles_legenda.append(plt.Line2D([0], [0], marker='o', color='w', 
                                        markerfacecolor=cor, markersize=8, 
                                        label=f'Cluster {cluster_id + 1} ({count} destinos)', 
                                        markeredgecolor='black'))
    
    # Configurar o plot
    plt.title("Mapa de Natal - RN\nRede Viária e Destinos Agrupados por Clusters", 
              fontsize=16, weight='bold', pad=20)
    plt.xlabel("Longitude", fontsize=12, weight='bold')
    plt.ylabel("Latitude", fontsize=12, weight='bold')
    
    # Definir limites do plot baseado nos dados reais
    if destinos_plotados > 0 or node_coords:
        plt.xlim(min_lon - 0.005, max_lon + 0.005)
        plt.ylim(min_lat - 0.005, max_lat + 0.005)
    else:
        # Limites padrão para Natal-RN se não houver dados
        plt.xlim(-35.3, -35.1)
        plt.ylim(-5.9, -5.7)
    
    # Adicionar grade
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Adicionar legenda
    plt.legend(handles=handles_legenda, loc='upper left', bbox_to_anchor=(1.05, 1), 
              fontsize=10, title="Clusters", title_fontsize=12)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Adicionar informações sobre a área e clusters
    info_text = f"Área: {abs(max_lat - min_lat):.4f}° × {abs(max_lon - min_lon):.4f}°\n"
    info_text += f"Nós no grafo: {len(node_coords)}\n"
    info_text += f"Destinos plotados: {destinos_plotados}\n"
    info_text += f"Clusters: {n_clusters}"
    
    plt.text(0.02, 0.98, info_text, transform=plt.gca().transAxes, 
             fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8))
    
    # Imprimir estatísticas dos clusters
    print("\n=== ESTATÍSTICAS DOS CLUSTERS ===")
    for cluster_id in cluster_ids_ordenados:
        count = destinos_por_cluster.get(cluster_id, 0)
        print(f"Cluster {cluster_id + 1}: {count} destinos")
    
    print("Mapa com clusters plotado com sucesso!")
    plt.show()
    
    return mapa_cores, destinos_por_cluster

def plotar_mapa_natal_com_destinos(graph, node_coords, destinos, czoonoses, bounds=None):
    """
    Plota um mapa da cidade de Natal mostrando a rede viária e os pontos de destino.
    
    Parâmetros:
    - graph: grafo da rede viária
    - node_coords: coordenadas dos nós do grafo
    - destinos: dicionário com destinos carregados do JSON
    - czoonoses: coordenadas do centro de zoonoses (lat, lon)
    - bounds: limites da área (min_lat, min_lon, max_lat, max_lon) - opcional
    """

    plt.figure(figsize=(16, 12))
    
    # Definir ou calcular limites para a área do mapa
    if bounds is None or bounds == (0, 0, 0, 0):
        # Calcular limites automaticamente baseado nos destinos e centro de zoonoses
        print("Calculando limites automaticamente...")
        
        lats = [czoonoses[0]]  # lat do centro de zoonoses
        lons = [czoonoses[1]]  # lon do centro de zoonoses
        
        # Adicionar coordenadas dos destinos
        for lon, lat in destinos.values():
            lats.append(lat)
            lons.append(lon)
        
        # Adicionar coordenadas dos nós do grafo se disponíveis
        if node_coords:
            for lat, lon in node_coords.values():
                lats.append(lat)
                lons.append(lon)
        
        # Calcular limites com margem
        margem = 0.01  # ~1km aproximadamente
        min_lat = min(lats) - margem
        max_lat = max(lats) + margem
        min_lon = min(lons) - margem
        max_lon = max(lons) + margem
        
        print(f"Limites calculados: lat({min_lat:.4f}, {max_lat:.4f}), lon({min_lon:.4f}, {max_lon:.4f})")
    else:
        min_lat, min_lon, max_lat, max_lon = bounds
        print(f"Usando limites fornecidos: lat({min_lat:.4f}, {max_lat:.4f}), lon({min_lon:.4f}, {max_lon:.4f})")
    
    print("Plotando rede viária de Natal...")
    
    # Plotar arestas do grafo (rede viária)
    edges_plotted = 0
    for node in graph:
        if node in node_coords:
            lat1, lon1 = node_coords[node]  # lat, lon
            x1, y1 = lon1, lat1  # converter para x, y (lon, lat)
            
            for neighbor, distance, speed in graph[node]:
                if neighbor in node_coords:
                    lat2, lon2 = node_coords[neighbor]
                    x2, y2 = lon2, lat2
                    
                    # Plotar apenas se as coordenadas estão dentro dos limites
                    if (min_lat <= lat1 <= max_lat and min_lon <= lon1 <= max_lon and
                        min_lat <= lat2 <= max_lat and min_lon <= lon2 <= max_lon):
                        plt.plot([x1, x2], [y1, y2], 'gray', linewidth=0.6, alpha=0.9)
                        edges_plotted += 1
    
    print(f"Plotadas {edges_plotted} arestas da rede viária")
    
    # Plotar o centro de zoonoses
    lat_czoonoses, lon_czoonoses = czoonoses
    plt.plot(lon_czoonoses, lat_czoonoses, 'ro', markersize=12, 
             label='Centro de Zoonoses', markeredgecolor='darkred', markeredgewidth=2)
    
    # Plotar destinos por bairro
    print("Plotando destinos...")
    destinos_plotados = 0
    
    if not destinos:
        print("AVISO: Nenhum destino foi carregado!")
    else:
        print(f"Destinos disponíveis: {len(destinos)}")
        
    cores_bairros = plt.cm.Set3(np.linspace(0, 1, max(12, len(destinos))))
    bairros_unicos = {}
    
    for i, (nome_destino, coordenadas) in enumerate(destinos.items()):
        # Verificar formato das coordenadas (lon, lat) ou (lat, lon)
        if len(coordenadas) == 2:
            # Assumir que está no formato (lon, lat) baseado no código original
            lon, lat = coordenadas
            
            # Verificar se as coordenadas fazem sentido para Natal-RN
            # Natal: aproximadamente lat -5.7 a -5.8, lon -35.2 a -35.3
            if not (-6.0 <= lat <= -5.0 and -36.0 <= lon <= -34.0):
                print(f"AVISO: Coordenadas suspeitas para {nome_destino}: {coordenadas}")
                # Tentar trocar lat/lon
                lat, lon = coordenadas
                
        else:
            print(f"ERRO: Formato de coordenadas inválido para {nome_destino}: {coordenadas}")
            continue
            
        # Extrair nome do bairro (remover sufixo numérico se existir)
        nome_bairro = nome_destino.split('_')[0]
        
        # Atribuir cor única por bairro
        if nome_bairro not in bairros_unicos:
            bairros_unicos[nome_bairro] = len(bairros_unicos)
        
        cor_idx = bairros_unicos[nome_bairro] % len(cores_bairros)
        cor = cores_bairros[cor_idx]
        
        # Plotar ponto
        plt.plot(lon, lat, 'o', color=cor, markersize=8, 
                markeredgecolor='black', markeredgewidth=1, alpha=0.8)
        
        # Adicionar rótulo com nome do destino
        plt.text(lon, lat+0.003, nome_destino, fontsize=8, 
                ha='center', va='bottom', weight='normal',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))
        
        destinos_plotados += 1
        print(f"Plotado: {nome_destino} em ({lon:.4f}, {lat:.4f})")
    
    print(f"Plotados {destinos_plotados} destinos")
    
    # Criar legenda para bairros únicos
    handles_legenda = []
    for bairro, idx in bairros_unicos.items():
        cor_idx = idx % len(cores_bairros)
        cor = cores_bairros[cor_idx]
        handles_legenda.append(plt.Line2D([0], [0], marker='o', color='w', 
                                        markerfacecolor=cor, markersize=8, 
                                        label=bairro, markeredgecolor='black'))
    
    # Adicionar centro de zoonoses à legenda
    handles_legenda.insert(0, plt.Line2D([0], [0], marker='o', color='w', 
                                       markerfacecolor='red', markersize=10, 
                                       label='Centro de Zoonoses', markeredgecolor='darkred'))
    
    # Configurar o plot
    plt.title("Mapa de Natal - RN\nRede Viária e Pontos de Destino", 
              fontsize=16, weight='bold', pad=20)
    plt.xlabel("Longitude", fontsize=12, weight='bold')
    plt.ylabel("Latitude", fontsize=12, weight='bold')
    
    # Definir limites do plot baseado nos dados reais
    if destinos_plotados > 0 or node_coords:
        plt.xlim(min_lon - 0.005, max_lon + 0.005)
        plt.ylim(min_lat - 0.005, max_lat + 0.005)
    else:
        # Limites padrão para Natal-RN se não houver dados
        plt.xlim(-35.3, -35.1)
        plt.ylim(-5.9, -5.7)
    
    # Adicionar grade
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Adicionar legenda
    plt.legend(handles=handles_legenda, loc='upper left', bbox_to_anchor=(1.05, 1), 
              fontsize=10, title="Locais", title_fontsize=12)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Adicionar informações sobre a área
    info_text = f"Área: {abs(max_lat - min_lat):.4f}° × {abs(max_lon - min_lon):.4f}°\n"
    info_text += f"Nós no grafo: {len(node_coords)}\n"
    info_text += f"Destinos plotados: {destinos_plotados}"
    
    plt.text(0.02, 0.98, info_text, transform=plt.gca().transAxes, 
             fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8))
    
    print("Mapa plotado com sucesso!")
    plt.show()


# Em plot_functions.py
import folium
import matplotlib.pyplot as plt
import numpy as np

def plotar_mapa_com_rotas(rotas_salvas, node_coords, destinos, labels_clusters, czoonoses_coords):
    """
    Gera e salva um mapa interativo com Folium que exibe os pontos de destino,
    o Centro de Zoonoses e as rotas planejadas para cada cluster.

    Parâmetros:
    - rotas_salvas: Dicionário com as rotas planejadas {cluster_id: (rota, distancia)}.
    - node_coords: Dicionário com as coordenadas de cada nó do grafo.
    - destinos: Dicionário {nome: (lon, lat)} com todos os destinos.
    - labels_clusters: Dicionário {nome: cluster_id} que mapeia destinos a clusters.
    - czoonoses_coords: Tupla (lat, lon) com as coordenadas do CZO.
    """
    # 1. Configuração inicial do mapa
    map_center = czoonoses_coords
    mapa = folium.Map(location=map_center, zoom_start=12, tiles="CartoDB positron")

    # Gera um conjunto de cores distintas para cada cluster
    num_clusters = len(set(labels_clusters.values()))
    cores = [plt.cm.tab10(i) for i in np.linspace(0, 1, num_clusters)]
    mapa_cores = {i: f'#{int(c[0]*255):02x}{int(c[1]*255):02x}{int(c[2]*255):02x}' for i, c in enumerate(cores)}

    # 2. Desenhar as rotas no mapa
    for cluster_id, (rota, distancia) in rotas_salvas.items():
        if not rota:
            continue

        # Converte a lista de nós da rota em uma lista de coordenadas (lat, lon)
        rota_coords = [(node_coords[node][0], node_coords[node][1]) for node in rota if node in node_coords]
        
        cor_cluster = mapa_cores.get(cluster_id, '#000000') # Preto como cor padrão

        # Cria a linha da rota
        folium.PolyLine(
            locations=rota_coords,
            color=cor_cluster,
            weight=3,
            opacity=0.8,
            popup=f"<b>Cluster {cluster_id + 1}</b><br>Distância: {distancia / 1000:.2f} km"
        ).add_to(mapa)

    # 3. Adicionar os marcadores dos pontos de destino
    for nome, (lon, lat) in destinos.items():
        cluster_id = labels_clusters.get(nome)
        if cluster_id is not None:
            cor_ponto = mapa_cores.get(cluster_id, '#000000')
            folium.CircleMarker(
                location=(lat, lon),
                radius=5,
                color=cor_ponto,
                fill=True,
                fill_color=cor_ponto,
                fill_opacity=1,
                popup=f"<b>{nome}</b><br>Cluster: {cluster_id + 1}"
            ).add_to(mapa)

    # 4. Adicionar o marcador do Centro de Zoonoses
    folium.Marker(
        location=czoonoses_coords,
        popup="<b>Centro de Zoonoses (CZO)</b><br>Início/Fim das Rotas",
        icon=folium.Icon(color='red', icon='star')
    ).add_to(mapa)

    # 5. Salvar o mapa em um arquivo HTML
    nome_arquivo = 'mapa_com_rotas.html'
    mapa.save(nome_arquivo)
    print(f"\nMapa com as rotas foi gerado e salvo como '{nome_arquivo}'")