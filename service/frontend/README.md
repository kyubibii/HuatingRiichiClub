# Frontend Quick Start

Vue 3 + TypeScript + Vite admin frontend for HuatingRiichiClub.

## Prerequisites

- Node.js 20+
- `pnpm`

## Install Dependencies

```bash
cd service/frontend
pnpm install
```

## Start Development Server

```bash
cd service/frontend
pnpm dev
```

After startup:

- Dev server: <http://localhost:5173>

## API Proxy

The Vite dev server proxies `/api` requests to `http://localhost:8000`.

Make sure the FastAPI backend is running before testing pages that call the backend.

## Production Build

```bash
cd service/frontend
pnpm build
```

Build output directory:

- `service/frontend/dist`

This directory is mounted by FastAPI in production mode.

## Preview Production Build

```bash
cd service/frontend
pnpm preview
```
