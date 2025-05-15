# Avaliação Comparativa de Algoritmos de Caminho Mais Curto em Grafos Urbanos

by <br/>
[Daniel Bruno Trindade da Silva](https://github.com/daniel-trindade) <br/>
[André Luiz Lima Souza](https://github.com/andreluizlimaa)

***
## Vídeo de Apresentação

<a href="https://youtu.be/_fylSRF4SX8" target="_blank">
  <img src="https://upload.wikimedia.org/wikipedia/commons/b/b8/YouTube_Logo_2017.svg" alt="YouTube" width="200"/>
</a>

***
## 1. Introdução

A mobilidade urbana eficiente é um fator determinante para a qualidade dos serviços de emergência, especialmente em grandes centros urbanos. Neste contexto, a escolha de algoritmos de menor caminho pode influenciar diretamente no tempo de resposta de ambulâncias e, por consequência, na eficácia do atendimento médico. Este relatório tem como objetivo avaliar e comparar o desempenho de três algoritmos de cálculo de rotas — Dijkstra tradicional (complexidade O(n²)), Dijkstra com min-heap (melhoria em eficiência), e o algoritmo implementado na biblioteca OSMnx — aplicados a um cenário realista: o deslocamento de ambulâncias partindo do Hospital Walfredo Gurgel, em Natal/RN, com destino aos bairros com maior incidência de acidentes de transito com vítimas.

A análise considera três principais aspectos: (i) desempenho computacional dos algoritmos, em termos de tempo de processamento; (ii) similaridade das rotas geradas, com foco em distância e topologia; e (iii) impacto ambiental estimado, avaliado por meio da pegada de carbono associada às rotas. A partir dessa comparação, busca-se entender qual abordagem oferece melhor equilíbrio entre velocidade de cálculo, precisão nas rotas e sustentabilidade ambiental, contribuindo para o aprimoramento de estratégias logísticas em situações críticas de emergência.

## 2. Metodologia
### 2.2 Obtenção de informações 
Para a realização deste estudo, foi selecionado como ponto de partida o Hospital Walfredo Gurgel, localizado em Natal/RN. A escolha se justifica pelo fato de o hospital ser a principal referência na cidade para o atendimento de vítimas de acidentes de trânsito, recebendo a maioria dos casos de urgência e emergência da região metropolitana.

Com o objetivo de simular trajetos realistas e representativos do cotidiano do atendimento das ambulancias de socorro, foram definidos como destinos os cinco bairros de Natal com o maior número de acidentes de trânsito registrados. Essa seleção foi baseada nos dados do [Anuário Estatístico de Acidentes de Trânsito de 2018](https://www2.natal.rn.gov.br/sttu2/paginas/File/estatisticas/Anuario_Estatistico_de_Acidentes_de_Transito_2018.pdf), produzido pela prefeitura da cidade de Natal, o qual foi a fonte de informação mais atual que podemos obter de forma segura.

Os Bairros com maior indice de acidentes em 2018 foram:
1. Lagoa Nova - 871 acidentes (16,00%)
2. Tirol - 392 acidentes (7,20%)
3. Capim Macio - 376 acidentes (6,91%)
4. Alecrim - 350 acidentes (6,43%)
5. Potengi - 318 acidentes (5,84%)

Assim, o presente estudo utilizará os algoritmos selecionados para calcular as rotas mais curtas partindo do Hospital Walfredo Gurgel em direção a cada um dos cinco bairros mencionados. O objetivo é simular cenários de deslocamento de ambulâncias e, com isso, analisar o desempenho e a eficiência de cada abordagem na geração dessas rotas.

### 2.3 Código
Para realizar a comparação de desempenho entre os algoritmos, foram desenvolvidos três códigos distintos, cada um implementando uma abordagem específica de cálculo de menor caminho:

- O primeiro, [`cmc_OSMnx.py`](/tarefa_4/cmc_OSMnx.py), utiliza a biblioteca **OSMnx**, que permite acessar e manipular diretamente dados do OpenStreetMap. Essa ferramenta fornece uma interface de alto nível para construção de grafos urbanos e cálculo de rotas com base em atributos reais da malha viária.

- O segundo, [`cmc_dijkstra_trad.py`](/tarefa_4/cmc_dijkstra_trad.py), implementa o algoritmo de **Dijkstra tradicional**, utilizando uma estrutura simples (como uma lista) para armazenar os vértices ainda não visitados. Isso resulta em uma complexidade de tempo O(n²), o que pode ser ineficiente para grafos grandes.

- Por fim, o terceiro código, [`cmc_dijkstra_min_heap.py`](/tarefa_4/cmc_dijkstra_min_heap.py), também implementa o algoritmo de **Dijkstra**, mas substitui a busca linear por uma **fila de prioridade** (_min-heap_), otimizando significativamente o desempenho. Essa estrutura reduz o tempo de seleção do próximo nó com menor custo para O(log n), tornando o algoritmo mais eficiente.

Em todos os três códigos, foi utilizada a biblioteca [`codecarbon`](https://codecarbon.io/) para estimar a **pegada de carbono** gerada durante a execução dos algoritmos. Essa ferramenta permite monitorar o consumo energético do processo e calcular sua emissão estimada de CO₂ equivalente, fornecendo uma métrica adicional para comparar a **eficiência ambiental** de cada abordagem.

## 3. Resultados
Foram traçadas rotas tendo como origem o hospital e como destino cada um dos bairos listados, para tal tivemos os seguintes resultados:

### 3.1 - Mapas

- **OSMnx**
![plot gerado pelo OSMnx](/tarefa_4/imgs/plot_osmnx.png)

- **Dijkstra (Tradicional e Min-Heap)**
![plt gerado pelo Dijkstra](/tarefa_4/imgs/plot_dijkstra_trad.png)

- **Erro de rota para potengi do OSMnx**
![Erro osmnx](/tarefa_4/imgs/erro_osmnx.png)


### 3.2 - Distancia Percorrida em metros

|             | OSMnx       | Dijkstra Tradicional | Dijkstra Min-Heap |
|-------------|-------------|----------------------|-------------------|
| Lagoa Nova  | 5362,19     | 5854,68              | 5854,68           |
| Tirol       | 2945,06     | 3135,74              | 3135,74           |
| Capim Macio | 5901,37     | 7314,65              | 7314,65           |
| Alecrim     | 3819,98     | 3906,83              | 3906,83           |
| Potengi     | 16096,24    | 11982,82             | 11982,82          |


### 3.3 - Pegada de Carbono

![Resultados do codecarbom](/tarefa_4/imgs/pegada_de_carbono.png)


## Análise dos Resultados

### Rotas

A partir dos resultados obtidos na criação de rotas observa-se que, os algoritmos Dijkstra (tradicional e com min-heap) produziram rotas idênticas, o que confirma que ambas as implementações geram os mesmos caminhos, diferindo apenas na estrutura interna e eficiência de execução.

Por outro lado, o algoritmo da biblioteca OSMnx gerou rotas com distâncias ligeiramente menores em quatro dos cinco casos, o que sugere que ele pode estar considerando informações adicionais do grafo, como restrições de tráfego, sentidos das vias e configurações mais detalhadas da rede viária. No entanto, no trajeto entre o Hospital Walfredo Gurgel e o bairro Potengi, o OSMnx apresentou um comportamento inadequado: ele evitou utilizar a ponte Presidente Costa e Silva, optando consistentemente pela ponte Newton Navarro, mesmo quando se tentou forçar a rota com um ponto intermediário sobre a ponte desejada. O algoritmo ainda retornava pela ponte Newton Navarro até a Costa e Silva e só então seguia em direção ao bairro Potengi, o que resultou em um aumento significativo da distância total percorrida.

Ainda com relação ao comportamento inadequado do OSMnx na tentativa de criar a rota para o bairro do Potengi, acreditamos que o mesmo possa ter obtido informações de que a ponte está inoperante (devido a reformas) pela API, pois ao consultar a ponte pelo site do _OpenStreetMap_ observamos o seguinte comentário:

>"Bloqueio viário em razão das obras na Av. Felizardo Firmino Moura, com restrição de acesso, conforme explicado em site da Prefeitura Municipal: https://natal.rn.gov.br/news/post2/38197"

Como ambos os algoritmos utilizam dados do _OpenStreetMap_, é possível que a API empregada na obtenção das informações para o algoritmo de Dijkstra esteja desatualizada ou desconsidere detalhes específicos da rede viária, como a acessibilidade ou restrições associadas à ponte Presidente Costa e Silva.

### Pegada de Carbono

Com relação a pegada de corbono, o algoritmo Dijkstra Tradicional apresenta as maiores emissões de carbono, significativamente superiores às demais abordagens. O osmnx tem a menor emissão, seguido pelo Dijkstra min-heap, que é 6,75 vezes mais eficiente em carbono do que o dijkstra Tradicional. Isso mostra como a utilização de uma estrutura de dados menos eficiente pode causar um grande impacto no desempenho de uma aplicação.

No consumo de energia, mais uma vez, o Dijkstra Tradicional consome muito mais energia que os outros, sendo cerca de 17 vezes mais alto que o consumo do osmnx e 7,4 vezes mais alto que o Dijkstra min-heap. O osmnx é o mais eficiente nesse aspecto.

O tempo de execução do dijkstra Tradicional é extremamente alto, quase 7 vezes mais demorado que o Dijkstra min-heap e quase 16 vezes mais demorado que o osmnx. O osmnx é o algoritmo mais rápido.

De forma geral o osmnx se destaca como a solução mais eficiente em todas as frentes: menor tempo de execução, menor consumo energético e menor pegada de carbono. O dijkstra Tradicional, apesar de conhecido, é significativamente menos eficiente, sendo o pior em todas as métricas analisadas. O dijkstra Min-heap representa um bom meio-termo entre desempenho e sustentabilidade, com consumo energético e emissões moderados, e tempo de execução aceitável.


## Conclusão
A avaliação dos algoritmos de menor caminho aplicada ao contexto urbano da cidade de Natal/RN revelou diferenças significativas tanto em desempenho computacional quanto em sustentabilidade ambiental. A análise demonstrou que, embora o algoritmo de Dijkstra tradicional gere rotas corretas, sua implementação com complexidade O(n²) é altamente ineficiente, apresentando o maior tempo de execução, maior consumo de energia e maior emissão de carbono entre os três métodos avaliados.

A versão otimizada com estrutura de min-heap se mostrou uma alternativa viável, mantendo a precisão das rotas e reduzindo consideravelmente o impacto ambiental e o tempo de processamento, representando assim um bom equilíbrio entre desempenho e eficiência energética.

Por fim, o algoritmo da biblioteca OSMnx se destacou como a solução mais eficiente e sustentável. Além de ser o mais rápido, também apresentou o menor consumo energético e a menor pegada de carbono. Apesar de uma inconsistência pontual na criação da rota para o bairro Potengi — provavelmente causada por dados de tráfego atualizados indicando a interdição de uma ponte —, o OSMnx demonstrou considerar aspectos mais complexos da malha viária, como restrições temporárias e condições reais das vias, o que o torna uma opção robusta para aplicações em cenários urbanos dinâmicos.

Dessa forma, considerando tanto os aspectos técnicos quanto ambientais, o OSMnx é a abordagem mais recomendada para o cálculo de rotas em sistemas de apoio à mobilidade urbana em situações críticas, como o deslocamento de ambulâncias, contribuindo não apenas para a agilidade do atendimento, mas também para a redução do impacto ambiental dessas operações.



