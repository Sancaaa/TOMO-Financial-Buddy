# Graph Report - .  (2026-07-12)

## Corpus Check
- Corpus is ~23,345 words - fits in a single context window. You may not need a graph.

## Summary
- 672 nodes · 1327 edges · 47 communities (40 shown, 7 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 203 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Web PWA Frontend
- Backend Domain Services
- Telegram Bot Dispatcher
- Concepts & Domain Models
- Frontend NPM Dependencies
- Quick-Add Parser
- Recurring Transactions
- Transactions API
- OCR Receipt Extraction
- TypeScript Config
- Analytics API
- Telegram Webhook & Client
- Saving Goals
- Web API Client
- Accounts API
- Categories API
- Auth Dependencies
- Budgets API
- Budget Bot Tests
- Bot Message Formatting
- Security & Login (JWT)
- Receipts API
- Schema Sync & Startup
- Database Seeding
- Design & Delivery Concepts
- FastAPI App Entrypoint
- Analytics Tests
- Database Session
- Auth Schemas
- Test Fixtures (conftest)
- App Configuration
- Vite Config
- Backend Requirements
- Docker Compose
- refWeb Celebration Page

## God Nodes (most connected - your core abstractions)
1. `overview()` - 23 edges
2. `Category` - 22 edges
3. `Transaction` - 21 edges
4. `handle_update()` - 20 edges
5. `now_local()` - 17 edges
6. `compilerOptions` - 17 edges
7. `suggest_category()` - 16 edges
8. `TelegramClient` - 15 edges
9. `apply_balance()` - 15 edges
10. `FakeTG` - 15 edges

## Surprising Connections (you probably didn't know these)
- `Tomo Mascot Icon (maskable SVG)` --references--> `TOMO Tomato Design System`  [INFERRED]
  web/public/tomo.svg → README.md
- `_seed_user()` --calls--> `hash_password()`  [INFERRED]
  backend/app/seed.py → backend/app/core/security.py
- `TOMO Tomato Design System` --conceptually_related_to--> `Hand-Drawn SVG Charts`  [INFERRED]
  README.md → web/README.md
- `_month_range()` --calls--> `now_local()`  [INFERRED]
  backend/app/api/analytics.py → backend/app/core/clock.py
- `trend()` --calls--> `now_local()`  [INFERRED]
  backend/app/api/analytics.py → backend/app/core/clock.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Daily Automation Job Flow** — automation_scheduler, backend_app_scheduler, backend_app_services_recurring, backend_app_services_digest, backend_app_services_alerts, budgeting_engine [INFERRED 0.85]

## Communities (47 total, 7 thin omitted)

### Community 0 - "Web PWA Frontend"
Cohesion: 0.06
Nodes (85): App(), BudgetBar(), STATUS_COLOR, Bars(), Donut(), Slice, TrendBar, Layout() (+77 more)

### Community 1 - "Backend Domain Services"
Cohesion: 0.06
Nodes (55): now_local(), datetime, Waktu sekarang di zona lokal (default WIB, +7)., Budget, BudgetAlert, Budget total atau override per-periode.      - category_id NULL  = budget TOTAL, Catatan alert budget terkirim, agar tidak dobel (sekali per ambang/periode)., Category (+47 more)

### Community 2 - "Telegram Bot Dispatcher"
Cohesion: 0.11
Nodes (34): _authorized(), _budget_text(), _day_bounds(), _default_account(), _find_expense_category(), _handle_budget(), _handle_callback(), _handle_command() (+26 more)

### Community 3 - "Concepts & Domain Models"
Cohesion: 0.10
Nodes (29): Inter-Account Transfer, Learning Auto-Categorizer, Daily Scheduler Automation, KeywordRule, Aturan kata kunci -> kategori yang dipelajari dari koreksi user.      Setiap kal, _builtin_lookup(), _category_by_name(), learn_from_correction() (+21 more)

### Community 4 - "Frontend NPM Dependencies"
Cohesion: 0.06
Nodes (31): react, react-dom, react-router-dom, @tanstack/react-query, @types/react, @types/react-dom, typescript, vite (+23 more)

### Community 5 - "Quick-Add Parser"
Cohesion: 0.12
Nodes (29): _amount_value(), _clean_desc(), _detect_type(), _extract_date(), parse_amount(), parse_quick_input(), ParsedInput, datetime (+21 more)

### Community 6 - "Recurring Transactions"
Cohesion: 0.13
Nodes (23): create_recurring(), delete_recurring(), list_recurring(), Session, update_recurring(), Transaksi berulang bulanan (kos, langganan) yang dibuat otomatis scheduler., RecurringTx, BaseModel (+15 more)

### Community 7 - "Transactions API"
Cohesion: 0.13
Nodes (27): create_transaction(), create_transfer(), delete_transaction(), get_transaction(), list_transactions(), _month_range(), datetime, Session (+19 more)

### Community 8 - "OCR Receipt Extraction"
Cohesion: 0.11
Nodes (26): ocr_transaction(), Unggah foto struk → simpan + OCR → kembalikan draft untuk dikonfirmasi.      Dra, OCRDraft, OCRItem, OCRResult, BaseModel, ReceiptOut, _call_vision() (+18 more)

### Community 9 - "TypeScript Config"
Cohesion: 0.08
Nodes (25): DOM, DOM.Iterable, ES2021, src, vite/client, vite.config.ts, vite-plugin-pwa/client, compilerOptions (+17 more)

### Community 10 - "Analytics API"
Cohesion: 0.17
Nodes (19): _month_range(), datetime, Session, summary(), trend(), CategorySlice, BaseModel, SummaryOut (+11 more)

### Community 11 - "Telegram Webhook & Client"
Cohesion: 0.14
Nodes (7): Session, webhook(), Kembalikan file_path Telegram untuk file_id (langkah sebelum download)., Klien tipis untuk Telegram Bot API (mode webhook, panggilan sinkron)., TelegramClient, main(), Kelola webhook Telegram dari CLI.  Contoh:     python -m scripts.telegram_admin

### Community 12 - "Saving Goals"
Cohesion: 0.25
Nodes (15): contribute(), create_goal(), delete_goal(), list_goals(), Session, _to_out(), update_goal(), Target nabung: target + terkumpul + tenggat opsional. (+7 more)

### Community 13 - "Web API Client"
Cohesion: 0.18
Nodes (13): api, ApiError, getToken(), listeners, login(), onTokenChange(), req(), setToken() (+5 more)

### Community 14 - "Accounts API"
Cohesion: 0.24
Nodes (12): create_account(), delete_account(), list_accounts(), Account, Session, update_account(), Account, AccountBase (+4 more)

### Community 15 - "Categories API"
Cohesion: 0.27
Nodes (11): create_category(), delete_category(), list_categories(), Category, Session, update_category(), CategoryBase, CategoryCreate (+3 more)

### Community 16 - "Auth Dependencies"
Cohesion: 0.18
Nodes (8): me(), get_current_user(), Session, export_csv(), Session, User, FastAPI, StreamingResponse

### Community 17 - "Budgets API"
Cohesion: 0.32
Nodes (10): get_budgets(), get_safe_to_spend(), put_budget(), Session, _to_overview_out(), BudgetOverviewOut, BudgetSet, CategoryBudgetOut (+2 more)

### Community 18 - "Budget Bot Tests"
Cohesion: 0.29
Nodes (6): FakeTG, _msg(), test_budget_set_category(), test_budget_set_total_and_show(), test_budget_unknown_category(), test_quickadd_appends_safe_to_spend()

### Community 19 - "Bot Message Formatting"
Cohesion: 0.40
Nodes (7): esc(), format_rupiah(), datetime, Decimal, summary_text(), _tanggal_id(), tx_confirmation()

### Community 20 - "Security & Login (JWT)"
Cohesion: 0.25
Nodes (8): login(), Session, create_access_token(), decode_access_token(), hash_password(), Kembalikan subject (user id) jika token valid, None jika tidak., verify_password(), OAuth2PasswordRequestForm

### Community 22 - "Receipts API"
Cohesion: 0.38
Nodes (5): get_receipt(), get_receipt_image(), Session, Receipt, FileResponse

### Community 23 - "Schema Sync & Startup"
Cohesion: 0.29
Nodes (6): ensure_schema(), Penyesuaian skema ringan untuk kolom baru pada tabel yang sudah ada.  `create_al, lifespan(), db(), Session dengan skema bersih + data seed, untuk test service & bot., Engine

### Community 24 - "Database Seeding"
Cohesion: 0.57
Nodes (6): Session, Isi data awal sekali saat startup: user pertama, kategori default, akun cash.  I, seed(), _seed_account(), _seed_categories(), _seed_user()

### Community 25 - "Design & Delivery Concepts"
Cohesion: 0.29
Nodes (7): Hand-Drawn SVG Charts, JWT Bearer Authentication, Single-Origin PWA Serving, TOMO Tomato Design System, Web PWA HTML Entry Point, Tomo Mascot Icon (maskable SVG), Web PWA README (Phase 4)

### Community 26 - "FastAPI App Entrypoint"
Cohesion: 0.33
Nodes (3): StaticFiles dengan fallback ke index.html (client-side routing PWA)., SPAStaticFiles, StaticFiles

### Community 28 - "Database Session"
Cohesion: 0.40
Nodes (4): Base, get_db(), Session, DeclarativeBase

### Community 29 - "Auth Schemas"
Cohesion: 0.60
Nodes (4): LoginRequest, BaseModel, Token, UserOut

## Knowledge Gaps
- **59 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+54 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Quick-Add Text Parsing` connect `Concepts & Domain Models` to `Web PWA Frontend`, `Quick-Add Parser`?**
  _High betweenness centrality (0.225) - this node is a cross-community bridge._
- **Why does `Category` connect `Backend Domain Services` to `Telegram Bot Dispatcher`, `Concepts & Domain Models`, `Analytics API`, `Categories API`, `Budget Bot Tests`, `Database Seeding`, `Database Session`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Why does `suggest_category()` connect `Concepts & Domain Models` to `OCR Receipt Extraction`, `Backend Domain Services`, `Telegram Bot Dispatcher`, `Transactions API`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `overview()` (e.g. with `get_budgets()` and `get_safe_to_spend()`) actually correct?**
  _`overview()` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `Category` (e.g. with `delete_category()` and `list_categories()`) actually correct?**
  _`Category` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `Transaction` (e.g. with `export_csv()` and `delete_transaction()`) actually correct?**
  _`Transaction` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `handle_update()` (e.g. with `webhook()` and `test_callback_change_category_and_learn()`) actually correct?**
  _`handle_update()` has 13 INFERRED edges - model-reasoned connections that need verification._