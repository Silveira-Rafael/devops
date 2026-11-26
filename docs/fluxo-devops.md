# Fluxo DevOps completo (Fases 1 e 2)

Imagem usada no relatório: [`fluxograma-devops.png`](fluxograma-devops.png).

```mermaid
flowchart TD
    A[Desenvolvedor faz commit] --> B[Pull request para a main<br/>branch protegida]
    B --> C

    subgraph CI [Fase 1 - Integração Contínua]
        C[Lint flake8 + 27 testes<br/>cobertura mínima 80%] --> D[Build Docker<br/>+ smoke test /health]
        C --> E[Terraform fmt + init + validate]
    end

    D --> F{CI verde na main?}
    E --> F
    F -- Não --> A

    subgraph CD [Fase 2 - Entrega Contínua]
        F -- Sim --> G[CD dispara<br/>workflow_run]
        G --> H[Publica imagem no GHCR<br/>tags: sha e latest]
        H --> I[Deploy em staging<br/>docker compose pull + up]
        I --> J{Smoke test ok?}
        J -- Sim --> K[Ambiente validado<br/>logs coletados e staging encerrado]
        J -- Não --> L[Pipeline vermelho<br/>ler os logs]
    end
```

## Etapas do CD

| Etapa | Onde | O que faz |
|-------|------|-----------|
| Gatilho | `.github/workflows/cd.yml` | Roda após o workflow **CI** terminar com sucesso na `main` (ou manualmente) |
| Publicar imagem | job `publish-image` | Constrói a imagem e publica no GitHub Container Registry com as tags `sha` e `latest` |
| Deploy em staging | job `deploy-staging` | Baixa a imagem publicada e sobe com `docker compose` (`scripts/deploy.sh`) |
| Verificação | `scripts/deploy.sh` | Espera o `/health` e cria e lista uma tarefa (smoke test) |
| Encerramento | job `deploy-staging` | Coleta os logs e derruba o ambiente, mesmo se houver falha |
