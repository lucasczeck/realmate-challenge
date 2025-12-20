# Instruções de Instalação e Uso - Realmate Challenge

Este documento contém todas as instruções necessárias para clonar, configurar e executar o projeto Realmate Challenge.

## 📋 Índice

- [Pré-requisitos](#pré-requisitos)
- [Clonagem do Repositório](#clonagem-do-repositório)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Executando o Projeto](#executando-o-projeto)
- [Endpoints da API](#endpoints-da-api)
- [Sistema de Logs](#sistema-de-logs)
- [Testes](#testes)

---

## Pré-requisitos

Antes de começar, certifique-se de ter instalado em sua máquina:

- **Docker** (versão 20.10 ou superior)
- **Docker Compose** (versão 2.0 ou superior)
- **Git**

Para verificar se você possui essas ferramentas instaladas, execute:

```bash
docker --version
docker-compose --version
git --version
```

---

## Clonagem do Repositório

Para clonar o repositório, execute o seguinte comando:

```bash
git clone https://github.com/lucasczeck/realmate-challenge.git
cd realmate-challenge
```

---

## Configuração do Ambiente

O projeto utiliza variáveis de ambiente para configuração do banco de dados. Você pode criar um arquivo `.env` na raiz do projeto (opcional) com as seguintes variáveis:

```env
DB_NAME=realmate_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

**Nota:** Se o arquivo `.env` não for criado, o projeto utilizará os valores padrão definidos no `docker-compose.yaml` e `settings.py`.

---

## Executando o Projeto

### 1. Iniciando os Serviços

Para iniciar todos os serviços (banco de dados PostgreSQL e aplicação Django), execute:

```bash
docker-compose up --build
```

Este comando irá:
- Construir as imagens Docker necessárias
- Iniciar o container do PostgreSQL
- Executar as migrações do banco de dados
- Executar os testes automaticamente
- Iniciar o servidor Django na porta 80

### 2. Acessando a Aplicação

Após a inicialização bem-sucedida, a API estará disponível em:

- **URL Base:** `http://localhost:80`
- **Admin Django:** `http://localhost:80/admin/`

### 3. Parando os Serviços

Para parar os serviços, pressione `Ctrl+C` no terminal ou execute:

```bash
docker-compose down
```

Para remover também os volumes (incluindo os dados do banco):

```bash
docker-compose down -v
```

### 4. Visualizando os Logs

Para acompanhar os logs dos containers em tempo real:

```bash
docker-compose logs -f
```

Para ver apenas os logs de um serviço específico:

```bash
docker-compose logs -f web
docker-compose logs -f db
```

---

## Endpoints da API

A API possui os seguintes endpoints disponíveis:

### 1. POST `/webhook/`

Recebe eventos de webhook do sistema de atendimento.

**URL:** `http://localhost:80/webhook/`

**Método:** `POST`

**Content-Type:** `application/json`

**Tipos de Eventos Suportados:**

#### 1.1. Nova Conversa (NEW_CONVERSATION)

Cria uma nova conversa no sistema.

**Request Body:**
```json
{
    "type": "NEW_CONVERSATION",
    "timestamp": "2025-02-21T10:20:41.349308",
    "data": {
        "id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
    }
}
```

**Response (200 Created):**
```json
{
    "status": "CREATED",
    "id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a",
    "type": "NEW_CONVERSATION"
}
```

#### 1.2. Nova Mensagem (NEW_MESSAGE)

Adiciona uma nova mensagem a uma conversa existente.

**Request Body - Mensagem Recebida:**
```json
{
    "type": "NEW_MESSAGE",
    "timestamp": "2025-02-21T10:20:42.349308",
    "data": {
        "id": "49108c71-4dca-4af3-9f32-61bc745926e2",
        "direction": "RECEIVED",
        "content": "Olá, tudo bem?",
        "conversation_id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
    }
}
```

**Request Body - Mensagem Enviada:**
```json
{
    "type": "NEW_MESSAGE",
    "timestamp": "2025-02-21T10:20:44.349308",
    "data": {
        "id": "16b63b04-60de-4257-b1a1-20a5154abc6d",
        "direction": "SENT",
        "content": "Tudo ótimo e você?",
        "conversation_id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
    }
}
```

**Response (200 Created):**
```json
{
    "status": "CREATED",
    "id": "49108c71-4dca-4af3-9f32-61bc745926e2",
    "type": "NEW_MESSAGE"
}
```

**Valores Aceitos para `direction`:**
- `RECEIVED` - Mensagem recebida
- `SENT` - Mensagem enviada

#### 1.3. Fechar Conversa (CLOSE_CONVERSATION)

Fecha uma conversa existente.

**Request Body:**
```json
{
    "type": "CLOSE_CONVERSATION",
    "timestamp": "2025-02-21T10:20:45.349308",
    "data": {
        "id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
    }
}
```

**Response (200 OK):**
```json
{
    "status": "CLOSED",
    "id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a",
    "type": "CLOSE_CONVERSATION"
}
```

**Códigos de Resposta Possíveis:**
- `200` - Operação realizada com sucesso
- `400` - Erro de validação (campos obrigatórios ausentes)
- `422` - Erro de regra de negócio (conversa já fechada, ID duplicado, etc.)

---

### 2. GET `/conversations/`

Lista todas as conversas, com opção de filtros.

**URL:** `http://localhost:80/conversations/`

**Método:** `GET`

**Query Parameters (Opcionais):**
- `status` - Filtra por status da conversa (`OPEN` ou `CLOSED`)
- `date` - Filtra por data de criação no formato `YYYY-MM-DD`

**Exemplos de Uso:**

```bash
# Listar todas as conversas
GET http://localhost:80/conversations/

# Filtrar por status
GET http://localhost:80/conversations/?status=OPEN
GET http://localhost:80/conversations/?status=CLOSED

# Filtrar por data
GET http://localhost:80/conversations/?date=2025-02-21

# Combinar filtros
GET http://localhost:80/conversations/?status=OPEN&date=2025-02-21
```

**Response (200 OK):**
```json
{
    "conversations": [
        {
            "id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a",
            "status": "OPEN",
            "create_timestamp": "2025-02-21T10:20:41.349308",
            "edit_timestamp": null
        },
        {
            "id": "7b52c458-9e91-5df0-95cb-8bg77g470f7b",
            "status": "CLOSED",
            "create_timestamp": "2025-02-21T09:15:30.123456",
            "edit_timestamp": "2025-02-21T10:20:45.349308"
        }
    ]
}
```

**Códigos de Resposta Possíveis:**
- `200` - Sucesso
- `422` - Erro de validação (status ou formato de data inválido)

---

### 3. GET `/conversations/<conversation_id>/`

Retorna os detalhes completos de uma conversa específica, incluindo todas as suas mensagens.

**URL:** `http://localhost:80/conversations/<conversation_id>/`

**Método:** `GET`

**Parâmetros de URL:**
- `conversation_id` - UUID da conversa (obrigatório)

**Exemplo de Uso:**

```bash
GET http://localhost:80/conversations/6a41b347-8d80-4ce9-84ba-7af66f369f6a/
```

**Response (200 OK):**
```json
{
    "id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a",
    "created_at": "2025-02-21T10:20:41.349308",
    "closed_at": null,
    "status": "OPEN",
    "messages": [
        {
            "id": "49108c71-4dca-4af3-9f32-61bc745926e2",
            "content": "Olá, tudo bem?",
            "direction": "RECEIVED",
            "created_at": "2025-02-21T10:20:42.349308"
        },
        {
            "id": "16b63b04-60de-4257-b1a1-20a5154abc6d",
            "content": "Tudo ótimo e você?",
            "direction": "SENT",
            "created_at": "2025-02-21T10:20:44.349308"
        }
    ]
}
```

**Códigos de Resposta Possíveis:**
- `200` - Sucesso
- `400` - Conversa não encontrada

---

## Sistema de Logs

O projeto possui um sistema completo de log de requisições implementado através do módulo `core.log`. Todas as requisições HTTP recebidas pela API são automaticamente registradas no banco de dados PostgreSQL.

### Como Funciona

O sistema de logs utiliza um **middleware Django** (`LogMiddleware`) que intercepta todas as requisições HTTP antes e depois do processamento, capturando informações detalhadas sobre cada requisição e resposta.

### Tabela de Log

Os logs são armazenados na tabela `log` do banco de dados PostgreSQL. A tabela possui os seguintes campos:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | Identificador único do log (gerado automaticamente) |
| `status_code` | Integer | Código de status HTTP da resposta (200, 201, 400, etc.) |
| `reason_phrase` | CharField(500) | Frase de motivo do status HTTP |
| `metodo` | CharField(30) | Método HTTP utilizado (GET, POST, PUT, DELETE, etc.) |
| `ip` | GenericIPAddress | Endereço IP do cliente |
| `ip_externo` | Text | IP externo (extraído de X-Forwarded-For, se disponível) |
| `path` | CharField(500) | Caminho da URL da requisição |
| `session_key` | CharField(200) | Chave da sessão Django (se existir) |
| `host` | Text | Host da requisição |
| `remote_addr` | Text | Endereço remoto |
| `http_x_encaminhado` | Text | Valor do header X-Forwarded-For completo |
| `body` | Text | Corpo da requisição (body) |
| `params` | Text | Parâmetros de query string (GET) |
| `info_user` | Text | Informações completas do user agent |
| `referer` | Text | URL de referência (se disponível) |
| `info_user_navegador_familia` | CharField(200) | Família do navegador (Chrome, Firefox, etc.) |
| `info_user_navegador_versao` | CharField(50) | Versão do navegador |
| `info_user_aparelho_familia` | CharField(200) | Família do dispositivo |
| `info_user_aparelho_modelo` | CharField(200) | Modelo do dispositivo |
| `info_user_os_familia` | CharField(200) | Família do sistema operacional |
| `info_user_os_versao` | CharField(50) | Versão do sistema operacional |
| `info_user_is_bot` | Boolean | Indica se é um bot |
| `info_user_is_email_client` | Boolean | Indica se é um cliente de email |
| `info_user_is_mobile` | Boolean | Indica se é um dispositivo móvel |
| `info_user_is_pc` | Boolean | Indica se é um computador |
| `info_user_is_tablet` | Boolean | Indica se é um tablet |
| `info_user_is_touch_capable` | Boolean | Indica se o dispositivo tem tela touch |

### Características de Segurança

O sistema de logs possui algumas proteções de segurança:

- **Senhas não são logadas:** Se o campo `password` estiver presente nos parâmetros GET ou no body POST, esses dados não serão salvos no log (campo fica vazio).
- **Tratamento de Erros:** Se ocorrer algum erro durante o salvamento do log, o sistema não interrompe a requisição principal, garantindo que a API continue funcionando normalmente.

### Acessando os Logs

Você pode acessar os logs de várias formas:

#### 1. Via Django Admin

Acesse `http://localhost:80/admin/` e navegue até a seção de Logs (se configurado no admin).

#### 2. Via Banco de Dados

Conecte-se ao banco de dados PostgreSQL e execute:

```sql
SELECT * FROM log ORDER BY created_at DESC LIMIT 100;
```

#### 3. Via Django Shell

```bash
docker-compose exec web python manage.py shell
```

```python
from core.log.models import Log

# Listar os últimos 10 logs
logs = Log.objects.all().order_by('-created_at')[:10]
for log in logs:
    print(f"{log.created_at} - {log.metodo} {log.path} - {log.status_code}")
```

### Estrutura do Módulo

O sistema de logs está organizado da seguinte forma:

```
core/
└── log/
    ├── __init__.py
    ├── models.py          # Modelo Log
    ├── middleware.py      # LogMiddleware que intercepta requisições
    ├── admin.py           # Configuração do admin Django
    └── migrations/        # Migrações do banco de dados

BO/
└── log/
    └── log.py             # Classe Log que salva os dados
```

O fluxo de funcionamento é:

1. **Requisição chega** → `LogMiddleware` intercepta
2. **Middleware captura** informações da requisição (método, path, IP, body, etc.)
3. **Requisição é processada** pela view correspondente
4. **Resposta é gerada** → Middleware captura informações da resposta (status_code, reason_phrase)
5. **Log é salvo** no banco de dados através da classe `BO.log.log.Log`

---

## Testes

O projeto possui testes automatizados que são executados automaticamente antes de iniciar o servidor web.

### Executando Testes Manualmente

Para executar os testes manualmente:

```bash
docker-compose run test
```

Ou, se preferir executar dentro do container:

```bash
docker-compose exec web pytest
```

### Estrutura de Testes

Os testes estão organizados em:

- `api/tests/` - Testes das views e modelos da API
- `BO/tests/` - Testes das classes de negócio

---

## Troubleshooting

### Problema: Porta 80 já está em uso

**Solução:** Altere a porta no arquivo `docker-compose.yaml`:

```yaml
ports:
  - "8080:8000"  # Altere 80 para 8080 ou outra porta disponível
```

### Problema: Erro ao conectar ao banco de dados

**Solução:** Verifique se o container do banco está rodando:

```bash
docker-compose ps
```

Se necessário, recrie os containers:

```bash
docker-compose down -v
docker-compose up --build
```

### Problema: Migrações não foram aplicadas

**Solução:** Execute as migrações manualmente:

```bash
docker-compose exec web python manage.py migrate
```

---

## Tecnologias Utilizadas

- **Django 5.1.6** - Framework web
- **Django REST Framework** - Framework para APIs REST
- **PostgreSQL 16** - Banco de dados
- **Poetry** - Gerenciamento de dependências
- **Docker & Docker Compose** - Containerização e orquestração
- **Pytest** - Framework de testes

---

**Última atualização:** 2025

