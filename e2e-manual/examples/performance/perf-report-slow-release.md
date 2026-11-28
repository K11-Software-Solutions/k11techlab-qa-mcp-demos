## Performance: ❌ needs attention

Scenario **browse** on **local** (builtin engine: 4 virtual users for 8s), **480 requests** at 57.62 req/s, error rate 0.00%, p95 118.0 ms, p99 136.2 ms.

### Findings

- **regression**: GET /orders/{id}: p95 77.4 → 131.2 ms (+69.5%, p=0.0000)

### Endpoints

| Endpoint | Requests | Errors | p50 | p95 | p99 | Max | vs baseline |
|---|---:|---:|---:|---:|---:|---:|---|
| `DELETE /orders/{id}` | 60 | 0 (0.0%) | 22.0 | 43.1 | 55.9 | 60.0 | ≈ -55.7% (97.4 → 43.1 ms), not significant |
| `GET /orders` | 90 | 0 (0.0%) | 19.5 | 76.2 | 112.8 | 168.0 | 🟢 -40.3% (127.7 → 76.2 ms) |
| `GET /orders/{id}` | 210 | 0 (0.0%) | 96.0 | 131.2 | 139.7 | 163.0 | 🔺 +69.5% (77.4 → 131.2 ms) |
| `POST /orders` | 120 | 0 (0.0%) | 20.0 | 52.6 | 66.0 | 96.0 | 🟢 -51.8% (109.1 → 52.6 ms) |

SLOs: 8/8 met.

Compared with the baseline from 2026-11-28T03:44:54+00:00 on **p95**: a regression needs > 15% and > 15 ms slower, with p < 0.01.

> Database steps are skipped under load; they still run in API functional tests.

<sub>k11-performance-qa-mcp 0.2.0 · 2026-11-28T03:45:06+00:00</sub>
