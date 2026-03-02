# FitTech (PHP + MySQL Web App)

FitTech is a simple fitness dashboard web app with:

- Workout logging + stats
- Nutrition logging + daily plan
- Store (products / cart / checkout)
- User profile & achievements

## Tech stack

- Frontend: HTML / CSS / JavaScript
- Backend: PHP (REST-like endpoints under `api/`)
- Database: MySQL (`database_init.sql`)

## Project structure

- `index.html`, `login.html`, `register.html`, `training.html`, `store.html`: pages
- `css/`: styles
- `js/`: frontend logic + API calls
- `api/`: PHP API endpoints
- `includes/`: shared PHP utilities (DB, auth, config, helpers)

## Quick start (XAMPP)

1. Put this project into your XAMPP `htdocs` (example folder name: `fit-tech-project`).
2. Create/import database:
   - Open phpMyAdmin
   - Run/import `database_init.sql` (creates `fittech_db` and tables)
3. Update base URL if needed:
   - `includes/config.php` → `BASE_URL`
   - `js/config.js` → `FITTECH_CONFIG.BASE_URL`
4. Visit:
   - `index.html` (dashboard)
   - `register.html` / `login.html`

## Notes

- `.DS_Store` and other OS/editor files are ignored via `.gitignore`.
- `test_config.php` is intentionally ignored (local debug page; don’t publish by accident).

