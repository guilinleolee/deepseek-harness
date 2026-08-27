/**
 * ASR 适配层 · faster-whisper（本地推理）
 * 通过 HTTP 调用 faster-whisper-server 容器
 * 零费用 · 零 API Key
 */
import axios from 'axios';

export interface ASRResult {
  text: string;
  language: string;
  duration?: number;
}

export class WhisperASRProvider {
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.WHISPER_BASE_URL || 'http://faster-whisper:8000';
    console.log(`[ASR] faster-whisper 初始化 · baseURL=${this.baseURL}`);
  }

  async transcribe(audioBuffer: Buffer, filename: string = "audio.webm"): Promise<ASRResult> {
    const FormData = (await import("form-data")).default;
    const formData = new FormData();
    formData.append("file", audioBuffer, { filename });
    formData.append("language", "zh");
    formData.append("response_format", "json");

    const resp = await axios.post(`${this.baseURL}/v1/audio/transcriptions`, formData, {
      headers: formData.getHeaders(),
      timeout: 60000
    });

    return {
      text: resp.data.text || "",
      language: resp.data.language || "zh",
      duration: resp.data.duration
    };
  }
}

let instance: WhisperASRProvider | null = null;
export function getASR(): WhisperASRProvider {
  if (!instance) instance = new WhisperASRProvider();
  return instance;
}
