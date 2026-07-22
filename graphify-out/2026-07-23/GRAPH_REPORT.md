# Graph Report - D:\Project\financeTracker  (2026-07-19)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 845 nodes · 1575 edges · 67 communities (51 shown, 16 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 186 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `091eba21`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- User
- Category
- suggest_category
- Account
- FastAPI
- package.json
- p
- admin.py
- period_summary
- run_due_recurring
- compilerOptions
- Manage.tsx
- MainActivity
- contribute
- ocr_transaction
- App.tsx
- queries.ts
- TelegramClient
- format.ts
- History.tsx
- api.ts
- test_multiuser.py
- FakeTG
- Icon.tsx
- get_budgets
- Dashboard.tsx
- account.py
- test_api.py
- Add.tsx
- transaction.py
- security.py
- analytics.py
- category.py
- goal.py
- receipt.py
- recurring.py
- test_analytics.py
- test_auth_security.py
- database.py
- test_ocr_account.py
- now_local
- Settings
- money.py
- colors.ts
- deploy.sh
- vite.config.ts
- Account
- Backend Python Dependencies
- Docker Compose (db + api services)
- OCRResult
- Tomato Celebration Page (refWeb)
- TransactionList
- User

## God Nodes (most connected - your core abstractions)
1. `User` - 65 edges
2. `Category` - 27 edges
3. `handle_update()` - 22 edges
4. `Transaction` - 22 edges
5. `overview()` - 22 edges
6. `Account` - 20 edges
7. `apply_balance()` - 18 edges
8. `compilerOptions` - 17 edges
9. `MainActivity` - 16 edges
10. `suggest_category()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `Tomo Mascot Icon (maskable SVG)` --references--> `TOMO Tomato Design System`  [INFERRED]
  web/public/tomo.svg → README.md
- `TOMO Tomato Design System` --conceptually_related_to--> `Hand-Drawn SVG Charts`  [INFERRED]
  README.md → web/README.md
- `list_transactions()` --calls--> `TransactionList`  [EXTRACTED]
  backend/app/api/transactions.py → web/src/lib/types.ts
- `ocr_transaction()` --calls--> `OCRResult`  [EXTRACTED]
  backend/app/api/transactions.py → web/src/lib/types.ts
- `admin()` --indirect_call--> `User`  [INFERRED]
  backend/tests/test_budget_bot.py → backend/app/models/user.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Daily Automation Job Flow** — automation_scheduler, backend_app_scheduler, backend_app_services_recurring, backend_app_services_digest, backend_app_services_alerts, budgeting_engine [INFERRED 0.85]

## Communities (67 total, 16 thin omitted)

### Community 0 - "User"
Cohesion: 0.07
Nodes (54): create_category(), delete_category(), list_categories(), Category, Session, update_category(), get_admin_user(), get_current_user() (+46 more)

### Community 1 - "Category"
Cohesion: 0.06
Nodes (55): Budget, BudgetAlert, Base, Budget total atau override per-periode.      - category_id NULL  = budget TOTAL, Catatan alert budget terkirim, agar tidak dobel (sekali per ambang/periode)., Category, Base, _already_sent() (+47 more)

### Community 2 - "suggest_category"
Cohesion: 0.06
Nodes (47): Inter-Account Transfer, Learning Auto-Categorizer, Daily Scheduler Automation, KeywordRule, Base, Aturan kata kunci -> kategori yang dipelajari dari koreksi user.      Setiap kal, _builtin_lookup(), _category_by_name() (+39 more)

### Community 3 - "Account"
Cohesion: 0.08
Nodes (47): AccountCreate, AccountUpdate, create_account(), delete_account(), list_accounts(), net_worth(), Account, Session (+39 more)

### Community 4 - "FastAPI"
Cohesion: 0.06
Nodes (32): Session, webhook(), ensure_schema(), Penyesuaian skema ringan untuk kolom baru pada tabel yang sudah ada.  `create_al, _check_security(), lifespan(), Session, Cegah deploy dengan kredensial/secret default.      - JWT_SECRET default + STATI (+24 more)

### Community 5 - "package.json"
Cohesion: 0.06
Nodes (31): react, react-dom, react-router-dom, @tanstack/react-query, @types/react, @types/react-dom, typescript, vite (+23 more)

### Community 6 - "p"
Cohesion: 0.12
Nodes (29): _amount_value(), _clean_desc(), _detect_type(), _extract_date(), parse_amount(), parse_quick_input(), ParsedInput, datetime (+21 more)

### Community 7 - "admin.py"
Cohesion: 0.14
Nodes (26): _admin_count(), create_user(), delete_user(), list_users(), Session, Dashboard admin: kelola user (khusus admin).  Buat/hapus user, reset password, j, _to_out(), update_user() (+18 more)

### Community 8 - "period_summary"
Cohesion: 0.13
Nodes (23): _month_range(), datetime, Session, summary(), trend(), esc(), format_rupiah(), datetime (+15 more)

### Community 9 - "run_due_recurring"
Cohesion: 0.14
Nodes (22): _assert_owned(), create_recurring(), delete_recurring(), list_recurring(), Session, update_recurring(), Base, Transaksi berulang bulanan (kos, langganan) yang dibuat otomatis scheduler. (+14 more)

### Community 10 - "compilerOptions"
Cohesion: 0.08
Nodes (25): DOM, DOM.Iterable, ES2021, src, vite/client, vite.config.ts, vite-plugin-pwa/client, compilerOptions (+17 more)

### Community 11 - "Manage.tsx"
Cohesion: 0.12
Nodes (25): useContributeGoal(), useDeleteAccount(), useDeleteCategory(), useDeleteGoal(), useDeleteRecurring(), useLinkCode(), useReconcile(), useRecurring() (+17 more)

### Community 12 - "MainActivity"
Cohesion: 0.13
Nodes (9): MainActivity, AppCompatActivity, Boolean, Bundle, Int, KeyEvent, ProgressBar, SwipeRefreshLayout (+1 more)

### Community 13 - "contribute"
Cohesion: 0.22
Nodes (18): _assert_owned_account(), contribute(), create_goal(), delete_goal(), _get_owned_goal(), list_goals(), Session, Tambah/tarik tabungan.      Bila akun sumber diberikan dan target punya akun tab (+10 more)

### Community 14 - "ocr_transaction"
Cohesion: 0.13
Nodes (17): get_receipt(), get_receipt_image(), Session, ocr_transaction(), Unggah foto struk → simpan + OCR → kembalikan draft untuk dikonfirmasi.      Dra, Base, Receipt, build_draft() (+9 more)

### Community 15 - "App.tsx"
Cohesion: 0.21
Nodes (14): App(), Layout(), AuthCtx, AuthProvider(), Ctx, useAuth(), useAdminUsers(), useCreateUser() (+6 more)

### Community 16 - "queries.ts"
Cohesion: 0.20
Nodes (16): TxFilters, Account, AdminUser, BudgetOverview, Category, LinkCode, NetWorth, OCRResult (+8 more)

### Community 17 - "TelegramClient"
Cohesion: 0.17
Nodes (5): Kembalikan file_path Telegram untuk file_id (langkah sebelum download)., Klien tipis untuk Telegram Bot API (mode webhook, panggilan sinkron)., TelegramClient, main(), Kelola webhook Telegram dari CLI.  Contoh:     python -m scripts.telegram_admin

### Community 18 - "format.ts"
Cohesion: 0.15
Nodes (9): BudgetBar(), STATUS_COLOR, Bars(), Slice, TrendBar, MONTHS, rupiah(), rupiahShort() (+1 more)

### Community 19 - "History.tsx"
Cohesion: 0.25
Nodes (11): PageHead(), Sheet(), TxEditSheet(), downloadCsv(), currentMonth(), useCategories(), useDeleteTransaction(), useInvalidateData() (+3 more)

### Community 20 - "api.ts"
Cohesion: 0.17
Nodes (8): Tomato(), api, ApiError, listeners, login(), req(), setToken(), token

### Community 21 - "test_multiuser.py"
Cohesion: 0.24
Nodes (11): _bob(), _makan(), Isolasi antar-user + guard admin — jaring pengaman multi-tenant.  Admin (user #1, Buat user 'bob' via admin, kembalikan header Authorization-nya., test_admin_guard_blocks_non_admin(), test_admin_reset_password_and_unlink(), test_cannot_attach_another_users_category_or_account(), test_me_reports_admin_flag() (+3 more)

### Community 22 - "FakeTG"
Cohesion: 0.26
Nodes (7): admin(), FakeTG, _msg(), test_budget_set_category(), test_budget_set_total_and_show(), test_budget_unknown_category(), test_quickadd_appends_safe_to_spend()

### Community 23 - "Icon.tsx"
Cohesion: 0.22
Nodes (10): CATEGORY_ICON, categoryIcon(), Icon(), IconName, NAME_ICON, P, ADMIN_TAB, Tab (+2 more)

### Community 24 - "get_budgets"
Cohesion: 0.32
Nodes (10): get_budgets(), get_safe_to_spend(), put_budget(), Session, _to_overview_out(), BudgetOverviewOut, BudgetSet, CategoryBudgetOut (+2 more)

### Community 25 - "Dashboard.tsx"
Cohesion: 0.32
Nodes (10): useBudgets(), useGoals(), useNetWorth(), useQuickAdd(), useSummary(), useTrend(), QuickMode(), Analytics() (+2 more)

### Community 26 - "account.py"
Cohesion: 0.29
Nodes (10): AccountBase, AccountCreate, AccountOut, AccountUpdate, NetWorthOut, BaseModel, Total kekayaan = jumlah saldo semua akun (+ rincian per akun)., Hasil rekonsiliasi: berapa akun dikoreksi + saldo terkini. (+2 more)

### Community 28 - "Add.tsx"
Cohesion: 0.36
Nodes (9): useAccounts(), useCreateTransaction(), useOcr(), useTransfer(), Add(), FormMode(), Mode, OcrMode() (+1 more)

### Community 29 - "transaction.py"
Cohesion: 0.39
Nodes (8): BaseModel, TransactionBase, TransactionCreate, TransactionList, TransactionOut, TransactionQuick, TransactionUpdate, TransferCreate

### Community 31 - "analytics.py"
Cohesion: 0.53
Nodes (5): CategorySlice, BaseModel, SummaryOut, TrendOut, TrendPoint

### Community 32 - "category.py"
Cohesion: 0.53
Nodes (5): CategoryBase, CategoryCreate, CategoryOut, CategoryUpdate, BaseModel

### Community 33 - "goal.py"
Cohesion: 0.53
Nodes (5): GoalContribute, GoalCreate, GoalOut, GoalUpdate, BaseModel

### Community 34 - "receipt.py"
Cohesion: 0.53
Nodes (5): OCRDraft, OCRItem, OCRResult, BaseModel, ReceiptOut

### Community 35 - "recurring.py"
Cohesion: 0.53
Nodes (5): BaseModel, RecurringBase, RecurringCreate, RecurringOut, RecurringUpdate

### Community 38 - "database.py"
Cohesion: 0.40
Nodes (4): Base, get_db(), Session, DeclarativeBase

### Community 39 - "test_ocr_account.py"
Cohesion: 0.60
Nodes (4): _account(), Regresi: transaksi tanpa akun tidak mengurangi saldo, tapi tetap muncul di anali, test_accountless_expense_shows_in_analytics_but_not_balance(), test_expense_created_with_account_reduces_balance()

### Community 40 - "now_local"
Cohesion: 0.67
Nodes (3): now_local(), datetime, Waktu sekarang di zona lokal (default WIB, +7).

## Knowledge Gaps
- **65 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+60 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `Account`, `FastAPI`, `admin.py`, `period_summary`, `run_due_recurring`, `contribute`, `ocr_transaction`, `FakeTG`, `get_budgets`?**
  _High betweenness centrality (0.201) - this node is a cross-community bridge._
- **Why does `Quick-Add Text Parsing` connect `suggest_category` to `Add.tsx`, `p`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Why does `list_transactions()` connect `Account` to `User`, `queries.ts`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `User` (e.g. with `_admin_count()` and `list_users()`) actually correct?**
  _`User` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `Category` (e.g. with `delete_category()` and `list_categories()`) actually correct?**
  _`Category` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `handle_update()` (e.g. with `webhook()` and `test_callback_change_category_and_learn()`) actually correct?**
  _`handle_update()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `Transaction` (e.g. with `_to_out()` and `export_csv()`) actually correct?**
  _`Transaction` has 20 INFERRED edges - model-reasoned connections that need verification._