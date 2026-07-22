# Graph Report - financeTracker  (2026-07-23)

## Corpus Check
- 119 files · ~54,495 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 936 nodes · 1951 edges · 70 communities (52 shown, 18 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 266 edges (avg confidence: 0.79)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7efb874a`
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
- Quick-Add Text Parsing
- Saving Goals
- Single-Origin PWA Serving

## God Nodes (most connected - your core abstractions)
1. `User` - 72 edges
2. `now_local()` - 28 edges
3. `Category` - 27 edges
4. `overview()` - 27 edges
5. `Transaction` - 25 edges
6. `handle_update()` - 22 edges
7. `Account` - 20 edges
8. `rupiah()` - 19 edges
9. `apply_balance()` - 18 edges
10. `MainActivity` - 17 edges

## Surprising Connections (you probably didn't know these)
- `Tomo Mascot Icon (maskable SVG)` --references--> `TOMO Tomato Design System`  [INFERRED]
  web/public/tomo.svg → README.md
- `admin()` --indirect_call--> `User`  [INFERRED]
  backend/tests/test_budget_bot.py → backend/app/models/user.py
- `test_cycle_bounds_custom_day()` --calls--> `_bounds()`  [INFERRED]
  backend/tests/test_budget.py → backend/app/services/budget.py
- `test_cycle_bounds_default_unchanged()` --calls--> `_bounds()`  [INFERRED]
  backend/tests/test_budget.py → backend/app/services/budget.py
- `_to_out()` --indirect_call--> `Transaction`  [INFERRED]
  backend/app/api/admin.py → backend/app/models/transaction.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Daily Automation Job Flow** — automation_scheduler, backend_app_scheduler, backend_app_services_recurring, backend_app_services_digest, backend_app_services_alerts, budgeting_engine [INFERRED 0.85]

## Communities (70 total, 18 thin omitted)

### Community 0 - "User"
Cohesion: 0.07
Nodes (58): _budget_text(), _day_bounds(), _default_account(), _find_expense_category(), _handle_budget(), _handle_callback(), _handle_command(), _handle_link() (+50 more)

### Community 1 - "Category"
Cohesion: 0.07
Nodes (54): Base, get_db(), Session, Budget, BudgetAlert, Budget total atau override per-periode.      - category_id NULL  = budget TOTAL, Catatan alert budget terkirim, agar tidak dobel (sekali per ambang/periode)., Category (+46 more)

### Community 2 - "suggest_category"
Cohesion: 0.14
Nodes (19): KeywordRule, Aturan kata kunci -> kategori yang dipelajari dari koreksi user.      Setiap kal, _builtin_lookup(), _category_by_name(), learn_from_correction(), Category, Session, Tebak kategori transaksi dari deskripsi, dan belajar dari koreksi user.  Urutan (+11 more)

### Community 3 - "Account"
Cohesion: 0.07
Nodes (57): create_account(), delete_account(), list_accounts(), net_worth(), Account, Session, Total kekayaan bersih = jumlah saldo semua akun.      Transfer & tabungan-goal a, Hitung ulang saldo dari transaksi; koreksi bila ada yang meleset. (+49 more)

### Community 4 - "FastAPI"
Cohesion: 0.11
Nodes (18): ensure_schema(), Penyesuaian skema ringan untuk kolom baru pada tabel yang sudah ada.  `create_al, _check_security(), lifespan(), Session, Cegah deploy dengan kredensial/secret default.      - JWT_SECRET default + STATI, StaticFiles dengan fallback ke index.html (client-side routing PWA)., SPAStaticFiles (+10 more)

### Community 5 - "package.json"
Cohesion: 0.06
Nodes (34): react, react-dom, react-router-dom, @tanstack/react-query, @types/react, @types/react-dom, typescript, vite (+26 more)

### Community 6 - "p"
Cohesion: 0.12
Nodes (29): _amount_value(), _clean_desc(), _detect_type(), _extract_date(), parse_amount(), parse_quick_input(), ParsedInput, datetime (+21 more)

### Community 7 - "admin.py"
Cohesion: 0.34
Nodes (12): _admin_count(), create_user(), delete_user(), list_users(), Session, Dashboard admin: kelola user (khusus admin).  Buat/hapus user, reset password, j, _to_out(), update_user() (+4 more)

### Community 8 - "period_summary"
Cohesion: 0.11
Nodes (39): comparison(), heatmap(), _month_range(), datetime, Session, summary(), top_merchants_endpoint(), trend() (+31 more)

### Community 9 - "run_due_recurring"
Cohesion: 0.12
Nodes (24): _assert_owned(), create_recurring(), delete_recurring(), list_recurring(), Session, update_recurring(), Transaksi berulang bulanan (kos, langganan) yang dibuat otomatis scheduler., RecurringTx (+16 more)

### Community 10 - "compilerOptions"
Cohesion: 0.08
Nodes (25): DOM, DOM.Iterable, ES2021, src, vite/client, vite.config.ts, vite-plugin-pwa/client, compilerOptions (+17 more)

### Community 11 - "Manage.tsx"
Cohesion: 0.14
Nodes (22): useCycle(), useDeleteAccount(), useDeleteCategory(), useDeleteGoal(), useDeleteRecurring(), useLinkCode(), useSaveAccount(), useSaveCategory() (+14 more)

### Community 12 - "MainActivity"
Cohesion: 0.13
Nodes (9): MainActivity, AppCompatActivity, Boolean, Bundle, Int, KeyEvent, ProgressBar, SwipeRefreshLayout (+1 more)

### Community 13 - "contribute"
Cohesion: 0.23
Nodes (18): _assert_owned_account(), contribute(), create_goal(), delete_goal(), _get_owned_goal(), list_goals(), Session, Tambah/tarik tabungan.      Bila akun sumber diberikan dan target punya akun tab (+10 more)

### Community 14 - "ocr_transaction"
Cohesion: 0.09
Nodes (29): ocr_transaction(), Unggah foto struk → simpan + OCR → kembalikan draft untuk dikonfirmasi.      Dra, OCRDraft, OCRItem, OCRResult, BaseModel, ReceiptOut, _call_vision() (+21 more)

### Community 15 - "App.tsx"
Cohesion: 0.08
Nodes (23): Backend — TOMO (友) · Fase 1–6, Budgeting & otomasi (Fase 5), Catatan, Endpoint (Fase 1), Fase 6 (opsional), Menjalankan dengan Docker (disarankan), Menjalankan lokal (tanpa Docker, untuk dev), Menjalankan test (+15 more)

### Community 16 - "queries.ts"
Cohesion: 0.14
Nodes (26): TxFilters, useAdminUsers(), useCreateUser(), useDeleteUser(), useUpdateUser(), Account, AdminUser, BudgetOverview (+18 more)

### Community 17 - "TelegramClient"
Cohesion: 0.14
Nodes (7): Session, webhook(), Kembalikan file_path Telegram untuk file_id (langkah sebelum download)., Klien tipis untuk Telegram Bot API (mode webhook, panggilan sinkron)., TelegramClient, main(), Kelola webhook Telegram dari CLI.  Contoh:     python -m scripts.telegram_admin

### Community 18 - "format.ts"
Cohesion: 0.17
Nodes (19): Bars(), Donut(), Slice, TrendBar, Heatmap(), WD, dateLabel(), monthLong() (+11 more)

### Community 19 - "History.tsx"
Cohesion: 0.48
Nodes (5): PageHead(), downloadCsv(), currentMonth(), useTransactions(), History()

### Community 20 - "api.ts"
Cohesion: 0.11
Nodes (25): App(), IconName, ADMIN_TAB, Layout(), Tab, TABS, Tomato(), api (+17 more)

### Community 21 - "test_multiuser.py"
Cohesion: 0.24
Nodes (11): _bob(), _makan(), Isolasi antar-user + guard admin — jaring pengaman multi-tenant.  Admin (user #1, Buat user 'bob' via admin, kembalikan header Authorization-nya., test_admin_guard_blocks_non_admin(), test_admin_reset_password_and_unlink(), test_cannot_attach_another_users_category_or_account(), test_me_reports_admin_flag() (+3 more)

### Community 22 - "FakeTG"
Cohesion: 0.26
Nodes (7): admin(), FakeTG, _msg(), test_budget_set_category(), test_budget_set_total_and_show(), test_budget_unknown_category(), test_quickadd_appends_safe_to_spend()

### Community 23 - "Icon.tsx"
Cohesion: 0.33
Nodes (5): CATEGORY_ICON, Icon(), NAME_ICON, P, Sheet()

### Community 24 - "get_budgets"
Cohesion: 0.22
Nodes (17): get_alerts(), get_budgets(), get_cycle(), get_safe_to_spend(), put_budget(), put_cycle(), Session, Status ambang budget saat ini untuk banner web (read-only, tanpa dedup). (+9 more)

### Community 25 - "Dashboard.tsx"
Cohesion: 0.19
Nodes (17): BudgetBar(), STATUS_COLOR, categoryIcon(), TxList(), CATEGORY_COLORS, categoryColor(), FALLBACK, rupiah() (+9 more)

### Community 26 - "account.py"
Cohesion: 0.12
Nodes (20): _cat_id(), _future_day_this_month(), _makan_id(), date, Tanggal di bulan berjalan yang >= hari ini (untuk next_run recurring)., test_alerts_endpoint_readonly(), test_budget_default_derived_from_categories(), test_budget_overview_and_safe_to_spend() (+12 more)

### Community 28 - "Add.tsx"
Cohesion: 0.23
Nodes (16): TxEditSheet(), todayInput(), useAccounts(), useCategories(), useContributeGoal(), useCreateTransaction(), useDeleteTransaction(), useInvalidateData() (+8 more)

### Community 29 - "transaction.py"
Cohesion: 0.17
Nodes (10): get_admin_user(), get_current_user(), Session, Batasi endpoint ke admin (kelola user)., export_csv(), Session, decode_access_token(), Kembalikan subject (user id) jika token valid, None jika tidak. (+2 more)

### Community 30 - "security.py"
Cohesion: 0.22
Nodes (12): change_password(), create_link_code(), login(), me(), Session, Buat kode sekali-pakai; user kirim `/link <kode>` ke bot untuk menautkan chat., _recent_fails(), unlink_telegram() (+4 more)

### Community 31 - "analytics.py"
Cohesion: 0.40
Nodes (7): esc(), format_rupiah(), datetime, Decimal, summary_text(), _tanggal_id(), tx_confirmation()

### Community 32 - "category.py"
Cohesion: 0.27
Nodes (11): create_category(), delete_category(), list_categories(), Category, Session, update_category(), CategoryBase, CategoryCreate (+3 more)

### Community 33 - "goal.py"
Cohesion: 0.38
Nodes (7): SwipeAction, SwipeRow(), clampOffset(), detectIntent(), Intent, resolveOffset(), tapAction()

### Community 34 - "receipt.py"
Cohesion: 0.39
Nodes (8): AdminUserUpdate, LinkCodeOut, LoginRequest, PasswordChange, BaseModel, Token, UserCreate, UserOut

### Community 35 - "recurring.py"
Cohesion: 0.33
Nodes (4): _cleanup_db(), ID admin ter-seed — dipakai test service/model yang butuh user_id., _remove_db(), uid()

### Community 36 - "test_analytics.py"
Cohesion: 0.15
Nodes (14): get_receipt(), get_receipt_image(), Session, Receipt, _cid(), _mk(), test_comparison_down_reports_saver_category(), test_comparison_none_when_no_prev() (+6 more)

### Community 38 - "database.py"
Cohesion: 0.67
Nodes (3): TOMO Tomato Design System, Web PWA HTML Entry Point, Tomo Mascot Icon (maskable SVG)

### Community 39 - "test_ocr_account.py"
Cohesion: 0.60
Nodes (4): _account(), Regresi: transaksi tanpa akun tidak mengurangi saldo, tapi tetap muncul di anali, test_accountless_expense_shows_in_analytics_but_not_balance(), test_expense_created_with_account_reduces_balance()

## Knowledge Gaps
- **98 isolated node(s):** `deploy.sh script`, `name`, `private`, `version`, `type` (+93 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `admin.py` to `category.py`, `User`, `Category`, `Account`, `test_analytics.py`, `FastAPI`, `recurring.py`, `period_summary`, `run_due_recurring`, `contribute`, `ocr_transaction`, `FakeTG`, `get_budgets`, `transaction.py`, `security.py`?**
  _High betweenness centrality (0.161) - this node is a cross-community bridge._
- **Why does `now_local()` connect `User` to `Category`, `Account`, `period_summary`, `run_due_recurring`, `contribute`, `ocr_transaction`, `account.py`, `security.py`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `Category` connect `Category` to `category.py`, `User`, `suggest_category`, `Account`, `FastAPI`, `period_summary`, `run_due_recurring`, `FakeTG`, `account.py`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `User` (e.g. with `_admin_count()` and `list_users()`) actually correct?**
  _`User` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `now_local()` (e.g. with `_month_range()` and `trend()`) actually correct?**
  _`now_local()` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 26 inferred relationships involving `Category` (e.g. with `delete_category()` and `list_categories()`) actually correct?**
  _`Category` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `overview()` (e.g. with `get_budgets()` and `get_safe_to_spend()`) actually correct?**
  _`overview()` has 12 INFERRED edges - model-reasoned connections that need verification._