---
name: webapp
description: End-to-end workflow for building web application features in QuantLab. Load this skill when the task involves FastAPI endpoints, React components, or full-stack API+UI work.
---

# Webapp Feature — Orchestrator Workflow

## Overview

This skill coordinates building a webapp feature (API endpoint + frontend
component) through all agent gates. The orchestrator loads this checklist;
specialists load their detail files (`api.md`, `frontend.md`).

## Checklist

- [ ] Step 1: Check existing API in `api/routes.py`
- [ ] Step 2: Add request/response schemas in `api/schemas.py`
- [ ] Step 3: Implement endpoint in `api/routes.py`
- [ ] Step 4: Write API tests in `mocktests/test_api.py`
- [ ] Step 5: Add TypeScript types in `web/src/types.ts`
- [ ] Step 6: Add API client function in `web/src/api.ts`
- [ ] Step 7: Create React component in `web/src/components/`
- [ ] Step 8: Run `python -m pytest mocktests/test_api.py -v`
- [ ] Step 9: Run `npm run build` in `web/` to verify TypeScript
- [ ] Step 10: Run full mock suite to verify nothing broken
- [ ] Step 11: Documentation Expert updates docs
- [ ] Step 12: Code Reviewer runs deep-dive audit
- [ ] Step 13: Release Manager cuts release

## Per-Step Details

### Step 1 — Check Existing API
Inspect `api/routes.py` for an existing endpoint that handles the desired
functionality. If it exists, skip to Step 4 (testing). If not, proceed
with Steps 2–3.

### Step 2 — Schema Definition
Add Pydantic models to `api/schemas.py` for request body and response.
Use snake_case fields. Return models must match what the frontend consumes.

### Step 3 — Endpoint Implementation
Add the route in `api/routes.py`. Follow existing patterns: use dependency
injection for database access, return typed responses, handle errors with
HTTPException. Import schemas from `api/schemas.py`.

### Step 4 — API Tests
Write mock tests in `mocktests/test_api.py` covering: happy path, missing
required fields, invalid values, edge cases. Use `client.post()` / `client.get()`
with JSON payloads. Assert status codes and response shapes.

### Step 5 — TypeScript Types
If the API returns new shapes, add `interface` definitions in
`web/src/types.ts`. Use `export interface`. Match schema field names
(camelCase in TS).

### Step 6 — API Client Function
Add a typed fetch wrapper in `web/src/api.ts`. Use `import type` for the
response type from `types.ts`. The function should call the FastAPI
endpoint and return the typed response.

### Step 7 — React Component
Create the component in `web/src/components/`. Use Tailwind CSS v4 utility
classes only (no custom CSS). Use Recharts for any charts. Import types
with `import type`.

### Step 8 — API Test Verification
Run `python -m pytest mocktests/test_api.py -v`. All tests must pass.
If red, fix the endpoint or schema, then re-run.

### Step 9 — TypeScript Build Verification
Run `npm run build` in `web/`. No TypeScript errors allowed. If errors
appear, fix type mismatches or missing imports, then re-run.

### Step 10 — Full Mock Suite
Run `bash scripts/verify.sh` or `python -m pytest mocktests/ -v`. Full
suite must be green. If red, return to the relevant step with
reproduction.

### Step 11 — Documentation
Update README if the feature is user-visible. Update `docs/` if the
feature changes architecture or API surface.

### Step 12 — Code Reviewer
Deep-dive per `docs/code_review_guide.md`. Verify: endpoint follows
patterns, types are consistent across TS and Python, no secrets logged,
error handling is correct.

### Step 13 — Release Manager
Bump version per conventions. Commit with descriptive message.

## Key Files

| File | Purpose |
|------|---------|
| `api/main.py` | FastAPI app setup and middleware |
| `api/schemas.py` | Pydantic request/response models |
| `api/routes.py` | Endpoint implementations |
| `web/src/types.ts` | TypeScript type definitions |
| `web/src/api.ts` | API client functions |
| `web/src/components/` | React components |
| `mocktests/test_api.py` | API endpoint tests |

## Conventions

- Use `import type` for TypeScript type-only imports
- Tailwind CSS v4 utility classes only, no custom CSS files
- Recharts for all chart components
- FastAPI with Pydantic validation on all request/response models
- No comments unless asked
- snake_case in Python, camelCase in TypeScript
- Match field names between schema and TS interface (snake_case in
  Python, camelCase in TS with `alias` or `model_config` if needed)

## Verification

After all steps, run `bash scripts/verify.sh` to confirm the full
suite passes. For a quick check, run Steps 8 and 9 in parallel.

## Troubleshooting

### Port 8000 Conflict
If the API returns 404 or the frontend shows "Failed to load indicators":
1. Check for conflicting processes: `lsof -i :8000`
2. Kill conflicting processes: `kill <PID>`
3. Restart the backend: `uvicorn api.main:app --reload --port 8000`

### Silent Fetch Failures
Frontend API calls must have visible error handling. Never use
`.catch(console.error)` alone — always add error state to React
components so users see when backend requests fail.
