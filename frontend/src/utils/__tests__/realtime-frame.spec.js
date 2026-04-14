import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  createLatestFrameScheduler,
  getRealtimeCaptureSize,
} from "../realtime-frame";

describe("getRealtimeCaptureSize", () => {
  it("保留宽高比并限制最长边", () => {
    expect(
      getRealtimeCaptureSize({
        width: 1920,
        height: 1080,
        targetLongEdge: 640,
      }),
    ).toEqual({
      width: 640,
      height: 360,
    });
  });

  it("小尺寸输入不放大", () => {
    expect(
      getRealtimeCaptureSize({
        width: 320,
        height: 240,
        targetLongEdge: 640,
      }),
    ).toEqual({
      width: 320,
      height: 240,
    });
  });
});

describe("createLatestFrameScheduler", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-04-14T00:00:00.000Z"));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("首帧立即提交，间隔内仅保留最新帧", async () => {
    const commit = vi.fn();
    const scheduler = createLatestFrameScheduler({
      commit,
      minIntervalMs: 100,
    });

    scheduler.enqueue({ id: 1 });
    scheduler.enqueue({ id: 2 });
    await vi.advanceTimersByTimeAsync(0);

    expect(commit).toHaveBeenCalledTimes(1);
    expect(commit).toHaveBeenLastCalledWith({ id: 2 });

    scheduler.enqueue({ id: 3 });
    scheduler.enqueue({ id: 4 });
    await vi.advanceTimersByTimeAsync(99);

    expect(commit).toHaveBeenCalledTimes(1);

    await vi.advanceTimersByTimeAsync(1);

    expect(commit).toHaveBeenCalledTimes(2);
    expect(commit).toHaveBeenLastCalledWith({ id: 4 });
  });

  it("dispose 会取消未提交帧", async () => {
    const commit = vi.fn();
    const scheduler = createLatestFrameScheduler({
      commit,
      minIntervalMs: 100,
    });

    scheduler.enqueue({ id: 1 });
    await vi.advanceTimersByTimeAsync(0);
    scheduler.enqueue({ id: 2 });
    scheduler.dispose();
    await vi.advanceTimersByTimeAsync(100);

    expect(commit).toHaveBeenCalledTimes(1);
    expect(commit).toHaveBeenLastCalledWith({ id: 1 });
  });
});
