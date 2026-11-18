# Coffee Rating

A list of coffees where each **Vote** click is a `POST` to the backend, which updates a vote count in SQLite.

## Run

```bash
pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000** in your browser (don't open the HTML files directly; the page must be served by Flask).

## How it works

1. On first start `app.py` creates `coffee.db` and seeds six coffees.
2. The page loads the list from `GET /api/coffees` (sorted by votes, highest first).
3. Clicking **Vote** sends `POST /api/coffees/<id>/vote`.
4. The backend runs `UPDATE coffees SET votes = votes + 1 WHERE id = ?`. The increment happens inside SQL, so rapid or simultaneous clicks never overwrite each other. It returns the updated coffee, or `404` if the id doesn't exist.
5. The page re-sorts and redraws the list, so the leaderboard moves as votes come in.

Votes persist in `coffee.db`; delete that file to reset everything.

## Structure

```
app.py
requirements.txt
templates/  index.html
static/     app.js, style.css
```
