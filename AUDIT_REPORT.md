# Smart CLI — Layihə Audit Hücumi

**Tarix:** 19.10.2026  
**Versiya:** 1.0.0 (stabil branch: `main`)  
**Auditor:** Cline (AI coding agent)  
**Dil:** Azərbaycan Türkçəsi

## 1. Giriş və Məqsəd

Bu sənətdə `smart-cli` layihəsinin funksional, arxitektural, təhlükəsizlik, test və davam etdirilə bilirlik səviyyəsi auditorluk edilib. Nəticədə “güclü” və “zəif” tərəflər müəyyən edilmiş, sonra “bu layihə mənim olsa necə davam edirdim, MVP nə qədər olmalı” sualına cavab verib davam etdirilə bilən bir yol xəttişi təklif edilib.

Audit əsas mənbəyində aşağıdakı faylların oxunması və real testlərin işlədilməsi var: `pyproject.toml`, `README.md`, `CHANGELOG.md`, `src/smart_cli.py`, `src/cli.py`, `src/core/*`, `src/agents/*`, `src/utils/*`, `tests/test_cli.py`, `tests/test_security.py`, `docs/*`, `.github/workflows/ci.yml`, `.pre-commit-config.yaml`, `SECURITY.md`, `Dockerfile`.

## 2. Layihənin Qısa Təsviri

Smart CLI — Python (3.9+) əsasında yazılmış, interaktiv AI-assistent CLI aləti. Əsas xüsusiyyətləri: Typer + Rich CLI interfeysi; çok-agent arxitektura (Orchestrator → Analyzer / Architect); PBKDF2 + Fernet ilə şifrələnmiş konfiqurasiya; hibrid cache (memory + SQLite + Redis opsional); sessiya və kontekst idarəsi; mod sistemi (`smart`, `code`, `analysis` stabil; `architect`, `learning`, `fast`, `orchestrator` eksperimental); AI cəhd optimizasiya və büdcə profilləri; GitHub enteqrasiyası; GitHub Actions CI (Python 3.9–3.12) + Codecov; Dockerfile və `.pre-commit-config.yaml`.

## 3. Güclü Tərəflər (Strengths)

### 3.1 Modular və təmiz arxitektura
Kod `src/core`, `src/agents`, `src/utils`, `src/handlers`, `src/integrations` kataloqlarına ayrılıb. Hər komponent (request routing, mode switching, caching, session management) ayrı moduldadır. Bu layihəni scaling və sürdürdürməyə yarayır.

### 3.2 Təhlükəsizlik (konfiqurasiya səviyyəsində)
- API açarları PBKDF2 + Fernet ilə şifrələnib (`secure_config.enc`)
- Kalit faylı (`config.key`) Unix-də `600` icazə ilə yaradılır (testdə yoxlanılır)
- `.env` avtomatik yüklənir, environment dəyişənləri priorit vardır
- GitHub token və API açarları `SECURITY.md` ilə dəstəklənir

### 3.3 Çok-agent sistemi və fallbackträge
`SmartCLIOrchestrator` sorğuları klassifaya edib düzgün agentə yönləndirir. AnalyzerAgent, ArchitectAgent, TesterAgent üçün fallback (yedek) məntiyi var — AI unavailable olmasa də sistem səslənir.

### 3.4 CLI interfeysi və interaktiv rejim
Typer ilə qurulmuş, `--help`, `--version`, `config show`, `config api-key` əmrləri işləyir. Interaktiv loop (`smart >`) git branch-ini və dəyişiklik sayı göstərir. Rich formatting ilə gözəl output.

### 3.5 Test infrastrukturası
- pytest + pytest-asyncio, marklər (unit, integration, e2e, performance, security, mode_system)
- `tests/test_cli.py` — 11 test, hepsi ✅
- `tests/test_security.py` — şifrləmə, icazələr, environment masking testləri
- End-to-end workflow testləri (fixture repo ilə)
- ExecutionLogger — machine-readable JSON workflow logları
- CI: Python 3.9–3.12 matrix, Codecov cobertura, `--cov-fail-under=80`

### 3.6 AI client mechanisms
`SimpleOpenRouterClient` retry + eksponentik backoff (429/500), fallback model handling, response caching, OpenRouter/Anthropic avtomatik seçimi.

### 3.7 Dokümentasiya
`ARCHITECTURE.md`, `ROADMAP.md`, `BACKLOG.md`, `MODE_SYSTEM.md`, `TESTING.md`, `RELEASE.md`, `SECURITY.md`, `CONTRIBUTING.md` hazır və ayrıntılı.

### 3.8 Real runtime dependensiyaları yoxlanıldı
`typer`, `rich`, `requests`, `yaml`, `cryptography`, `psutil`, `aiohttp` hepsi import edilir. `tests/test_cli.py` (11 test) və `tests/test_security.py` realda davam edirlər (37 test ✅).

## 4. Zəif Tərəflər (Weaknesses)

### 4.1 İmtina yolu (dual import) problemi — `src/smart_cli.py`
```python
try:
    from .agents.orchestrator import ...
except ImportError:
    from agents.orchestrator import ...
```
Bu pattern hər moduldə tekrarlanır. Paketoloji problemini gizlədib, debugging-ü qoradır. **Təsviyyə:** yalnız relative import saxla, `try/except ImportError` bloklarını silin.

### 4.2 “LEGACY METHODS”lərinin saxlanılması — `src/smart_cli.py`
`_get_user_input`, `_handle_ai_fallback`, `_process_ai_request` və digər “Replaced by RequestRouter” metodları müsavvədə qalıb. Bu dead code-dir. **Təsviyyə:** silin və ya `@deprecated` işarətləyin.

### 4.3 `cache.py`-də təhlükəsiz pickle serdekləşdirilməsi
Redis layer-unda `pickle.dumps(value)` / `pickle.loads(payload)` işlətilir. Bu RCE (remote code execution) təhlükəsini çəkir. **Təsviyyə:** Redis-u JSON-ə çevirin.

### 4.4 `ConfigManager` import zamanında side effect
`load_env_file_manual()` modulu import edildikdə işləyir. Bu test isolation-unu bozar. **Təsviyyə:** lazy-load edin və ya `load()` metodu ilə çağırın.

### 4.5 Hardcoded master key fallback
```python
password = os.environ.get("SMART_CLI_MASTER_KEY", "default-key-change-me")
```
Productionda təhlükə yaradır. **Təsviyyə:** default olmasın; `SMART_CLI_MASTER_KEY` tələb edilsin.

### 4.6 Fayl/terminal əməliyyatlarında sandbox yoxdur
`SimpleGitManager`, `SimpleTerminalManager`, `FileManager` istifadəçidən gələn əmrləri qoruma olmadan işləyə bilər. Realda sandbox qat义 yoxdur. **Təsviyyə:** read-only default, `--write` flag-ə explicit onay, command allowlist, path traversal qorunması.

### 4.7 AI provider qatısı hekkiqəti
Yalnız OpenRouter və Anthropic desteklənir. Gerçek multi-provider abstraction (OpenAI, Gemini, Azure, local LLM) yoxdur. **Təsviyyə:** provider adapter pattern və ya `litellm` inteqrasiyası.

### 4.8 Test qapsı (coverage) gercekdən əks etmir
`pytest.ini`-de `--cov-fail-under=80` var, ancaq full test suite timeout-a yatır (30s-də sona çalışmadı). Əsas testlər CLI və security layerindədir; `core/*`, `agents/*`, `utils/*` üçün unit test sayısı az. `test_security.py`-də əksər “real implementation” testləri `pass` ilə bitirilir. **Təsviyyə:** core/agents/utils üçün unit testlər artırın, `pass` testlərini reallaşdırın.

### 4.9 CI-da statik analiz yoxdur
`.github/workflows/ci.yml` yalnız test + coverage verir. bandit, flake8, mypy, black yalnız `.pre-commit-config.yaml`-da var, CI iş sessionuna daxil edilməyib. **Təsviyyə:** CI job-a lint/type/security scan əlavə edin.

### 4.10 Mod sistemi kismən eksperimental
`architect`, `learning`, `fast`, `orchestrator` modları “experimental” işarətdi; user-facing dəyər kəməydir. **Təsviyyə:** MVP-də stabil modların (`smart`, `code`, `analysis`) interfaces-ini dondurun, digərləri “experimental” package-ə ayırın.

### 4.11 API açarı validasyonu zəif
Yalnız `startswith(...)` və uzunluq yoxlanır. Gerçek açarın işləyip işləmədiyi test olunmur. **Təsviyyə:** lightweight connectivity check (models list endpoint) əlavə edin.

### 4.12 `agent_memory.py` filepath relative-dir
`memory_dir = Path(memory_dir or "cache/agent_memory")` — çalışma dizinindən asılıdır. **Təsviyyə:** `Path.home() / ".smart-cli"` və ya config_dir-əlaqəli absolute path istifadə edin.

### 4.13 Qeydiyyat (audit log) yoxdur
“Configuration changes should be logged” yazılıb ancaq realda `pass`. Kim, ne zaman, hansı açarı dəyişdirmişə dair real audit journal yoxdur. **Təsviyyə:** immutable audit log əlavə edin.

### 4.14 i18n / l10n problemi
Identity sorğuları Azərbaycan Türkçəsi + İngilis dilində (`kim sənsən`, `who are users`). Bu çatışma yaradır. **Təsviyyə:** dil secimi və message catalog.

### 4.15 Plugin / genişləndirme sistemi yoxdur
Yeni komandalar və agentlar elave etmək üçün resmi plugin API yoxdur.

## 5. Təhlükəsizlik Xülasəsi (Security Summary)

| Əsas sektor | Status | Təsviyyə |
|---|---|---|
| API açarı şifrləməsi | ✅ Güclü | Master key default-unu kaldırın |
| Fayl icazələri | ✅ 600 key/secure file | Bütün konfiq faylları 600 olsun |
| Redis serialization | ⚠️ Riskli | `pickle` → JSON |
| Sandbox / command injection | ❌ Yoxdur | Read-only default + allowlist |
| Audit log | ❌ Yoxdur | Konfiq dəyişikliklərinin jurnalı |
| AI provider abstraction | ⚠️ Kismən | Multi-provider adapter |
| Secrets scanning | ✅ `.secrets.baseline` | CI-da detect-secretsə çevirin |
| SAST (bandit) | ⚠️ Yalnız pre-commit | CI workflow-ya əlavə edin |

## 6. Əgər Bu Layihə Mənim Olsaydı, Necə Davam Etdirdim? (Mənim Əsas Təkmilləşdirmələrim)

1. **Dual import bloklarını sil**, yalnız relative import saxla.
2. **Dead code-u təmizlə** (`LEGACY METHODS`).
3. **Cache-də `pickle`-dən istifadə dayandırın** (JSON və ya memory/sqlite-only).
4. **Config-loader-u lazy edin**, `SMART_CLI_MASTER_KEY` tələb edin.
5. **File/terminal əməliyyatlarına read-only default və `--write` onay qatını əlavə edin.**
6. **Core/agents/utils üçün unit testlər yazın**, `pass` testlərini reallaşdırın.
7. **CI-də bandit + flake8 + mypy + pre-commit run əlavə edin.**
8. **Audit journal (config dəyişiklik jurnalı) yaradın.**
9. **Provider abstraction (litellm və ya adapter pattern) daxil edin.**
10. **Mod systemini stationarye çevirin** (`smart`, `code`, `analysis` → stable; digərlərini “experimental” package-ə ayır).

## 7. MVP (Minimum Viable Product) — Nə Olmalıdır?

Layihə artıq v1.0.0, ancaq davam etmək üçün “stabil MVP” dəyərini aşağıdakı etmək mantıqlıdır.

### MVP faydalı yaradıcısı (value proposition)
> “Əməliyyat sistemi integral olmaqla, API açarlarını təhlükəsiz saxlayan, multi-agent (analiz+arhitektura) Dürstəklə interaktiv CLI-assistent.”

### MVP funksional əlaqəsi (P1 — must-have)
1. **CLI Entry Point** (`smart`): `--help`, `--version`, `config show`, `config api-key <key>`, interaktiv `smart >` loop
2. **Secure Config**: PBKDF2+Fernet şifrləmə, `config.key` (600), `.env` load, `SMART_CLI_MASTER_KEY` tələbin, audit journal
3. **AI Client**: OpenRouter/Anthropic, retry+backoff, fallback model, response cache (memory+SQLite, pickle yox), provider interface
4. **Session + Context**: session başlat/bitir, tarixçə, kontekst optimizasiya
5. **Orchestrator + Analyzer + Architect**: sorğu klassifikasiya, fallbackträge, read-only default
6. **File/Git/Terminal**: read-only fayl oxuma, `git status`, sadə emr çalıştırma (`--write` əgər icazə verilsə), path traversal qorunması
7. **Test Suite**: pytest, CLI + security + core/agents/utils unit testləri, coverage ≥80%, `--cov-fail-under=80`
8. **CI/CD**: GitHub Actions (Python 3.9–3.12), test+coverage+Codecov, bandit+flake8+mypy+pre-commit
9. **Docker**: Dockerfile, `.dockerignore`, `docker run` əməliyyatı
10. **Dokumentasiya**: README, ARCHITECTURE, SECURITY, CONTRIBUTING, ROADMAP (kısa)

### MVP olmayan (P2+ — sonra)
- Multi-provider (OpenAI, Gemini, local LLM)
- Parallel agent execution
- Real sandboxing (Docker container per command)
- Plugin sistemi
- Batch workflows
- Cost tracking/dashboard
- i18n

### MVP uğrul criterionu
- `smart --help` və `smart version` işləyir
- `smart config api-key sk-...` şifrələnib yadda saxlanılır və oxunur
- `smart > analyze this codebase` → orchestrator → analyzer → cavab (fallback ilə də)
- `pytest` → ≥80% coverage, hepsi ✅
- CI yeşil keçir (test + bandit + flake8 + mypy)
- `docker build -t smart-cli .` uğurlu olur

## 8. Davam Etmək Üçün Yol Xəttişi (Roadmap)

| P | Həftə | Məqsəd | Əsas Tapşırıqlar |
|---|-------|--------|------------------|
| P1 | 1–2 | **Stabil MVP** | Dual import silinmə, legacy metodların törənməsi, pickle → JSON, master key tələbin, read-only default, unit testlər, CI security scan |
| P1 | 3–4 | **MVP təkmilləşdirmə** | Audit journal, provider interface (litellm/adapter), mod sistemi stationarye çevrilmə, Docker publish |
| P2 | 5–6 | **Təhlükəsizlik** | Real sandbox (container), command allowlist, secret rotation, connectivity check |
| P2 | 7–8 | **Test genişləndirilməsi** | E2E workflow testləri, performance benchmark, security penetration |
| P3 | 9–10 | **Multi-provider** | OpenAI, Google Gemini, local LLM adapter, model seçimi UI |
| P3 | 11–12 | **Uzandırmaq** | Parallel agent execution, cost tracking dashboard, plugin sistemi |

## 9. Nəticə

Smart CLI — ciddi bir potensial sahib, modulyar, təhlükəsiz konfiqurasiya və testli bir CLI alətidir. Asılı problemlər meestal arxitektural (dual import, legacy code) və təhlükəsizlik (pickle, sandbox, audit log) səviyyəsindədir. MVP-ni göstərdiyi kimi donduraraq, static analysis-i CI-ə daxil edərək və core/agents/utils test qapsını artıraraq layihəni istiqamətli şekilde davam ettirmək olar.

Bu sənəd layihənin cari vəziyyətinin referansıdır və sonraki sprintlər üçün əsasalqaldır bilər.
