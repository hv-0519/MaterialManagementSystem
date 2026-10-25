# Material Management System (MMS)

An enterprise material-request-to-inventory workflow system: Material Request → Receiver Verification → Purchase Supervisor Approval → Purchase Order → Material Receiving → Inventory, plus a Material Conversion engine for kitting/repackaging bulk stock into sellable units (with BOM and batch-packing rules).

## Tech Stack
- **Backend:** FastAPI + MySQL (`mysql-connector-python`)
- **Frontend:** Vue 3 + Vite

## Prerequisites
- Python 3.10+
- Node.js 18+
- MySQL 8+ (running locally or reachable)

---

## Setup — from a fresh clone

### 1. Clone the repo
```bash
git clone https://github.com/hv-0519/MaterialManagementSystem.git
cd MaterialManagementSystem
```

### 2. Database
Create the database and load the schema + seed data:
```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS mms_prototype;"
```
On Windows PowerShell (`<` isn't supported directly):
```powershell
cd database
cmd /c "mysql -u root -p mms_prototype < schema.sql"
cmd /c "mysql -u root -p mms_prototype < seed.sql"
```
On macOS/Linux:
```bash
cd database
mysql -u root -p mms_prototype < schema.sql
mysql -u root -p mms_prototype < seed.sql
```

### 3. Backend
```bash
cd backend
python -m venv .venv
```
Activate the virtual environment:
- Windows: `.venv\Scripts\activate`
- macOS/Linux: `source .venv/bin/activate`

Install dependencies:
```bash
pip install -r requirements.txt
```

Create your `.env` file from the template and fill in your actual DB credentials:
```bash
cp .env.example .env     # macOS/Linux
copy .env.example .env   # Windows
```

Run the backend:
```bash
uvicorn main:app --reload
```
Confirm it's working by opening `http://localhost:8000/` — you should see `{"message":"Material Management System API is running"}`. Interactive API docs are at `http://localhost:8000/docs`.

### 4. Frontend
Open a **new** terminal (keep the backend running):
```bash
cd frontend
npm install
npm run dev
```
Open the URL it prints (typically `http://localhost:5173`).

---

## Project Structure
```
MaterialManagementSystem/
├── backend/
│   ├── main.py            # FastAPI app — all endpoints
│   ├── database.py        # DB connection helper
│   ├── requirements.txt
│   └── .env               # not committed — see .env.example
├── database/
│   ├── schema.sql         # table definitions
│   └── seed.sql           # sample data
└── frontend/
    ├── src/
    │   ├── views/          # one .vue file per page
    │   ├── components/     # shared UI pieces (sidebar, header, etc.)
    │   ├── services/        # api.js — Axios instance
    │   └── router/index.js  # routes + sidebar nav config
    ├── package.json
    └── vite.config.js
```

## Environment Variables (`backend/.env`)
| Variable | Description |
|---|---|
| `DB_HOST` | MySQL host, typically `localhost` |
| `DB_PORT` | MySQL port, typically `3306` |
| `DB_NAME` | Database name, `mms_prototype` |
| `DB_USER` | MySQL username |
| `DB_PASSWORD` | MySQL password |

## Roles
- **Receiver** — verifies incoming material requests
- **Purchase Supervisor** — approves/rejects verified requests, reviews purchase orders
- **Admin** — full access

## Core Workflow
```
Material Request → Receiver Verification → Purchase Supervisor Review
→ Approve / Reject → Purchase Order → Material Receiving → Inventory
```

## Material Conversion Engine
Handles bulk-to-kit conversions (e.g. 50L bulk liquid → 5L cans with stickers, packed into cartons in batches of 4). Two rule types:
- **BOM (`bom_components` table):** per-unit components always consumed (e.g. 1 can = 5L liquid + 2 stickers)
- **Packing rule (`packing_rules` table):** batch-threshold packaging, with remainder below the threshold left unpackaged (e.g. every 4 cans = 1 carton)

Conversions are atomic — if any required material is short on stock, nothing is deducted. All component/package/output movements are logged per-transaction in `conversion_transactions` / `conversion_transaction_lines` for audit purposes.

## Troubleshooting
- **Frontend shows "Could not load dashboard data":** the backend isn't running, or isn't reachable at the URL the frontend expects. Confirm `uvicorn` is running and showing `Application startup complete`.
- **PowerShell `<` redirect error running `.sql` files:** PowerShell doesn't support `<` — wrap the command in `cmd /c "..."` as shown above.
- **`Run with PowerShell` does nothing:** your execution policy is likely blocking unsigned scripts. Run manually instead: `powershell -ExecutionPolicy Bypass -File "path\to\script.ps1"`.
