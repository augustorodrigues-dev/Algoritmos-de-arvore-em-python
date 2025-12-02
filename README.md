# Helldivers: Grafos da Super-Terra v3.4

> **"Pela Democracia Gerenciada!"**

Este é um projeto educacional interativo que utiliza a temática do jogo *Helldivers 2* para ensinar conceitos fundamentais de Teoria dos Grafos e Algoritmos. O sistema simula um mapa galáctico onde o jogador deve usar diferentes algoritmos para resolver problemas de logística, conectividade e navegação entre planetas.

## 📋 Funcionalidades

O projeto conta com 5 fases distintas, cada uma focada em um tipo de grafo e algoritmo específico:

* **Fase 1 (Autômatos):** Busca em Largura (**BFS**) em grafos não-ponderados.
* **Fase 2 (Terminídeos):** Algoritmo de **Dijkstra** para caminhos mínimos em grafos ponderados.
* **Fase 3 (Iluminados):** Busca em Profundidade (**DFS**) para detecção de ciclos em grafos direcionados.
* **Fase 4 (Zona Instável):** Algoritmo de **Bellman-Ford** (visualização de relaxamento de arestas).
* **Fase 5 (Abastecimento):** Árvore Geradora Mínima (**MST**) usando o algoritmo de **Prim**.

### Recursos Extras
* **Visualização Algorítmica:** Animações neon destacam nós visitados, arestas relaxadas e vizinhos em tempo real.
* **Modo Passo a Passo:** Controle total da execução com botão de "Próximo Passo" ou tecla `[Espaço]`.
* **Controle de Velocidade:** Ajuste o delay da animação (de 50ms a 2000ms) via interface.
* **Simulação de Dano:** Pressione `[R]` para destruir rotas aleatórias e visualizar a fragmentação dos componentes conexos.

## 🚀 Instalação e Execução

### Pré-requisitos
* Python 3.10 ou superior.
* Biblioteca `pygame`.

### Passo a Passo

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/helldivers-grafos.git](https://github.com/seu-usuario/helldivers-grafos.git)
    cd helldivers-grafos
    ```

2.  **Crie um ambiente virtual (recomendado):**
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Linux/Mac:
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute o jogo:**
    ```bash
    python main.py
    ```

## 🎮 Controles

| Tecla / Ação | Função |
| :--- | :--- |
| **1 - 5** | Trocar de Fase (BFS, Dijkstra, DFS, Bellman-Ford, MST) |
| **Mouse Esq.** | Selecionar Planetas (Origem e Destino) |
| **B** | Executar BFS (Fase 1) |
| **D** | Executar Dijkstra (Fase 2) |
| **C** | Detectar Ciclos (Fase 3) |
| **F** | Executar Bellman-Ford (Fase 4) |
| **M** | Gerar MST (Fase 5) |
| **P** | Alternar entre modo **Automático** e **Manual** |
| **Espaço** | Avançar um passo (no Modo Manual) |
| **R** | Evento Aleatório (Destrói uma rota) |
| **T** | Mostrar/Esconder Tutorial |
| **ESC** | Sair |

## 📂 Estrutura do Projeto

O código foi refatorado para seguir boas práticas de engenharia de software:

* `main.py`: Loop principal, gerenciamento de eventos e renderização da animação.
* `ui.py`: Desenho da interface, botões, HUD e tutoriais.
* `graph_system.py`: Estrutura de dados do grafo (Lista de Adjacência).
* `levels.py`: Configuração dos mapas (coordenadas e conexões dos 16 planetas).
* `config.py`: Cores, constantes e configurações globais.
* `models.py`: Classes `Planeta` e `Aresta`.
* **Algoritmos:**
    * `bfs.py`: Lógica da Busca em Largura.
    * `dfs.py`: Lógica da Busca em Profundidade.
    * `dijkstra.py`: Lógica do Dijkstra.
    * `bellman_ford.py`: Lógica do Bellman-Ford.
    * `mst.py`: Lógica do algoritmo de Prim.

## 🎨 Assets

O jogo procura por imagens na pasta `assets/`. Caso não as encontre, ele rodará normalmente usando formas geométricas primitivas.
* `assets/background.png`: Imagem de fundo (1280x720).
* `assets/logo.png`: Logo para a tela inicial.

---
*Desenvolvido para fins educacionais.*