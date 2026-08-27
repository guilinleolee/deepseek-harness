/**
 * TTS 适配层 · edge-tts（微软 Edge 免费 API）
 * 完全免费 · 无需 API Key
 * 中文音色：zh-CN-XiaoxiaoNeural（晓晓）/ zh-CN-YunxiNeural（云希）
 */
import { EdgeTTS } from 'edge-tts';
import * as Minio from 'minio';

export interface TTSOptions {
  voice?: string;
  rate?: string;
  pitch?: string;
}

export class EdgeTTSProvider {
  private defaultVoice: string;
  private minioClient: Minio.Client;
  private bucket: string;

  constructor() {
    this.defaultVoice = process.env.TTS_DEFAULT_VOICE || 'zh-CN-XiaoxiaoNeural';
    this.minioClient = new Minio.Client({
      endPoint: process.env.MINIO_ENDPOINT || "minio",
      port: parseInt(process.env.MINIO_PORT || "9000", 10),
      useSSL: false,
      accessKey: process.env.MINIO_ROOT_USER || 'minio_admin',
      secretKey: process.env.MINIO_ROOT_PASSWORD || 'minio_secret_2026'
    });
    this.bucket = process.env.MINIO_BUCKET || 'cs-audio';
    console.log(`[TTS] edge-tts 初始化 · voice=${this.defaultVoice} · bucket=${this.bucket}`);
  }

  async synthesize(text: string, options: TTSOptions = {}): Promise<{ url: string }> {
    const voice = options.voice || this.defaultVoice;
    const tts = new EdgeTTS({ voice, rate: options.rate || "+0%", pitch: options.pitch || "+0Hz" });

    const audioChunks: Buffer[] = [];
    tts.on("data", (chunk: Buffer) => audioChunks.push(chunk));

    await new Promise<void>((resolve, reject) => {
      tts.on("end", () => resolve());
      tts.on("error", (err: any) => reject(err));
      tts.synthesize(text);
    });

    const audioBuffer = Buffer.concat(audioChunks);
    const filename = `tts/${Date.now()}-${Math.random().toString(36).slice(2, 8)}.mp3`;

    await this.ensureBucket();
    await this.minioClient.putObject(this.bucket, filename, audioBuffer, audioBuffer.length, {
      "Content-Type": "audio/mpeg"
    });

    const url = `http://${process.env.MINIO_ENDPOINT}:${process.env.MINIO_PORT}/${this.bucket}/${filename}`;
    return { url };
  }

  private async ensureBucket(): Promise<void> {
    try {
      const exists = await this.minioClient.bucketExists(this.bucket);
      if (!exists) {
        await this.minioClient.makeBucket(this.bucket, 'us-east-1');
      }
    } catch (e) {
      console.error("[TTS] MinIO bucket 错误:", e);
    }
  }
}

let instance: EdgeTTSProvider | null = null;
export function getTTS(): EdgeTTSProvider {
  if (!instance) instance = new EdgeTTSProvider();
  return instance;
}
