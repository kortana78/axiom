# Render pulse (monitoring only)

Render's free tier cannot run Lean + Mathlib (512 MB RAM, sleeps when idle).
The prover workers therefore run on the Oracle VPS. This tiny service is an
optional **status beacon**: it reads the supervisor heartbeat that the VPS
commits to `results/abc_prover/supervisor.json` and exposes `/healthz`.

## Deploy

1. Create a new **Web Service** on Render from this repository.
2. Set the build command to `pip install -r deploy/pulse/requirements.txt`.
3. Set the start command to `python deploy/pulse/app.py`.
4. Add `AXIOM_STATUS_URL` (defaults to the raw GitHub URL above) and
   `AXIOM_MAX_AGE` in seconds (default `21600`).
5. Point a free uptime monitor (e.g. UptimeRobot) at `https://<app>.onrender.com/healthz`
   every 5 minutes. Rendering a request keeps this beacon awake; the beacon
   does **not** keep the VPS awake because the VPS never sleeps.

`/healthz` returns `200` only when the published heartbeat is fresh, at least
one worker is running, and the prover status is still `OPEN` / `NO_PROOF`.
It returns `503` otherwise. It never starts, stops, or promotes anything.
