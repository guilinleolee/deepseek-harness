/**
 * 客服工作台后端 · 主入口
 * 协议：MIT · 作者：天龙引擎 dragon-engine V2.5
 */
import 'dotenv/config';
import Fastify from 'fastify';
import cors from '@fastify/cors';
import websocket from '@fastify/websocket';
import { healthRoutes } from './routes/health';

const PORT = parseInt(process.env.PORT || "8080", 10);
const NODE_ENV = process.env.NODE_ENV || 'development';

const app = Fastify({
  logger: {
    level: NODE_ENV === 'production' ? 'info' : 'debug'
  }
});

app.register(cors, { origin: true, credentials: true });
app.register(websocket);
app.register(healthRoutes, { prefix: '/health' });

app.get('/', async () => ({
  name: 'customer-service-backend',
  version: '0.1.0',
  engine: 'dragon-engine-V2.5'
}));

const start = async () => {
  try {
    await app.listen({ port: PORT, host: "0.0.0.0" });
    app.log.info(`客服工作台后端已启动: http://localhost:${PORT}`);
  } catch (err) {
    app.log.error(err);
    process.exit(1);
  }
};

start();
