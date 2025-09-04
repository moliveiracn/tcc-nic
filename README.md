# TCC - Impacto Econômico de Hobbies Femininos

Este projeto investiga a contradição entre a desvalorização patriarcal de hobbies femininos e seu real impacto econômico global. Foca em estudos de caso como BTS, Lady Gaga e jogos digitais com grande apelo ao público feminino.

## 🎯 Objetivo
Analisar como atividades consideradas "fúteis" por normas patriarcais — como fanatismo por artistas pop ou jogos femininos — geram receita bilionária, moldando indústrias culturais e impactando economias locais e globais.

---

## 📁 Estrutura do Projeto

```
tcc-nic-main/
│
├── config.py               # Caminhos padrão (input/output)
├── analyze_processed_data.py # Análise de dados de planilhas (ocupação hoteleira etc)
├── artists_info.py         # Coleta dados brutos de artistas (Spotify, Last.fm, etc.)
├── flights_parser.py       # Coleta dados brutos de voos
├── preprocess_data.py      # Orquestra a coleta, processamento e salvamento de todos os dados
├── reddit_scraper.py       # Coleta dados brutos de comentários do Reddit
├── README.md               # Este arquivo
├── data/
│   ├── raw/                # Dados brutos (ex: Excel, CSVs, asc)
│   └── processed/          # Dados limpos/tratados   
└── output/
    └── graphs/             # Gráficos gerados automaticamente
```
---

## 🧰 Requisitos
- Python 3.11 ou superior

Crie e ative um ambiente virtual antes de instalar as dependências:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

---

## Variáveis de Ambiente

Alguns scripts requerem credenciais fornecidas via variáveis de ambiente:

- `SPOTIFY_CLIENT_ID` e `SPOTIFY_CLIENT_SECRET` – acesso à API do Spotify
- `LASTFM_API_KEY` – chave da API do Last.fm
- `REDDIT_CID`, `REDDIT_CSECRET` e `REDDIT_USER_AGENT` – credenciais da API do Reddit

Configure-as no terminal antes de executar os scripts:

```bash
export SPOTIFY_CLIENT_ID="..."
export SPOTIFY_CLIENT_SECRET="..."
export LASTFM_API_KEY="..."
export REDDIT_CID="..."
export REDDIT_CSECRET="..."
export REDDIT_USER_AGENT="..."
```

---

## ⚙️ Uso

Todos os scripts usam `config.py` para definir caminhos. Por exemplo:

```python
from config import DATA_RAW, GRAPH_OUTPUT
df = pd.read_csv(DATA_RAW / "exemplo.csv")
df.plot().savefig(GRAPH_OUTPUT / "grafico1.png")
```

### Executar módulos

O script `run.py` orquestra os diferentes componentes do projeto. Use a opção
`--module` para escolher qual parte executar:

```bash
# Coleta, processa e salva todos os dados brutos (artistas, voos, reddit, excel)
python run.py --module preprocess

# Gera gráficos e estatísticas a partir dos dados processados
python run.py --module excel --metrics "Visitors" "Average Room Rate"
```

Argumentos úteis:

- `excel`: `--metrics` recebe uma lista de indicadores específicos para analisar
  (por padrão, todos são utilizados).

---

## 📊 Fontes de Dados

- LVCVA (Las Vegas Convention & Visitors Authority)
- Spotify / ChartMasters / Billboard
- Reddit (r/MakeupAddiction, r/LadyGaga etc)
- The Hollywood Reporter, US BTS Army

---

## 📚 Base Teórica

- Feminismo interseccional (Butler, Connell, Kimmel)
- Economia cultural (Bourdieu, Pine & Gilmore)
- Estudos de fandom e gênero (Pascoe, Kaufman, Green)

---
