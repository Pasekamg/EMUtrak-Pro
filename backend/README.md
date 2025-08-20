# EMUTrak Backend (Django API)

Features
- JWT auth (SimpleJWT)
- Roles via JWT claim: superuser=admin, staff=editor, normal viewer
- Patients CRUD (`/api/patients/`)
- Audit log read-only for admin (`/api/audit/`)
- CORS enabled for `https://pasekamg.github.io`

Quick start (dev)
```
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # create your admin
python manage.py runserver 0.0.0.0:8000
```
Then obtain token:
```
POST /api/auth/token/  {"username":"<admin>","password":"<pwd>"}
```
Use returned `access` as `Authorization: Bearer <token>` and also send header `X-Role: admin|editor|viewer` (frontend handles this).

Deploy
- Works on Render, Railway, Fly.io, or any server.
- Set env: `DJANGO_SECRET_KEY`, `DEBUG=0` (prod).
