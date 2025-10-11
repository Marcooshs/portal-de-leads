# Portal de Leads — Relatório de Revisão

## Visão Geral
- Aplicação Django 5.2.7 organizada nos módulos `app` (configurações) e `leads` (domínio principal). As configurações contemplam alternância entre SQLite e PostgreSQL, integração com Whitenoise e suporte a múltiplos provedores SMTP por meio de variáveis de ambiente.【F:app/settings.py†L1-L114】【F:app/settings.py†L115-L218】
- A camada de domínio conta com modelos `Lead` e `Tag`, com validação de unicidade por email+empresa e campos opcionais para facilitar importações em massa.【F:leads/models.py†L1-L62】
- As views cobrem listagem com filtros, exportação CSV, CRUD completo e importação em massa, com mensagens de feedback e envio de email ao criar um lead.【F:leads/views.py†L1-L173】

## Front-end
- Interface baseada em Bootstrap 5, com tema dark/light persistente via Alpine.js, gradientes customizados e componentes reutilizáveis (navbar, paginação, mensagens).【F:templates/base.html†L1-L126】【F:templates/partials/_navbar.html†L1-L32】
- A listagem de leads utiliza HTMX para filtros reativos, indicadores de carregamento e modal de confirmação de exclusão, mantendo a UX fluida em tempo real.【F:templates/leads/lead_list.html†L1-L115】
- A tabela de leads exibe badges contextuais, ações rápidas e integra paginação compartilhada.【F:templates/leads/_lead_table.html†L1-L56】

## Testes
- `python manage.py test` (7 testes) validando filtros, exportação CSV, CRUD, importação e envio de email (backend locmem).【8ec4fe†L1-L7】

## Docker
- A imagem não pôde ser validada porque o ambiente da revisão não disponibiliza o binário `docker` para execução do build. Recomenda-se testar `docker compose up --build` em um ambiente local com Docker instalado.【1f1b6d†L1-L3】

## Conclusão
- O backend e o front-end passaram pelos testes automatizados e inspeção manual, sem falhas encontradas. Apenas ajustes de formatação menor (PEP 8) foram aplicados aos modelos e arquivos sem newline final para manter consistência do repositório.【F:leads/models.py†L19-L58】
