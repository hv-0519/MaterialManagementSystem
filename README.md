# Material Management System (MMS)

FastAPI + MySQL backend, Vue 3 (CDN, no build) frontend.

## Stack
- Backend: FastAPI, MySQL (database: mms_prototype), run with uvicorn
- Frontend: 8 static HTML pages in mms-frontend/ (Vue via CDN)

## First-time setup

### 1. Database (needs MySQL running)
    mysql -u root -p < database/schema.sql
    mysql -u root -p mms_prototype < database/seed.sql

### 2. Backend
    cd backend
    python -m venv venv
    .\venv\Scripts\Activate.ps1            # Windows PowerShell
    pip install fastapi uvicorn mysql-connector-python python-dotenv pydantic

Create backend/.env (NOT committed) with:
    DB_HOST=localhost
    DB_PORT=3306
    DB_NAME=mms_prototype
    DB_USER=root
    DB_PASSWORD=your_password_here

### 3. Run (two terminals)
Terminal 1 - API:
    cd backend
    .\venv\Scripts\Activate.ps1
    uvicorn main:app --reload --port 8000

Terminal 2 - frontend:
    cd mms-frontend
    python -m http.server 5500

Open http://localhost:5500/01-dashboard.html

## Workflow
Material Request -> Receiver Verification -> Purchase Approval ->
(auto) Purchase Order + Receiving + Inventory -> Material Receiving ->
Inventory. Plus a Conversion/kitting engine (BOM + packing rules).

## Notes
- user_id is hardcoded to 1 in the backend (single-user prototype).
- CORS is open to all origins for local dev; tighten before any deployment.
- inventory.material_id has a UNIQUE constraint (required by the conversion engine).
