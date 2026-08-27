---
license: UNKNOWN
name: browser-automation
description: "Load a web page in a headless browser and report what actually happened — console errors, failed network requests, page title, and optional DOM assertions or a screenshot. Use to verify your own web work instead of asking the user to look at the screen. Triggers on: check the page, does it render, verify the UI, QA the app, is it broken, console errors, did my change work."
allowed-tools: Bash(node *skills/browser-automation/browser.mjs:*)
triggers: ["browser automation", "browser-automation"]
---

# browser-automation

Closes the edit → run → **look at it** → fix loop that otherwise requires the
user to describe what is on their screen.

## Usage

```bash
node <this-skill-dir>/browser.mjs <url> [options]
```

`<this-skill-dir>` is the folder you just read this file from — `browser.mjs`
sits beside it. Use that path literally rather than guessing at a home
directory.

| option | meaning |
|---|---|
| `--snapshot`        | list every interactive element with a clickable ref (add `--full` for the whole accessibility tree) |
| `--wait <selector>` | block until the selector appears (default: DOM ready) |
| `--eval <js>`       | run an expression in the page, print the JSON result |
| `--script <file>`   | drive a sequence — see **Scripting** below |
| `--screenshot <p>`  | write a PNG (read it afterwards if you need to *see* it) |
| `--timeout <ms>`    | navigation timeout, default 30000 |

## Driving by ref, not by selector

`--snapshot` returns the page's interactive elements, each with a ref:

```
@e5 button "Audit my code"
@e9 button "Select your model" [haspopup=menu]
@e10 button "Manual" [haspopup=menu]
@e11 button "Send" [disabled]
```

Click `@e10` and you get what the page says is there — no selector to author
from a DOM you cannot see. This matters most for **icon-only buttons**, which
have no accessible name at all: `getByRole('button', {name: …})` cannot find
them, and they show up here as `@e1 button [haspopup=dialog]`.

A ref is stamped into the page, so it dies on navigation or a re-render.
**Re-snapshot after anything that changes the page** — the refs renumber, and a
stale one matches nothing.

`--full` returns the accessibility tree instead (headings, text, links). Use
refs to *act*, `--full` to *read*.

## Scripting a sequence

`--script` runs a file that default-exports `async (page, ui) => result`.

**`page` is a Playwright `Page`** (the driver is patchright, a Playwright fork),
so use the Playwright API — `page.locator`, `page.getByRole`, `page.getByText`,
`page.waitForFunction`, `page.evaluate`. It is NOT Puppeteer: `page.$` and
friends mostly work, but `getByRole` and `locator` do not exist there, so code
written against Puppeteer will fail in confusing ways.

**`ui` is the ref helper**, and is usually the shorter path:

| call | does |
|---|---|
| `await ui.snapshot()` | the ref listing above, as a string |
| `await ui.snapshot({full: true})` | the accessibility tree instead |
| `await ui.click('@e7')` | click that element |
| `await ui.fill('@e3', 'text')` | fill an input |
| `await ui.text('@e5')` | its inner text |
| `ui.ref('@e5')` | the raw locator, for anything else |

Whatever you return is printed as JSON. The runner owns the browser, the
console/network capture and the teardown; the script only drives and asserts.

```js
// qa.mjs  —  node <this-skill-dir>/browser.mjs http://localhost:3000 --script ./qa.mjs
export default async function run(page, ui) {
  // Look at what is there before deciding what to click.
  const before = await ui.snapshot()
  const signIn = before.match(/@(e\d+) button "Sign in"/)?.[1]
  if (!signIn) return { error: 'no sign-in button', snapshot: before }

  await ui.click(signIn)
  await page.waitForTimeout(500)

  // The page changed, so the old refs are gone — snapshot again.
  const after = await ui.snapshot()
  return { opened: after.includes('textbox'), after }
}
```

Navigation to the URL argument has already happened before your function runs.
You can navigate further with `page.goto(...)`.

## Read the text before the pixels

Console errors and failed requests catch most "it's broken" cases and cost
almost nothing. A screenshot is expensive in tokens and usually only needed for
layout questions. The report leads with the cheap signals on purpose.

## Interpreting the report

- `console.error` / uncaught exceptions → almost always a real bug.
- `requests failed` → a 404 on a JS chunk usually means a stale build is being
  served; a 500 means the server, not the page.
- `title` empty and `bodyChars` near zero → the app did not mount at all. Check
  the console section first, not the DOM.

## Examples

```bash
# Did my change render?
node <this-skill-dir>/browser.mjs http://localhost:3000

# Assert something specific about the DOM
node <this-skill-dir>/browser.mjs http://localhost:3000 \
  --eval "document.querySelectorAll('[data-testid=row]').length"

# Wait for a late-mounting element before judging the page
node <this-skill-dir>/browser.mjs http://localhost:3000 --wait "[data-testid=grid]"
```

## Gotchas found by using this

- **Keep the trailing slash** on a path-prefixed app. `http://host/app` and
  `http://host/app/` resolve relative asset URLs differently, and without it a
  page can return HTTP 200 with `bodyChars 0` and never mount. An app that 200s
  but renders nothing is usually this, not a crash.
- **A failing request is not automatically a bug.** Apps routinely probe for
  optional local services that are simply not running. Check whether the
  dependency is meant to exist before reporting it.
- **Never assert on text your own input put on the page.** A check for
  "console error" matches the prompt you just typed into the app as readily as
  the thing you were looking for, and the test passes while proving nothing.
  Match only strings that can come from the system under test.
- **Wait for content, not for a fixed delay.** A client-rendered app that is
  merely slow is indistinguishable from one that is broken unless you actually
  wait for something to appear.
- **Prefer a ref over a selector.** A selector that silently matches nothing and
  an element that is genuinely absent produce the same failure, and you cannot
  tell them apart without looking. `--snapshot` first, then act on what it
  listed. When a check still says something is missing, screenshot before
  reporting it.
- Third-party analytics failures are filtered out; they are noise, not signal.

## One run, one browser

Each invocation launches a browser, does the work, and closes it. Cookies,
logins and page state do **not** survive to the next invocation, so anything
needing several steps must happen inside a single `--script` run rather than
across several calls.

## Notes

- Resolves `patchright` from an installed CodeGPT extension, then a dev
  checkout, then a global copy — so it normally needs no install of its own. If
  none is found it says what it looked for.
- Headless. It never touches the user's real browser profile or cookies.
