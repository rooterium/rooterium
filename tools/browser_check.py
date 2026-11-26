"""Visual and console check of a local page in headless Chrome.

Opens a URL with device emulation (real phone widths, which plain
`--headless --window-size` cannot do below 500 px), prints console
messages, exceptions and CSP violations, optionally runs a JavaScript
expression (e.g. clicks) and saves a screenshot. YouTube requests are
blocked so tests never contact it. Software WebGL (SwiftShader) is enabled
so the MapLibre map renders.

Not part of the app; development helper only. Run on the host:

    uv run --no-project --with websockets python tools/browser_check.py \\
        http://localhost:8000/ /tmp/home.png --width 390 --height 900 \\
        --eval 'document.documentElement.scrollWidth'

Options: --cookie sessionid=… (to view as a logged-in user),
--wait SECONDS (time to collect messages before --eval/screenshot),
--reduced-motion (emulate prefers-reduced-motion: reduce).
"""

import argparse
import asyncio
import base64
import json
import subprocess
import tempfile
import time
import urllib.request

import websockets

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT = 9333
BLOCKED = ["*youtube*", "*ytimg*", "*googlevideo*"]


def start_chrome():
    profile = tempfile.mkdtemp()
    return subprocess.Popen(
        [
            CHROME,
            "--headless=new",
            "--use-angle=swiftshader",
            "--enable-unsafe-swiftshader",
            f"--remote-debugging-port={PORT}",
            f"--user-data-dir={profile}",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def page_websocket_url():
    for _ in range(100):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json") as response:
                targets = json.load(response)
            return next(t for t in targets if t["type"] == "page")[
                "webSocketDebuggerUrl"
            ]
        except OSError, StopIteration:
            time.sleep(0.1)
    raise SystemExit("Chrome did not start (is another check still running?)")


def report(msg):
    method = msg.get("method")
    if method == "Log.entryAdded":
        entry = msg["params"]["entry"]
        if "GPU stall" not in entry["text"]:
            print(f"LOG {entry['level']} {entry['source']}: {entry['text'][:300]}")
    elif method == "Runtime.consoleAPICalled":
        args = " ".join(
            str(a.get("value", a.get("description", ""))) for a in msg["params"]["args"]
        )
        print(f"CONSOLE {msg['params']['type']}: {args[:300]}")
    elif method == "Runtime.exceptionThrown":
        details = msg["params"]["exceptionDetails"]
        description = (details.get("exception") or {}).get("description", "")
        print("EXCEPTION", details.get("text"), description[:600])


async def check(args):
    chrome = start_chrome()
    try:
        async with websockets.connect(page_websocket_url(), max_size=50_000_000) as ws:
            counter = 0

            async def call(method, **params):
                nonlocal counter
                counter += 1
                await ws.send(
                    json.dumps({"id": counter, "method": method, "params": params})
                )
                while True:
                    msg = json.loads(await ws.recv())
                    if msg.get("id") == counter:
                        return msg.get("result", {})
                    report(msg)

            await call(
                "Emulation.setDeviceMetricsOverride",
                width=args.width,
                height=args.height,
                deviceScaleFactor=1,
                mobile=args.width < 600,
            )
            if args.reduced_motion:
                await call(
                    "Emulation.setEmulatedMedia",
                    features=[{"name": "prefers-reduced-motion", "value": "reduce"}],
                )
            await call("Network.enable")
            await call("Network.setBlockedURLs", urls=BLOCKED)
            await call("Page.enable")
            await call("Log.enable")
            await call("Runtime.enable")
            if args.cookie:
                name, value = args.cookie.split("=", 1)
                await call(
                    "Network.setCookie",
                    name=name,
                    value=value,
                    domain="localhost",
                    path="/",
                )
            await call("Page.navigate", url=args.url)
            end = time.time() + args.wait
            while time.time() < end:
                try:
                    report(json.loads(await asyncio.wait_for(ws.recv(), 0.5)))
                except TimeoutError:
                    continue
            if args.eval:
                result = await call(
                    "Runtime.evaluate",
                    expression=args.eval,
                    awaitPromise=True,
                    returnByValue=True,
                )
                print("EVAL", json.dumps(result.get("result", {}).get("value")))
                await asyncio.sleep(1.5)
            shot = await call("Page.captureScreenshot", format="png")
            with open(args.out, "wb") as file:
                file.write(base64.b64decode(shot["data"]))
            print("saved", args.out)
    finally:
        chrome.terminate()
        chrome.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("url")
    parser.add_argument("out", help="PNG file to write")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=900)
    parser.add_argument("--cookie", help="e.g. sessionid=…")
    parser.add_argument("--eval", help="JavaScript expression, may return a promise")
    parser.add_argument("--wait", type=float, default=3.0)
    parser.add_argument(
        "--reduced-motion",
        action="store_true",
        help="emulate prefers-reduced-motion: reduce",
    )
    asyncio.run(check(parser.parse_args()))


if __name__ == "__main__":
    main()
