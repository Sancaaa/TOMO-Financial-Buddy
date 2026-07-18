# Graph Report - .  (2026-07-18)

## Corpus Check
- 21 files · ~25,717 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 721 nodes · 1329 edges · 48 communities (34 shown, 14 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 178 edges (avg confidence: 0.79)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Web PWA Components
- Accounts, Transactions & Net Worth API
- Auth Deps, Export & Schema Sync
- Telegram Bot Dispatcher
- Budgeting Engine
- OCR Receipt Extraction
- Categories & Keyword Rules
- Analytics & Bot Formatting
- Frontend NPM Dependencies
- Recurring Transactions
- Web App Shell & API Client
- TypeScript / Vite Config
- Saving Goals (money-linked)
- Telegram Webhook & Client
- Database & Budget Alerts
- Quick-Add Parser
- Parser Tests
- Auth: Login, Change-Password, Rate-Limit
- Scheduler & Daily Digest
- Budget Bot Tests
- Transactions/Timezone API Tests
- Budget Semantics Tests
- Transaction Schemas
- Receipt/OCR Schemas
- Analytics Tests
- Auth Security Tests
- App Configuration
- Vite Dev Proxy
- Account (model)
- Transaction (model)
- Category (model)
- Transaction (ref)
- Backend Python Deps
- Docker Compose
- OCRResult (schema)
- Tomato Celebration Page
- TransactionList (schema)

## God Nodes (most connected - your core abstractions)
1. `overview()` - 21 edges
2. `handle_update()` - 20 edges
3. `compilerOptions` - 17 edges
4. `apply_balance()` - 17 edges
5. `TelegramClient` - 15 edges
6. `Transaction` - 15 edges
7. `suggest_category()` - 15 edges
8. `FakeTG` - 15 edges
9. `p()` - 15 edges
10. `Account` - 15 edges

## Surprising Connections (you probably didn't know these)
- `Tomo Mascot Icon (maskable SVG)` --references--> `TOMO Tomato Design System`  [INFERRED]
  web/public/tomo.svg → README.md
- `TOMO Tomato Design System` --conceptually_related_to--> `Hand-Drawn SVG Charts`  [INFERRED]
  README.md → web/README.md
- `list_transactions()` --calls--> `TransactionList`  [EXTRACTED]
  backend/app/api/transactions.py → web/src/lib/types.ts
- `create_transaction()` --calls--> `Transaction`  [EXTRACTED]
  backend/app/api/transactions.py → web/src/lib/types.ts
- `quick_add()` --calls--> `Transaction`  [EXTRACTED]
  backend/app/api/transactions.py → web/src/lib/types.ts

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Daily Automation Job Flow** — automation_scheduler, backend_app_scheduler, backend_app_services_recurring, backend_app_services_digest, backend_app_services_alerts, budgeting_engine [INFERRED 0.85]

## Communities (48 total, 14 thin omitted)

### Community 0 - "Web PWA Components"
Cohesion: 0.05
Nodes (82): BudgetBar(), STATUS_COLOR, Bars(), Donut(), Slice, TrendBar, PageHead(), Sheet() (+74 more)

### Community 1 - "Accounts, Transactions & Net Worth API"
Cohesion: 0.06
Nodes (51): Account, create_account(), delete_account(), list_accounts(), net_worth(), Session, Total kekayaan bersih = jumlah saldo semua akun.      Transfer & tabungan-goal a, Hitung ulang saldo dari transaksi; koreksi bila ada yang meleset. (+43 more)

### Community 2 - "Auth Deps, Export & Schema Sync"
Cohesion: 0.05
Nodes (35): get_current_user(), Session, export_csv(), Session, get_receipt(), get_receipt_image(), Session, ensure_schema() (+27 more)

### Community 3 - "Telegram Bot Dispatcher"
Cohesion: 0.10
Nodes (37): _authorized(), _budget_text(), _day_bounds(), _default_account(), _find_expense_category(), _handle_budget(), _handle_callback(), _handle_command() (+29 more)

### Community 4 - "Budgeting Engine"
Cohesion: 0.10
Nodes (35): get_budgets(), get_safe_to_spend(), put_budget(), Session, _to_overview_out(), BudgetOverviewOut, BudgetSet, CategoryBudgetOut (+27 more)

### Community 5 - "OCR Receipt Extraction"
Cohesion: 0.08
Nodes (36): Inter-Account Transfer, Learning Auto-Categorizer, Daily Scheduler Automation, _call_vision(), extract_receipt(), _parse(), datetime, Decimal (+28 more)

### Community 6 - "Categories & Keyword Rules"
Cohesion: 0.10
Nodes (29): create_category(), delete_category(), list_categories(), Category, Session, update_category(), Category, KeywordRule (+21 more)

### Community 7 - "Analytics & Bot Formatting"
Cohesion: 0.12
Nodes (26): _month_range(), datetime, Session, summary(), trend(), esc(), format_rupiah(), datetime (+18 more)

### Community 8 - "Frontend NPM Dependencies"
Cohesion: 0.06
Nodes (31): react, react-dom, react-router-dom, @tanstack/react-query, @types/react, @types/react-dom, typescript, vite (+23 more)

### Community 9 - "Recurring Transactions"
Cohesion: 0.13
Nodes (23): create_recurring(), delete_recurring(), list_recurring(), Session, update_recurring(), Transaksi berulang bulanan (kos, langganan) yang dibuat otomatis scheduler., RecurringTx, BaseModel (+15 more)

### Community 10 - "Web App Shell & API Client"
Cohesion: 0.13
Nodes (20): App(), Layout(), TABS, Tomato(), api, ApiError, getToken(), listeners (+12 more)

### Community 11 - "TypeScript / Vite Config"
Cohesion: 0.08
Nodes (25): DOM, DOM.Iterable, ES2021, src, vite/client, vite.config.ts, vite-plugin-pwa/client, compilerOptions (+17 more)

### Community 12 - "Saving Goals (money-linked)"
Cohesion: 0.22
Nodes (17): contribute(), create_goal(), delete_goal(), list_goals(), Session, Tambah/tarik tabungan.      Bila akun sumber diberikan dan target punya akun tab, _to_out(), update_goal() (+9 more)

### Community 13 - "Telegram Webhook & Client"
Cohesion: 0.14
Nodes (7): Session, webhook(), Kembalikan file_path Telegram untuk file_id (langkah sebelum download)., Klien tipis untuk Telegram Bot API (mode webhook, panggilan sinkron)., TelegramClient, main(), Kelola webhook Telegram dari CLI.  Contoh:     python -m scripts.telegram_admin

### Community 14 - "Database & Budget Alerts"
Cohesion: 0.16
Nodes (14): Base, get_db(), Session, Budget, BudgetAlert, Budget total atau override per-periode.      - category_id NULL  = budget TOTAL, Catatan alert budget terkirim, agar tidak dobel (sekali per ambang/periode)., _already_sent() (+6 more)

### Community 15 - "Quick-Add Parser"
Cohesion: 0.23
Nodes (15): _amount_value(), _clean_desc(), _detect_type(), _extract_date(), parse_amount(), parse_quick_input(), ParsedInput, datetime (+7 more)

### Community 16 - "Parser Tests"
Cohesion: 0.26
Nodes (14): p(), test_backdate_hari_lalu(), test_backdate_kemarin(), test_backdate_tanggal(), test_dot_thousands(), test_filler_prefix_stripped(), test_income_keyword(), test_juta_comma_decimal() (+6 more)

### Community 17 - "Auth: Login, Change-Password, Rate-Limit"
Cohesion: 0.22
Nodes (12): change_password(), login(), me(), Session, _recent_fails(), LoginRequest, PasswordChange, BaseModel (+4 more)

### Community 18 - "Scheduler & Daily Digest"
Cohesion: 0.22
Nodes (12): build_scheduler(), daily_job(), _prev_period(), datetime, Scheduler in-process (APScheduler): recurring tx, digest harian, alert budget, r, _send(), build_daily_digest(), build_period_review() (+4 more)

### Community 19 - "Budget Bot Tests"
Cohesion: 0.29
Nodes (6): FakeTG, _msg(), test_budget_set_category(), test_budget_set_total_and_show(), test_budget_unknown_category(), test_quickadd_appends_safe_to_spend()

### Community 21 - "Budget Semantics Tests"
Cohesion: 0.33
Nodes (9): _cat_id(), _makan_id(), _spend_today(), test_budget_alerts_dedup(), test_budget_default_derived_from_categories(), test_budget_overview_and_safe_to_spend(), test_budget_status_transitions(), test_derived_total_counts_only_budgeted_spending() (+1 more)

### Community 22 - "Transaction Schemas"
Cohesion: 0.39
Nodes (8): BaseModel, TransactionBase, TransactionCreate, TransactionList, TransactionOut, TransactionQuick, TransactionUpdate, TransferCreate

### Community 23 - "Receipt/OCR Schemas"
Cohesion: 0.53
Nodes (5): OCRDraft, OCRItem, OCRResult, BaseModel, ReceiptOut

## Knowledge Gaps
- **60 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+55 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `apply_balance()` connect `Accounts, Transactions & Net Worth API` to `Recurring Transactions`, `Telegram Bot Dispatcher`, `Saving Goals (money-linked)`?**
  _High betweenness centrality (0.127) - this node is a cross-community bridge._
- **Why does `Transaction` connect `Web PWA Components` to `Accounts, Transactions & Net Worth API`?**
  _High betweenness centrality (0.117) - this node is a cross-community bridge._
- **Why does `_handle_quick_add()` connect `Telegram Bot Dispatcher` to `Accounts, Transactions & Net Worth API`, `Budgeting Engine`, `Categories & Keyword Rules`, `Quick-Add Parser`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `overview()` (e.g. with `get_budgets()` and `get_safe_to_spend()`) actually correct?**
  _`overview()` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `handle_update()` (e.g. with `webhook()` and `test_callback_change_category_and_learn()`) actually correct?**
  _`handle_update()` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `apply_balance()` (e.g. with `contribute()` and `create_transaction()`) actually correct?**
  _`apply_balance()` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `TelegramClient` (e.g. with `webhook()` and `_send()`) actually correct?**
  _`TelegramClient` has 3 INFERRED edges - model-reasoned connections that need verification._