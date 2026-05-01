import { describe, expect, it } from "vitest";

import {
  buildRealtimeResultUrls,
  getRealtimeSamplingPlan,
  readMp4VideoTrackInfo,
} from "../realtime-video";

const createBox = (type, ...payloads) => {
  const bodySize = payloads.reduce((total, payload) => total + payload.length, 0);
  const size = 8 + bodySize;
  const box = new Uint8Array(size);
  const view = new DataView(box.buffer);
  view.setUint32(0, size);
  box.set(new TextEncoder().encode(type), 4);

  let offset = 8;
  for (const payload of payloads) {
    box.set(payload, offset);
    offset += payload.length;
  }
  return box;
};

const uint32 = (value) => {
  const bytes = new Uint8Array(4);
  new DataView(bytes.buffer).setUint32(0, value);
  return bytes;
};

const createSyntheticMp4 = () => {
  const mdhd = (() => {
    const payload = new Uint8Array(24);
    const view = new DataView(payload.buffer);
    view.setUint32(12, 1000);
    view.setUint32(16, 10000);
    return createBox("mdhd", payload);
  })();

  const hdlr = (() => {
    const payload = new Uint8Array(24);
    payload.set(new TextEncoder().encode("vide"), 8);
    return createBox("hdlr", payload);
  })();

  const stts = (() => {
    const payload = new Uint8Array(16);
    const view = new DataView(payload.buffer);
    view.setUint32(4, 1);
    view.setUint32(8, 300);
    view.setUint32(12, 1);
    return createBox("stts", payload);
  })();

  const stbl = createBox("stbl", stts);
  const minf = createBox("minf", stbl);
  const mdia = createBox("mdia", mdhd, hdlr, minf);
  const trak = createBox("trak", mdia);
  const moov = createBox("moov", trak);
  const ftyp = createBox("ftyp", new TextEncoder().encode("isom0000isom"));

  const bytes = new Uint8Array(ftyp.length + moov.length);
  bytes.set(ftyp, 0);
  bytes.set(moov, ftyp.length);
  return bytes.buffer;
};

describe("readMp4VideoTrackInfo", () => {
  it("从 MP4 视频轨道中读取真实帧率", () => {
    const info = readMp4VideoTrackInfo(createSyntheticMp4());

    expect(info).toEqual({
      durationSeconds: 10,
      fps: 30,
      sampleCount: 300,
    });
  });
});

describe("getRealtimeSamplingPlan", () => {
  it("真实 FPS 可用时优先按真实 FPS 计算采样计划", () => {
    const plan = getRealtimeSamplingPlan({
      durationSeconds: 10,
      frameSkip: 3,
      sourceFps: 30,
    });

    expect(plan.sourceFps).toBe(30);
    expect(plan.sampleFps).toBe(10);
    expect(plan.totalFrames).toBe(100);
    expect(plan.timestamps[0]).toBe(0);
    expect(plan.timestamps.at(-1)).toBeCloseTo(9.9, 6);
  });

  it("无法探测真实 FPS 时回退到默认 FPS", () => {
    const plan = getRealtimeSamplingPlan({
      durationSeconds: 10,
      frameSkip: 5,
      sourceFps: null,
    });

    expect(plan.sourceFps).toBe(25);
    expect(plan.sampleFps).toBe(5);
    expect(plan.totalFrames).toBe(50);
  });
});

describe("buildRealtimeResultUrls", () => {
  it("结果页优先使用后端录制的原始采样视频", () => {
    expect(
      buildRealtimeResultUrls({
        uploadedOriginalUrl: "blob:uploaded",
        recordedOriginalUrl: "https://example.com/original-recorded.mp4",
        recordedResultUrl: "https://example.com/result.mp4",
        previewUrl: "blob:preview",
      }),
    ).toEqual({
      originalUrl: "https://example.com/original-recorded.mp4",
      resultUrl: "https://example.com/result.mp4",
      resultVideoUrl: "https://example.com/result.mp4",
    });
  });
});
