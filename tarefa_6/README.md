# Roteirização das Praias de Natal com Algoritmo de Kruskal

Este projeto acadêmico, desenvolvido para a disciplina de Algoritmos e Estrutura de Dados do curso de Engenharia da Computação, demonstra a aplicação prática da teoria dos grafos para resolver um problema de otimização do mundo real.

O objetivo foi encontrar a rota mais curta que conecta todas as principais praias da cidade de Natal-RN, utilizando o Algoritmo de Kruskal para gerar uma Árvore Geradora Mínima (MST).

##  Visão Geral

O problema foi modelado da seguinte forma:
- **Vértices**: As praias de Natal.
- **Arestas**: Os caminhos e ruas que conectam as praias.
- **Pesos**: A distância (em metros) de cada caminho.

Utilizando a biblioteca **OSMNX**, a malha viária da cidade foi extraída do OpenStreetMap e, com a ajuda da biblioteca **NetworkX**, foi aplicado o algoritmo de Kruskal para encontrar a rota de menor custo total, que foi então visualizada em um mapa.

## Conceitos Fundamentais

- **Grafos**: Estruturas de dados compostas por vértices e arestas, ideais para modelar redes.
- **Árvore Geradora Mínima (MST)**: Um subconjunto de arestas de um grafo que conecta todos os vértices sem formar ciclos e com a menor soma de pesos possível.
- **Algoritmo de Kruskal**: Um algoritmo "guloso" que constrói uma MST selecionando as arestas de menor peso, desde que não formem ciclos.

## Tecnologias Utilizadas

- **Python 3**: Linguagem de programação principal.
- **Jupyter Notebook**: Ambiente de desenvolvimento interativo.
- **OSMNX**: Para obter dados de mapas e redes viárias do OpenStreetMap.
- **NetworkX**: Para criar, manipular e estudar grafos.
- **Matplotlib**: Para visualizar os dados e gerar o mapa final.
- **GeoPandas**: Utilizado pelo OSMNX para manipulação de dados geoespaciais.

## Como Executar o Projeto

### Pré-requisitos

- Python 3.8 ou superior
- Pip (gerenciador de pacotes do Python)

### Instalação

1.  Clone este repositório para a sua máquina local.
2.  Instale as bibliotecas necessárias:
    ```bash
    pip install jupyter osmnx networkx matplotlib
    ```

### Execução

1.  Navegue até o diretório do projeto pelo terminal.
2.  Inicie o Jupyter Notebook:
    ```bash
    jupyter notebook
    ```
3.  No seu navegador, abra o arquivo `kruskal_natal.ipynb`.
4.  Execute as células de código em sequência, de cima para baixo. A última célula irá gerar e salvar o mapa `rota.jpg`.

## Metodologia do Código

O processo implementado no notebook segue 4 etapas principais:

1.  **Aquisição de Dados**: O mapa viário de Natal é baixado via OSMNX, e as localizações geográficas das praias são extraídas como Pontos de Interesse (POIs).
2.  **Construção do Grafo de Interesse**: Em vez de usar o mapa inteiro da cidade, um grafo menor e completo é construído. Neste grafo, os vértices são apenas as praias, e o peso de cada aresta é a distância real do caminho mais curto entre duas praias na malha viária.
3.  **Cálculo da MST**: O algoritmo de Kruskal (via NetworkX) é aplicado sobre o "grafo de interesse" para encontrar a Árvore Geradora Mínima.
4.  **Visualização**: O resultado é plotado em um mapa, onde a malha viária da cidade aparece ao fundo e a rota otimizada (a MST) é destacada.

## Resultados

O resultado final é um mapa que exibe a rota mais curta (aproximadamente **28 km**) para conectar todas as 17 praias identificadas. A rota é representada pela linha vermelha, que corresponde à Árvore Geradora Mínima.

![Mapa da Rota Otimizada](rota.jpg)

## Autor
