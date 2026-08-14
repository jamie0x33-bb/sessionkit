from sessionkit import cache


def test_put_and_get_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)
    cache.put("gcal", {"tools": [1, 2]})
    assert cache.get("gcal") == {"tools": [1, 2]}


def test_get_missing_key_is_none(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)
    assert cache.get("nope") is None


def test_expired_entry_is_refetched(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(cache, "TTL_SECONDS", 0)
    cache.put("gcal", {"tools": []})
    assert cache.get("gcal") is None


def test_clear_removes_entries(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)
    cache.put("a", {})
    cache.put("b", {})
    assert cache.clear() == 2


def test_keys_lists_cached_ids(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)
    cache.put("gcal", {})
    cache.put("finance", {})
    assert cache.keys() == ["finance", "gcal"]
