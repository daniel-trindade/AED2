# Otimização Logística para Vigilância em Saúde: Uma Abordagem Comparativa de Algoritmos de Menor Caminho em Grafos.

by <br/>
[Daniel Bruno Trindade da Silva](https://github.com/daniel-trindade) <br/>
[Maria Eduarda Lima da Luz](https://github.com/marialluz) <br/>
[André Luiz Lima Souza](https://github.com/andreluizlimaa)

***

## 1. Introdução
A efetividade da vigilância epidemiológica contra arboviroses como dengue, Zika e chikungunya, que se apoia em ferramentas como as ovitrampas para o monitoramento do Aedes aegypti, é intrinsecamente dependente da eficiência logística. Este desafio se materializa no cenário operacional do Centro de Controle de Zoonoses (CCZ) de Natal, onde a gestão da manutenção de 65 armadilhas por 10 funcionários constitui um complexo Problema de Roteirização de Veículos (VRP). O objetivo primordial é minimizar os custos operacionais, como tempo e distância percorrida, pois uma abordagem não otimizada resulta em desperdício de recursos, sobrecarga das equipes e comprometimento direto dos resultados do programa de saúde pública.

Diante deste cenário, este trabalho, propõe-se a desenvolver e avaliar uma solução sistemática para este problema. O objetivo principal é determinar as rotas mais eficientes para as equipes do CCZ, tratando a cidade de Natal como um grafo onde os pontos de coleta são os vértices a serem visitados. Para tal, este estudo abordará quatro objetivos específicos:


1. Desenvolver uma estratégia de setorização para distribuir de forma equilibrada os 65 pontos de coleta entre os 10 funcionários disponíveis.
2. Aplicar e comparar o desempenho de três algoritmos clássicos de busca de menor caminho:
   1. Dijkstra tradicional;
   2. Dijkstra (min-heap);
   3. A estrela (A*)
3. Avaliar os algoritmos não apenas por métricas de desempenho tradicionais (como tempo de execução e custo da rota), mas também por sua pegada de carbono computacional, utilizando a biblioteca CodeCarbon para introduzir uma análise de sustentabilidade.
4. Validar a eficácia da estratégia de setorização proposta através da comparação dos resultados com uma execução do algoritmo A∗ em um cenário sem estratégia, ou seja, não setorizado, servindo como linha de base (baseline).

Ao final, espera-se que este estudo não apenas forneça uma solução prática e otimizada para o CCZ de Natal, mas também contribua com uma análise comparativa sobre a aplicabilidade e eficiência de diferentes algoritmos de busca em um problema real de logística, destacando os trade-offs entre performance e impacto ambiental computacional.

## 2. Metodologia
Para alcançar os objetivos propostos, a metodologia deste estudo foi dividida em três fases principais e sequenciais: (i) setorização dos pontos de coleta através de clusterização; (ii) aplicação de algoritmos de busca para a otimização das rotas em cada setor; e (iii) coleta e análise de métricas de desempenho e impacto ambiental. Cada etapa é detalhada a seguir.

### 2.1. Estratégia de Setorização com K-Means
Dada a complexidade de otimizar simultaneamente as rotas para 10 agentes em 65 pontos distintos, a primeira etapa consistiu em simplificar o Problema de Roteirização de Veículos (VRP) através de uma abordagem de "dividir para conquistar". Para isso, foi desenvolvida uma estratégia de setorização para distribuir os 65 pontos de coleta de forma lógica e geográfica entre os 10 funcionários disponíveis.

Utilizou-se o algoritmo de clusterização _K-Means_ para agrupar os 65 pontos de coleta, baseando-se em suas coordenadas geográficas, em 10 clusters (sub-áreas) distintos. O _K-Means_ foi escolhido por sua eficiência em particionar dados em um número pré-definido de grupos (k=10), minimizando a distância intra-cluster. O resultado deste processo foi a atribuição de um conjunto exclusivo de pontos de coleta para cada um dos 10 agentes, transformando um problema complexo em 10 subproblemas menores e independentes.

A setorização feita pelo _K-Means_ resultou na seguinte distribuição dos pontos de coleta:

![Pontos de coleta Clusterizados](/tarefa_5/imgs/mapa%20com%20pontos%20divididos%20por%20clusters.jpg)

### 2.2. Implementação e Execução dos Algoritmos de Otimização
Com os clusters definidos, a fase seguinte focou em resolver o Problema do Caixeiro Viajante (PCV) para cada um dos 10 subconjuntos de pontos. Para cada agente, a rota deveria obrigatoriamente iniciar no Centro de Controle de Zoonoses (CCZ), visitar todos os pontos de coleta designados em seu cluster e, por fim, retornar ao CCZ.

Para encontrar o caminho mais curto em cada sub-rota, foram implementados e executados três algoritmos distintos, permitindo uma análise comparativa:

- Dijkstra (Tradicional): Uma implementação clássica do algoritmo, que encontra o caminho mais curto entre um nó inicial e todos os outros nós no grafo.

- Dijkstra com Min-Heap: Uma variação otimizada do Dijkstra que utiliza uma estrutura de dados de fila de prioridade (min-heap) para selecionar o próximo vértice a ser visitado, resultando em maior performance computacional.

- A-Star (A∗): Um algoritmo de busca informada que utiliza uma função heurística para estimar o custo do caminho até o destino, guiando a busca de forma mais inteligente e, potencialmente, mais rápida que os métodos não informados.

A implementação dos algoritmos pode ser encontrada no arquivo [routes_functions.py](/tarefa_5/routes_functions.py).

### 2.3. Coleta de Métricas para Análise Comparativa
A fim de realizar uma comparação robusta entre os três algoritmos, foram definidas e coletadas duas métricas principais para cada rota gerada:

- Distância Total da Rota: O custo principal da solução, medido em quilômetros (km). Esta métrica avalia a eficiência da rota gerada em termos de deslocamento físico.

- Pegada de Carbono Computacional: Para avaliar o impacto ambiental do processamento, a execução de cada algoritmo foi monitorada pela biblioteca Python codecarbon. Esta ferramenta estima as emissões de CO2 geradas pelo consumo de energia do hardware durante o tempo de execução, fornecendo uma métrica de sustentabilidade computacional.

Ao final desta etapa, os resultados obtidos — distâncias das rotas e suas respectivas pegadas de carbono — foram compilados para permitir uma análise detalhada sobre qual algoritmo oferece a melhor combinação de eficiência de rota, desempenho computacional e sustentabilidade para o problema proposto.

## 3. Resultados

### Distancias Percoridas 

### Pegadas de Carbono Computacional
![Gráficos de Pegada de Carbono](/tarefa_5/imgs/comparativo%20emissao%20de%20carbono.png)


## 4. Analise dos resultados

## 5. Conclusões