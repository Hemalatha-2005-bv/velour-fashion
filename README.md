# VELOUR E-Commerce

A full-stack clothing brand e-commerce site built with **FastAPI** (backend) and **vanilla HTML/CSS/JS** (frontend).

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Auth | JWT via python-jose |
| Storage | JSON flat files |
| Frontend | HTML, CSS, Vanilla JS |
| Hosting | Render.com |

## Project Structure

```
velour/
├── backend/
│   ├── main.py           # FastAPI app entry point
│   ├── requirements.txt
│   ├── middleware/auth.py # JWT auth
│   ├── models/schemas.py  # Pydantic models
│   ├── routers/           # auth, products, cart, wishlist, orders
│   ├── utils/file_store.py
│   └── data/              # JSON data files
└── frontend/
    ├── index.html
    ├── shop.html
    ├── product.html
    ├── auth.html
    ├── cart.html
    ├── checkout.html
    ├── css/               # base, layout, components
    └── js/                # api.js, auth.js, ui.js
```

## Run Locally

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Open `http://localhost:8000`

## API Docs

Available at `http://localhost:8000/api/docs` (Swagger UI)

## Environment Variables

| Variable | Description |
|---|---|
| `VELOUR_SECRET_KEY` | JWT signing secret (change in production) |
| `PORT` | Server port (set automatically by Render) |
