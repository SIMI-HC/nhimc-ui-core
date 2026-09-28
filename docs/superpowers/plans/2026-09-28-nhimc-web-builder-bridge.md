# NHIMC Web Builder Bridge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Provide ChatGPT Web and other MCP-capable hosts one callable operation that turns NHIMC v3 authoring HTML into the exact browser-verified, downloadable `index.html` without exposing repository paths or source-only files.

**Architecture:** A small Node.js Streamable HTTP MCP server invokes the Core v3 local delivery CLI inside an isolated temporary job, accepts only inline authoring HTML, and publishes verified bytes through a short-lived opaque download URL. The service is stateless at the MCP layer, keeps artifacts in a bounded in-memory-indexed temporary store, returns no link on failure, and stays operationally `WEB_BOOTSTRAP` until a deployed HTTPS endpoint passes a real ChatGPT download test.

**Tech Stack:** Node.js 22+, `@modelcontextprotocol/sdk@1.30.1`, `zod@4.6.5`, Python 3.11+, Chromium, Docker, Node built-in test runner, Streamable HTTP MCP, HTML.

**Spec:** `docs/superpowers/specs/2026-09-28-nhimc-canonical-template-delivery-design.md`

## Global Constraints

- This plan depends on the completed Core plan `docs/superpowers/plans/2026-09-28-nhimc-canonical-template-composition.md` and its version `3.0.0` APIs.
- MCP endpoint is exactly `/mcp`; artifact downloads are `GET /artifacts/<64-lowercase-hex-token>/index.html`; health check is `GET /healthz`.
- The only public tool is `build_nhimc_artifact` with inline `authoring_html` and optional `requested_filename` fixed to `index.html`.
- Input limit is 1,048,576 UTF-8 bytes, verified artifact limit is 10,485,760 bytes, build timeout is 120 seconds, maximum concurrent builds is 2, and artifact TTL is 600 seconds.
- The Bridge accepts no URL, path, shell argument, external asset, archive, or sidecar from a caller and performs no fetch on behalf of authoring content.
- Every job uses a new mode-`0700` temporary directory and is deleted after failure, expiry, shutdown, or successful store eviction.
- Logs contain request ID, outcome, duration, artifact byte count, and digest prefix only; they never contain business HTML, Korean business text, patient data, menu data, full SHA-256, artifact token, or download URL.
- A successful tool result returns structured status/digest metadata and one MCP `resource_link` with media type `text/html` and name `index.html`; a failed result returns no resource or download URL.
- Download responses use `Content-Type: text/html; charset=utf-8`, `Content-Disposition: attachment; filename="index.html"`, `Cache-Control: no-store, private, max-age=0`, `Pragma: no-cache`, and `X-Content-Type-Options: nosniff`.
- The generated file remains fully offline after download; the Bridge URL is not embedded in it.
- A repository, plugin manifest, or reachable health check does not make ChatGPT Web `READY`; the deployed MCP tool must be callable and its returned exact file must pass an end-to-end download test.

## Review Focus

- Two builds may finish concurrently while the store is at capacity; admission, artifact registration, expiry, and cleanup must never cross-link one user's bytes or token to another job.
- A client may disconnect during Python/Chrome execution or artifact streaming; the child process and temporary directory must be terminated/cleaned without leaving a reusable partial artifact.
- `NHIMC_PUBLIC_BASE_URL` may contain a path prefix or trailing slash; generated URLs must preserve the deployment prefix and contain exactly one `/artifacts/` separator.
- A caller may send valid JSON with a UTF-8 string whose byte length exceeds its character count; the 1 MiB limit must use `Buffer.byteLength`, not JavaScript string length.
- A valid receipt may refer to a file larger than the service limit or a symlink swapped after verification; the Bridge must reject non-regular files and recheck size/digest immediately before store registration and streaming.

---

## File Structure

- `bridge/src/config.mjs`: parses and validates all environment-controlled service limits and executable paths.
- `bridge/src/build-runner.mjs`: writes caller input to a private job, invokes the Core delivery CLI without a shell, and validates its one-line JSON result.
- `bridge/src/artifact-store.mjs`: owns opaque token creation, TTL/capacity enforcement, exact-byte lookup, and cleanup.
- `bridge/src/tool-contract.mjs`: defines Zod input/output schemas, annotations, public error mapping, and successful MCP content.
- `bridge/src/server.mjs`: creates the MCP server and Node HTTP routes for `/mcp`, `/healthz`, and artifact downloads.
- `bridge/src/index.mjs`: process entry point, signal handling, and structured metadata-only logging.
- `bridge/test/`: unit and integration tests with fake builders plus one real Core/Chromium end-to-end test.
- `bridge/Dockerfile`: reproducible Node/Python/Chromium runtime containing only publishable Core files.
- `bridge/compose.yaml`: local operational smoke environment.
- `bridge/README.md`: Korean deployment, health, MCP Inspector, and ChatGPT developer-mode runbook.
- `mcp.json`: portable plugin MCP declaration written only after a real stable HTTPS endpoint exists.
- `scripts/configure_remote_mcp.py`: validates a deployed HTTPS `/mcp` URL and deterministically writes `mcp.json`.

### Task 1: Create the bounded Bridge package and configuration contract

**Files:**
- Create: `bridge/package.json`
- Create: `bridge/package-lock.json`
- Create: `bridge/src/config.mjs`
- Create: `bridge/test/config.test.mjs`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: environment variables and the repository root.
- Produces: `loadConfig(env: NodeJS.ProcessEnv, bridgeRoot: URL) -> BridgeConfig`, where `BridgeConfig` contains `port`, `publicBaseUrl`, `pythonExecutable`, `coreRoot`, `browserPath`, `inputBytes`, `artifactBytes`, `timeoutMs`, `maxConcurrent`, `ttlMs`, and `maxArtifacts`.

- [ ] **Step 1: Write failing configuration tests**

```javascript
test('loads the fixed safe defaults', () => {
  const config = loadConfig({ NHIMC_PUBLIC_BASE_URL: 'https://builder.example.com' }, import.meta.url);
  assert.equal(config.port, 8787);
  assert.equal(config.inputBytes, 1_048_576);
  assert.equal(config.artifactBytes, 10_485_760);
  assert.equal(config.timeoutMs, 120_000);
  assert.equal(config.maxConcurrent, 2);
  assert.equal(config.ttlMs, 600_000);
});

test('rejects a non-https public URL outside local development', () => {
  assert.throws(
    () => loadConfig({ NODE_ENV: 'production', NHIMC_PUBLIC_BASE_URL: 'http://builder.example.com' }, import.meta.url),
    /NHIMC_PUBLIC_BASE_URL must use https/
  );
});
```

Add tests for missing production base URL, trailing slash normalization, path-prefix preservation, integer bounds, missing Core CLI, and an invalid explicit browser path.

- [ ] **Step 2: Create the package with exact dependency versions**

```json
{
  "name": "@nhimc/ui-core-builder-bridge",
  "version": "3.0.0",
  "private": true,
  "type": "module",
  "engines": {"node": ">=22.0.0"},
  "scripts": {
    "start": "node src/index.mjs",
    "test": "node --test test/*.test.mjs"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "1.30.1",
    "zod": "4.6.5"
  }
}
```

Run: `cd bridge; npm install --package-lock-only; npm test`

Expected: tests FAIL because `src/config.mjs` is absent; `package-lock.json` pins the full dependency graph.

- [ ] **Step 3: Implement strict configuration parsing**

```javascript
export function loadConfig(env, bridgeRoot) {
  const production = env.NODE_ENV === 'production';
  const publicBaseUrl = normalizeBaseUrl(env.NHIMC_PUBLIC_BASE_URL ?? 'http://127.0.0.1:8787', production);
  return Object.freeze({
    port: boundedInt(env.PORT, 8787, 1, 65535, 'PORT'),
    publicBaseUrl,
    pythonExecutable: env.NHIMC_PYTHON ?? (process.platform === 'win32' ? 'python' : 'python3'),
    coreRoot: resolveCoreRoot(env.NHIMC_CORE_ROOT, bridgeRoot),
    browserPath: resolveOptionalRegularFile(env.NHIMC_BROWSER_PATH, 'NHIMC_BROWSER_PATH'),
    inputBytes: 1_048_576,
    artifactBytes: 10_485_760,
    timeoutMs: 120_000,
    maxConcurrent: 2,
    ttlMs: 600_000,
    maxArtifacts: 32,
  });
}
```

Only `PORT`, `NHIMC_PUBLIC_BASE_URL`, `NHIMC_PYTHON`, `NHIMC_CORE_ROOT`, and `NHIMC_BROWSER_PATH` are configurable; security limits remain code constants for this release.

- [ ] **Step 4: Run configuration tests**

Run: `cd bridge; npm test`

Expected: all configuration tests PASS.

- [ ] **Step 5: Ignore only generated local Bridge state**

Add `/bridge/node_modules/`, `/bridge/.tmp/`, and `/bridge/coverage/` to `.gitignore`; do not ignore `package-lock.json`, tests, deployment files, or manifests.

- [ ] **Step 6: Commit the bounded package**

```bash
git add bridge/package.json bridge/package-lock.json bridge/src/config.mjs bridge/test/config.test.mjs .gitignore
git commit -m "feat: scaffold bounded builder bridge"
```

### Task 2: Run the Core verifier in isolated jobs without shell interpolation

**Files:**
- Create: `bridge/src/build-runner.mjs`
- Create: `bridge/test/build-runner.test.mjs`
- Create: `bridge/test/fixtures/fake-builder.mjs`

**Interfaces:**
- Consumes: `BridgeConfig` and Core CLI `scripts/build_verified_artifact.py --input PATH --output PATH`.
- Produces: `BuildRunner`, `BuildResult`, and `runner.build(authoringHtml: string, signal?: AbortSignal) -> Promise<BuildResult>`.

- [ ] **Step 1: Write failing isolated-runner tests**

```javascript
test('passes paths as argv and returns exact verified metadata', async () => {
  const runner = new BuildRunner(fakeConfig({ pythonExecutable: process.execPath, builderScript: FAKE_BUILDER }));
  const result = await runner.build(validAuthoring);
  assert.equal(result.filename, 'index.html');
  assert.equal(result.mimeType, 'text/html');
  assert.match(result.sha256, /^[0-9a-f]{64}$/);
  assert.equal(await readFile(result.path, 'utf8'), '<!doctype html><title>verified</title>');
});

test('measures UTF-8 bytes rather than JavaScript characters', async () => {
  const runner = new BuildRunner(fakeConfig({ inputBytes: 5 }));
  await assert.rejects(runner.build('한글'), /authoring_html exceeds 1048576 bytes|input limit/);
});
```

Add tests for no shell use, `requested_filename` irrelevance, timeout termination, abort termination, nonzero exit, malformed/multiline stdout, output size cap, missing file, symlink output, digest mismatch, concurrency limit, and stderr redaction.

- [ ] **Step 2: Run runner tests before implementation**

Run: `cd bridge; node --test test/build-runner.test.mjs`

Expected: FAIL because `BuildRunner` does not exist.

- [ ] **Step 3: Define the exact runner result**

```javascript
/** @typedef {{jobDir:string,path:string,filename:'index.html',mimeType:'text/html',sha256:string,bytes:number,manifest:object}} BuildResult */

export class BuildRunner {
  constructor(config, dependencies = {}) {}
  async build(authoringHtml, signal) {}
  async dispose(result) {}
}
```

- [ ] **Step 4: Implement private job creation and child execution**

Create jobs with `mkdtemp(join(tmpdir(), 'nhimc-build-'))`, immediately `chmod(jobDir, 0o700)`, write `source.html` with mode `0o600`, and spawn an argv array with `shell: false`, hidden windows on Windows, piped stdout/stderr, and `NHIMC_BROWSER_PATH` only when configured. Enforce the two-job semaphore before creating the directory.

- [ ] **Step 5: Validate the Core CLI response and bytes**

Require exactly one nonempty stdout line containing JSON fields `status: "PASS"`, `filename: "index.html"`, `mimeType: "text/html"`, lowercase SHA-256, and positive bytes. Open the output with `lstat`/`open` using regular-file checks, enforce 10 MiB, recompute SHA-256 from the file descriptor, parse its completion manifest, and reject any mismatch before returning `BuildResult`.

- [ ] **Step 6: Implement timeout, abort, and cleanup**

On timeout or caller abort, terminate the child process tree (`taskkill /T /F /PID` on Windows; process group `SIGTERM` then `SIGKILL` on Linux), wait for close, remove only the explicit job directory with recursive `rm`, and release the semaphore in `finally`. Convert child stderr to a fixed public code; never include it in a tool response or normal log.

- [ ] **Step 7: Run all runner tests**

Run: `cd bridge; node --test test/build-runner.test.mjs`

Expected: PASS, including concurrency, Unicode-byte limit, timeout, abort, symlink, and tamper cases.

- [ ] **Step 8: Commit the isolated runner**

```bash
git add bridge/src/build-runner.mjs bridge/test/build-runner.test.mjs bridge/test/fixtures/fake-builder.mjs
git commit -m "feat: isolate verified artifact builds"
```

### Task 3: Store exact artifacts behind opaque expiring URLs

**Files:**
- Create: `bridge/src/artifact-store.mjs`
- Create: `bridge/test/artifact-store.test.mjs`

**Interfaces:**
- Consumes: `BuildResult` and `BuildRunner.dispose()`.
- Produces: `ArtifactStore.register(result: BuildResult) -> ArtifactRecord`, `get(token: string) -> ArtifactRecord | null`, `openVerified(token: string) -> Promise<{record, handle}>`, `remove(token: string) -> Promise<void>`, and `close() -> Promise<void>`.

- [ ] **Step 1: Write failing opacity, expiry, race, and tamper tests**

```javascript
test('registers a non-enumerable 256-bit token', async () => {
  const record = await store.register(buildResult);
  assert.match(record.token, /^[0-9a-f]{64}$/);
  assert.equal(store.get('0'.repeat(64)), null);
  assert.equal(Object.prototype.hasOwnProperty.call(store, 'records'), false);
});

test('rechecks bytes immediately before streaming', async () => {
  const record = await store.register(buildResult);
  await appendFile(buildResult.path, '<!-- tampered -->');
  await assert.rejects(store.openVerified(record.token), /artifact changed after verification/);
  assert.equal(store.get(record.token), null);
});
```

Add fake-clock tests for exactly 600 seconds, invalid token shapes, capacity 32 oldest-expiry eviction, concurrent registrations at capacity, cleanup callbacks exactly once, symlink/file replacement, closed-store behavior, and shutdown cleanup.

- [ ] **Step 2: Run store tests before implementation**

Run: `cd bridge; node --test test/artifact-store.test.mjs`

Expected: FAIL because the store module is absent.

- [ ] **Step 3: Implement private state and immutable records**

```javascript
export class ArtifactStore {
  #records = new Map();
  #closed = false;
  constructor({ ttlMs, maxArtifacts, artifactBytes, now = Date.now, randomBytesFn = randomBytes, dispose }) {}
  async register(result) {}
  get(token) {}
  async openVerified(token) {}
  async remove(token) {}
  async close() {}
}
```

Generate `randomBytes(32).toString('hex')`, retry on collision, freeze public records, schedule one unreferenced expiry timer per record, and keep no method that lists records.

- [ ] **Step 4: Make stream-time validation race-resistant**

`openVerified()` validates token syntax, expiry, and record presence; opens the file; compares `fstat` regular-file status, device/inode where supported, byte count, and SHA-256 read through that handle; then returns the still-open handle. HTTP streaming must use that handle and close it in `finally` so a pathname swap cannot change delivered bytes.

- [ ] **Step 5: Run store tests**

Run: `cd bridge; node --test test/artifact-store.test.mjs`

Expected: PASS for opacity, TTL, capacity, concurrency, tampering, and cleanup.

- [ ] **Step 6: Commit the artifact store**

```bash
git add bridge/src/artifact-store.mjs bridge/test/artifact-store.test.mjs
git commit -m "feat: serve opaque expiring artifacts"
```

### Task 4: Expose the narrow Streamable HTTP MCP tool and download route

**Files:**
- Create: `bridge/src/tool-contract.mjs`
- Create: `bridge/src/server.mjs`
- Create: `bridge/src/index.mjs`
- Create: `bridge/test/tool-contract.test.mjs`
- Create: `bridge/test/server.test.mjs`

**Interfaces:**
- Consumes: `BridgeConfig`, `BuildRunner`, and `ArtifactStore`.
- Produces: `createNhimcMcpServer(dependencies) -> McpServer`, `createHttpServer(dependencies) -> http.Server`, and the public `build_nhimc_artifact` tool.

- [ ] **Step 1: Write failing tool-result tests**

```javascript
test('success returns metadata and exactly one html resource_link', async () => {
  const result = await invokeTool({ authoring_html: validAuthoring });
  assert.deepEqual(result.structuredContent, {
    status: 'PASS', filename: 'index.html', mimeType: 'text/html',
    sha256: DIGEST, bytes: 2427275, downloadUrl: EXPECTED_URL, expiresAt: EXPECTED_EXPIRY
  });
  const links = result.content.filter(item => item.type === 'resource_link');
  assert.deepEqual(links, [{ type: 'resource_link', uri: EXPECTED_URL, name: 'index.html', mimeType: 'text/html', description: '검증된 NHIMC 오프라인 단일 HTML' }]);
});

test('failure returns no resource or url', async () => {
  const result = await invokeTool({ authoring_html: '<nhimc-frame></nhimc-frame>' });
  assert.equal(result.isError, true);
  assert.equal(result.content.some(item => item.type === 'resource_link'), false);
  assert.equal(JSON.stringify(result).includes('/artifacts/'), false);
});
```

Add tests for absent/empty/oversize input, unknown fields, any filename other than `index.html`, output schema, annotations, and stable public error codes.

- [ ] **Step 2: Write failing HTTP route tests**

Test `GET /healthz`, CORS `OPTIONS /mcp`, MCP `POST/GET/DELETE`, unknown routes, malformed tokens, missing/expired artifacts, download headers, exact bytes, `HEAD` rejection, no directory listing, URL path-prefix preservation, disconnect cleanup, and absence of authoring content in captured logs.

Run: `cd bridge; node --test test/tool-contract.test.mjs test/server.test.mjs`

Expected: FAIL because the MCP and HTTP modules are absent.

- [ ] **Step 3: Define exact Zod schemas and tool annotations**

```javascript
export const inputSchema = {
  authoring_html: z.string().min(1).describe('NHIMC v3 authoring HTML; not a URL or file path'),
  requested_filename: z.literal('index.html').default('index.html')
};

export const outputSchema = {
  status: z.literal('PASS'),
  filename: z.literal('index.html'),
  mimeType: z.literal('text/html'),
  sha256: z.string().regex(/^[0-9a-f]{64}$/),
  bytes: z.number().int().positive().max(10_485_760),
  downloadUrl: z.string().url(),
  expiresAt: z.string().datetime()
};
```

Register annotations `{ readOnlyHint: false, destructiveHint: false, idempotentHint: true, openWorldHint: false }`. Tool description must say it builds and Chrome-verifies one offline NHIMC HTML and returns the exact file; it must not suggest URL fetching.

- [ ] **Step 4: Implement the stateless MCP handler**

For each `/mcp` request, create a fresh `McpServer` and `StreamableHTTPServerTransport({ sessionIdGenerator: undefined, enableJsonResponse: true })`, connect, call `transport.handleRequest(req, res)`, and close both on response close. Support the official `POST`, `GET`, `DELETE`, and CORS preflight behavior; return plain 404 for unsupported OAuth discovery routes while authentication is intentionally absent.

- [ ] **Step 5: Implement tool execution and safe public failures**

Measure `Buffer.byteLength(authoring_html, 'utf8')` before calling the runner. On success, register the result, join its token URL against the normalized public base URL, and return Korean text plus structured output and exactly one resource link. Map validation, capacity, timeout, verifier, and internal failures to stable codes `INVALID_AUTHORING`, `BUSY`, `BUILD_TIMEOUT`, `VERIFICATION_FAILED`, and `INTERNAL_ERROR`; never return child stderr or job paths.

- [ ] **Step 6: Implement exact download streaming**

Match only `/artifacts/(?<token>[0-9a-f]{64})/index.html`. Call `store.openVerified(token)`, set the mandated headers plus exact `Content-Length`, stream from the returned file handle, close the handle, and retain the artifact until expiry so ChatGPT can retry the same link. Any mismatch removes the record and returns 410 without bytes.

- [ ] **Step 7: Implement process startup and metadata-only logs**

Generate an independent request ID, log JSON fields `{event, requestId, status, durationMs, bytes, digestPrefix}` only, and use signal handlers that stop accepting requests, abort active builds, close the store, then exit. Health returns 200 only after config, Core CLI, and browser preflight succeed.

- [ ] **Step 8: Run all Bridge unit/integration tests**

Run: `cd bridge; npm test`

Expected: PASS with no leaked HTML, token, full digest, local path, or child stderr in captured logs.

- [ ] **Step 9: Commit the MCP server**

```bash
git add bridge/src/tool-contract.mjs bridge/src/server.mjs bridge/src/index.mjs bridge/test/tool-contract.test.mjs bridge/test/server.test.mjs
git commit -m "feat: expose verified html builder over mcp"
```

### Task 5: Package a reproducible Chromium service and run real end-to-end tests

**Files:**
- Create: `bridge/Dockerfile`
- Create: `bridge/.dockerignore`
- Create: `bridge/compose.yaml`
- Create: `bridge/test/real-build.test.mjs`
- Create: `bridge/test/real-mcp-e2e.test.mjs`
- Modify: `bridge/package.json`

**Interfaces:**
- Consumes: publishable Core v3 tree, Node lockfile, Python standard library, and Chromium.
- Produces: Linux container listening on port 8787, real tool invocation, and byte-identical HTTP download verified against returned metadata.

- [ ] **Step 1: Write a real local build test**

```javascript
test('real runner builds the canonical operations screen', { timeout: 180_000 }, async () => {
  const source = await readFile(resolve(CORE_ROOT, 'tests/fixtures/authoring/operations/index.html'), 'utf8');
  const result = await runner.build(source);
  try {
    assert.equal(result.filename, 'index.html');
    assert.ok(result.bytes > 1_000_000);
    assert.equal(result.sha256, await sha256File(result.path));
  } finally {
    await runner.dispose(result);
  }
});
```

- [ ] **Step 2: Write a real MCP-to-download test**

Start the server on an ephemeral loopback port, invoke `build_nhimc_artifact` through an MCP client transport, fetch the returned resource link, and assert status 200, attachment filename, text/html MIME, no-store headers, byte length, SHA-256, completion manifest, canonical Frame root, canonical Template root, and absence of `<nhimc-frame>`.

- [ ] **Step 3: Run the real tests on the workstation**

Run: `cd bridge; node --test test/real-build.test.mjs test/real-mcp-e2e.test.mjs`

Expected: PASS using the installed Chrome/Edge and Python, with the downloaded bytes exactly matching `structuredContent.sha256`.

- [ ] **Step 4: Create the locked runtime image**

Use a Debian-based `node:22-bookworm-slim` image pinned by digest at implementation time, install `python3` and `chromium` with no recommended packages, copy the repository publishable tree plus `bridge/package*.json`, run `npm ci --omit=dev`, set an unprivileged UID/GID, set `NHIMC_CORE_ROOT=/app/core`, `NHIMC_PYTHON=python3`, `NHIMC_BROWSER_PATH=/usr/bin/chromium`, and run `node bridge/src/index.mjs`. Do not copy `.git`, `.worktrees`, `.tmp`, unsafe fixtures, downloads, or local secrets.

- [ ] **Step 5: Add container health and resource restrictions**

`compose.yaml` binds `127.0.0.1:8787:8787`, uses a read-only root filesystem, `tmpfs: /tmp` with size 128 MiB and mode 1777, drops all Linux capabilities, sets `no-new-privileges`, limits memory to 1 GiB and PIDs to 256, and checks `http://127.0.0.1:8787/healthz`.

- [ ] **Step 6: Build and run the container smoke test**

Run: `docker build -f bridge/Dockerfile -t nhimc-ui-core-builder:3.0.0 .`

Run: `docker compose -f bridge/compose.yaml up -d --wait`

Run: `node --test bridge/test/real-mcp-e2e.test.mjs`

Run: `docker compose -f bridge/compose.yaml down`

Expected: image builds, health becomes ready, real MCP build/download passes inside Linux Chromium, and shutdown leaves no artifact volume.

- [ ] **Step 7: Commit the reproducible service**

```bash
git add bridge/Dockerfile bridge/.dockerignore bridge/compose.yaml bridge/test/real-build.test.mjs bridge/test/real-mcp-e2e.test.mjs bridge/package.json bridge/package-lock.json
git commit -m "test: certify builder bridge end to end"
```

### Task 6: Add portable plugin wiring without making a false readiness claim

**Files:**
- Create: `scripts/configure_remote_mcp.py`
- Create: `tests/python/test_remote_mcp_config.py`
- Modify: `plugin.json`
- Modify: `.codex-plugin/plugin.json`
- Modify: `skills/nhimc-ui/SKILL.md`
- Modify: `registry/project.json`
- Create after deployment: `mcp.json`

**Interfaces:**
- Consumes: a stable deployed HTTPS URL ending in `/mcp` that passes MCP initialization and tool discovery.
- Produces: `validate_remote_mcp_url(value: str) -> str`, deterministic portable `mcp.json`, plugin instructions that call `build_nhimc_artifact`, and a status that remains non-READY until Task 8.

- [ ] **Step 1: Write failing remote-MCP manifest tests**

```python
def test_writes_portable_streamable_http_manifest(self):
    output = self.folder / "mcp.json"
    write_mcp_manifest("https://builder.example.com/mcp", output)
    self.assertEqual(json.loads(output.read_text("utf-8")), {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
        "mcpServers": {"nhimc_builder": {"type": "streamable-http", "url": "https://builder.example.com/mcp"}},
    })

def test_rejects_local_or_non_mcp_url(self):
    for value in ("http://builder.example.com/mcp", "https://localhost/mcp", "https://builder.example.com/api"):
        with self.subTest(value=value), self.assertRaises(ValueError):
            validate_remote_mcp_url(value)
```

Also assert plugin version 3.0.0, portable root schema, no embedded credentials/query/fragment, and no `mcp.json` generated when remote probe fails.

- [ ] **Step 2: Run the manifest tests before implementation**

Run: `python -m unittest tests.python.test_remote_mcp_config -v`

Expected: FAIL because the configurator does not exist.

- [ ] **Step 3: Implement deterministic configuration with a live preflight**

The CLI accepts `--url` and `--output mcp.json`, requires public HTTPS with path exactly ending `/mcp`, rejects username/password/query/fragment and loopback/private/link-local IP literals, performs MCP initialize plus `tools/list`, requires exactly one public tool named `build_nhimc_artifact`, and writes the manifest atomically only after success.

- [ ] **Step 4: Update portable and compatibility plugin metadata**

Keep root `plugin.json` canonical and version 3.0.0. Add OpenAI interface copy that says the plugin produces a verified offline NHIMC `index.html`; keep `.codex-plugin/plugin.json` as a compatibility fallback. Do not hard-code a deployment URL in either plugin manifest; the portable URL lives only in generated `mcp.json`.

- [ ] **Step 5: Update Skill behavior for the tool boundary**

When `build_nhimc_artifact` is available, the Skill sends only valid v3 authoring HTML, checks `status == PASS`, and returns the resource link as the actual download. When the tool is absent or errors, it reports `WEB_BOOTSTRAP / context-only` and never attaches authoring source as `index.html`.

- [ ] **Step 6: Keep the readiness registry fail-closed**

Retain `verified-builder-bridge-connected-and-download-tested` as the sole ChatGPT Web `READY` capability, but record deployment state separately as `not-configured`, `configured-not-e2e-tested`, or `download-tested`. Repository tests must reject `READY` whenever `mcp.json` is absent or the end-to-end verification record from Task 8 is absent/mismatched.

- [ ] **Step 7: Run plugin and public-safety tests**

Run: `python -m unittest tests.python.test_remote_mcp_config tests.python.test_platform_adapters tests.python.test_release_build -v`

Run: `python scripts/validate_public.py`

Expected: PASS before deployment with ChatGPT Web still not READY and without a fabricated remote URL.

- [ ] **Step 8: Commit deployable plugin wiring**

```bash
git add scripts/configure_remote_mcp.py tests/python/test_remote_mcp_config.py plugin.json .codex-plugin/plugin.json skills/nhimc-ui/SKILL.md registry/project.json
git commit -m "feat: wire verified builder bridge plugin"
```

### Task 7: Document Korean operator and user workflows

**Files:**
- Create: `bridge/README.md`
- Modify: `README.md`
- Modify: `bootstrap.md`
- Modify: `CHANGELOG.md`
- Create: `docs/builder-bridge-operations.md`
- Modify: `tests/python/test_platform_adapters.py`

**Interfaces:**
- Consumes: local CLI, Bridge HTTP contract, deployment configuration command, and fail-closed readiness state.
- Produces: Korean instructions that distinguish local generation, remote MCP deployment, plugin connection, and actual downloadable-file verification.

- [ ] **Step 1: Write failing documentation contract tests**

```python
def test_bridge_docs_name_the_actual_chatgpt_connection_gate(self):
    text = (ROOT / "bridge/README.md").read_text("utf-8")
    for phrase in ("/mcp", "build_nhimc_artifact", "index.html", "ChatGPT 개발자 모드", "다운로드", "context-only"):
        self.assertIn(phrase, text)

def test_primary_usage_does_not_make_user_run_python(self):
    primary = extract_section((ROOT / "README.md").read_text("utf-8"), "사용법", "유지보수")
    self.assertNotIn("python scripts/build_single_html.py", primary)
```

- [ ] **Step 2: Run documentation tests before writing the runbooks**

Run: `python -m unittest tests.python.test_platform_adapters -v`

Expected: FAIL because the Bridge runbook and exact lifecycle copy are absent.

- [ ] **Step 3: Write the Korean user path**

Explain: locally, invoke `bootstrap.md` then request a screen and receive one verified `index.html`; in ChatGPT Web, install/connect the deployed plugin, request a screen, allow the `build_nhimc_artifact` call, and click the returned `index.html`. Explicitly state that the 5 KB `<nhimc-frame>` authoring source is not the final file.

- [ ] **Step 4: Write the Korean operator path**

Document environment variables, container build, local MCP Inspector test, deployment requirements, stable HTTPS `/mcp`, no-auth risk boundary, log fields, health behavior, TTL, capacity, cleanup, rollout, rollback, incident shutdown, manifest generation, and the exact ChatGPT developer-mode connection test.

- [ ] **Step 5: Add maintainer diagnostics without moving them into primary usage**

Place `build_single_html.py`, `build_verified_artifact.py`, direct browser verification, receipt inspection, Docker commands, and MCP Inspector commands under a clearly labeled maintainer section. Explain each command's purpose and what PASS output means.

- [ ] **Step 6: Run documentation, link, and public scans**

Run: `python -m unittest tests.python.test_platform_adapters -v`

Run: `python scripts/validate_public.py`

Run: `python scripts/validate_contracts.py`

Expected: PASS with no dead local-only links presented to web users and no secret/internal address in publishable content.

- [ ] **Step 7: Commit the runbooks**

```bash
git add bridge/README.md README.md bootstrap.md CHANGELOG.md docs/builder-bridge-operations.md tests/python/test_platform_adapters.py
git commit -m "docs: explain verified web download workflow"
```

### Task 8: Deploy, connect, and record the real ChatGPT Web download gate

**Files:**
- Create after successful deployment: `mcp.json`
- Create after successful end-to-end test: `registry/chatgpt-web-verification.json`
- Modify: `registry/project.json`
- Modify: `tests/python/test_platform_adapters.py`
- Modify: `PUBLIC_ASSET_REVIEW.md`

**Interfaces:**
- Consumes: an approved public container host with stable HTTPS, the deployed Bridge, ChatGPT developer mode, and the Core transport-management v3 authoring fixture.
- Produces: a live portable MCP manifest, a non-secret verification record bound to endpoint origin/tool/schema/artifact digest, and only then the ChatGPT Web `READY` status.

- [ ] **Step 1: Deploy the locked container without repository or patient secrets**

Deploy image `nhimc-ui-core-builder:3.0.0` to the selected host with one writable 128 MiB temporary filesystem, 1 GiB memory, 256 PID limit, two concurrent requests, no persistent artifact volume, and HTTPS termination. Configure `NHIMC_PUBLIC_BASE_URL` to the stable public origin/path and keep deployment credentials outside the repository.

- [ ] **Step 2: Verify public health and MCP discovery**

Set `$bridgeUrl` to the actual deployed URL ending `/mcp` and run:

```powershell
python scripts/configure_remote_mcp.py --url $bridgeUrl --output mcp.json
```

Expected: MCP initialize succeeds, `tools/list` exposes only `build_nhimc_artifact`, and a deterministic root `mcp.json` is written. If this fails, delete no existing known-good manifest and retain non-READY status.

- [ ] **Step 3: Invoke a real remote build outside ChatGPT**

Use MCP Inspector or the repository integration client to send the UTF-8 contents of `tests/fixtures/authoring/transport-management/index.html`. Download the returned link and verify response headers, filename `index.html`, exact byte count and SHA-256, completion manifest, `file://` Chrome PASS, and expiry after 600 seconds.

- [ ] **Step 4: Connect the deployed `/mcp` endpoint in ChatGPT developer mode**

Create/install the personal plugin from the exact deployed `/mcp` URL, open a fresh ChatGPT Work conversation, invoke the plugin directly, request the hospital transport-management screen, and confirm one `build_nhimc_artifact` call with inline v3 authoring HTML and `requested_filename: "index.html"`.

- [ ] **Step 5: Download and independently verify the ChatGPT-returned file**

Click the returned `index.html`, save it to an empty folder, confirm no sidecar files, compute SHA-256, compare it to the tool's structured result, open it offline through `file://`, and run the repository's exact standalone verifier against that downloaded path. Reject the readiness gate if ChatGPT shows source code, a non-clickable local path, an expired link before first access, different bytes, or any runtime/resource error.

- [ ] **Step 6: Write the non-secret verification record**

Create `registry/chatgpt-web-verification.json` with exact fields `schemaVersion`, `verifiedAt`, `endpointOrigin`, `mcpPath`, `serverName`, `serverVersion`, `toolName`, `toolSchemaSha256`, `artifactSha256`, `artifactBytes`, `coreVersion`, `upstreamCommit`, and `result: "PASS"`. Store only origin/path, never deployment tokens, artifact URL tokens, authoring HTML, business rows, full logs, or account identifiers.

- [ ] **Step 7: Make readiness mechanically depend on the verification record**

Update platform tests so `READY` requires: `mcp.json` URL origin/path matching the verification record, tool/schema digest matching the current server code, Core/upstream versions matching registries, `result == PASS`, and verification age no greater than 30 days. Then change ChatGPT Web state to `READY`; otherwise keep `WEB_BOOTSTRAP`.

- [ ] **Step 8: Run final local and remote release gates**

Run: `cd bridge; npm test`

Run: `python scripts/verify_all.py`

Run: `python scripts/verify_release.py`

Run the remote MCP/download probe documented in `docs/builder-bridge-operations.md`.

Expected: unit, real-browser, parity, public-safety, release, and remote download gates all PASS against the same Core version and pinned canonical commit.

- [ ] **Step 9: Record review and commit operational activation**

Update `PUBLIC_ASSET_REVIEW.md` with the verified Bridge version and confirm no unresolved `BLOCKING:` item.

```bash
git add mcp.json registry/chatgpt-web-verification.json registry/project.json tests/python/test_platform_adapters.py PUBLIC_ASSET_REVIEW.md
git commit -m "ops: verify chatgpt web artifact delivery"
```

- [ ] **Step 10: Publish only after independent review**

Run: `git status --short`

Run: `git diff origin/feature/nhimc-ui-core...HEAD --stat`

Expected: clean worktree and only planned Core/Bridge/plugin files. Request a whole-branch code and security review, address findings with tests, rerun Task 8 Step 8, then push the feature branch and open the Pull Request. Do not publish a `READY` claim if the deployed endpoint or verification record is absent, stale, or mismatched.
