# AWS DeepRacer K1999 Offline Optimizer 🏎️💨

Este repositório contém uma aplicação web interativa construída com
**Streamlit** para realizar o pré-processamento offline de pistas do AWS
DeepRacer. A ferramenta aplica o algoritmo de otimização de trajetória
**K1999** e calcula um perfil de velocidade baseado na física de
aderência lateral, gerando as matrizes de coordenadas prontas para serem
inseridas na Função de Recompensa (_Reward Function_).

### 👤 Autores
- **Pedro Victor Venâncio dos Santos** - Desenvolvedor & Pesquisador
- **Francisco Marcelino Almeida de Araújo** - Co-orientador

---

## 🧠 O que este projeto faz?

Quando treinamos um modelo no AWS DeepRacer, a linha central da pista
nem sempre é o caminho mais rápido. Pilotos reais "cortam" as curvas
(_tangenciamento/apex_) para manter a velocidade. Este projeto faz
exatamente esse cálculo matemático de forma offline, evitando gastar
horas de treinamento na nuvem.

O script `app.py` realiza **3 passos fundamentais**:

### 1. Otimização K1999 (O Elástico)

Pega os pontos do centro da pista e aplica um algoritmo iterativo que
funciona como um "elástico", tensionando a linha para que ela fique o
mais reta e curta possível, respeitando uma margem de segurança das
bordas interna e externa.

### 2. Física e Velocidade

Com a nova linha traçada, o código calcula o raio de cada curva e,
usando a fórmula da força centrípeta, define a velocidade máxima sem
derrapagem.

### 3. Lookahead (Frenagem Antecipada)

Analisa os pontos à frente para prever curvas fechadas e reduz a
velocidade gradativamente nas retas anteriores, simulando uma frenagem
real.

### Resultado final

Gera um código Python formatado (`TRACK_DATA`) com coordenadas:

```python
[X, Y, Velocidade]
```

---

## 🏁 Pistas Testadas e Otimizadas

- **Reinvent Base** (Simples) - Pista básica de treinamento
- **Tokyo Training Track** (Complexa) - Múltiplas curvas fechadas
- **2022 Summit Speedway** - Circuito de alta velocidade

### 📊 Resultados Principais

| Métrica | Resultado |
|---------|-----------|
| **Melhor Tempo (Tokyo Track)** | 17.74s com K1999 |
| **Consistência Baseline** | Superior em testes Zero-Shot Transfer |
| **Generalização K1999** | Otimizado para circuitos conhecidos |
| **Cenários Imprevistos** | Treinamento convencional recomendado |

---

## 🗺️ Onde encontrar os arquivos das pistas (.npy)?

👉 https://github.com/aws-deepracer-community/deepracer-race-data/tree/main/raw_data/tracks

---

## ✨ Funcionalidades

- **Otimização Geométrica (K1999)**
- **Velocidade Baseada em Física**
- **Frenagem e Aceleração Inteligentes**
- **Geração Automática de Código**

---

## 🚀 Como Executar

```bash
git clone https://github.com/PedroVenanci0/deepraceroptimization.git
cd deepraceroptimization
```

```bash
python -m venv venv
```

```bash
venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

```bash
streamlit run app.py
```

---

## 🛠️ Como Usar

1.  Upload do `.npy`
2.  Aguarde processamento
3.  Copie o Modelo B

---

## 🤝 Contribuições

Abra Issue ou Pull Request.

---

## 📚 Finalidade

- Aprendizado por Reforço
- Navegação Autônoma
