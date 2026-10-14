/**
 * 测试夹具：受控 OpenAI 兼容上游。仅用于本地验收计量链路——
 * model 含 "stream" 走 SSE（末块带 usage），否则返回 JSON（带 usage）。
 * 不属于平台组件，不进 data/。
 */
import { createServer } from 'node:http'

createServer((req, res) => {
  let raw = ''
  req.on('data', (c) => { raw += c })
  req.on('end', () => {
    const body = JSON.parse(raw || '{}')
    const usage = { prompt_tokens: 100, completion_tokens: 20 }
    if (body.stream === true) {
      res.writeHead(200, { 'content-type': 'text/event-stream' })
      res.write(`data: ${JSON.stringify({ choices: [{ delta: { role: 'assistant' } }] })}\n\n`)
      res.write(`data: ${JSON.stringify({ choices: [{ delta: { content: 'ok' } }], usage })}\n\n`)
      res.write('data: [DONE]\n\n')
      res.end()
    } else {
      res.writeHead(200, { 'content-type': 'application/json' })
      res.end(JSON.stringify({ choices: [{ message: { role: 'assistant', content: 'ok' } }], usage }))
    }
  })
}).listen(9410, '127.0.0.1', () => console.log('mock upstream on 9410'))
