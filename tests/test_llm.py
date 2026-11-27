"""LLM adapter: schema, limits, retries, no-key skip, and untrusted output."""
import json
import os
import sys
import tempfile
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from axiom.llm import client, config, ideas, schema, usage

QUEUE = {"problems": [{
    "id": "two_unit", "active": True, "start_modulus": 12,
    "statement": "forall n >= 2: exists x >= 1: exists y >= 1: 2/n = 1/x + 1/y",
    "grammar": {"T": 20, "D": 12},
}]}


def _queue_file(d):
    p = os.path.join(d, "queue.json")
    json.dump(QUEUE, open(p, "w"))
    return p


def test_no_key_skips_without_writing():
    d = tempfile.mkdtemp()
    qp = _queue_file(d)
    with mock.patch.dict(os.environ, {}, clear=True):
        res = ideas.run("two_unit", 5, qp, os.path.join(d, "results"),
                        out_path=os.path.join(d, "ideas.json"))
    assert res["enabled"] is False and res["reason"] == "no LLM_API_KEY"
    assert not os.path.exists(os.path.join(d, "ideas.json"))


def test_single_provider_from_primary_env():
    env = {"LLM_BASE_URL": "https://example.test/v1",
           "LLM_API_KEY": "secret", "LLM_MODEL": "free-model"}
    ps = config.load_providers(env)
    assert len(ps) == 1 and ps[0].model == "free-model"
    assert "secret" not in json.dumps(ps[0].public())


def test_multiple_providers_and_missing_key():
    env = {"LLM_PROVIDERS": json.dumps([
        {"name": "a", "base_url": "https://a.test/v1", "api_key": "ka", "model": "ma"},
        {"name": "b", "base_url": "https://b.test/v1", "api_key_env": "B_KEY", "model": "mb"},
        {"name": "c", "base_url": "https://c.test/v1", "model": "mc"},
    ]), "B_KEY": "kb"}
    ps = config.load_providers(env)
    assert [p.name for p in ps] == ["a", "b"]


def test_parse_json_text_tolerates_fences():
    obj = client.parse_json_text('```json\n{"ideas": [{"x": 1}]}\n```')
    assert obj["ideas"][0]["x"] == 1


def test_client_retries_and_returns_usage():
    p = config.Provider("p", "https://example.test/v1", "k", "m",
                        max_retries=1, total_timeout=10)
    calls = []

    def transport(url, headers, payload, timeout):
        calls.append(url)
        if len(calls) == 1:
            raise client.TransientError("HTTP 503")
        return 200, {}, json.dumps({
            "choices": [{"message": {"content": "```json\n{\"ok\": true}\n```"}}],
            "usage": {"prompt_tokens": 7, "completion_tokens": 3},
        })

    sleeps = []
    c = client.LLMClient(p, transport=transport, sleep=sleeps.append)
    r = c.chat([{"role": "user", "content": "hi"}])
    assert r.attempts == 2 and r.prompt_tokens == 7 and r.completion_tokens == 3
    assert sleeps and "chat/completions" in calls[0]


def test_client_retries_empty_content():
    p = config.Provider("p", "https://example.test/v1", "k", "m",
                        max_retries=1, total_timeout=10)
    calls = []

    def transport(url, headers, payload, timeout):
        calls.append(url)
        if len(calls) == 1:
            return 200, {}, json.dumps({
                "choices": [{"message": {"content": ""}}],
            })
        return 200, {}, json.dumps({
            "choices": [{"message": {"content": "{\"ok\": true}"}}],
        })

    c = client.LLMClient(p, transport=transport, sleep=lambda _s: None)
    r = c.chat([{"role": "user", "content": "hi"}])
    assert r.attempts == 2 and r.text == "{\"ok\": true}"


def test_client_gives_up_after_retries():
    p = config.Provider("p", "https://example.test/v1", "k", "m",
                        max_retries=1, total_timeout=10)

    def transport(*_a):
        raise client.TransientError("HTTP 500")

    c = client.LLMClient(p, transport=transport, sleep=lambda _s: None)
    try:
        c.chat([{"role": "user", "content": "hi"}])
    except client.LLMError:
        pass
    else:
        raise AssertionError("client accepted a failing transport")


def test_schema_rejects_bad_witness_idea():
    good = {"order": ["x", "y"], "atoms": ["n"], "mult": [1], "T": 20, "D": 12}
    assert schema.validate_witness_idea(good, ["x", "y"])["T"] == 20
    for bad in (
        {**good, "atoms": ["not_an_atom"]},
        {**good, "order": ["x"]},
        {**good, "T": 0},
        {**good, "mult": [0]},
        {**good, "tie": "yes"},
    ):
        try:
            schema.validate_witness_idea(bad, ["x", "y"])
        except ValueError:
            pass
        else:
            raise AssertionError(f"accepted bad idea {bad}")


def test_schema_sunit_heuristic():
    d = {"S": [2, 3, 5], "method": "p_adic_log", "q": 2,
         "parameters": {"precision": 30}, "priority": 3}
    assert schema.validate_sunit_heuristic(d)["q"] == 2
    for bad in (
        {**d, "S": [2, 4]},
        {**d, "method": "magic"},
        {**d, "q": 7},
        {**d, "parameters": {"nested": {"x": 1}}},
    ):
        try:
            schema.validate_sunit_heuristic(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"accepted bad heuristic {bad}")


def test_run_with_fake_provider_writes_validated_ideas():
    d = tempfile.mkdtemp()
    qp = _queue_file(d)
    p = config.Provider("fake", "https://example.test/v1", "k", "fake-model",
                        max_retries=0, total_timeout=10)

    def transport(url, headers, payload, timeout):
        body = {
            "choices": [{"message": {"content": json.dumps({"ideas": [{
                "order": ["x", "y"], "atoms": ["n", "nv"], "mult": [1],
                "T": 30, "D": 12, "note": "fake",
            }]})}}],
            "usage": {"prompt_tokens": 11, "completion_tokens": 5},
        }
        return 200, {}, json.dumps(body)

    out = os.path.join(d, "ideas.json")
    res = ideas.run("two_unit", 10, qp, os.path.join(d, "results"),
                    out_path=out, providers=[p], transport=transport,
                    max_requests=1)
    assert res["enabled"] and res["accepted"] == 1
    data = json.load(open(out))
    assert data["ideas"][0]["source"] == "llm:fake-model"
    used = json.load(open(os.path.join(d, "results", "llm_usage.json")))
    assert used["providers"]["fake"]["requests"] == 1


def test_load_hand_ideas_includes_validated_llm_file():
    from axiom.ideas.space import load_hand_ideas
    d = tempfile.mkdtemp()
    hand = os.path.join(d, "ideas.json")
    llm = os.path.join(d, "llm_ideas.json")
    base = {"order": ["x"], "atoms": ["n"], "mult": [1], "T": 10, "D": 6}
    json.dump({"ideas": [dict(base, source="hand")]}, open(hand, "w"))
    json.dump({"ideas": [dict(base, atoms=["nv"], source="llm:test")]}, open(llm, "w"))
    ideas_list = load_hand_ideas(hand)
    assert {i.source for i in ideas_list} == {"hand", "llm:test"}


def test_usage_daily_limit_and_reset():
    d = tempfile.mkdtemp()
    path = os.path.join(d, "usage.json")
    led = usage.UsageLedger(path)
    assert led.can_request("p", 1)
    led.record("p", requests=1)
    assert not led.can_request("p", 1)
    led.data["date"] = "1999-01-01"
    led.save()
    led2 = usage.UsageLedger(path)
    assert led2.can_request("p", 1)
