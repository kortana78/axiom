"""Tests for the persistent abc prover fleet (no network, no real Lean)."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from axiom.abc_prover import CHECKED, NO_PROOF, REJECTED, ROUTES_PATH
from axiom.abc_prover.ledger import utc_now
from axiom.abc_prover.merge import merge_all
from axiom.abc_prover.pool import ProviderPool, QuotaStore, SharedUsage
from axiom.abc_prover.supervisor import Supervisor, health
from axiom.abc_prover.worker import heartbeat, run_once, worker_paths
from axiom.llm.client import LLMResponse
from axiom.llm.config import Provider

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROUTES = os.path.join(ROOT, ROUTES_PATH)

GOOD_LEAN = "theorem one_pos : (0 : Nat) < 1 := by norm_num"


def _provider(name="free-a", day=10):
    return Provider(name, f"https://{name}.test/v1", f"secret-{name}",
                    "fake-model", max_requests_per_run=1,
                    max_requests_per_day=day, max_retries=0)


def _transport(content):
    def transport(url, headers, payload, timeout):
        body = {
            "choices": [{"message": {"content": content}}],
            "usage": {"prompt_tokens": 7, "completion_tokens": 3},
        }
        return 200, {}, json.dumps(body)
    return transport


def _checker(calls=None):
    def check(code, name):
        if calls is not None:
            calls.append((code, name))
        return {
            "ok": True, "status": CHECKED, "reason": "fake acceptance",
            "axioms": [], "output": "", "seconds": 0.1,
        }
    return check


def test_quota_store_caps_per_provider_per_day(tmp_path):
    q = QuotaStore(str(tmp_path), today=lambda: "2026-01-01")
    assert q.reserve("a", 2)
    assert q.reserve("a", 2)
    assert not q.reserve("a", 2)
    assert q.used("a") == 2
    assert q.reserve("b", 1)
    assert not q.reserve("b", 1)
    q2 = QuotaStore(str(tmp_path), today=lambda: "2026-01-02")
    assert q2.reserve("a", 1)


def test_pool_rotates_and_stops_at_daily_cap(tmp_path):
    usage = SharedUsage(str(tmp_path / "usage.json"))
    quota = QuotaStore(str(tmp_path / "quota"),
                       today=lambda: "2026-01-01")
    pool = ProviderPool([_provider("a", 1), _provider("b", 1)], usage, quota,
                        clock=lambda: 100.0)
    leases = [pool.acquire() for _ in range(3)]
    names = [lease.provider.name for lease in leases if lease is not None]
    assert names == ["a", "b"]
    assert leases[2] is None
    assert "daily request cap" in pool.last_reason


def test_pool_cools_down_after_failure(tmp_path):
    now = [100.0]
    usage = SharedUsage(str(tmp_path / "usage.json"))
    quota = QuotaStore(str(tmp_path / "quota"),
                       today=lambda: "2026-01-01")
    pool = ProviderPool([_provider("a", 10)], usage, quota,
                        clock=lambda: now[0], cooldown_base=30.0)
    lease = pool.acquire()
    assert lease is not None
    pool.record_failure(lease.provider, RuntimeError("boom"))
    assert pool.acquire() is None
    assert "cooling down" in pool.last_reason
    now[0] += 31.0
    assert pool.acquire() is not None


def test_merge_prefers_checked_and_keeps_target_unpromoted(tmp_path):
    workers = tmp_path / "workers"
    for worker, status in (("w1", REJECTED), ("w2", CHECKED)):
        directory = workers / worker
        directory.mkdir(parents=True)
        attempt = {
            "id": "sha256:same", "name": "one_pos", "route": "definitions",
            "status": status, "lean": GOOD_LEAN, "target_like": True,
            "checked_at": "2026-01-01T00:00:00Z",
        }
        (directory / "ledger.json").write_text(
            json.dumps({"attempts": [attempt]}), encoding="utf-8")

    status = merge_all(
        ledger_path=str(tmp_path / "ledger.json"),
        status_path=str(tmp_path / "status.json"),
        routes_path=ROUTES,
        target_path=str(tmp_path / "target.lean"),
        workers_dir=str(workers))
    assert status["abc"] == "OPEN"
    assert status["verdict"] == NO_PROOF
    assert status["checked_lemmas"] == 1
    assert status["rejected_lemmas"] == 0
    ledger = json.loads((tmp_path / "ledger.json").read_text(encoding="utf-8"))
    assert ledger["attempts"][0]["status"] == CHECKED
    target = (tmp_path / "target.lean").read_text(encoding="utf-8")
    assert "NOT lean/Abc/Proof.lean" in target
    assert GOOD_LEAN in target


def test_worker_run_once_merges_and_heartbeat_has_no_key(tmp_path):
    proposal = json.dumps({"proposals": [{
        "name": "one_pos", "lean": GOOD_LEAN, "route": "definitions",
        "rationale": "test",
    }]})
    usage = SharedUsage(str(tmp_path / "usage.json"))
    quota = QuotaStore(str(tmp_path / "quota"),
                       today=lambda: "2026-01-01")
    pool = ProviderPool([_provider("a", 10)], usage, quota,
                        clock=lambda: 100.0)
    paths = worker_paths("w1", str(tmp_path / "workers"))
    report, status = run_once(
        "w1", pool, _checker(), rounds=1, max_proposals=1, max_requests=1,
        time_budget=30, transport=_transport(proposal),
        ledger_path=paths["ledger"], status_path=paths["status"],
        target_path=paths["target"],
        usage_path=str(tmp_path / "usage.json"),
        context_ledger_path=str(tmp_path / "global_ledger.json"),
        routes_path=ROUTES,
        global_ledger_path=str(tmp_path / "global_ledger.json"),
        global_status_path=str(tmp_path / "global_status.json"),
        global_target_path=str(tmp_path / "global_target.lean"),
        workers_dir=str(tmp_path / "workers"))
    assert report["abc"] == "OPEN"
    assert report["checked"] == 1
    assert status["abc"] == "OPEN"
    assert status["verdict"] == NO_PROOF
    assert status["checked_lemmas"] == 1
    hb = heartbeat("w1", pool, report, status, utc_now(), 1,
                   path=paths["heartbeat"])
    assert hb["abc"] == "OPEN" and hb["verdict"] == NO_PROOF
    blob = json.dumps(hb)
    assert "secret-" not in blob
    assert "api_key" not in blob


def test_supervisor_status_is_honest_and_health_detects_staleness(tmp_path):
    sup = Supervisor(
        workers=2, workers_dir=str(tmp_path / "workers"),
        status_path=str(tmp_path / "supervisor.json"),
        ledger_path=str(tmp_path / "ledger.json"),
        prover_status_path=str(tmp_path / "prover_status.json"),
        routes_path=ROUTES, target_path=str(tmp_path / "target.lean"),
        merge_interval=5, restart_delay=1)
    data = sup.status()
    assert data["abc"] == "OPEN"
    assert data["verdict"] == NO_PROOF
    assert data["workers_requested"] == 2
    assert data["workers_running"] == 0

    ok, message = health(str(tmp_path / "supervisor.json"))
    assert not ok and "no workers" in message

    healthy = dict(data, workers_running=2, updated_utc=utc_now())
    (tmp_path / "supervisor.json").write_text(
        json.dumps(healthy), encoding="utf-8")
    ok, message = health(str(tmp_path / "supervisor.json"))
    assert ok, message

    stale = dict(healthy, updated_utc="2020-01-01T00:00:00Z")
    (tmp_path / "supervisor.json").write_text(
        json.dumps(stale), encoding="utf-8")
    ok, message = health(str(tmp_path / "supervisor.json"))
    assert not ok and "stale" in message


def test_dashboard_shows_fleet_but_top_line_stays_open(tmp_path):
    from axiom.swarm import dashboard

    root = tmp_path / "results"
    (root / "abc_proof").mkdir(parents=True)
    (root / "abc_prover").mkdir(parents=True)
    (root / "abc_proof" / "status.json").write_text(
        json.dumps({"verdict": "OPEN", "reason": "no proof"}),
        encoding="utf-8")
    (root / "abc_prover" / "supervisor.json").write_text(
        json.dumps({"workers_running": 2, "workers_requested": 3,
                    "updated_utc": utc_now()}), encoding="utf-8")
    queue = tmp_path / "queue.json"
    queue.write_text('{"problems": []}', encoding="utf-8")
    dashboard.build(str(queue), str(root))
    html = (root / "index.html").read_text(encoding="utf-8")
    md = (root / "SUMMARY.md").read_text(encoding="utf-8")
    for text in (html, md):
        assert "abc conjecture: OPEN. No result here proves it." in text
        assert "ABC prover fleet" in text
        assert "2/3 workers online" in text


def test_pool_public_never_contains_keys(tmp_path):
    usage = SharedUsage(str(tmp_path / "usage.json"))
    quota = QuotaStore(str(tmp_path / "quota"),
                       today=lambda: "2026-01-01")
    pool = ProviderPool([_provider("a")], usage, quota)
    blob = json.dumps(pool.public())
    assert "secret-a" not in blob
    assert "api_key" not in blob
