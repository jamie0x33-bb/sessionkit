from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__, cache, config, connectors, registry, skills


def _status(args) -> int:
    rt = config.load()
    print(f"skills {__version__}")
    print(f"sandbox:          {'yes' if config.in_sandbox() else 'no'}")
    print(f"connector base:   {rt.base_url or '(unset)'}")
    print(f"connector target: {rt.target_base_url or '(unset)'}")
    if rt.ready:
        print("connector calls should work")
    else:
        print("connector calls will fail; one half of a pair is unset")
    return 0 if rt.ready else 1


def _register(args) -> int:
    try:
        result = registry.register()
    except registry.RegistryError as exc:
        print(f"registration failed: {exc}", file=sys.stderr)
        return 3
    print(f"registered as {result.get('session_id')}")
    return 0


def _forget(args) -> int:
    print("forgotten" if registry.forget() else "not registered")
    return 0


def _list(args) -> int:
    items = connectors.connected() if args.connected else connectors.list_connectors()
    if args.json:
        print(json.dumps(items, indent=2))
        return 0
    for c in items:
        print(f"{c.get('status','?'):<13} {c.get('source_id',''):<26} {len(c.get('tools', []))} tools")
    return 0


def _find(args) -> int:
    for c in connectors.find(args.query):
        print(f"{c.get('status','?'):<13} {c.get('source_id',''):<26} {c.get('display_name','')}")
    return 0


def _describe(args) -> int:
    cached = cache.get(args.source_id)
    if cached is None:
        cached = connectors.describe(args.source_id)
        cache.put(args.source_id, cached)
    print(json.dumps(cached, indent=2))
    return 0


def _call(args) -> int:
    arguments = json.loads(args.arguments) if args.arguments else {}
    print(json.dumps(connectors.call_tool(args.source_id, args.tool, arguments), indent=2))
    return 0


def _new(args) -> int:
    print(f"created {skills.scaffold(Path(args.directory), args.name, args.description)}")
    return 0


def _validate(args) -> int:
    result = skills.validate(Path(args.directory))
    for e in result.errors:
        print(f"error:   {e}")
    for w in result.warnings:
        print(f"warning: {w}")
    print("valid" if result.ok else "invalid")
    return 0 if result.ok else 1


def _cached(args) -> int:
    for k in cache.keys():
        print(k)
    return 0


def _clear_cache(args) -> int:
    print(f"removed {cache.clear()} cached schemas")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="sessionkit", description="Inspect and debug Perplexity Computer sessions")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="show the resolved environment").set_defaults(func=_status)

    sub.add_parser("register", help="register this session with the schema registry").set_defaults(func=_register)
    sub.add_parser("forget", help="forget the registration").set_defaults(func=_forget)

    l = sub.add_parser("list", help="list connectors")
    l.add_argument("--connected", action="store_true")
    l.add_argument("--json", action="store_true")
    l.set_defaults(func=_list)

    f = sub.add_parser("find", help="search connectors by name")
    f.add_argument("query")
    f.set_defaults(func=_find)

    de = sub.add_parser("describe", help="describe one connector's tools")
    de.add_argument("source_id")
    de.set_defaults(func=_describe)

    ca = sub.add_parser("call", help="call a connector tool")
    ca.add_argument("source_id")
    ca.add_argument("tool")
    ca.add_argument("--arguments", help="JSON object")
    ca.set_defaults(func=_call)

    n = sub.add_parser("new", help="scaffold a skill directory")
    n.add_argument("name")
    n.add_argument("--description", default="Describe when this skill applies.")
    n.add_argument("--directory", default=".")
    n.set_defaults(func=_new)

    v = sub.add_parser("validate", help="validate a skill directory")
    v.add_argument("directory")
    v.set_defaults(func=_validate)

    sub.add_parser("clear-cache", help="drop cached schemas").set_defaults(func=_clear_cache)
    sub.add_parser("cached", help="list cached schema ids").set_defaults(func=_cached)

    args = p.parse_args(argv)
    try:
        return args.func(args)
    except connectors.ConnectorError as exc:
        print(f"connector service error {exc.status}: {exc.body[:300]}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
