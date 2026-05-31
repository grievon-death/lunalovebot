FROM python:3.14-alpine3.22

# Atualiza a imagem.
RUN apk update && \
    apk upgrade --no-cache

# Instala dependências do projeto.
RUN apk add --no-cache build-base linux-headers \
        gcc bash mariadb-dev python3-dev

# Atualiza o gerenciador de pacotes do python e adicionais de building.
RUN pip install --upgrade pip setuptools wheel

# Cria o diretório de trabalho.
WORKDIR /opt/luna

# Copia o projeto para dentro da imagem.
COPY . .

# Instala os pacotes do projeto.
RUN pip install -r requirements.txt
