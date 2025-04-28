import json
import networkx as nx
import itertools
import matplotlib.pyplot as plt

# Carregar o JSON
with open('comidas_db.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Criar o grafo
G = nx.Graph()

# Construir o grafo
for receita, categorias in data.items():
    ingredientes_na_receita = []

    # Para cada categoria, adiciona o ingrediente e o tipo
    for tipo, ingredientes in categorias.items():
        for ingrediente in ingredientes:
            if not G.has_node(ingrediente):
                G.add_node(ingrediente, tipo=tipo)
            ingredientes_na_receita.append(ingrediente)
    
    # Conectar todos os ingredientes entre si na mesma receita
    for ing1, ing2 in itertools.combinations(ingredientes_na_receita, 2):
        if G.has_edge(ing1, ing2):
            G[ing1][ing2]["peso"] += 1
        else:
            G.add_edge(ing1, ing2, peso=1)

assortatividade = nx.attribute_assortativity_coefficient(G, 'tipo')
print(f"Assortatividade por tipo de ingrediente: {assortatividade:.4f}")

# Agora vamos plotar
plt.figure(figsize=(22, 22))  # Deixar o gráfico grande

# Layout
pos = nx.spring_layout(G, seed=42)

# Nova paleta suave
tipo_to_color = {
    "carboidrato": "#FFB347",    # laranja suave
    "proteína": "#FF6961",       # vermelho salmão
    "gordura": "#B19CD9",        # lilás claro
    "vegetal": "#77DD77",        # verde menta
    "fruta": "#FFD1DC",          # rosa bebê
    "laticínio": "#AEC6CF",      # azul claro
    "tempero": "#FDFD96",        # amarelo pastel
    "outro": "#D3D3D3"           # cinza claro
}

# Cor de cada nó
node_colors = []
node_sizes = []
for node in G.nodes:
    tipo = G.nodes[node].get('tipo', 'outro')
    node_colors.append(tipo_to_color.get(tipo, "#D3D3D3"))
    
    grau = G.degree(node)
    node_sizes.append(200 + grau * 50)  # Tamanho proporcional ao grau

# Desenhar
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, edgecolors='black')
nx.draw_networkx_edges(G, pos, width=1, alpha=0.4)
nx.draw_networkx_labels(G, pos, font_size=8)

# Legenda
import matplotlib.patches as mpatches
handles = [mpatches.Patch(color=cor, label=tipo) for tipo, cor in tipo_to_color.items()]
plt.legend(handles=handles, loc='upper right', fontsize=12)

plt.axis('off')
plt.title('Grafo de Co-ocorrência de Ingredientes', fontsize=22)
plt.show()
