from collections.abc import Callable, Sequence

from fastapi import Depends, params


def _inject_dependencies(
    funcs: Sequence[Callable] | None = None,
) -> Sequence[params.Depends] | None:
    """Wraps a list of functions in FastAPI's Depends."""
    if funcs is None:
        return None

    for func in funcs:
        if not callable(func):
            raise TypeError(f"All dependencies must be callable. Got {type(func)} instead.")

    return [Depends(func) for func in funcs]
