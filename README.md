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
├── analyze_excel.py        # Análise de dados de planilhas (ocupação hoteleira etc)
├── artists_info.py         # Dados e estatísticas de artistas como BTS
├── flights_parser.py       # Parser de dados de voos
├── reddit_scraper.py       # Coleta comentários e dados temáticos do Reddit
├── README.md               # Este arquivo
├── data/
│   ├── raw/                # Dados brutos (ex: Excel, CSVs, asc)
│   └── processed/          # Dados limpos/tratados
└── output/
    └── graphs/             # Gráficos gerados automaticamente
```

---

## 🧰 Requisitos
Instalar dependências:
```bash
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
# Coleta informações de artistas (Spotify/Last.fm)
python run.py --module artists

# Processa dados brutos de voos com destino a Las Vegas
python run.py --module flights

# Busca comentários no Reddit (aceita parâmetros extras)
python run.py --module reddit --post-limit 50 --comment-limit 20 --output comments.csv

# Padroniza dados de turismo antes da análise
python run.py --module preprocess

# Gera gráficos e estatísticas a partir dos dados processados
python run.py --module excel --metrics "Visitors" "Average Room Rate"
```

Argumentos úteis:

- `reddit`: `--post-limit` controla quantos posts buscar por par de termos, e
  `--comment-limit` quantos comentários capturar por post (opcionalmente,
  `--output` define o arquivo CSV de saída).
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