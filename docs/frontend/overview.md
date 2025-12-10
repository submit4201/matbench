# Module: Frontend

## Path

`frontend/src/`

## Overview

The frontend is a **React/Vite** application using **TypeScript**. It communicates with the backend via REST API (`start_scenario`, `state`, `action`).

## Key Components

### `App.tsx` & `Layout.tsx`

- **Role**: Main container. Fetches `GET /state` every few seconds (polling) or on action trigger.
- **State Management**: React `useState` / `useEffect`. No Redux/Context currently visible (simple prop drilling). # [ ] should we consider this?

### `types.ts`

- **Role**: Source of truth for API contracts. Mirrors backend Pydantic models.
- **Critical Sync**: `Laundromat`, `Vendor`, `Ticket`, `SocialScore` interfaces must match Backend serialization exactly.

### `Dashboard.tsx`
# ! [ ] current not working 5:49 am 12/8/2025 
- **Role**: Primary view. Displays charts and key metrics.

## Backend Connection

- **State Fetching**: Polling `GET /state`.
- **Action Submission**: `POST /action`.
- **Next Turn**: `POST /next_turn` (Manually triggered by "Next Week" button). # [ ]  we should have a daily option as well as real time option  eventually daily is a must 

## Refactoring Suggestions

- **Types Sharing**: `types.ts` is manually maintained.
  - _Suggestion_: Use a tool to generate TypeScript interfaces from Python Pydantic models automatically (e.g., `datamodel-code-generator` or OpenAPI generator). # [ ]  agreeed lets do this 
- **Polling**: Polling `GET /state` can be inefficient.
  - _Suggestion_: Use WebSockets for real-time updates, especially for "Chat" and "Progress Bar" features. # [ ]  agreeed lets do this
