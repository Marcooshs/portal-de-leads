# Portal de Leads (Django)

Aplicação web para gestão de leads com **autenticação**, **CRUD**, **filtros/busca**, **tags**, **importação/exportação CSV**, **notificação por e-mail** e UI com **Bootstrap**.  

---

## 🧩 Funcionalidades

- Login/Logout (views nativas do Django)
- Lista de leads com filtros (texto, status, fonte, tag, dono) e paginação
- CRUD de leads (criar, editar, remover)
- Tags (ManyToMany) para classificar leads
- Importação **CSV** (cria em massa)
- Exportação **CSV** (streaming, abre bem no Excel)
- Notificação por e-mail ao criar lead (usa SMTP configurável)
- Templates com **Bootstrap 5**
- Servir estáticos com **WhiteNoise**
- Estrutura pronta para **PostgreSQL** (ou SQLite em dev)

### Campos do Lead
- `name`, `email`, `phone`, `company`
- `status`: `NEW` (Novo), `QLF` (Qualificado), `WON` (Ganho), `LST` (Perdido), `CLD` (Frio)
- `source`: `WEB`, `ADS`, `REF`, `EVT`, `OTH`
- `owner` (usuário responsável), `tags` (ManyToMany)
- `value` (Decimal), `notes` (Texto), `created_at`, `updated_at`

---

## 🚀 Rotas Principais

- **Leads (lista):** `/`
- **Novo lead:** `/novo/`
- **Editar lead:** `/<id>/editar/`
- **Remover lead:** `/<id>/remover/` *(confirmação via POST)*
- **Importar CSV:** `/importar/`
- **Exportar CSV:** `/?format=csv` *(ou botão na lista)*
- **Login:** `/accounts/login/`
- **Logout:** `/accounts/logout/`
- **Admin:** `/admin/`

---

## 🧰 Stack

- **Backend:** Django 5.x
- **Banco:** PostgreSQL (ou SQLite para dev)
- **Front:** Django Templates + Bootstrap 5 (HTMX opcional)
- **E-mails:** SMTP (Gmail/Outlook/etc.)
- **Estáticos:** WhiteNoise
- **.env:** `python-dotenv`

---

## ⚙️ Como rodar localmente

### 1) Pré-requisitos
- Python 3.12+  
- (Opcional) PostgreSQL 16+  
- Git

### 2) Clonar e criar venv
```powershell
git clone https://github.com/Marcooshs/portal-de-leads.git
cd portal-de-leads
python -m venv .venv
.\.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
