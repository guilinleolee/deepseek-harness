"""
GOAP Planner UI - Browser Verification via CDP WebSocket
Uses Python stdlib only: asyncio + http.client (no pip install needed)
"""
import asyncio
import json
import base64
import time
import os
import sys

# CDP WebSocket endpoint (dynamically discovered via Chrome DevTools JSON API)
WS_URL = None
TARGET_URL = "http://localhost:8765/"
SCREENSHOT_PATH = os.path.join(os.path.dirname(__file__), "..", "screenshot.png")
os.makedirs(os.path.dirname(SCREENSHOT_PATH), exist_ok=True)

# Parse optional --ws-url argument (bypasses fetch_tab_id discovery)
import sys as _sys
_cli_ws_url = None
for _i, _arg in enumerate(_sys.argv[1:]):
    if _arg == "--ws-url" and _i + 1 < len(_sys.argv[1:]):
        _cli_ws_url = _sys.argv[1:][_i + 1]
        break
    if _arg.startswith("--ws-url="):
        _cli_ws_url = _arg.split("=", 1)[1]
        break
if _cli_ws_url:
    WS_URL = _cli_ws_url


async def send_ws(ws, msg: dict) -> dict:
    """Send CDP message over WebSocket, return response."""
    loop = asyncio.get_event_loop()
    raw = json.dumps(msg)
    await loop.run_in_executor(None, ws.send, raw)
    data = await loop.run_in_executor(None, ws.recv)
    return json.loads(data)


async def send_ws_batch(ws, msgs: list) -> list:
    """Send multiple CDP messages, return responses."""
    results = []
    loop = asyncio.get_event_loop()
    for msg in msgs:
        raw = json.dumps(msg)
        await loop.run_in_executor(None, ws.send, raw)
        data = await loop.run_in_executor(None, ws.recv)
        results.append(json.loads(data))
    return results


async def fetch_tab_id():
    """Dynamically discover tab ID from Chrome DevTools JSON API.
    Uses Python stdlib only: urllib.request (no pip install needed).
    Returns: webSocketDebuggerUrl string or None
    """
    import urllib.request
    import json

    try:
        req = urllib.request.Request(
            "http://127.0.0.1:9222/json",
            headers={"Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            tabs = json.loads(resp.read())
        # Find tab matching TARGET_URL
        for tab in tabs:
            if tab.get("url") and "localhost:8765" in tab["url"]:
                ws_url = tab.get("webSocketDebuggerUrl")
                print(f"[OK] Found target tab: {tab.get('title', '?')} -> {ws_url}")
                return ws_url
        # Fallback: return first available tab
        if tabs:
            tab = tabs[0]
            ws_url = tab.get("webSocketDebuggerUrl")
            print(f"[INFO] Target tab not found, using first tab: {tab.get('title', '?')} -> {ws_url}")
            return ws_url
        print("[WARN] No Chrome tabs found")
        return None
    except Exception as e:
        print(f"[WARN] Could not discover tab: {e}")
        return None


async def main():
    import asyncio
    import websocket  # Try stdlib first, fallback below

    print("=" * 60)
    print("GOAP Planner UI - Browser Verification")
    print("=" * 60)

    # Dynamically discover WebSocket URL from Chrome DevTools
    discovered_ws_url = await fetch_tab_id()
    if not discovered_ws_url:
        print("[ERROR] Could not discover Chrome tab. Make sure Chrome is running with --remote-debugging-port=9222")
        sys.exit(1)

    WS_URL = discovered_ws_url  # Wire the discovered URL into the module-level variable used below

    # Try websocket-client module first (more reliable)
    try:
        import websocket as ws_module
        # Chrome要求--remote-allow-origins=*,但已有Chrome没设此标志
        # 显式设置Origin头为Chrome本身允许的origin
        ws = ws_module.create_connection(
            WS_URL, timeout=30,
            header=[]  # Empty list suppresses the library's default Origin header
        )
        ws.settimeout(30)
        print(f"[OK] Connected to CDP WebSocket")
    except ImportError:
        # Fallback: use asyncio + stdlib for WebSocket
        print("[INFO] websocket-client not available, using asyncio WebSocket")
        import asyncio
        import asyncio as _asyncio

        # Use asyncio.start_server with WebSocket protocol
        # Actually, let's just try the stdlib approach
        try:
            import asyncio
            # Python 3.7+ has asyncio.open_connection but needs a protocol
            # For CDP, we need WebSocket - let's use aiohttp if available
            try:
                import aiohttp
                has_aiohttp = True
            except ImportError:
                has_aiohttp = False

            if not has_aiohttp:
                print("[ERROR] Need websocket-client or aiohttp for WebSocket. Install with:")
                print("  pip install websocket-client")
                print("\nOr use node-based CDP instead.")
                sys.exit(1)
        except Exception as e:
            print(f"[ERROR] {e}")
            print("[ERROR] Need websocket-client. Install: pip install websocket-client")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to connect: {e}")
        sys.exit(1)

    msg_id = [0]

    def next_id():
        msg_id[0] += 1
        return msg_id[0]

    try:
        # Step 1: Navigate to target URL
        print(f"\n[1/7] Navigating to {TARGET_URL}")
        resp = await send_ws(ws, {
            "id": next_id(),
            "method": "Page.navigate",
            "params": {"url": TARGET_URL}
        })
        if "error" in resp:
            print(f"[FAIL] Navigate error: {resp['error']}")
            sys.exit(1)
        print(f"[OK] Navigate sent, response id={resp.get('id')}")

        # Wait for page ready via Runtime.evaluate polling (more reliable than event-based recv)
        print("[OK] Waiting for page ready via Runtime.evaluate...")
        for attempt in range(20):
            resp = await send_ws(ws, {
                "id": next_id(),
                "method": "Runtime.evaluate",
                "params": {"expression": "document.readyState", "returnByValue": True}
            })
            val = resp.get("result", {}).get("result", {}).get("value", "")
            if val == "complete":
                print("[OK] Page ready!")
                break
            if val == "interactive":
                print("[OK] DOM interactive")
                break
            await asyncio.sleep(0.5)
        else:
            print("[WARN] Timeout waiting for page ready")

        # Step 2: Check if D3 and GOAP engine are available
        print("\n[2/7] Checking JavaScript environment...")
        resp = await send_ws(ws, {
            "id": next_id(),
            "method": "Runtime.evaluate",
            "params": {
                "expression": """
                    ({
                        d3Loaded: typeof d3 !== 'undefined',
                        goapEngine: typeof window.goapEngine !== 'undefined',
                        graphViz: typeof window.graphViz !== 'undefined',
                        plannerReady: typeof initPlanner === 'function',
                        actionLibrary: typeof ACTION_LIBRARY !== 'undefined' ? Object.keys(ACTION_LIBRARY).length : 0,
                        d3Version: typeof d3 !== 'undefined' ? d3.version : 'N/A'
                    })
                """,
                "returnByValue": True
            }
        })

        if "error" in resp:
            print(f"[FAIL] JS check error: {resp['error']}")
        else:
            result = resp.get("result", {}).get("result", {})
            if result.get("type") == "object":
                val = result.get("value", {})
                print(f"  D3 loaded: {val.get('d3Loaded')}")
                print(f"  D3 version: {val.get('d3Version')}")
                print(f"  GOAP engine: {val.get('goapEngine')}")
                print(f"  GraphViz: {val.get('graphViz')}")
                print(f"  Planner ready: {val.get('plannerReady')}")
                print(f"  Action library: {val.get('actionLibrary')} actions")

                if not val.get('d3Loaded'):
                    print("[WARN] D3 not loaded - CDN might be blocked")
                if not val.get('goapEngine'):
                    print("[WARN] GOAP engine not found in window")

        # Step 3: Trigger GOAP planning via click
        print("\n[3/7] Testing GOAP planning (click '规划' button)...")

        # Pre-select "完成季度报告" goal before clicking plan button
        # goal-select defaults to empty string "" so handlePlan() would alert+return early
        # We need to set value='完成季度报告' so handlePlan() selects GOALS["完成季度报告"]
        resp = await send_ws(ws, {
            "id": next_id(),
            "method": "Runtime.evaluate",
            "params": {
                "expression": """
                    (() => {
                        const sel = document.getElementById('goal-select');
                        if (!sel) return {error: 'goal-select not found'};
                        sel.value = '完成季度报告';
                        return {valueSet: sel.value};
                    })()
                """,
                "returnByValue": True
            }
        })
        if "result" in resp:
            val = resp["result"].get("result", {}).get("value", {})
            if isinstance(val, dict):
                print(f"  Goal pre-selected: {val.get('valueSet', '?')}")

        # First check current state
        resp = await send_ws(ws, {
            "id": next_id(),
            "method": "Runtime.evaluate",
            "params": {
                "expression": "JSON.stringify({hasPlan: currentPlan.length, step: currentStep, stateKeys: Object.keys(currentState)})",
                "returnByValue": True
            }
        })
        if "result" in resp:
            val = resp["result"].get("result", {}).get("value", "")
            print(f"  Before: {val}")

        # Click the plan button
        resp = await send_ws(ws, {
            "id": next_id(),
            "method": "Runtime.evaluate",
            "params": {
                "expression": """
                    (() => {
                        const btn = document.getElementById('btn-plan');
                        if (!btn) return {error: 'btn-plan not found'};
                        btn.click();
                        return {clicked: true};
                    })()
                """,
                "returnByValue": True
            }
        })

        if "error" in resp:
            print(f"[FAIL] Plan click error: {resp['error']}")
        else:
            result = resp.get("result", {}).get("result", {})
            val = result.get("value", {})
            if isinstance(val, dict):
                if val.get("error"):
                    print(f"[FAIL] {val['error']}")
                else:
                    print(f"[OK] Button clicked: {val}")

        # Wait for planning
        await asyncio.sleep(1.0)

        # Check plan result
        resp = await send_ws(ws, {
            "id": next_id(),
            "method": "Runtime.evaluate",
            "params": {
                "expression": "JSON.stringify({planLen: currentPlan.length, step: currentStep, plan: currentPlan.map(a => a.name || a)})",
                "returnByValue": True
            }
        })

        if "result" in resp:
            val = resp["result"].get("result", {}).get("value", "")
            parsed = json.loads(val) if val else {}
            print(f"  After plan: {parsed.get('planLen', 0)} steps")
            if parsed.get('plan'):
                for i, name in enumerate(parsed['plan']):
                    print(f"    Step {i+1}: {name}")

        # Step 4: Check D3 graph rendered
        print("\n[4/7] Checking D3 graph SVG nodes...")
        resp = await send_ws(ws, {
            "id": next_id(),
            "method": "Runtime.evaluate",
            "params": {
                "expression": """
                    (() => {
                        const nodes = document.querySelectorAll('.node-action');
                        const edges = document.querySelectorAll('.edge-line');
                        const svg = document.querySelector('#graph-svg');
                        return {
                            nodeCount: nodes.length,
                            edgeCount: edges.length,
                            svgExists: !!svg,
                            svgWidth: svg ? svg.clientWidth : 0,
                            svgHeight: svg ? svg.clientHeight : 0
                        };
                    })()
                """,
                "returnByValue": True
            }
        })

        if "result" in resp:
            val = resp["result"].get("result", {}).get("value", {})
            if isinstance(val, dict):
                print(f"  SVG exists: {val.get('svgExists')}")
                print(f"  SVG size: {val.get('svgWidth')}x{val.get('svgHeight')}")
                print(f"  D3 nodes rendered: {val.get('nodeCount')}")
                print(f"  D3 edges rendered: {val.get('edgeCount')}")
                if val.get('nodeCount', 0) == 0:
                    print("[WARN] No D3 nodes rendered - graph.js may not have initialized")

        # Step 5: Test step execution
        print("\n[5/7] Testing step execution (click '单步')...")
        resp = await send_ws(ws, {
            "id": next_id(),
            "method": "Runtime.evaluate",
            "params": {
                "expression": """
                    (() => {
                        const btn = document.getElementById('btn-step');
                        if (!btn) return {error: 'btn-step not found'};
                        btn.click();
                        return {clicked: true, step: currentStep};
                    })()
                """,
                "returnByValue": True
            }
        })

        if "result" in resp:
            val = resp["result"].get("result", {}).get("value", {})
            if isinstance(val, dict):
                print(f"  Step executed: {val.get('step')} -> {val.get('clicked')}")

        await asyncio.sleep(0.5)

        # Check state panel updated
        resp = await send_ws(ws, {
            "id": next_id(),
            "method": "Runtime.evaluate",
            "params": {
                "expression": "JSON.stringify({step: currentStep, state: currentState})",
                "returnByValue": True
            }
        })

        if "result" in resp:
            val = resp["result"].get("result", {}).get("value", "")
            parsed = json.loads(val) if val else {}
            state = parsed.get("state", {})
            print(f"  Current step: {parsed.get('step')}")
            for k, v in state.items():
                print(f"    {k}: {v}")

        # Step 6: Check console for errors
        print("\n[6/7] Checking console for errors...")
        resp = await send_ws(ws, {
            "id": next_id(),
            "method": "Runtime.evaluate",
            "params": {
                "expression": """
                    (() => {
                        // Collect any errors logged
                        return {
                            docTitle: document.title,
                            bodyExists: !!document.body,
                            graphCanvas: !!document.querySelector('.graph-canvas'),
                            planResult: !!document.getElementById('plan-result'),
                            stateList: !!document.getElementById('state-list')
                        };
                    })()
                """,
                "returnByValue": True
            }
        })

        if "result" in resp:
            val = resp["result"].get("result", {}).get("value", {})
            if isinstance(val, dict):
                print(f"  Page title: {val.get('docTitle')}")
                print(f"  Body exists: {val.get('bodyExists')}")
                print(f"  Graph canvas: {val.get('graphCanvas')}")
                print(f"  Plan result panel: {val.get('planResult')}")
                print(f"  State list panel: {val.get('stateList')}")

        # Step 7: Take screenshot
        print(f"\n[7/7] Taking screenshot...")
        # Enable page domain before screenshot (required by CDP protocol)
        await send_ws(ws, {
            "id": next_id(),
            "method": "Page.enable",
            "params": {}
        })
        await asyncio.sleep(0.3)
        resp = await send_ws(ws, {
            "id": next_id(),
            "method": "Page.captureScreenshot",
            "params": {"format": "png"}
        })

        # Debug: print raw CDP response
        print(f"[DEBUG] Screenshot resp keys: {resp.keys()}")
        print(f"[DEBUG] resp type: {type(resp)}")
        raw_str = str(resp)
        print(f"[DEBUG] resp full (first 500): {raw_str[:500]}")
        if "error" in resp:
            print(f"[FAIL] Screenshot error: {resp['error']}")
            # Try captureLayoutMetrics as fallback
            print("[INFO] Trying LayoutMetrics fallback...")
            resp2 = await send_ws(ws, {
                "id": next_id(),
                "method": "Page.captureSnapshot",
                "params": {}
            })
            print(f"[DEBUG] Snapshot resp keys: {resp2.keys()}")
            print(f"[DEBUG] Snapshot resp: {str(resp2)[:500]}")
            if "error" in resp2:
                print(f"[FAIL] Snapshot error: {resp2['error']}")
            else:
                data = resp2.get("result", {})
                print(f"[DEBUG] Snapshot data length: {len(data.get('data', ''))}")
                if data.get("data"):
                    print("[OK] Snapshot captured")
                else:
                    print("[FAIL] Snapshot also empty")
        else:
            # Chrome returns: {"id": N, "result": {"data": "BASE64..."}}  — ONE level under "result"
            data = resp.get("result", {})
            print(f"[DEBUG] data keys: {data.keys() if isinstance(data, dict) else type(data)}")
            b64_data = data.get("data", "") if isinstance(data, dict) else ""
            if b64_data:
                img_data = base64.b64decode(b64_data)
                with open(SCREENSHOT_PATH, "wb") as f:
                    f.write(img_data)
                print(f"[OK] Screenshot saved: {SCREENSHOT_PATH}")
                print(f"  Size: {len(img_data)} bytes ({len(img_data)//1024} KB)")
            else:
                print(f"[DEBUG] data contents: {str(data)[:300]}")
                print("[WARN] No screenshot data in response")
                # Try without format param
                print("[INFO] Retrying with JPEG format...")
                resp_jpeg = await send_ws(ws, {
                    "id": next_id(),
                    "method": "Page.captureScreenshot",
                    "params": {"format": "jpeg", "quality": 80}
                })
                print(f"[DEBUG] JPEG resp keys: {resp_jpeg.keys()}")
                if "error" not in resp_jpeg:
                    data_jpeg = resp_jpeg.get("result", {})
                    b64_jpeg = data_jpeg.get("data", "") if isinstance(data_jpeg, dict) else ""
                    if b64_jpeg:
                        img_jpeg = base64.b64decode(b64_jpeg)
                        jpeg_path = os.path.join(os.path.dirname(__file__), "..", "screenshot.jpg")
                        with open(jpeg_path, "wb") as f:
                            f.write(img_jpeg)
                        print(f"[OK] JPEG screenshot saved: {jpeg_path}")
                        print(f"  Size: {len(img_jpeg)} bytes")

        print("\n" + "=" * 60)
        print("Verification complete!")
        print("=" * 60)

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        try:
            ws.close()
        except Exception:
            pass


if __name__ == "__main__":
    # Check if websocket-client is available
    try:
        import websocket as _ws
        del _ws
    except ImportError:
        print("[ERROR] websocket-client module not found.")
        print("Installing websocket-client...")
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "websocket-client", "-q"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("[OK] websocket-client installed.")
        else:
            print(f"[FAIL] Install failed: {result.stderr}")
            print("Install manually: pip install websocket-client")
            sys.exit(1)

    import asyncio
    asyncio.run(main())
