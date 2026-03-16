# Desafio Técnico IBGE - Flask + Arquitetura em Camadas

Projeto desenvolvido para resolver o desafio técnico com foco em:

- código organizado em camadas (`controllers`, `services`, `repositories`, `domain`);
- princípios SOLID (responsabilidades separadas e inversão de dependência via contratos);
- nomes de classes, funções e variáveis claros;
- tratamento de erros (IBGE indisponível, token ausente, falha de envio).

## O que o projeto faz

1. Lê o `input.csv` com municípios e populações.
2. Consulta a API de localidades do IBGE.
3. Encontra o melhor match para cada município (normalização + fuzzy matching).
4. Gera `resultado.csv` com os status:
   - `OK`
   - `NAO_ENCONTRADO`
   - `ERRO_API`
   - `AMBIGUO`
5. Calcula estatísticas no formato exigido.
6. Envia as estatísticas para a Edge Function com `Authorization: Bearer <ACCESS_TOKEN>`.
7. Exibe no console o `score` e o `feedback` (quando o envio ocorre).

## Estrutura do projeto

```text
.
├── app.py
├── input.csv
├── requirements.txt
├── src/
│   ├── app_factory.py
│   ├── cli.py
│   ├── config/
│   │   └── settings.py
│   ├── controllers/
│   │   ├── challenge_controller.py
│   │   └── home_controller.py
│   ├── domain/
│   │   ├── interfaces.py
│   │   └── models.py
│   ├── repositories/
│   │   ├── correction_repository.py
│   │   ├── ibge_repository.py
│   │   └── supabase_auth_repository.py
│   └── services/
│       ├── challenge_service.py
│       ├── csv_service.py
│       ├── matching_service.py
│       ├── stats_service.py
│       └── text_normalizer.py
├── static/
└── templates/
```

## Requisitos

- Python 3.12+
- Acesso à internet para API do IBGE e Edge Function

## Instalação

```bash
pip install -r requirements.txt
```

Crie seu arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

## Configuração de ambiente

Use `.env.example` como referência e exporte as variáveis no shell.

As variáveis em `.env` são carregadas automaticamente pelo projeto.

Variáveis principais:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `CORRECTION_FUNCTION_URL`
- `IBGE_API_URL`
- `HTTP_TIMEOUT_SECONDS`
- `FUZZY_CUTOFF`

Para login automático (opcional):

- `SUPABASE_EMAIL`
- `SUPABASE_PASSWORD`

Token direto (opcional):

- `ACCESS_TOKEN`

## Como rodar (CLI) - recomendado para o desafio

### 1) Processar sem enviar (teste local)

```bash
python -m src.cli --input input.csv --output resultado.csv --no-submit
```

### 2) Processar e enviar com token já obtido

```bash
python -m src.cli --input input.csv --output resultado.csv --access-token "SEU_ACCESS_TOKEN"
```

Você também pode definir `ACCESS_TOKEN` no `.env` e rodar sem `--access-token`.

### 3) Processar e enviar com login automático (sem passar token)

```bash
python -m src.cli \
  --input input.csv \
  --output resultado.csv \
  --email "seu_email@dominio.com" \
  --password "sua_senha"
```

Se `SUPABASE_EMAIL` e `SUPABASE_PASSWORD` estiverem no `.env`, você pode simplesmente rodar:

```bash
python -m src.cli --input input.csv --output resultado.csv
```

Prioridade de autenticação na CLI:

1. `--access-token`
2. `ACCESS_TOKEN` no `.env`
3. Login com `--email/--password`
4. Login com `SUPABASE_EMAIL/SUPABASE_PASSWORD` no `.env`

Saída esperada no terminal:

- Caminho do `resultado.csv`
- Objeto `stats`
- `score` e `feedback` quando o envio for concluído

## Como rodar (Flask)

```bash
flask --app app.py --debug run
```

Endpoint HTTP para executar o pipeline:

- `POST /api/challenge/run`

Exemplo de body JSON:

```json
{
  "input_file": "input.csv",
  "output_file": "resultado.csv",
  "should_submit": true,
  "access_token": "SEU_ACCESS_TOKEN"
}
```

Você também pode enviar `email` e `password` no body para login automático.

## Formato do resultado.csv

Colunas geradas:

- `municipio_input`
- `populacao_input`
- `municipio_ibge`
- `uf`
- `regiao`
- `id_ibge`
- `status`

## Estatísticas calculadas

- `total_municipios`
- `total_ok`
- `total_nao_encontrado`
- `total_erro_api`
- `pop_total_ok`
- `medias_por_regiao`

## Decisões técnicas

- **SOLID / SRP**: cada camada tem responsabilidade única.
- **DIP**: `ChallengeService` depende de contratos (`interfaces`) e não de implementações concretas.
- **Matching robusto**:
  - normalização de acentos e caracteres especiais;
  - comparação case-insensitive;
  - fuzzy matching por similaridade (`SequenceMatcher`).
- **Resiliência**:
  - falha no IBGE gera linhas com `ERRO_API`;
  - token ausente não quebra o processamento, apenas impede o envio.

## Melhorias futuras

- testes unitários para `matching_service` e `stats_service`;
- retry/backoff para chamadas HTTP;
- cache local da base de municípios do IBGE para reduzir latência.
