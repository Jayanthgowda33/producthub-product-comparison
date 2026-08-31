# ProductHub — AI Multi-Vendor Marketplace
### Full Build Roadmap (VS Code, from scratch)

**Stack:** Django + Django REST Framework (backend) · React + Vite (frontend) · PostgreSQL · Redis + Celery · pgvector + LLM API (AI features) · Docker (deployment)

> This is a multi-week project. Build it phase by phase — don't try to jump ahead. Each phase ends with something runnable.

---

## Phase 0 — Prerequisites & VS Code Setup

**Install:**
- Python 3.11+, Node.js 20+, PostgreSQL 15+, Redis, Git, Docker Desktop (optional but recommended)
- VS Code extensions: Python, Pylance, Django, ESLint, Prettier, Docker, Thunder Client (API testing), GitLens

**Project folder layout:**
```
producthub/
├── backend/          # Django project
├── frontend/         # React app
├── docker-compose.yml
└── README.md
```
Open the root `producthub/` folder in VS Code as a multi-root workspace so backend and frontend live side by side.

---

## Phase 1 — Backend Skeleton

```bash
mkdir producthub && cd producthub
python -m venv backend/venv
source backend/venv/bin/activate    # Windows: backend\venv\Scripts\activate
pip install django djangorestframework django-cors-headers psycopg2-binary python-decouple djangorestframework-simplejwt celery redis django-filter drf-spectacular
django-admin startproject config backend
cd backend
python manage.py startapp accounts
python manage.py startapp vendors
python manage.py startapp products
python manage.py startapp orders
python manage.py startapp payments
python manage.py startapp ai_engine
```

Configure `settings.py`: add all apps + `rest_framework`, `corsheaders`, `django_filters` to `INSTALLED_APPS`; set up PostgreSQL in `DATABASES`; add JWT auth to `REST_FRAMEWORK` default authentication classes; add CORS middleware.

**Checkpoint:** `python manage.py runserver` works, admin panel loads at `/admin`.

---

## Phase 2 — Data Models (the core of the whole system)

Design in this order, since each depends on the last:

1. **accounts** — Custom `User` model with a `role` field (`customer` / `vendor` / `admin`). Use `AbstractUser`.
2. **vendors** — `VendorProfile` (linked to User), store name, verification status, payout details.
3. **products** — `Category` (self-referencing for subcategories), `Product` (belongs to vendor + category), `ProductImage`, `ProductVariant` (size/color/price/stock).
4. **orders** — `Cart`, `CartItem`, `Order`, `OrderItem`, `OrderStatusHistory`.
5. **payments** — `Payment` (linked to Order, gateway reference, status).
6. **reviews** (small app or inside products) — `Review` linked to Product + User.

Run migrations after each app: `python manage.py makemigrations && python manage.py migrate`.

**Checkpoint:** All models visible and manageable in Django Admin (`admin.py` registration).

---

## Phase 3 — Auth & Roles

- JWT auth via `djangorestframework-simplejwt`: `/api/auth/register`, `/api/auth/login`, `/api/auth/refresh`.
- Custom permission classes: `IsVendor`, `IsAdmin`, `IsCustomer`, `IsOwnerOrReadOnly`.
- Vendor signup flow: user registers → applies as vendor → admin approves.

**Checkpoint:** Can register as customer/vendor, log in, and get a JWT that gates vendor-only/admin-only endpoints.

---

## Phase 4 — Core Customer APIs

Build DRF `ViewSets` + serializers + routers for:
- `Products`: list/filter/search (by category, price, vendor), detail view
- `Cart`: add/remove/update items
- `Orders`: checkout flow → creates Order + OrderItems from Cart, reduces stock
- `Payment`: integrate Stripe or Razorpay test mode, webhook to confirm payment → update order status

**Checkpoint:** Full flow testable in Thunder Client/Postman: browse products → add to cart → checkout → pay (test mode) → order appears as "paid".

---

## Phase 5 — Vendor Dashboard APIs

- Vendor-scoped product CRUD (`/api/vendor/products/`) — only their own products
- Inventory endpoint: bulk stock updates, low-stock alerts
- Vendor order view: orders containing their products, update fulfillment status
- Analytics endpoint: revenue over time, best-sellers, order counts (use Django aggregation — `Sum`, `Count`, `annotate`)

---

## Phase 6 — Admin APIs

- User management: list/suspend users
- Vendor approval queue
- Platform-wide reports: GMV, top vendors, category performance
- Most of this can lean on Django Admin directly, customized with `list_display`, `list_filter`, and custom admin actions — don't rebuild everything as a separate API unless you want a custom admin frontend.

---

## Phase 7 — AI Layer (`ai_engine` app)

This is what makes it a flagship project — three features:

1. **AI Search (semantic)**
   - Generate embeddings for each product (title + description) using an embeddings API, store in Postgres via `pgvector` (`pip install pgvector`, add `VectorField` to Product).
   - Search endpoint embeds the query and does a cosine-similarity nearest-neighbor lookup instead of plain keyword match.

2. **Recommendations**
   - "Similar products": nearest neighbors of a product's embedding.
   - "For you": based on a user's purchase/view history, average the embeddings of what they interacted with, find nearest products.
   - Precompute with a Celery periodic task so it's fast at request time.

3. **AI Shopping Assistant**
   - A chat endpoint (`/api/ai/assistant/`) that takes a user message + conversation history.
   - Give the LLM tool access to your own search/recommendation functions (function calling), so it can query real inventory instead of hallucinating products — this is a RAG pattern, not just a wrapped chatbot.
   - Stream responses back to the frontend if you want a "typing" effect.

**Checkpoint:** Searching "warm jacket for winter" returns relevant products even without the exact words; asking the assistant "what's a good gift under $50" returns real, in-stock products.

---

## Phase 8 — Frontend (React + Vite)

```bash
cd producthub
npm create vite@latest frontend -- --template react
cd frontend
npm install axios react-router-dom zustand @tanstack/react-query tailwindcss
```

**Structure:**
```
src/
├── api/            # axios instance + endpoint functions
├── components/      # shared UI
├── pages/
│   ├── customer/    # Home, ProductDetail, Cart, Checkout, OrderHistory
│   ├── vendor/       # VendorDashboard, Inventory, VendorOrders, Analytics
│   └── admin/        # AdminDashboard, UserManagement, VendorApprovals
├── store/            # zustand stores (auth, cart)
└── App.jsx           # routes, role-based route guards
```

Build customer flow first end-to-end (browse → cart → checkout), then vendor dashboard, then admin, then wire in the AI search bar and assistant chat widget last.

---

## Phase 9 — Payments (real integration)

- Stripe Checkout or Razorpay Orders API in test mode.
- Webhook endpoint in Django to confirm payment asynchronously (don't trust the frontend redirect alone).

---

## Phase 10 — Docker & Deployment

`docker-compose.yml` with services: `backend`, `frontend` (or serve built static via nginx), `db` (postgres+pgvector image), `redis`, `celery`.

Deploy target suggestions: Railway/Render for backend+db, Vercel/Netlify for frontend, or a single VPS with Docker Compose for everything.

---

## Suggested Build Order (realistic pacing)

| Week | Focus |
|---|---|
| 1 | Phase 0–2: setup + models |
| 2 | Phase 3–4: auth + customer APIs |
| 3 | Phase 5–6: vendor + admin APIs |
| 4 | Phase 7: AI search, recommendations, assistant |
| 5 | Phase 8: full frontend |
| 6 | Phase 9–10: payments, polish, deploy |

---

## Next Step

Tell me which phase to start actually coding, and I'll scaffold real files with you (models, serializers, views, React components) — building it incrementally like this will actually stick, versus one giant code dump.
