const DEFAULT_SOURCE_FPS = 25;
const DEFAULT_MIN_SAMPLE_FPS = 2;
const DEFAULT_MAX_SAMPLE_FPS = 12;
const VIDEO_TRACK_HANDLER = "vide";
const MP4_EOF_EPSILON_SECONDS = 1e-6;

const textDecoder = new TextDecoder();

const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

const readBoxHeader = (buffer, offset) => {
  if (offset + 8 > buffer.byteLength) return null;

  const view = new DataView(buffer, offset);
  let size = view.getUint32(0);
  const type = textDecoder.decode(new Uint8Array(buffer, offset + 4, 4));
  let headerSize = 8;

  if (size === 1) {
    if (offset + 16 > buffer.byteLength) return null;
    const largeSizeView = new DataView(buffer, offset + 8);
    const largeSize = Number(largeSizeView.getBigUint64(0));
    if (!Number.isFinite(largeSize) || largeSize < 16) return null;
    size = largeSize;
    headerSize = 16;
  } else if (size === 0) {
    size = buffer.byteLength - offset;
  }

  if (!Number.isFinite(size) || size < headerSize) return null;
  const end = offset + size;
  if (end > buffer.byteLength) return null;

  return {
    type,
    size,
    headerSize,
    dataOffset: offset + headerSize,
    end,
  };
};

const findChildBox = (buffer, parentBox, targetType) => {
  let offset = parentBox.dataOffset;
  while (offset < parentBox.end) {
    const child = readBoxHeader(buffer, offset);
    if (!child) break;
    if (child.type === targetType) {
      return child;
    }
    offset = child.end;
  }
  return null;
};

const iterateBoxes = (buffer, start, end, visitor) => {
  let offset = start;
  while (offset < end) {
    const box = readBoxHeader(buffer, offset);
    if (!box) break;
    visitor(box);
    offset = box.end;
  }
};

const readUint32 = (buffer, offset) => new DataView(buffer, offset, 4).getUint32(0);

const readUint64 = (buffer, offset) => {
  const value = new DataView(buffer, offset, 8).getBigUint64(0);
  return Number(value);
};

const readMdhd = (buffer, mdhdBox) => {
  const version = new DataView(buffer, mdhdBox.dataOffset, 1).getUint8(0);
  if (version === 1) {
    const timescale = readUint32(buffer, mdhdBox.dataOffset + 20);
    const duration = readUint64(buffer, mdhdBox.dataOffset + 24);
    return { timescale, duration };
  }

  const timescale = readUint32(buffer, mdhdBox.dataOffset + 12);
  const duration = readUint32(buffer, mdhdBox.dataOffset + 16);
  return { timescale, duration };
};

const readHdlrType = (buffer, hdlrBox) =>
  textDecoder.decode(new Uint8Array(buffer, hdlrBox.dataOffset + 8, 4));

const readSttsSampleCount = (buffer, sttsBox) => {
  const entryCount = readUint32(buffer, sttsBox.dataOffset + 4);
  let totalSamples = 0;
  let offset = sttsBox.dataOffset + 8;

  for (let index = 0; index < entryCount; index += 1) {
    if (offset + 8 > sttsBox.end) {
      return 0;
    }
    totalSamples += readUint32(buffer, offset);
    offset += 8;
  }

  return totalSamples;
};

export const readMp4VideoTrackInfo = (arrayBuffer) => {
  if (!(arrayBuffer instanceof ArrayBuffer)) return null;

  let result = null;
  iterateBoxes(arrayBuffer, 0, arrayBuffer.byteLength, (box) => {
    if (box.type !== "moov" || result) return;

    iterateBoxes(arrayBuffer, box.dataOffset, box.end, (trakBox) => {
      if (trakBox.type !== "trak" || result) return;

      const mdia = findChildBox(arrayBuffer, trakBox, "mdia");
      if (!mdia) return;

      const hdlr = findChildBox(arrayBuffer, mdia, "hdlr");
      if (!hdlr || readHdlrType(arrayBuffer, hdlr) !== VIDEO_TRACK_HANDLER) {
        return;
      }

      const mdhd = findChildBox(arrayBuffer, mdia, "mdhd");
      const minf = findChildBox(arrayBuffer, mdia, "minf");
      const stbl = minf ? findChildBox(arrayBuffer, minf, "stbl") : null;
      const stts = stbl ? findChildBox(arrayBuffer, stbl, "stts") : null;
      if (!mdhd || !stts) return;

      const { timescale, duration } = readMdhd(arrayBuffer, mdhd);
      const sampleCount = readSttsSampleCount(arrayBuffer, stts);
      if (!timescale || !duration || !sampleCount) return;

      const durationSeconds = duration / timescale;
      const fps = sampleCount / durationSeconds;
      if (!Number.isFinite(durationSeconds) || durationSeconds <= 0) return;
      if (!Number.isFinite(fps) || fps <= 0) return;

      result = {
        durationSeconds,
        fps,
        sampleCount,
      };
    });
  });

  return result;
};

export const probeMp4VideoTrackInfo = async (file) => {
  if (!file || typeof file.arrayBuffer !== "function") return null;

  const mime = String(file.type || "").toLowerCase();
  const name = String(file.name || "").toLowerCase();
  const isMp4 =
    mime.includes("mp4") ||
    mime.includes("quicktime") ||
    name.endsWith(".mp4") ||
    name.endsWith(".m4v") ||
    name.endsWith(".mov");
  if (!isMp4) {
    return null;
  }

  try {
    return readMp4VideoTrackInfo(await file.arrayBuffer());
  } catch (error) {
    console.warn("MP4 视频轨道信息探测失败:", error);
    return null;
  }
};

export const getRealtimeSamplingPlan = ({
  durationSeconds,
  frameSkip,
  sourceFps,
  fallbackSourceFps = DEFAULT_SOURCE_FPS,
  minSampleFps = DEFAULT_MIN_SAMPLE_FPS,
  maxSampleFps = DEFAULT_MAX_SAMPLE_FPS,
}) => {
  const normalizedDuration = Math.max(0, Number(durationSeconds) || 0);
  const normalizedFrameSkip = Math.max(1, Math.round(Number(frameSkip) || 1));
  const normalizedSourceFps = Number(sourceFps);
  const resolvedSourceFps =
    Number.isFinite(normalizedSourceFps) && normalizedSourceFps > 0
      ? normalizedSourceFps
      : fallbackSourceFps;
  const sampleFps = clamp(
    Math.round(resolvedSourceFps / normalizedFrameSkip) || minSampleFps,
    minSampleFps,
    maxSampleFps,
  );
  const sampleIntervalSeconds = 1 / sampleFps;
  const totalFrames = Math.max(
    1,
    Math.ceil(normalizedDuration / sampleIntervalSeconds),
  );
  const maxSeekTime = Math.max(
    0,
    normalizedDuration - MP4_EOF_EPSILON_SECONDS,
  );
  const timestamps = Array.from({ length: totalFrames }, (_, index) =>
    Math.min(index * sampleIntervalSeconds, maxSeekTime),
  );

  return {
    durationSeconds: normalizedDuration,
    sourceFps: resolvedSourceFps,
    sampleFps,
    sampleIntervalSeconds,
    totalFrames,
    timestamps,
  };
};

export const buildRealtimeResultUrls = ({
  uploadedOriginalUrl,
  recordedOriginalUrl,
  recordedResultUrl,
  previewUrl,
}) => ({
  originalUrl: recordedOriginalUrl || uploadedOriginalUrl || "",
  resultUrl: recordedResultUrl || previewUrl || "",
  resultVideoUrl: recordedResultUrl || "",
});
