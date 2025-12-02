# Helldivers: Grafos da Super-Terra v2.0

**Pela Democracia Gerenciada!** Este é um projeto educacional interativo que utiliza a temática do jogo *Helldivers* para ensinar conceitos fundamentais de Teoria dos Grafos e Algoritmos.

## 📋 Sobre o Projeto

O sistema simula um mapa galáctico onde o jogador deve usar diferentes algoritmos para resolver problemas de logística e conectividade entre planetas. O projeto foi refatorado para seguir boas práticas de engenharia de software, dividindo responsabilidades em múltiplos módulos.

### Funcionalidades e Algoritmos
* **Fase 1 (Autômatos):** Grafos não-direcionados e não-ponderados.
    * *Algoritmo:* BFS (Busca em Largura) para travessia.
* **Fase 2 (Terminídeos):** Grafos ponderados (com pesos nas rotas).
    * *Algoritmo:* Dijkstra para encontrar o caminho mais curto.
* **Fase 3 (Iluminados):** Dígrafos (Grafos direcionados).
    * *Algoritmo:* DFS (Busca em Profundidade) para detecção de ciclos.
* **Dinâmica Extra:** Detecção de Componentes Conexos (desconexão do grafo ao remover rotas).

## 🚀 Instalação e Execução

### Pré-requisitos
* Python 3.10 ou superior.
* Pip (gerenciador de pacotes).

### Passo a Passo

1.  **Clone ou baixe o repositório.**

2.  **Crie um ambiente virtual (opcional, mas recomendado):**
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

| Tecla | Ação |
| :--- | :--- |
| **1, 2, 3** | Trocar de Fase (Inimigo/Algoritmo) |
| **B** | Executar BFS (Fase 1 - Requer origem selecionada) |
| **D** | Executar Dijkstra (Fase 2 - Requer origem e destino) |
| **C** | Detectar Ciclos (Fase 3 - Varredura automática) |
| **R** | Evento Aleatório (Destrói uma rota e analisa a rede) |
| **T** | Mostrar/Esconder Tutorial |
| **ESC** | Sair do Jogo |
| **Mouse** | Clique esquerdo para selecionar planetas (Origem/Destino) |

## 📂 Estrutura do Projeto

O código foi organizado nos seguintes módulos:

* `main.py`: Ponto de entrada. Gerencia o loop principal do jogo e eventos.
* `config.py`: Constantes globais, configurações de tela e paleta de cores.
* `models.py`: Classes de dados básicas (`Planeta`, `Aresta`).
* `graph_system.py`: Lógica pesada. Contém a estrutura de dados do grafo e implementações dos algoritmos (BFS, Dijkstra, DFS).
* `levels.py`: Construtores dos mapas específicos para cada fase.
* `ui.py`: Gerenciamento de interface, renderização de textos e HUD.

## 🎨 Assets (Opcional)

Para a experiência completa, crie uma pasta chamada `assets` na raiz do projeto e adicione:
* `background.png`: Imagem de fundo (1280x720 recomendado).
* `logo.png`: Logotipo para a tela inicial.

*Caso as imagens não existam, o jogo rodará normalmente com fundo preto e sem logo.*

---
*Desenvolvido para fins educacionais. Super-Terra conta com você!*