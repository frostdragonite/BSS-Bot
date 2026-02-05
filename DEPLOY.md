# Deploying (Railway, Render, Fly.io, etc.)

Config is stored in `panel_config.json`. On many hosts, redeploy = fresh filesystem, so that file would be lost unless you use **persistent storage**. The bot respects the **`DATA_DIR`** env var: when set, it reads/writes `panel_config.json` inside that directory.

| Host | Persistent storage | What to do |
|------|---------------------|------------|
| **Railway** | Volume | Create volume, mount at `/data`, set `DATA_DIR=/data` |
| **Render** | Persistent disk | Add disk, set mount path (e.g. `/data`), set `DATA_DIR=/data` |
| **Fly.io** | Volume | Create volume, mount at e.g. `/data`, set `DATA_DIR=/data` |
| **VPS** (DigitalOcean, Linode, etc.) | Server disk is persistent | Optional: set `DATA_DIR` to a path you prefer; otherwise the default path in the app dir is fine |
| **Heroku** | No local disk | Use a database or external store instead; the volume approach does not apply |

## Option: Railway volume

1. **Create a volume** in your Railway project (Dashboard → your service → Variables → Volumes, or New → Volume). Mount path: `/data`.

2. **Set env var** in the same service:
   ```bash
   DATA_DIR=/data
   ```

3. The bot will read/write `panel_config.json` from `/data`, which persists across redeploys.

**First deploy:** The file won’t exist yet. Set up your panels as usual (e.g. slash commands); the bot will create `/data/panel_config.json` when it first saves.

**Existing config:** If you already have a `panel_config.json` in the repo, the first run will use it from the project directory until the first save; after that, everything uses `/data/panel_config.json`. To start with your current data on the server, you can copy the file into the volume once (e.g. via a one-off command or by pasting content into a file in `/data`), or just reconfigure panels after the first deploy.

---

## Alternative: database

For multiple instances or more structure, you can later move config to a database (e.g. Railway PostgreSQL) and change `core/config_service.py` to read/write there instead of the JSON file.
