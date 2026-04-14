const DEFAULT_MIN_RENDER_INTERVAL_MS = 100;

export const getRealtimeCaptureSize = ({
  width,
  height,
  targetLongEdge = 640,
}) => {
  const sourceWidth = Math.max(1, Math.round(Number(width) || 0));
  const sourceHeight = Math.max(1, Math.round(Number(height) || 0));
  const normalizedTarget = Math.max(
    320,
    Math.min(1280, Math.round(Number(targetLongEdge) || 640)),
  );

  const sourceLongEdge = Math.max(sourceWidth, sourceHeight);
  if (sourceLongEdge <= normalizedTarget) {
    return {
      width: sourceWidth,
      height: sourceHeight,
    };
  }

  const scale = normalizedTarget / sourceLongEdge;
  return {
    width: Math.max(1, Math.round(sourceWidth * scale)),
    height: Math.max(1, Math.round(sourceHeight * scale)),
  };
};

export const createLatestFrameScheduler = ({
  commit,
  minIntervalMs = DEFAULT_MIN_RENDER_INTERVAL_MS,
  now = () => Date.now(),
  schedule = (callback, delay) => globalThis.setTimeout(callback, delay),
  clear = (timerId) => globalThis.clearTimeout(timerId),
}) => {
  let latestPayload = null;
  let timerId = null;
  let lastCommittedAt = null;
  let disposed = false;

  const queue = () => {
    if (disposed || timerId !== null || latestPayload === null) return;
    const wait =
      lastCommittedAt === null
        ? 0
        : Math.max(0, minIntervalMs - (now() - lastCommittedAt));
    timerId = schedule(flush, wait);
  };

  function flush() {
    if (timerId !== null) {
      clear(timerId);
      timerId = null;
    }
    if (disposed || latestPayload === null) return;

    const payload = latestPayload;
    latestPayload = null;
    lastCommittedAt = now();
    commit(payload);

    if (latestPayload !== null) {
      queue();
    }
  }

  return {
    enqueue(payload) {
      if (disposed) return;
      latestPayload = payload;
      queue();
    },
    flush,
    dispose() {
      disposed = true;
      latestPayload = null;
      if (timerId !== null) {
        clear(timerId);
        timerId = null;
      }
    },
  };
};
