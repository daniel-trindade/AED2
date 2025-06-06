""""
PARA EXECUÇÃO DESSE PROGRAMA SERÁ NECESSÁRIO A INSTALAÇÃO DE ALGUMAS BIBLIOTECAS:
Você pode instalar direto em sua maquina ou usar um ambiente virtual.
Caso opte por um ambiente virtual, execute os seguintes comandos:
estando dentro da pasta do projeto:
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
"""

from functions import carregar_destinos, obter_dados_estradas, criar_grafo, encontrar_no_mais_proximo, plotar_mapa_natal_com_destinos
from codecarbon import EmissionsTracker

# Iniciando o rastreador de emissões do code carbon
tracker = EmissionsTracker()
tracker.start()

# Carregar destinos do arquivo JSON
destinos = carregar_destinos('db.json')

# Coordenadas do centro de zoonoses
czoonoses = (-5.7532189, -35.2621815)

# Definir limites para extrair dados do OpenStreetMap (bounding box para Natal-RN)
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
print("Plotando mapa natal com destinos...")
plotar_mapa_natal_com_destinos(graph, node_coords, destinos, czoonoses, bounds)

# Código comentado para diagnóstico dos dados carregados
""" 
# Primeiro, verificar os dados carregados:
print("=== DIAGNÓSTICO DOS DADOS ===")
print(f"Destinos carregados: {len(destinos)}")
if destinos:
    print("Primeiros 3 destinos:")
    for i, (nome, coords) in enumerate(list(destinos.items())[:3]):
        print(f"  {nome}: {coords}")

print(f"Centro de zoonoses: {czoonoses}")
print(f"Bounds definido: {bounds}")
print(f"Nós no grafo: {len(node_coords) if node_coords else 0}") 
"""