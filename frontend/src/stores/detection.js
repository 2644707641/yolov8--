import { defineStore } from "pinia";
import { ref } from "vue";
import { supabase } from "../config/supabase";
import axios from "axios";
import { buildProtectedApiUrl } from "../utils/protected-url";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const SETTINGS_STORAGE_KEY = "yolov8.settings.v1";
const HISTORY_CACHE_TTL_MS = 60 * 1000;

const defaultDetectionParams = {
  imgSize: 640,
  confidence: 0.5,
  iouThreshold: 0.6,
  maxDetections: 300,
  frameSkip: 1,
};

const defaultRealtimePrefs = {
  recordEnabled: true,
  recordFps: 8,
  recordDurationSeconds: 0,
  sourceMode: "camera",
  networkStreamUrl: "",
};

const getStorage = () => {
  if (typeof window === "undefined") return null;
  return window.localStorage || null;
};

const loadLocalSettings = () => {
  const storage = getStorage();
  if (!storage) return {};
  try {
    return JSON.parse(storage.getItem(SETTINGS_STORAGE_KEY) || "{}");
  } catch (error) {
    console.warn("读取本地设置失败，已忽略:", error);
    return {};
  }
};

const saveLocalSettings = (payload) => {
  const storage = getStorage();
  if (!storage) return;
  storage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(payload));
};

const clearLocalSettings = () => {
  const storage = getStorage();
  if (!storage) return;
  storage.removeItem(SETTINGS_STORAGE_KEY);
};

const normalizeDefaults = (raw) => ({
  imgSize: Math.max(320, Number(raw.imgSize || 640)),
  confidence: Math.min(1, Math.max(0, Number(raw.confidence || 0.5))),
  iouThreshold: Math.min(1, Math.max(0, Number(raw.iouThreshold || 0.6))),
  maxDetections: Math.max(1, Number(raw.maxDetections || 1)),
  frameSkip: Math.max(1, Number(raw.frameSkip || 1)),
});

const normalizeRealtimePrefs = (raw) => ({
  recordEnabled: Boolean(raw.recordEnabled),
  recordFps: Math.max(1, Number(raw.recordFps || 8)),
  recordDurationSeconds: Math.max(0, Number(raw.recordDurationSeconds || 0)),
  sourceMode: raw.sourceMode === "network" ? "network" : "camera",
  networkStreamUrl: String(raw.networkStreamUrl || "").trim(),
});

export const useDetectionStore = defineStore("detection", () => {
  const localSettings = loadLocalSettings();
  const modelFile = ref(null);
  const modelUploaded = ref(false);
  const requestError = ref("");
  const detectionParams = ref(
    normalizeDefaults({
      ...defaultDetectionParams,
      ...(localSettings.defaults || {}),
    }),
  );
  const realtimePrefs = ref(
    normalizeRealtimePrefs({
      ...defaultRealtimePrefs,
      ...(localSettings.realtime || {}),
    }),
  );
  const isProcessing = ref(false);
  // 批量识别进度，{ percent, message, stage, current, total }
  const detectionProgress = ref({
    percent: 0,
    message: "",
    stage: "",
    current: 0,
    total: 0,
  });
  const detectionHistory = ref([]);
  const currentResult = ref(null);
  const historyLoading = ref(false);
  const historyError = ref("");
  const lastHistorySyncAt = ref(0);
  const historyCacheUserId = ref(null);
  const historyCacheFetchedAt = ref(0);
  const historyLoaded = ref(false);

  const updateHistoryState = (userId, items, fetchedAt = Date.now()) => {
    detectionHistory.value = Array.isArray(items) ? items : [];
    historyCacheUserId.value = userId || null;
    historyCacheFetchedAt.value = fetchedAt;
    historyLoaded.value = Boolean(userId);
    lastHistorySyncAt.value = fetchedAt;
  };

  const resetHistoryState = () => {
    detectionHistory.value = [];
    historyCacheUserId.value = null;
    historyCacheFetchedAt.value = 0;
    historyLoaded.value = false;
    lastHistorySyncAt.value = 0;
  };

  const hasFreshHistoryMemoryCache = (userId) => {
    if (!historyLoaded.value || historyCacheUserId.value !== userId) {
      return false;
    }
    return Date.now() - historyCacheFetchedAt.value <= HISTORY_CACHE_TTL_MS;
  };

  const persistSettings = () => {
    saveLocalSettings({
      defaults: detectionParams.value,
      realtime: realtimePrefs.value,
    });
  };

  const updateDefaults = (next = {}) => {
    detectionParams.value = normalizeDefaults({
      ...detectionParams.value,
      ...next,
    });
    persistSettings();
  };

  const updateRealtimePrefs = (next = {}) => {
    realtimePrefs.value = normalizeRealtimePrefs({
      ...realtimePrefs.value,
      ...next,
    });
    persistSettings();
  };

  // 上传模型文件到后端
  const getAuthHeader = async () => {
    const {
      data: { session },
      error,
    } = await supabase.auth.getSession();
    if (error || !session?.access_token) {
      throw new Error("未检测到有效的登录会话，请重新登录后重试");
    }
    return `Bearer ${session.access_token}`;
  };

  const extractBearerToken = (authHeader) => {
    if (typeof authHeader !== "string") return "";
    return authHeader.replace(/^Bearer\s+/i, "").trim();
  };

  const uploadModel = async (file, name = null, description = null) => {
    try {
      isProcessing.value = true;
      requestError.value = "";
      const formData = new FormData();
      formData.append("model", file);
      if (name) {
        formData.append("name", name);
      }
      if (description) {
        formData.append("description", description);
      }

      const authHeader = await getAuthHeader();

      const response = await axios.post(
        `${API_URL}/api/upload-model`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: authHeader,
          },
        },
      );

      modelFile.value = file;
      modelUploaded.value = true;

      return { success: true, data: response.data };
    } catch (error) {
      console.error("上传模型失败:", error);

      // 提取详细错误信息
      let errorMessage = "上传失败";
      if (error.response) {
        // 后端返回的错误
        errorMessage =
          error.response.data?.detail ||
          error.response.data?.message ||
          `HTTP ${error.response.status} 错误`;
        console.error("后端错误详情:", error.response.data);
      } else if (error.request) {
        // 请求已发送但没有收到响应
        errorMessage = "无法连接到后端服务，请确保后端已启动在端口8000";
      } else {
        // 请求配置错误
        errorMessage = error.message;
      }
      requestError.value = errorMessage;

      return { success: false, error: errorMessage };
    } finally {
      isProcessing.value = false;
    }
  };

  // 执行检测（SSE 流式进度版）
  const runDetection = async (file, type = "image") => {
    try {
      isProcessing.value = true;
      requestError.value = "";
      detectionProgress.value = {
        percent: 0,
        message: "正在准备上传...",
        stage: "prepare",
        current: 0,
        total: 0,
      };

      const formData = new FormData();
      formData.append("file", file);
      formData.append("type", type);
      formData.append("params", JSON.stringify(detectionParams.value));

      const authHeader = await getAuthHeader();
      const accessToken = extractBearerToken(authHeader);

      // 使用 fetch 读取 SSE 流
      const response = await fetch(`${API_URL}/api/detect`, {
        method: "POST",
        headers: {
          Authorization: authHeader,
          // 不设置 Content-Type，让浏览器自动设置 multipart/form-data boundary
        },
        body: formData,
      });

      if (!response.ok) {
        let detail = `HTTP ${response.status} 错误`;
        try {
          const errData = await response.json();
          detail = errData?.detail || errData?.message || detail;
        } catch (_) {}
        throw new Error(detail);
      }

      let result = null;
      const contentType = response.headers?.get?.("content-type") || "";

      if (contentType.includes("application/json")) {
        // 兼容当前后端返回 JSON 的协议
        result = await response.json();
        detectionProgress.value = {
          percent: 100,
          message: "识别完成！",
          stage: "result",
          current: 0,
          total: 0,
        };
      } else {
        // 兼容 SSE 流式协议
        const reader = response.body?.getReader?.();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";

        if (!reader) {
          throw new Error("识别响应为空，请重试");
        }

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // SSE 格式：每条消息以 \n\n 结尾
          const parts = buffer.split("\n\n");
          buffer = parts.pop(); // 最后一段可能不完整，保留

          for (const part of parts) {
            const line = part.trim();
            if (!line.startsWith("data:")) continue;
            const jsonStr = line.slice(5).trim();
            if (!jsonStr) continue;

            let event;
            try {
              event = JSON.parse(jsonStr);
            } catch (_) {
              continue;
            }

            if (event.stage === "error") {
              throw new Error(event.message || "识别过程中发生错误");
            }

            if (event.stage === "result") {
              // 最终结果
              result = event.data;
              detectionProgress.value = {
                percent: 100,
                message: "识别完成！",
                stage: "result",
                current: 0,
                total: 0,
              };
            } else {
              // 进度更新
              detectionProgress.value = {
                percent: event.percent ?? detectionProgress.value.percent,
                message: event.message ?? "",
                stage: event.stage ?? "",
                current: event.current ?? 0,
                total: event.total ?? 0,
              };
            }
          }
        }

        // 兜底：某些网关会把 JSON 当普通文本返回（非 SSE）
        if (!result && buffer.trim()) {
          try {
            result = JSON.parse(buffer.trim());
            detectionProgress.value = {
              percent: 100,
              message: "识别完成！",
              stage: "result",
              current: 0,
              total: 0,
            };
          } catch (_) {
            // ignore and let next validation throw
          }
        }
      }

      if (!result) {
        throw new Error("未收到识别结果，请重试");
      }

      const resultPayload =
        result?.data &&
        typeof result.data === "object" &&
        !Array.isArray(result.data) &&
        result.resultUrl === undefined &&
        result.originalUrlSupabase === undefined
          ? result.data
          : result;

      if (resultPayload?.success === false) {
        throw new Error(
          resultPayload?.detail || resultPayload?.message || "识别失败",
        );
      }

      console.log("[DEBUG] 后端返回的结果:", resultPayload);

      // 使用后端返回的URL（优先使用Supabase URL，如果没有则使用本地API URL）
      const originalUrl =
        resultPayload.originalUrlSupabase || URL.createObjectURL(file);
      const resultUrl =
        resultPayload.resultUrlSupabase ||
        (await buildProtectedApiUrl(resultPayload.resultUrl, accessToken));

      console.log("[DEBUG] 原始图片URL:", originalUrl);
      console.log("[DEBUG] 结果URL:", resultUrl);

      // 设置当前结果
      currentResult.value = {
        ...resultPayload,
        originalUrl: originalUrl,
        resultUrl: resultUrl,
        isSupabase: !!resultPayload.originalUrlSupabase,
      };

      console.log("[DEBUG] 当前结果设置为:", currentResult.value);

      // 推送加载历史记录进度
      detectionProgress.value = {
        percent: 100,
        message: "正在同步历史记录...",
        stage: "loading_history",
        current: 0,
        total: 0,
      };

      // 重新加载历史记录
      await loadHistory({ force: true });

      detectionProgress.value = {
        percent: 100,
        message: "全部完成！",
        stage: "done",
        current: 0,
        total: 0,
      };

      return { success: true, data: currentResult.value };
    } catch (error) {
      console.error("检测失败:", error);
      currentResult.value = null;

      const errorMessage = error.message || "检测失败";
      requestError.value = errorMessage;
      detectionProgress.value = {
        percent: 0,
        message: errorMessage,
        stage: "error",
        current: 0,
        total: 0,
      };

      return { success: false, error: errorMessage };
    } finally {
      isProcessing.value = false;
    }
  };

  // 加载历史记录
  const loadHistory = async ({ force = false } = {}) => {
    historyLoading.value = true;
    historyError.value = "";
    try {
      const {
        data: { user },
      } = await supabase.auth.getUser();
      const userId = user?.id;

      if (!userId) {
        resetHistoryState();
        return [];
      }

      if (!force && hasFreshHistoryMemoryCache(userId)) {
        lastHistorySyncAt.value = historyCacheFetchedAt.value;
        return detectionHistory.value;
      }

      if (historyCacheUserId.value && historyCacheUserId.value !== userId) {
        resetHistoryState();
      }

      const authHeader = await getAuthHeader();
      const response = await axios.get(`${API_URL}/api/history`, {
        headers: {
          Authorization: authHeader,
        },
      });

      const items = Array.isArray(response.data?.items)
        ? response.data.items
        : [];
      const fetchedAt = Date.now();
      updateHistoryState(userId, items, fetchedAt);
      return detectionHistory.value;
    } catch (error) {
      console.error("加载历史记录失败:", error);
      historyError.value = error?.message || "历史记录加载失败";
      return detectionHistory.value;
    } finally {
      historyLoading.value = false;
    }
  };

  // 删除历史记录
  const deleteHistory = async (id) => {
    try {
      requestError.value = "";
      const authHeader = await getAuthHeader();
      await axios.delete(`${API_URL}/api/history/${id}`, {
        headers: {
          Authorization: authHeader,
        },
      });

      const nextHistory = detectionHistory.value.filter(
        (item) => item.id !== id,
      );
      detectionHistory.value = nextHistory;
      if (historyCacheUserId.value) {
        historyCacheFetchedAt.value = Date.now();
      }

      return { success: true };
    } catch (error) {
      console.error("删除失败:", error);
      const errorMessage =
        error?.response?.data?.detail || error.message || "删除失败";
      requestError.value = errorMessage;
      return { success: false, error: errorMessage };
    }
  };

  // 从后端加载 realtime 偏好，覆盖本地缓存
  const initRealtimeFromBackend = async () => {
    try {
      const {
        data: { session },
      } = await supabase.auth.getSession();
      if (!session?.access_token) return;
      const response = await fetch(`${API_URL}/api/settings`, {
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });
      if (!response.ok) return;
      const data = await response.json();
      const realtime = data.settings?.realtime;
      if (realtime) {
        realtimePrefs.value = normalizeRealtimePrefs({
          ...defaultRealtimePrefs,
          ...realtime,
        });
        persistSettings();
      }
    } catch {
      // 后端加载失败，使用本地缓存
    }
  };

  // 清理缓存（退出登录时使用）
  const clearCache = () => {
    modelFile.value = null;
    modelUploaded.value = false;
    resetHistoryState();
    currentResult.value = null;
    requestError.value = "";
    historyLoading.value = false;
    historyError.value = "";
    // 重置参数到默认值
    detectionParams.value = { ...defaultDetectionParams };
    realtimePrefs.value = { ...defaultRealtimePrefs };
    clearLocalSettings();
    console.log("✅ 已清理用户检测缓存");
  };

  return {
    modelFile,
    modelUploaded,
    requestError,
    detectionParams,
    realtimePrefs,
    isProcessing,
    detectionProgress,
    detectionHistory,
    currentResult,
    historyLoading,
    historyError,
    lastHistorySyncAt,
    updateDefaults,
    updateRealtimePrefs,
    initRealtimeFromBackend,
    uploadModel,
    runDetection,
    loadHistory,
    deleteHistory,
    clearCache,
  };
});
