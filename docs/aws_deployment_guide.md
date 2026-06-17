# 🚀 Guia de Deploy na AWS — IFAL Projetos

Este guia detalha o processo para realizar o deploy em ambiente de produção da aplicação **IFAL Projetos** (Front-end Vue.js, Back-end FastAPI e Banco de Dados PostgreSQL) utilizando a infraestrutura da AWS.

---

## 📌 1. Requisitos Prévios e Variáveis de Ambiente

Antes de iniciar, certifique-se de configurar as variáveis de ambiente necessárias em um arquivo `.env` de produção.

### 🔐 Tabela de Variáveis de Produção

| Variável | Descrição | Exemplo / Recomendação |
|---|---|---|
| `POSTGRES_USER` | Usuário administrador do banco | `ifal_prod_user` |
| `POSTGRES_PASSWORD` | Senha segura do banco | *Utilizar uma string aleatória forte* |
| `POSTGRES_DB` | Nome do banco de dados | `ifal_projetos_prod` |
| `DATABASE_URL` | String de conexão assíncrona do FastAPI | `postgresql+asyncpg://user:pass@host:5432/db` |
| `SUAP_CLIENT_ID` | Client ID registrado no SUAP | *Obtido no painel de APIs do SUAP* |
| `SUAP_CLIENT_SECRET` | Client Secret registrado no SUAP | *Obtido no painel de APIs do SUAP* |
| `SUAP_REDIRECT_URI` | URI de callback de autenticação | `https://seu-dominio.com/api/auth/callback` |
| `JWT_SECRET` | Chave de assinatura para sessões locais | *Gerar com `openssl rand -hex 32`* |
| `CORS_ALLOWED_ORIGINS` | Origens permitidas para requisições | `https://seu-dominio.com` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tempo de expiração do token de acesso | `15` |
| `REFRESH_TOKEN_EXPIRE_MINUTES`| Tempo limite do refresh token | `30` |

> [!WARNING]
> ### Requisito de Segurança SUAP (HTTPS)
> A API de autenticação do SUAP exige que a `SUAP_REDIRECT_URI` utilize o protocolo **HTTPS** em ambiente de produção. Não será possível autenticar usuários se o deploy não possuir certificado SSL configurado.

---

## 🛠️ Opção A: Deploy Rápido com AWS EC2 e Docker Compose (Recomendado para MVP)

Esta abordagem é a mais simples e utiliza uma única instância virtual EC2 para executar todos os serviços da mesma forma que no ambiente de desenvolvimento.

### Passo 1: Instanciar a Instância EC2
1. No console da AWS, crie uma instância EC2 (Recomendado: `t3.medium` ou superior, com Amazon Linux 2 ou Ubuntu).
2. Configure o **Security Group** para liberar as seguintes portas:
   - `22` (SSH) — Apenas para o IP do administrador.
   - `80` (HTTP) — Aberto para o mundo.
   - `443` (HTTPS) — Aberto para o mundo.

### Passo 2: Instalar Docker e Docker Compose na Instância
Acesse a instância via SSH e execute os comandos de instalação:

```bash
# Para Ubuntu
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
# Recarregue a sessão para aplicar as permissões do grupo
exit
```

### Passo 3: Clonar o Repositório e Configurar o Ambiente
1. Clone o repositório dentro da instância:
   ```bash
   git clone <url-do-repositorio>
   cd Projeto-4-Bimestre
   ```
2. Crie o arquivo `.env` de produção:
   ```bash
   cp .env.example .env
   nano .env
   ```
   *Preencha com as credenciais reais descritas no item 1 deste guia.*

### Passo 4: Inicializar a Aplicação e Executar Migrações
1. Suba os contêineres em segundo plano:
   ```bash
   docker compose -f docker-compose.yml up -d --build
   ```
2. Aplique as migrações estruturais do banco de dados utilizando o Alembic empacotado na imagem backend:
   ```bash
   docker compose exec backend alembic upgrade head
   ```

---

## 🌐 Opção B: Deploy de Alta Disponibilidade (AWS ECS + RDS + ECR)

Para um ambiente corporativo tolerante a falhas, escalável e seguro, dividimos os serviços utilizando serviços nativos da AWS.

```mermaid
graph TD
    User([Usuário]) -->|HTTPS| ALB[Application Load Balancer]
    subgraph "VPC Privada"
        ALB -->|Porta 80| FE[ECS Task: Frontend Nginx]
        ALB -->|Porta 8000| BE[ECS Task: Backend FastAPI]
        BE -->|Porta 5432| RDS[(AWS RDS PostgreSQL)]
    end
    ECR[(AWS ECR)] -.->|Pull Images| FE & BE
```

### Passo 1: Criar Repositórios no Amazon ECR
Crie dois repositórios no AWS ECR para armazenar as imagens Docker da aplicação:
```bash
aws ecr create-repository --repository-name ifal-frontend
aws ecr create-repository --repository-name ifal-backend
```

### Passo 2: Construir e Publicar as Imagens
Autentique o Docker com o ECR, construa as imagens locally ou no CI e faça o push:
```bash
# Autenticar no ECR (substitua <aws_account_id> e <region>)
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com

# Build e Tag Backend
docker build -t ifal-backend -f docker/backend.Dockerfile backend/
docker tag ifal-backend:latest <aws_account_id>.dkr.ecr.<region>.amazonaws.com/ifal-backend:latest
docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/ifal-backend:latest

# Build e Tag Frontend
docker build -t ifal-frontend -f docker/frontend.Dockerfile frontend/
docker tag ifal-frontend:latest <aws_account_id>.dkr.ecr.<region>.amazonaws.com/ifal-frontend:latest
docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/ifal-frontend:latest
```

### Passo 3: Provisionar o Banco de Dados no AWS RDS
1. Crie uma instância de banco de dados **PostgreSQL** no AWS RDS (Recomendado: versão 16, classe db.t4g.micro para desenvolvimento/free tier).
2. Guarde o endpoint do banco gerado e configure o Security Group do RDS para permitir tráfego de entrada na porta `5432` originado apenas do Security Group do ECS backend.

### Passo 4: Executar as Migrações Iniciais
Antes de iniciar o serviço no ECS, é necessário criar o esquema das tabelas no RDS. Você pode rodar isso a partir de uma máquina auxiliar ou rodando uma task temporária no ECS:
```bash
# Com o ambiente virtual ativado localmente e apontando para o endpoint do RDS no .env:
DATABASE_URL=postgresql+asyncpg://user:password@rds-endpoint:5432/dbname alembic upgrade head
```

### Passo 5: Configurar o ECS (Fargate) e o Load Balancer
1. Crie uma **Task Definition** para o backend:
   - Imagem: URL do repositório ECR do backend.
   - Portas: Mapear a porta `8000`.
   - Variáveis de ambiente: Configure as chaves de produção (apontando a `DATABASE_URL` para o RDS).
2. Crie uma **Task Definition** para o frontend:
   - Imagem: URL do repositório ECR do frontend.
   - Portas: Mapear a porta `80`.
3. Configure o **Application Load Balancer (ALB)**:
   - Crie um Listener HTTPS (porta 443) associado a um certificado SSL do **AWS ACM**.
   - Crie dois Target Groups: um para o frontend (porta 80) e outro para o backend (porta 8000).
   - Configure regras de roteamento no ALB:
     - Requisições para `/api/*` devem ser direcionadas ao Target Group do Backend.
     - Demais requisições (`/*`) devem ser direcionadas ao Target Group do Frontend.

---

## 🔒 3. Configuração de HTTPS / SSL (Crucial para o SUAP)

### Opção 1: Certificado SSL gerenciado pela AWS (com ALB)
Se utilizar a Opção B, basta solicitar um certificado gratuito no **AWS Certificate Manager (ACM)** para o seu domínio e anexá-lo ao Listener HTTPS (porta 443) do ALB. O tráfego do cliente até o ALB será criptografado, e o ALB fará o proxy via HTTP para os contêineres ECS na rede privada.

### Opção 2: Let's Encrypt (com Nginx no EC2)
Se utilizar a Opção A (EC2 individual), instale o `certbot` na máquina host e configure o Nginx para rodar com HTTPS.

Exemplo rápido de configuração de renovação automática via Nginx no host:
```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com
```
O Certbot irá ler as configurações do Nginx na máquina, solicitar o certificado SSL e atualizar as configurações para escutar na porta 443 de forma transparente.
