from sessionkit import config


def test_runtime_is_not_ready_without_a_target(monkeypatch):
    monkeypatch.setenv("PPLX_CONNECTOR_BASE_URL", "https://example.test")
    monkeypatch.delenv("PPLX_CONNECTOR_TOOL_TARGET_BASE_URL", raising=False)
    monkeypatch.setenv("PPLX_CONNECTOR_API_KEY", "k")
    assert not config.load().ready


def test_headers_carry_the_target_base_url(monkeypatch):
    monkeypatch.setenv("PPLX_CONNECTOR_BASE_URL", "https://example.test")
    monkeypatch.setenv("PPLX_CONNECTOR_TOOL_TARGET_BASE_URL", "http://internal:5556")
    monkeypatch.setenv("PPLX_CONNECTOR_API_KEY", "k")
    h = config.load().headers()
    assert h["X-Base-Url"] == "http://internal:5556"
    assert h["x-app-apiclient"] == "asi-sandbox"


def test_workspace_bearer_prefers_the_proxy_token(monkeypatch):
    monkeypatch.setenv("PPLX_AGENT_PROXY_TOKEN", "agp_a")
    monkeypatch.setenv("PPLX_CONNECTOR_API_KEY", "agp_b")
    assert config.workspace_bearer() == "agp_a"
