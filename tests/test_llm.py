import json

import httpx
import pytest

from llmsec.llm.base import ChatResult, ModelSpec
from llmsec.llm.factory import expand_env, get_client, load_specs, make_client
from llmsec.llm.mock import MockClient
from llmsec.llm.openai_compat import OpenAICompatClient


def spec(**kw):
    base = dict(id="t", backend="openai_compat", model="m", base_url="http://x/v1")
    base.update(kw)
    return ModelSpec(**base)


def test_expand_env(monkeypatch):
    monkeypatch.setenv("FOO", "bar")
    monkeypatch.delenv("NOPE", raising=False)
    assert expand_env("${FOO}/v1") == "bar/v1"
    assert expand_env({"a": ["${NOPE:-dflt}"]}) == {"a": ["dflt"]}


def test_registry_loads_and_has_unique_ids():
    specs = load_specs()
    assert "mock" in specs and "qwen3-1.7b" in specs
    assert all(s.backend in {"openai_compat", "mock"} for s in specs.values())


def test_get_client_switches_backend_by_config():
    assert isinstance(get_client("mock"), MockClient)
    assert isinstance(get_client("qwen3-1.7b"), OpenAICompatClient)
    with pytest.raises(KeyError):
        get_client("does-not-exist")


def test_system_suffix_applied():
    c = MockClient(ModelSpec(id="m", backend="mock", model="m", system_suffix="/no_think"))
    c.chat([{"role": "system", "content": "S"}, {"role": "user", "content": "hi"}])
    assert c.calls[0]["messages"][0]["content"] == "S\n/no_think"


def _transport(handler):
    return httpx.MockTransport(handler)


def test_openai_compat_request_and_text_parse():
    seen = {}

    def handler(req):
        seen.update(json.loads(req.content))
        return httpx.Response(200, json={"model": "m", "choices": [{"message": {"content": "hello"}}],
                                         "usage": {"prompt_tokens": 3, "completion_tokens": 1}})

    c = OpenAICompatClient(spec(extra_body={"top_p": 1}), transport=_transport(handler))
    r = c.chat([{"role": "user", "content": "hi"}], temperature=0, seed=7)
    assert r.ok and r.text == "hello" and r.prompt_tokens == 3
    assert seen["seed"] == 7 and seen["temperature"] == 0 and seen["top_p"] == 1 and seen["stream"] is False


def test_openai_compat_tool_calls_string_and_dict_args():
    def handler(req):
        return httpx.Response(200, json={"choices": [{"message": {"content": None, "tool_calls": [
            {"id": "1", "function": {"name": "send_email", "arguments": '{"to": "a@b.c"}'}},
            {"id": "2", "function": {"name": "delete_file", "arguments": {"path": "x"}}},
        ]}}]})

    c = OpenAICompatClient(spec(), transport=_transport(handler))
    r = c.chat([{"role": "user", "content": "x"}], tools=[{"type": "function", "function": {"name": "send_email"}}])
    assert [t.name for t in r.tool_calls] == ["send_email", "delete_file"]
    assert r.tool_calls[0].arguments == {"to": "a@b.c"} and r.tool_calls[1].arguments == {"path": "x"}


def test_tools_dropped_when_model_has_no_tool_support():
    seen = {}

    def handler(req):
        seen.update(json.loads(req.content))
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    c = OpenAICompatClient(spec(supports_tools=False), transport=_transport(handler))
    c.chat([{"role": "user", "content": "x"}], tools=[{"type": "function"}])
    assert "tools" not in seen


def test_errors_are_returned_not_raised():
    c = OpenAICompatClient(spec(), transport=_transport(lambda req: httpx.Response(400, text="bad")), retries=0)
    r = c.chat([{"role": "user", "content": "x"}])
    assert not r.ok and "HTTP 400" in r.error

    def boom(req):
        raise httpx.ConnectError("down")

    r = OpenAICompatClient(spec(), transport=_transport(boom), retries=0).chat([{"role": "user", "content": "x"}])
    assert not r.ok and "ConnectError" in r.error


def test_make_client_unknown_backend():
    with pytest.raises(ValueError):
        make_client(ModelSpec(id="x", backend="nope", model="x"))


def test_mock_custom_responder():
    c = MockClient(responder=lambda m, t: ChatResult(text="fixed"))
    assert c.chat([{"role": "user", "content": "q"}]).text == "fixed"
