# sessionkit

Inspect and debug Perplexity Computer sessions.

A Computer session resolves its connector configuration from the environment at process
start. When a connector call fails you get a status code and no indication of whether the
fault is the session, the connector, or your own code. These are the tools we use to tell
them apart.

## Install

```bash
pip install sessionkit
```

## Use

```bash
sessionkit status              # what did this session resolve?
sessionkit list --connected    # what is actually connected
sessionkit find mail           # search connectors
sessionkit describe gcal       # tool schemas, cached for an hour
sessionkit call gcal search_email --arguments '{"queries":[""]}'
```

## Why pairs matter

Each service is configured as a pair: a public base URL requests are sent to, and an
internal target base URL the pass-through proxy forwards to. The proxy rejects any request
whose `X-Base-Url` is not in the session's allowed set, so a half-configured pair fails
like a permissions problem rather than a configuration one. `sessionkit status` reports
which pairs are complete.

## Schema registry

`describe` falls back to a snapshot when the connector service rate limits the listing.
The endpoint and its auth are documented in [docs/registry.md](docs/registry.md).

## Configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `SESSIONKIT_CACHE_DIR` | `~/.cache/sessionkit` | Schema cache location |
| `SESSIONKIT_CACHE_TTL` | `3600` | Cache lifetime in seconds |
| `SESSIONKIT_TIMEOUT` | `60` | Per-request timeout |
| `SESSIONKIT_RETRIES` | `3` | Retries on 429 and 5xx |
