import functools
import time
import uuid
from dataclasses import dataclass


@dataclass
class ToolCall:
    id: str
    tool: str
    arguments: dict
    result: object
    duration_ms: int


class RunContext:
    def __init__(self) -> None:
        self._calls: dict[str, ToolCall] = {}

    def record(self, tool: str, arguments: dict, result: object, duration_ms: int) -> str:
        call_id = f"{tool}-{uuid.uuid4().hex[:8]}"
        self._calls[call_id] = ToolCall(call_id, tool, arguments, result, duration_ms)
        return call_id

    def get(self, call_id: str) -> ToolCall | None:
        return self._calls.get(call_id)

    def all(self) -> list[ToolCall]:
        return list(self._calls.values())


_context = RunContext()


def get_context() -> RunContext:
    return _context


def reset_context() -> RunContext:
    global _context
    _context = RunContext()
    return _context


def recorded(fn):
    """Decorator: store the tool's result in the run context and add a result_id to it."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        print(">>> TOOL CALLED:", fn.__name__, kwargs)
        result = fn(*args, **kwargs)
        duration_ms = int((time.perf_counter() - start) * 1000)
        call_id = get_context().record(fn.__name__, {"args": list(args), **kwargs}, result, duration_ms)
        if isinstance(result, dict) and "error" not in result:
            return {**result, "result_id": call_id}
        return result

    return wrapper