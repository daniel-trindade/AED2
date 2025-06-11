# Otimização Logística para Vigilância em Saúde: Uma Abordagem Comparativa de Algoritmos de Menor Caminho em Grafos.

by <br/>
[Daniel Bruno Trindade da Silva](https://github.com/daniel-trindade) <br/>
[Maria Eduarda Lima da Luz](https://github.com/marialluz) <br/>
[André Luiz Lima Souza](https://github.com/andreluizlimaa)

***

## Vídeo de Apresentação

<a href="https://youtu.be/6qA9rjIAEvk" target="_blank">
  <img src="https://upload.wikimedia.org/wikipedia/commons/b/b8/YouTube_Logo_2017.svg" alt="YouTube" width="150"/>
</a>

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
### Mapas com rotas
#### A* com Clustering - 🔗  [Link para versão WEB](/tarefa_5/rotas_dos_algoritmos_html/mapa_com_rotas_a_star.html)
![A* com Clustering](/tarefa_5/imgs/rotas_a_star.png)
#### A* Random (sem clustering) 🔗  [Link para versão WEB](/tarefa_5/rotas_dos_algoritmos_html/rotas_operadores_a_star_random.html)
![A* Random (sem clustering)](/tarefa_5/imgs/rotas_a_star_random.png)

#### Dijkstra Tradicional 🔗  [Link para versão WEB](/tarefa_5/rotas_dos_algoritmos_html/mapa_com_rotas_dijkstra.html)
![Dijkstra Tradicional](/tarefa_5/imgs/rotas_dijkstra_trad.png)

#### Dijkstra MinHeap 🔗  [Link para versão WEB](/tarefa_5/rotas_dos_algoritmos_html/mapa_com_rotas_min_heap.html)
![Dijkstra MinHeap ](/tarefa_5/imgs/rotas_dijkstra_min_heap.png)

### Distâncias Percorridas 
| Algoritmo                   | Distância Total (km) | Nós Percorridos |
|----------------------------|----------------------|------------------|
| Dijkstra MinHeap           | 291.80               | 10.077           |
| A*                         | 291.80               | 10.077           |
| Dijkstra Tradicional       | ∞                    | 5.835            |
| A* Random (sem clustering) | 778.15               | 22.060           |

### Pegadas de Carbono Computacional
![Gráficos de Pegada de Carbono](/tarefa_5/imgs/comparativo%20emissao%20de%20carbono.png)

## 4. Analise dos resultados

### Comparação dos algoritmos

O A* Random (sem clustering) percorreu uma distância significativamente maior (778.15 km) e processou o maior número de nós (22.060) — mais que o dobro dos algoritmos baseados em clusters. Apesar disso, foi o mais rápido (11.06 s) e com menor impacto ambiental, sugerindo que sua estratégia de roteamento aleatório com heurística é altamente eficaz em encontrar soluções rápidas mesmo com mais dados.

Por outro lado, os métodos Dijkstra MinHeap e A* seguiram as mesmas rotas (291.8 km e 10.077 nós), dado que ambos foram aplicados com o mesmo particionamento (clusters). O A\* foi mais eficiente que o Dijkstra em todos os aspectos, com menos CO₂ emitido, menos energia consumida e menor tempo de execução.

O Dijkstra Tradicional, além de ter processado menos nós (5.835), apresentou tempo de execução extremamente elevado (2765.93 s) e altos valores absolutos de consumo e emissão, com falha no cálculo da distância (valor infinito). Isso inviabiliza sua comparação por km e evidencia a ineficiência do algoritmo na ausência de otimizações estruturais, como filas de prioridade.



## 5. Conclusões
Este estudo se propôs a desenvolver e avaliar uma solução de otimização logística para as equipes do Centro de Controle de Zoonoses (CCZ) de Natal, comparando a eficácia dos algoritmos A*, Dijkstra com Min-Heap e Dijkstra tradicional. A metodologia adotada, que combinou a setorização dos pontos de coleta com o algoritmo K-Means antes da otimização das rotas, provou ser um passo fundamental e de alto impacto. Os resultados demonstraram que essa estratégia reduziu a distância total percorrida em mais de 60% em comparação com uma abordagem não setorizada. Na análise comparativa, o algoritmo A* se consolidou como a solução mais equilibrada, pois não apenas encontrou a rota ótima de 291.80 km — em paridade com o Dijkstra Min-Heap —, mas o fez com maior eficiência computacional e menor pegada de carbono. Em contrapartida, a implementação do Dijkstra tradicional se mostrou completamente inviável, falhando em encontrar uma solução e consumindo recursos computacionais e ambientais em uma ordem de magnitude centenas de vezes superior, reforçando a necessidade de estruturas de dados otimizadas para problemas de grafos do mundo real.

As conclusões deste trabalho oferecem uma contribuição prática e de aplicação direta para o CCZ de Natal, fornecendo um modelo validado que pode ser implementado para gerar economia significativa de recursos, como tempo e combustível, e, consequentemente, ampliar a eficácia das ações de vigilância epidemiológica.