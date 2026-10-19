# Smart CLI — MVP Yol Xəttişi və Davam Etmə Planı

**Tarix:** 19.10.2026  
**Əsas sənəd:** `AUDIT_REPORT.md`  
**Məqsəd:** Auditin nəticəsində müəyyən edilmiş zəif tərfələri düzəldib, stabil bir MVP sürüşdürmək və sonra 3 qatlı yol xətti ilə developer etmək.

## 1. Həvârș Cəlbesi (Problem Tənqidi)

Auditte görülən əsas məhdudiyyətlər:

1. `src/smart_cli.py`-də dual `try/except ImportError` import (her moduldə tekrarlanır)
2. “LEGACY METHODS” — `_get_user_input`, `_handle_ai_fallback`, `_process_ai_request` dead code
3. `cache.py`-də `pickle` (Redis-də RCE riski)
4. `ConfigManager` import zamanında side effect (`load_env_file_manual()`)
5. Hardcoded master key fallback `"default-key-change-me"`
6. File/terminal əməliyyatlarında sandbox yoxdur (read-only default yox)
7. AI provider yalnız OpenRouter/Anthropic (multi-provider yox)
8. Core/agents/utils unit test qapsı az; `test_security.py`-də `pass` testləri
9. CI-də bandit/flake8/mypy/pre-commit yox (yalız test + coverage)
10. Mod sistemi kismən eksperimental; stabilize etmək lazımdır
11. Konfiq dəyişikliklərinin audit journalı yoxdur

## 2. MVP (Minimum Viable Product)

### 2.1 Məqsəd
> “Əməliyyat sistemi integral olmaqla, API açarlarını təhlükəsiz saxlayan, multi-agent (analiz+arhitektura) Dürstəklə interaktiv CLI-assistent.”

### 2.2 MVP funksional siyahısı (P1 — obligatori)

| № | Modul | Təsmil edilməli olan |
|---|-------|---------------------|
| 1 | **CLI Entry Point** | `smart --help`, `--version`, `config show`, `config api-key <key>`, interaktiv `smart >` loop |
| 2 | **Secure Config** | PBKDF2+Fernet şifrləmə, `config.key` (600), `.env` load, `SMART_CLI_MASTER_KEY` tələbin, audit journal |
| 3 | **AI Client** | OpenRouter/Anthropic, retry+backoff, fallback model, response cache (memory+SQLite, pickle yox), provider interface |
| 4 | **Session + Context** | session başlat/bitir, tarixçə, kontekst optimizasiya |
| 5 | **Orchestrator + Analyzer + Architect** | sorğu klassifikasiya, fallbackträge, read-only default |
| 6 | **File/Git/Terminal** | read-only fayl oxuma, `git status`, sadə emr çalıştırma (`--write` icazəsi olmadan təhlükəsiz), path traversal qorunması |
| 7 | **Test Suite** | pytest, CLI + security + core/agents/utils unit testləri, coverage ≥80%, `--cov-fail-under=80` |
| 8 | **CI/CD** | GitHub Actions (Python 3.9–3.12), test+coverage+Codecov, bandit+flake8+mypy+pre-commit |
| 9 | **Docker** | Dockerfile, `.dockerignore`, `docker build -t smart-cli .` uğurlu |
| 10 | **Dokumentasiya** | README, ARCHITECTURE, SECURITY, CONTRIBUTING, ROADMAP (kısa) |

### 2.3 MVP uğrul criterionları (Definition of Done)

- [ ] `smart --help` və `smart version` işləyir
- [ ] `smart config api-key sk-...` şifrələnib saxlanılır və düzgün oxunur
- [ ] `smart > analyze this codebase` → orchestrator → analyzer → cavab (fallback ilə də)
- [ ] `pytest` → ≥80% coverage, bütün testler ✅
- [ ] CI yeşil keçir (test + bandit + flake8 + mypy)
- [ ] `docker build -t smart-cli .` uğurlu olur

## 3. 3 Qatlı Yol Xəttişi

| Qat | Mərhələ | Həftə | Məqsəd | Əsas Tapşırıqlar |
|-----|--------|-------|--------|------------------|
| **P1** | MVP Sturdy | 1–2 | Dual import silmək, legacy metodları təmizləmək, `pickle` → JSON, `SMART_CLI_MASTER_KEY` tələb etmək, read-only default, unit testlər yazmaq, CI-də security scan | `src/smart_cli.py`, `src/utils/cache.py`, `src/utils/config.py`, `tests/` |
| **P1** | MVP Qalımlar | 3–4 | Audit journal yaratmaq, provider interface (litellm/adapter), mod sistemi stationarye çevrilmək (`smart`, `code`, `analysis` stable), Docker publish | `src/core/` (journal), provider adapter, `docs/MODE_SYSTEM.md` |
| **P2** | Təhlükəsizlik | 5–8 | Real sandbox (container per command), command allowlist, secret rotation, connectivity check, E2E + performance testləri | Sandbox layer, allowlist, `tests/e2e/`, `tests/performance/` |
| **P3** | Uzandırmaq | 9–12 | Multi-provider (OpenAI, Gemini, local LLM), parallel agent execution, cost tracking dashboard, plugin sistemi | Provider adapters, `src/core/parallel_execution.py` erweitert, cost dashboard |

## 4. Həftə 1–2 Əməliyyat Çədvəli (İlk Sprint)

Bu cədvəl indi qəbul edərək başlan bilər.

| Gün | Tapşırıq | Fayl(lar) | Nəticə |
|-----|---------|-----------|--------|
| 1 | Dual import bloklarını silin, yalnız relative import saxlayın | `src/smart_cli.py`, `src/core/*.py`, `src/utils/*.py` | Import problems yox |
| 2 | “LEGACY METHODS”-ləri silin (`_get_user_input`, `_handle_ai_fallback`, `_process_ai_request` və digərleri) | `src/smart_cli.py` | Dead code yox |
| 3 | `cache.py`-də `pickle` → JSON çevirin | `src/utils/cache.py` | RCE riski azaldı |
| 4 | `ConfigManager`-da import zamanında side effect-i lazy et (`load()`) | `src/utils/config.py` | Test isolation artsın |
| 5 | `SMART_CLI_MASTER_KEY` tələb edin, hardcoded default-unu silin | `src/utils/config.py` | Təhlükəsizlik artdı |
| 6 | File/Git/Terminal əməliyyatlarına read-only default və `--write` onay qatını əlavə edin | `src/core/simple_*.py` | Sandbox 첫basmaq |
| 7 | Core/agents/utils üçün unit testlər yazın; `test_security.py`-dəki `pass` testlərini reallaşdırın | `tests/test_config.py`, `tests/test_cache.py`, `tests/test_agents.py`, `tests/test_security.py` | Coverage ≥80% |
| 8 | CI workflow-ya bandit + flake8 + mypy + pre-commit run əlavə edin | `.github/workflows/ci.yml` | Statik analiz CI-də |
| 9 | Audit journal (config dəyişiklik jurnalı) yaradın | `src/core/` yeni fayl | Konfiq dəyişiklikləri qayd edilir |
| 10 | MVP uğrul criterionlarını yoxlayın: `pytest`, `docker build`, `smart --help` | — | MVP hazır |

## 5. Necə Əmələ Salınmalıdır?

1. **Bu iki sənəd (`AUDIT_REPORT.md` + `MVP_ROADMAP.md`) team/açıqlama olaraq qəbul edin.**
2. **Həftə 1–2 cədvəli GitHub project(board) və ya issues-ə çevirin.**
3. **Hər bir tapşırıq üçün PR açın; merge əvvəl `pre-commit run --all-files` və `pytest` uğurlu olmalıdır.**
4. **MVP criterionları Gegə təyin edildikdən sonra, P2 (Təhlükəsizlik) qatına keçin.**

## 6. Nəticə

Smart CLI ciddi potensial sahibdir: modulyar arxitektura, PBKDF2+Fernet şifrləməsi, çok-agent sistemi, zəngin test infra və dokumentasiya var. Asıl məhdudiyyətlər arxitektural (dual import, legacy code) və təhlükəsizlik (pickle, sandbox yox, audit log yox) səviyyəsindədir. Bəzi sətirlər düzeldildikdən sonra (MVP), layihə istiqamətli və sürdürdürülə bilən şəkildə davam edə bilər.

Bu sənəd davam etdirilmə üçün əsas referansdır.