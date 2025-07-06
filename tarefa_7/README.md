# Visualização e Avaliação de Métricas de Centralidade em Grafos Utilizando Gephi



by <br/>
[Daniel Bruno Trindade da Silva](https://github.com/daniel-trindade) <br/>
[Maria Eduarda Lima da Luz](https://github.com/marialluz) <br/>

***

## Vídeo de Apresentação

<a href="https://youtu.be/6qA9rjIAEvk" target="_blank">
  <img src="https://upload.wikimedia.org/wikipedia/commons/b/b8/YouTube_Logo_2017.svg" alt="YouTube" width="150"/>
</a>

***

A análise de redes complexas tem se tornado uma ferramenta essencial em diversas áreas do conhecimento. Os grafos permitem modelar e estudar sistemas onde as conexões entre elementos são tão relevantes quanto os próprios elementos.

Neste contexto, as métricas de centralidade são fundamentais para identificar os nós mais importantes ou influentes dentro de uma rede. Métricas como grau (degree), centralidade de proximidade (closeness centrality), centralidade de intermediação (betweenness centrality) e centralidade por autovetor (eigenvector centrality) fornecem diferentes perspectivas sobre a posição e a função estrutural de cada nó.

Este trabalho tem como objetivo realizar a análise de uma rede previamente construída, utilizando a ferramenta Gephi para gerar visualizações que destaquem as principais características estruturais da rede. Os tamanhos dos vértices serão proporcionais ao número de vizinhos (grau), enquanto as cores representarão diferentes métricas de centralidade. Além disso, será adotado um layout que facilite a percepção visual dessas variações, permitindo uma interpretação intuitiva e informativa da rede.

## Metodologia


### Processamento e Modelagem de Dados

Os dados que foram utilizados foram fornecidos pelo professor responsável pela disciplina. São o  [GraphTest_nodes](./Base%20de%20dados/GraphTest_nodes.txt)  que possui as informações pertinentes aos vertices e [GraphTest_edges](./Base%20de%20dados/GraphTest_edges.txt) que possui as informações pertinentes as arestas.

Para a etapa de processamento e modelagem dos dados, foi utilizado um [script Python](./Final_Project.ipynb) que emprega as bibliotecas pandas e NetworkX. 

Este script lê os arquivos, constroi o grafo, realiza um pré-processamento para tratar valores ausentes ou não numéricos e ao final prepara e exporta o grafo em um arquivo de formato GEXF que mais tarde seria necessário para gerar as visualizações no **Gephi**.

### Analise e Visualização da Rede

De posse do grafo gerado, utilizamos o software **Gephi**, uma ferramenta de código aberto amplamente utilizada para exploração e representação de grafos e redes complexas.

Inicialmente, a rede foi importada para o **Gephi**, onde foram aplicadas as métricas de centralidade disponíveis no módulo de estatísticas. Para este estudo, escolheu-se representar visualmente os nós com base em duas dimensões principais:

- **Tamanho dos vértices:** definido de forma proporcional ao grau de cada nó, ou seja, ao número de vizinhos diretamente conectados a ele. Essa abordagem facilita a identificação dos nós com maior conectividade local.

- **Cores dos vértices:** Em cada uma das visualizaçõpes são atribuidas atribuídas com base em uma métrica de centralidade global (Closeness, Betweenness, Degrees ou Eigenvector Centrality). Utilizou-se uma escala de cores contínua do azul ao vermelho, passando pelo amarelo, conforme expresso a seguir:

    - **Azul** representa os nós com menor valor na métrica escolhida;
    - **Amarelo** representa valores intermediários;
    - **Vermelho** representa os nós com os maiores valores, ou seja, os mais influentes de acordo com a centralidade analisada.

Para o posicionamento espacial dos nós na visualização, foi utilizado o layout ForceAtlas 2, um algoritmo de distribuição de grafos baseado em forças físicas. Esse layout é especialmente eficaz para evidenciar a estrutura da rede, agrupando vértices densamente conectados e separando regiões menos conectadas. Além disso, ele contribui para a percepção visual das variações de cor e tamanho, o que facilita a interpretação das métricas aplicadas.

Todas as imagens geradas foram exportadas diretamente do _Gephi_ após a aplicação dos layouts e ajustes visuais, como espessura das arestas, proporção dos nós e paleta de cores adequada.

### K-cores e K-shels



