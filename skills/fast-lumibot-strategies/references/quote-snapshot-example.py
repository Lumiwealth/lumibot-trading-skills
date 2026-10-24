
"""Bounded public-API quote reads; data acquisition only, never trading policy.

LumiBot 4.6.19+ get_quotes returns exact Asset keys, including None for missing
members. Schwab caps native requests at 50. A failed HTTP request raises
ConnectionError; that type alone does not establish provider-wide downtime.
Malformed members/response contracts can raise ValueError or TypeError during
numeric quote construction. Handle those only at the get_quotes acquisition
boundary; this is not a blanket handler for strategy logic or other exceptions. This
example never calls get_quote as a serial fallback or changes a quote's fields.
It cannot interrupt a blocking broker request. Call it before entering a
short-deadline order lifecycle, or use a provider timeout/control path that meets
the remaining deadline. Acquisition time is not provider quote freshness.
"""

import logging
import math
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable

from httpx import HTTPError


QUOTE_NOT_PROVIDED = object()


def quote_input(strategy: Any, asset: Any, quote: Any = QUOTE_NOT_PROVIDED) -> Any:
    """Preserve a supplied missing quote; only legacy omitted input fetches.

    Adapt an existing price helper's default and acquisition to this pattern,
    retaining its original pricing/fallback calculations after this step.
    None from a snapshot means unavailable, never permission for another read.
    """
    return strategy.get_quote(asset) if quote is QUOTE_NOT_PROVIDED else quote


@dataclass(frozen=True)
class QuoteSnapshot:
    quotes: dict[Any, Any]
    unavailable: dict[Any, str]
    acquired_at: dict[Any, float]
    request_count: int


def read_quote_snapshot(
    strategy: Any,
    assets: list[Any],
    *,
    deadline: float | None,
    max_requests: int | None = None,
    monotonic: Callable[[], float] = time.monotonic,
) -> QuoteSnapshot:
    """Read once per valid batch; isolate malformed members within a hard budget.

    Pass an actual armed deadline when time-sensitive work can overlap this
    acquisition. An idle pre-entry scan may explicitly pass None: its finite
    contract/request counts and the SDK's finite HTTP timeout still bound work,
    without inventing a quote-age cutoff or a cursor. None is not appropriate
    when a live cancellation deadline needs interleaved service.

    The default request budget derives from the unique contract count: complete
    binary isolation of N members in B initial batches needs at most 2*N-B
    requests. Idle callers should keep that default, not twice the batch count.
    An explicit tighter budget is allowed for an armed deadline; it can leave
    unresolved members that the caller must not call a completed scan.

    The caller owns existing error/retry policy, quote-age validation and order
    management. Inspect unavailable: provider failure, invalid response and
    exhausted budget do not mean that no market or eligible trade exists.
    Missing members remain missing for this snapshot. Isolate a failed batch
    within the same explicit request/deadline budget instead of declaring every
    unrelated instrument unavailable. Budget exhaustion preserves unread work
    as unresolved, not as a completed no-trade scan. Different providers may not implement native batching, so
    measure actual HTTP work before claiming a speed improvement.
    """
    assets = list(dict.fromkeys(assets))
    if max_requests is None:
        batch_count = (len(assets) + 49) // 50
        max_requests = max(1, 2 * len(assets) - batch_count)
    if type(max_requests) is not int or max_requests < 1:
        raise ValueError('max_requests must be a positive finite integer')
    if deadline is not None and not math.isfinite(deadline):
        raise ValueError('deadline must be a finite monotonic time')
    values = dict.fromkeys(assets)
    unavailable: dict[Any, str] = {}
    acquired_at: dict[Any, float] = {}
    pending = deque(assets[index:index + 50] for index in range(0, len(assets), 50))
    requests = 0
    failed_requests = 0
    while pending:
        reason = 'deadline' if deadline is not None and monotonic() >= deadline else (
            'request_budget' if requests >= max_requests else None)
        if reason:
            for batch in pending:
                unavailable.update(dict.fromkeys(batch, reason))
            break
        batch = pending.popleft()
        requests += 1
        try:
            quotes = strategy.get_quotes(batch)
            if not isinstance(quotes, dict) or any(asset not in quotes for asset in batch):
                raise ValueError('Quote adapter omitted requested members')
        except (ConnectionError, HTTPError, ValueError, TypeError) as exc:
            failed_requests += 1
            logging.getLogger(__name__).warning(
                "Quote batch acquisition failed: %s for %d requested assets; bounded recovery applies",
                type(exc).__name__, len(batch),
            )
            if len(batch) == 1:
                unavailable[batch[0]] = ('request_failed' if isinstance(exc, (ConnectionError, HTTPError))
                                         else 'invalid_response')
            else:
                middle = len(batch) // 2
                pending.appendleft(batch[middle:])
                pending.appendleft(batch[:middle])
            continue
        observed_at = monotonic()
        for asset in batch:
            values[asset] = quotes[asset]
            acquired_at[asset] = observed_at
            if quotes[asset] is None:
                unavailable[asset] = 'missing'
    deferred = sum(reason in {"deadline", "request_budget"} for reason in unavailable.values())
    if failed_requests or deferred:
        logging.getLogger(__name__).warning(
            "Quote acquisition: %d failed quote requests; %d retained quotes, "
            "%d unavailable/unread assets; reasons=%s",
            failed_requests, sum(value is not None for value in values.values()),
            len(unavailable), ",".join(sorted(set(unavailable.values()))) or "recovered",
        )
    return QuoteSnapshot(values, unavailable, acquired_at, requests)
