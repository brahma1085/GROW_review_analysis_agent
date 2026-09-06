# Implement UI Screens from Google Stitch

The goal is to translate the static HTML prototypes from the `stitch_feedback_intelligence_dashboard` folder into a fully functional, maintainable, and responsive frontend application.

## Proposed Changes

### 1. Initialize Frontend Project
- Create a new directory `frontend` in the project root.
- Initialize a React application using `npm create vite@latest frontend -- --template react-ts`.
- Install dependencies including `react-router-dom` for navigation and `lucide-react` or Google Material Symbols for icons.

### 2. Configure Tailwind CSS
- Install `tailwindcss`, `postcss`, and `autoprefixer`.
- Configure `tailwind.config.js` to match the exact color tokens, fonts (Inter, Plus Jakarta Sans), and dark mode class strategy found in the `code.html` files.
- Install necessary Tailwind plugins used in the prototypes (`@tailwindcss/forms`, `@tailwindcss/container-queries`).

### 3. Build the Core Layout & Design System
- **Layout Component:** Create a global layout featuring the responsive Sidebar (Desktop/Mobile) and Top Navigation Header (with Theme Toggle and Week Selector).
- **Theme Provider:** Implement a React Context to manage Dark/Light mode state, persisting the preference in `localStorage`.
- **Reusable UI Components:** Extract common elements (Cards, Buttons, Badges, Modals) from the `vibrant_fintech_core` prototype.

### 4. Migrate Screens to React Components
- **Leadership Executive Dashboard:** Translate `leadership_executive_dashboard_responsive_themeable` into the main `Dashboard.tsx` view.
- **Administrative Control Panel:** Translate `administrative_control_panel_responsive_themeable` into an `Admin.tsx` view.
- **Weekly Pulse (Themes & Quotes):** Translate `weekly_one_page_pulse_themes_verbatim_quotes_actions_1` and `2` into a dedicated `TrendsAndThemes.tsx` or similar sub-routes.

### 5. Routing Implementation
- Set up `react-router-dom` to navigate between:
  - `/` -> Leadership Dashboard
  - `/trends` -> Themes & Pulse
  - `/admin` -> Administrative Control Panel

### 6. Backend Integration & API Layer
To connect the React UI with the Python backend, we will introduce a REST API layer using **FastAPI**.
- **API Server Setup:** Create an API entrypoint (`src/api/server.py`) using FastAPI and Uvicorn to serve data to the frontend.
- **CORS Configuration:** Configure CORS middleware in FastAPI to allow requests from the local Vite development server (`http://localhost:5173`).
- **REST Endpoints:**
  - `GET /api/dashboard/summary`: Expose high-level metrics (Health Score, Review Volume, Sentiment).
  - `GET /api/dashboard/themes`: Expose the top themes and priorities for the Pulse view.
  - `POST /api/admin/trigger-run`: Expose an endpoint to manually trigger the `orchestrator.run()` pipeline asynchronously.
  - `GET /api/admin/status`: Expose the current status of the pipeline execution.
- **Frontend Data Fetching:** 
  - Implement API client functions in the React app (using `fetch` or `axios`).
  - Wire up the React components (`Dashboard.tsx`, `Admin.tsx`, `Pulse.tsx`) to consume these endpoints using `useEffect` and React state.
  - Make the "Trigger AI Agent Run Now" button in the Admin panel fully functional.

## Verification Plan

### Automated Tests
- Run `npm run build` in the frontend directory to ensure TypeScript compilation and Vite bundling succeed without errors.
- Run `pytest` on the backend to ensure existing agent tests pass.

### Manual Verification
- Start the backend FastAPI server using `uvicorn`.
- Start the frontend development server using `npm run dev`.
- Verify the Dashboard successfully loads data from the `/api/dashboard/summary` endpoint.
- Click "Trigger AI Agent Run Now" and verify the POST request is sent and the backend logs indicate the pipeline has started.
