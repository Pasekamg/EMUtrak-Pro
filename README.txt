EMUTrak Fullstack (Django API + Frontend)
========================================

This ZIP contains:
- backend/  → Django REST API with JWT auth, Patients CRUD, Audit log, CORS
- frontend/ → Static site that talks to the API (works on GitHub Pages)

Quick Dev
1) Backend: see backend/README.md. Start server on http://localhost:8000
2) Frontend: open frontend/index.html (or host it on GitHub Pages).
3) In the page header, paste your API base (e.g., http://localhost:8000 or https://yourapp.onrender.com), Save API, then Sign in.

Roles
- superuser = admin
- staff user = editor
- normal user = viewer
(Backend encodes role in JWT; frontend also sends X-Role header.)

Deployment Hint
- Deploy backend to Render/Railway/Fly. Set CORS to allow https://pasekamg.github.io in settings.py.
- Host frontend on GitHub Pages (Patients-List repo). Set API base to your deployed backend URL.
