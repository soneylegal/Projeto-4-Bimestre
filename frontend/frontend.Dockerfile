# Stage 1: Build
FROM node:20-slim AS builder

WORKDIR /app

# Copia arquivos de dependência do npm se existirem
COPY package*.json ./

# Como o código do frontend será inicializado do zero, se package.json não existir ainda,
# o Dockerfile pode falhar no build inicial se tentarmos rodar npm install sem package.json.
# Adicionaremos uma verificação simples ou geraremos um package.json básico no build.
RUN if [ -f package.json ]; then npm ci; else npm init -y && npm install vue vue-router pinia && npm install -D vite @vitejs/plugin-vue; fi

COPY . .

# Executa build se o script de build estiver disponível
RUN if grep -q "build" package.json; then npm run build; else mkdir dist && echo "Vue app is building..." > dist/index.html; fi

# Stage 2: Production
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
