# DevOps na Prática - Fase 1: Configuração e Automação Inicial

![CI](https://github.com/Silveira-Rafael/devops/actions/workflows/ci.yml/badge.svg)

Repositório do projeto da disciplina DevOps na Prática.

1. **Aplicação** (`app/`) – a *Task API*, uma API REST simples para gerenciar tarefas.
2. **Testes automatizados** (`tests/`) – 27 testes unitários e de integração (`unittest`).
3. **Pipeline de Integração Contínua** (`.github/workflows/ci.yml`) – GitHub Actions.
4. **Infraestrutura como Código** (`terraform/`) – scripts Terraform para a AWS.
5. **Contêiner** (`Dockerfile`) – empacotamento da aplicação.

## Endpoints da API

| Método | Rota           | Descrição                               |
|--------|----------------|-----------------------------------------|
| GET    | `/health`      | Verificação de saúde da aplicação       |
| GET    | `/tasks`       | Lista todas as tarefas                  |
| POST   | `/tasks`       | Cria tarefa (`{"title": "texto"}`)      |
| GET    | `/tasks/{id}`  | Consulta uma tarefa                     |
| PUT    | `/tasks/{id}`  | Atualiza `title` e/ou `done`            |
| DELETE | `/tasks/{id}`  | Remove uma tarefa                       |

## Executar localmente

```bash
# Aplicação
python -m app

# Em outro terminal:
curl http://localhost:8000/health
curl http://localhost:8000/tasks
```

Com Docker:

```bash
docker build -t task-api .
docker run --rm -p 8000:8000 task-api
```

## Testes e qualidade de código

```bash
pip install -r requirements-dev.txt
flake8 app tests                                    # análise estática
coverage run -m unittest discover -s tests -t . -v  # testes
coverage report --fail-under=80                     # cobertura mínima
```

## Pipeline de CI

Arquivo: [`.github/workflows/ci.yml`](.github/workflows/ci.yml). 
Executa a cada *push* e *pull request* para a branch `main`:

| Job                  | O que faz                                                                  |
|----------------------|----------------------------------------------------------------------------|
| `lint-and-test`      | flake8, testes, cobertura mínima de 80 % e artefato                        |
| `docker-build`       | Constrói a imagem e faz *smoke test* do `/health`                          |
| `terraform-validate` | `terraform fmt -check`, `init -backend=false` e `validate`                 |

## Infraestrutura como Código

Pasta: [`terraform/`](terraform/). Provisiona na AWS: VPC, sub-rede pública, Internet Gateway, tabela de
rotas, Security Group, instância EC2 e um bucket S3 de artefatos (versionado, criptografado e sem acesso público). 

Detalhes em
[`docs/arquitetura.md`](docs/arquitetura.md).

```bash
cd terraform
terraform init
terraform plan      # mostra o que seria criado (não cria nada)
# terraform apply   # CRIA recursos reais e pode gerar custos na AWS
```

## Fase 2: Entrega Contínua e containers

A Fase 2 expande o pipeline com **entrega contínua (CD)** e usa **Docker Compose** para o deploy.

| Arquivo                                  | Função                                                                  |
|------------------------------------------|-------------------------------------------------------------------------|
| [`.github/workflows/cd.yml`](.github/workflows/cd.yml) | Pipeline de CD: roda depois que o CI termina com sucesso na `main`      |
| [`docker-compose.yml`](docker-compose.yml) | Orquestração do contêiner (portas, healthcheck, limites e segurança)   |
| [`scripts/deploy.sh`](scripts/deploy.sh) | Script de deploy: sobe a aplicação, espera o `/health` e faz smoke test |
| [`docs/fluxo-devops.md`](docs/fluxo-devops.md) | Fluxograma completo do fluxo DevOps (Fases 1 e 2)                  |

**Jobs do CD**

| Job              | O que faz                                                                                    |
|------------------|----------------------------------------------------------------------------------------------|
| `publish-image`  | Constrói a imagem e publica no GitHub Container Registry (tags com o SHA do commit e `latest`) |
| `deploy-staging` | Baixa a imagem publicada, faz o deploy com Docker Compose, executa o smoke test, coleta os logs e encerra o ambiente |

Executar o deploy localmente (precisa de Docker):

```bash
bash scripts/deploy.sh up     # constrói a imagem, sobe e testa
bash scripts/deploy.sh logs   # mostra os logs
bash scripts/deploy.sh down   # encerra
```
