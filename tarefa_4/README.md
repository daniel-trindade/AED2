## Avaliação de algoritmos para o caminho mais curto em grafos urbanos

by <br/>
[Daniel Bruno Trindade da Silva](https://github.com/daniel-trindade) <br/>
[André Luiz Lima Souza](https://github.com/andreluizlimaa)


***
### 1. Introdução

A mobilidade urbana eficiente é um fator determinante para a qualidade dos serviços de emergência, especialmente em grandes centros urbanos. Neste contexto, a escolha de algoritmos de menor caminho pode influenciar diretamente no tempo de resposta de ambulâncias e, por consequência, na eficácia do atendimento médico. Este relatório tem como objetivo avaliar e comparar o desempenho de três algoritmos de cálculo de rotas — Dijkstra tradicional (complexidade O(n²)), Dijkstra com min-heap (melhoria em eficiência), e o algoritmo implementado na biblioteca OSMnx — aplicados a um cenário realista: o deslocamento de ambulâncias partindo do Hospital Walfredo Gurgel, em Natal/RN, com destino aos bairros com maior incidência de acidentes de transito com vítimas.

A análise considera três principais aspectos: (i) desempenho computacional dos algoritmos, em termos de tempo de processamento; (ii) similaridade das rotas geradas, com foco em distância e topologia; e (iii) impacto ambiental estimado, avaliado por meio da pegada de carbono associada às rotas. A partir dessa comparação, busca-se entender qual abordagem oferece melhor equilíbrio entre velocidade de cálculo, precisão nas rotas e sustentabilidade ambiental, contribuindo para o aprimoramento de estratégias logísticas em situações críticas de emergência.

### 2. Metodologia
#### 2.2 Obtenção de informações 
Para a realização deste estudo, foi selecionado como ponto de partida o Hospital Walfredo Gurgel, localizado em Natal/RN. A escolha se justifica pelo fato de o hospital ser a principal referência na cidade para o atendimento de vítimas de acidentes de trânsito, recebendo a maioria dos casos de urgência e emergência da região metropolitana.

Com o objetivo de simular trajetos realistas e representativos do cotidiano do atendimento pré-hospitalar, foram definidos como destinos os cinco bairros de Natal com o maior número de acidentes de trânsito registrados. Essa seleção foi baseada nos dados do [Anuário Estatístico de Acidentes de Trânsito de 2018](https://www2.natal.rn.gov.br/sttu2/paginas/File/estatisticas/Anuario_Estatistico_de_Acidentes_de_Transito_2018.pdf), produzido pela prefeitura da cidade de Natal, o qual foi a fonte de informação mais atual que podemos obter de forma segura.

Os Bairros com maior indice de acidentes foram:
1. Lagoa Nova - 871 acidentes (16,00%)
2. Tirol - 392 acidentes (7,20%)
3. Capim Macio - 376 acidentes (6,91%)
4. Alecrim - 350 acidentes (6,43%)
5. Potengi - 318 acidentes (5,84%)