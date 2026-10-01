import pytest

from sessionkit import registry


def test_register_without_a_bearer_is_an_error(monkeypatch):
    monkeypatch.delenv("PPLX_AGENT_PROXY_TOKEN", raising=False)
    monkeypatch.delenv("PPLX_CONNECTOR_API_KEY", raising=False)
    with pytest.raises(registry.RegistryError):
        registry.register()


def test_status_is_none_when_not_registered(tmp_path, monkeypatch):
    monkeypatch.setattr(registry, "STATE", tmp_path / "session.json")
    assert registry.status() is None


def test_forget_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setattr(registry, "STATE", tmp_path / "session.json")
    assert registry.forget() is False
