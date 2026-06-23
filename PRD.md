# Product Requirements Document (PRD)
## CrowdSense AI — Real-Time Crowd Management System

**Version:** 1.0.0
**Date:** June 2026
**Status:** In Development

---

## 1. Overview

CrowdSense AI is an AI-powered, real-time crowd management and monitoring platform. It ingests live video streams from cameras (RTSP, webcam, or video file), detects and tracks people using computer vision (YOLOv11), analyzes crowd density and zone behavior, and fires multi-channel alerts when thresholds are exceeded — all through a web-based dashboard.

---

## 2. Problem Statement

Public venues (stadiums, malls, transit hubs, campuses) face crowd safety risks due to overcrowding. Security teams lack real-time visibility into crowd density and cannot react proactively. Manual monitoring is slow, error-prone, and scales poorly with multiple camera feeds.

---

## 3. Goals

- Detect people in real time from one or more camera feeds.
- Track individuals across video frames using a multi-object tracker.
- Compute crowd density, heatmaps, and zone-level occupancy.
- Fire automated alerts (WebSocket, Email, Telegram) when occupancy violates thresholds.
- Provide a web dashboard for live monitoring, alert history, and analytics.

---

## 4. Users

| Role | Description |
|------|-------------|
| **Security Operator** | Monitors live feeds and receives real-time alerts |
| **Venue Manager** | Reviews historical analytics and alert logs |
| **System Admin** | Configures cameras, zones, thresholds, and alert channels |

---

## 5. Tech Stack

| Layer | Technology |
|-------|-----------|
| **Vision / AI** | Python, YOLOv11 (`yolo11n.pt`), ByteTrack tracker |
| **Backend API** | FastAPI (async), SQLAlchemy (async), Alembic migrations |
| **Task Queue** | Celery + Redis (NullRedis fallback for dev) |
| **Database** | PostgreSQL (production), SQLite (development) |
| **Cache / Pub-Sub** | Redis |
| **Frontend** | React (Vite), JSX |
| **Containerization** | Docker, Docker Compose, Nginx |

---

## 6. Core Features

### 6.1 Video Ingestion
- Support three source types: **video file**, **RTSP stream**, **webcam**.
- Threaded OpenCV reader with a configurable frame queue (default: 64 frames).
- Target FPS and resolution are configurable via environment variables.

### 6.2 Person Detection & Tracking
- YOLOv11 model for person detection with configurable confidence and IoU thresholds.
- ByteTrack multi-object tracker assigns persistent IDs across frames.
- Tracking parameters: `TRACK_BUFFER`, `MATCH_THRESH`, `MIN_HITS`.

### 6.3 Zone Management
- Configurable zones defined in `config/zones.yaml`.
- Each zone has: name, polygon boundary, and occupancy threshold.
- The system evaluates whether the detected person count in a zone exceeds its threshold.
- **Scene-level alerting**: Optionally alert when total frame count exceeds `ALERT_SCENE_THRESHOLD`.

### 6.4 Analytics Engine
- **Density grid**: Person positions mapped to a spatial grid (configurable scale).
- **Heatmap**: Temporal accumulation with configurable decay rate (`HEATMAP_DECAY`).
- **Zone statistics**: Per-zone count snapshots stored to the database.

### 6.5 Alert Rule Engine
- Evaluates each `CrowdSnapshot` for zone threshold violations.
- **Severity classification**:
  - `warning`: Count exceeds threshold.
  - `critical`: Count exceeds `threshold × ALERT_CRITICAL_RATIO` (default: 2×).
- **Cooldown**: Prevents alert spam — configurable via `ALERT_COOLDOWN_SECONDS` (default: 60s), backed by Redis (or in-memory fallback).
- Fired alerts are persisted to the database.

### 6.6 Multi-Channel Alert Delivery
| Channel | Mechanism | Config Key |
|---------|-----------|------------|
| **WebSocket** | Real-time push to connected dashboard clients | Always enabled |
| **Email** | SMTP (Gmail-compatible with App Password) | `ALERT_EMAIL_ENABLED` |
| **Telegram** | Telegram Bot API | `ALERT_TELEGRAM_ENABLED` |

### 6.7 REST API
Base prefix: `/api/v1`

| Router | Endpoints |
|--------|-----------|
| `auth` | Login, token management (JWT) |
| `cameras` | CRUD for camera sources |
| `analytics` | Crowd snapshot queries, density data |
| `heatmap` | Heatmap image retrieval |
| `alerts` | Alert history queries |
| `ingest` | Push snapshot data from vision worker |
| `websocket` | WebSocket connection endpoint |

Authentication: JWT (HS256), configurable expiry (`JWT_EXPIRE_MINUTES`).

### 6.8 Frontend Dashboard
Five main pages accessible via React Router:
1. **Dashboard** — Live camera view, real-time crowd count, active alerts.
2. **Analytics** — Historical trends, zone occupancy charts, heatmap viewer.
3. **Alerts** — Paginated alert history with severity indicators.
4. **Settings** — Camera management, zone configuration, threshold tuning.
5. **Login** — JWT-based authentication.

---

## 7. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| **Latency** | Alert delivery < 2s from threshold breach |
| **Scalability** | Support ≥ 5 simultaneous camera feeds |
| **Uptime** | 99.5% availability for the API layer |
| **Security** | JWT auth on all API routes; secrets managed via `.env` |
| **Deployability** | Full stack runnable via `docker-compose up` |
| **Fallback** | Operates without Redis using in-process NullRedis stub |

---

## 8. Deployment Architecture

```
[Camera / RTSP]
      │
[Vision Worker] ──→ /api/v1/ingest ──→ [FastAPI Backend]
                                              │
                         ┌────────────────────┤
                         │                    │
                    [PostgreSQL]          [Celery Worker]
                                              │
                                    ┌─────────┴──────────┐
                                 [Redis]            [Alert Engine]
                                    │                    │
                              [WebSocket]    [Email / Telegram]
                                    │
                             [React Frontend]
                             (via Nginx proxy)
```

---

## 9. Configuration Summary

All settings are driven by environment variables (`.env` / `.env.example`):

| Category | Key Variables |
|----------|--------------|
| Video | `VIDEO_SOURCE`, `VIDEO_PATH`, `RTSP_URL`, `TARGET_FPS` |
| Model | `MODEL_PATH`, `CONF_THRESHOLD`, `IOU_THRESHOLD`, `DEVICE` |
| Tracker | `TRACKER_NAME`, `TRACK_BUFFER`, `MATCH_THRESH` |
| Analytics | `DENSITY_GRID_SCALE`, `HEATMAP_DECAY`, `ZONES_CONFIG_PATH` |
| Database | `DATABASE_URL`, `DATABASE_POOL_SIZE` |
| Redis | `REDIS_URL` |
| Auth | `JWT_SECRET_KEY`, `JWT_EXPIRE_MINUTES` |
| Alerts | `ALERT_COOLDOWN_SECONDS`, `ALERT_CRITICAL_RATIO` |
| Email | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `ALERT_EMAIL_TO` |
| Telegram | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |

---

## 10. Out of Scope (v1.0)

- Face recognition or biometric identification.
- Mobile application.
- Multi-tenant / SaaS architecture.
- Audio-based crowd analysis.
- Hardware integration beyond IP/RTSP cameras.

---

## 11. Success Metrics

- Alert delivery latency ≤ 2 seconds from violation detection.
- Zero missed alerts when cooldown has expired and a threshold is breached.
- Dashboard reflects live crowd count within 1 second of frame processing.
- Full stack deployable in under 5 minutes via Docker Compose.

---

*Maintained by the CrowdSense AI development team.*
