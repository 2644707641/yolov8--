from __future__ import annotations

from collections import OrderedDict

DEFAULT_TRACK_MAX_AGE_SECONDS = 300.0
DEFAULT_TRACK_MAX_IDS = 4096


def _drop_empty_classes(registry: dict[str, OrderedDict[str, float]]) -> None:
    for class_name in list(registry.keys()):
        if not registry[class_name]:
            del registry[class_name]


def prune_live_track_registry(
    registry: dict[str, OrderedDict[str, float]],
    *,
    now_monotonic: float,
    max_age_seconds: float = DEFAULT_TRACK_MAX_AGE_SECONDS,
    max_total_ids: int = DEFAULT_TRACK_MAX_IDS,
) -> None:
    expire_before = now_monotonic - max(0.0, float(max_age_seconds))

    for class_name, track_times in list(registry.items()):
        expired_track_ids = [
            track_id
            for track_id, last_seen_at in track_times.items()
            if last_seen_at < expire_before
        ]
        for track_id in expired_track_ids:
            track_times.pop(track_id, None)

    _drop_empty_classes(registry)

    if max_total_ids <= 0:
        registry.clear()
        return

    total_ids = sum(len(track_times) for track_times in registry.values())
    if total_ids <= max_total_ids:
        return

    all_tracks = sorted(
        (
            (last_seen_at, class_name, track_id)
            for class_name, track_times in registry.items()
            for track_id, last_seen_at in track_times.items()
        ),
        key=lambda item: item[0],
    )

    for _, class_name, track_id in all_tracks:
        if total_ids <= max_total_ids:
            break
        track_times = registry.get(class_name)
        if not track_times or track_id not in track_times:
            continue
        del track_times[track_id]
        total_ids -= 1

    _drop_empty_classes(registry)


def track_live_detection(
    registry: dict[str, OrderedDict[str, float]],
    *,
    class_name: str,
    track_id: str,
    now_monotonic: float,
    max_age_seconds: float = DEFAULT_TRACK_MAX_AGE_SECONDS,
    max_total_ids: int = DEFAULT_TRACK_MAX_IDS,
) -> None:
    prune_live_track_registry(
        registry,
        now_monotonic=now_monotonic,
        max_age_seconds=max_age_seconds,
        max_total_ids=max_total_ids,
    )

    track_times = registry.setdefault(class_name, OrderedDict())
    if track_id in track_times:
        del track_times[track_id]
    track_times[track_id] = now_monotonic

    prune_live_track_registry(
        registry,
        now_monotonic=now_monotonic,
        max_age_seconds=max_age_seconds,
        max_total_ids=max_total_ids,
    )


def summarize_live_track_counts(
    registry: dict[str, OrderedDict[str, float]],
) -> tuple[dict[str, int], int, str]:
    class_counts = dict(
        sorted(
            (
                (class_name, len(track_times))
                for class_name, track_times in registry.items()
                if track_times
            ),
            key=lambda item: item[1],
            reverse=True,
        )
    )
    return class_counts, sum(class_counts.values()), "tracking_unique"
