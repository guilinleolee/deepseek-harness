/**
 * 健康检查路由 · 检查所有依赖服务
 */
import { FastifyPluginAsync } from 'fastify';

export const healthRoutes: FastifyPluginAsync = async (fastify) => {
  fastify.get('/', async () => {
    const checks = {
      backend: 'ok',
      database: 'unknown',
      minio: 'unknown',
      fastgpt: 'unknown',
      whisper: 'unknown',
      llm: 'unknown'
    };

    try {
      const { Pool } = await import('pg');
      const pool = new Pool({ connectionString: process.env.DATABASE_URL });
      await pool.query('SELECT 1');
      await pool.end();
      checks.database = 'ok';
    } catch (e) {
      checks.database = 'fail';
    }

    try {
      const axios = (await import('axios')).default;
      await axios.get(`http://${process.env.MINIO_ENDPOINT}:${process.env.MINIO_PORT}/minio/health/live`, { timeout: 3000 });
      checks.minio = 'ok';
    } catch (e) {
      checks.minio = 'fail';
    }

    try {
      const axios = (await import('axios')).default;
      await axios.get(`${process.env.FASTGPT_BASE_URL}/api/v1/dataset/list`, {
        headers: { Authorization: `Bearer ${process.env.FASTGPT_API_KEY}` },
        timeout: 3000
      });
      checks.fastgpt = 'ok';
    } catch (e) {
      checks.fastgpt = 'fail';
    }

    try {
      const axios = (await import('axios')).default;
      const r = await axios.get(`${process.env.WHISPER_BASE_URL}/`, { timeout: 3000 });
      if (r.status === 200) checks.whisper = "ok";
      else checks.whisper = 'fail';
    } catch (e) {
      checks.whisper = 'fail';
    }

    const allOk = Object.values(checks).every(v => v === "ok" || v === "unknown");
    return {
      status: allOk ? "ok" : "degraded",
      timestamp: new Date().toISOString(),
      services: checks
    };
  });

  fastify.get('/ping', async () => ({ pong: true, ts: Date.now() }));
};
