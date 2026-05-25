"""Static-typing regression tests for pqdict's generic parameters.

These guard against silently dropping the ``pqdict[KT, VT]`` parameterization,
which happened historically (see issue #38). The assertions are enforced by the
type checker (``mypy``/``pyright`` in CI) via :func:`assert_type`; at runtime
``assert_type`` is a no-op, so these also double as light smoke tests.
"""

from __future__ import annotations

from typing import Any

from typing_extensions import assert_type

from pqdict import nlargest, nsmallest, pqdict


def test_item_access_types() -> None:
    pq: pqdict[str, int] = pqdict()
    pq["a"] = 1
    for key, val in pq.items():
        assert_type(key, str)
        assert_type(val, int)
    assert_type(pq["a"], int)


def test_constructor_inference() -> None:
    # Use explicitly-typed inputs so the assertion does not depend on a
    # checker's literal-widening behavior (pyright keeps literals otherwise).
    mapping: dict[str, int] = {"a": 1, "b": 2}
    assert_type(pqdict(mapping), pqdict[str, int])

    pairs: list[tuple[str, int]] = [("a", 1), ("b", 2)]
    assert_type(pqdict(pairs), pqdict[str, int])


def test_peek_and_pop_types() -> None:
    pq: pqdict[str, int] = pqdict({"a": 1, "b": 2, "c": 3})
    assert_type(pq.top(), str)
    assert_type(pq.topvalue(), int)
    assert_type(pq.topitem(), tuple[str, int])
    assert_type(pq.popvalue(), int)
    assert_type(pq.popitem(), tuple[str, int])
    assert_type(list(pq.popkeys()), list[str])
    assert_type(list(pq.popvalues()), list[int])


def test_default_fallback_types() -> None:
    # With a ``default``, the return type widens to include the default's type.
    # (Unions are quoted so the file stays runtime-safe on Python 3.9, where
    # ``X | Y`` is not evaluatable at runtime.)
    pq: pqdict[str, int] = pqdict({"a": 1})
    assert_type(pq.top(None), "str | None")
    assert_type(pq.topvalue(None), "int | None")
    assert_type(pq.topitem(None), "tuple[str, int] | None")
    assert_type(pq.popvalue(None), "int | None")
    assert_type(pq.popitem(None), "tuple[str, int] | None")


def test_pop_types() -> None:
    # Hybrid pop: a key with no arg, a value with a key, value-or-default with both.
    pq: pqdict[str, int] = pqdict({"a": 1, "b": 2, "c": 3})
    assert_type(pq.pop("a"), int)
    assert_type(pq.pop("z", None), "int | None")
    assert_type(pq.pop(), str)


def test_module_function_types() -> None:
    assert_type(nlargest(2, {"a": 1}), list[str])
    assert_type(nsmallest(2, {1: "a"}), list[int])


def test_fromkeys_typechecks() -> None:
    # ``fromkeys`` parameterization is checker-dependent (mypy infers
    # ``pqdict[str, int]``; pyright and ty fall back to ``pqdict[Any, Any]``),
    # so we only assert that the call type-checks without error.
    _ = pqdict.fromkeys(["a", "b"], 0)


def test_unparameterized_defaults_to_any() -> None:
    # Bare construction must not require a type annotation (PEP 696 defaults).
    pq = pqdict()
    assert_type(pq, pqdict[Any, Any])
