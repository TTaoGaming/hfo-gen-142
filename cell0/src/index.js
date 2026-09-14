import { DurableObject } from "cloudflare:workers";

const TARGET_URL = "https://api.github.com/repos/TTaoGaming/hfo-gen-142/issues/6";

export default {
  async fetch(request, env) {
    return env.CELL.getByName("cell0").fetch(request);
  },
};

export class Cell0 extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.ctx = ctx;
    this.env = env;
  }

  async load() {
    return (await this.ctx.storage.get("state")) || {
      status: "NEW",
      cycles: 0,
      failures: 0,
      targetCycles: 0,
      intervalMs: 5000,
      lastError: null,
      lastObserved: null,
      lastDigest: null,
      lastRunAt: null,
      startedAt: null,
      completedAt: null,
      failNext: false,
    };
  }

  async save(state) {
    await this.ctx.storage.put("state", state);
  }

  async runCycle(source) {
    const state = await this.load();
    if (state.status !== "RUNNING") return state;
    if (state.cycles >= state.targetCycles) return state;

    if (state.failNext) {
      state.failNext = false;
      state.failures += 1;
      state.lastError = "INJECTED_FAILURE";
      state.lastRunAt = new Date().toISOString();
      await this.save(state);
      throw new Error("INJECTED_FAILURE");
    }

    const workId = `cell0:${state.cycles + 1}`;
    const response = await fetch(TARGET_URL, {
      headers: {
        "accept": "application/vnd.github+json",
        "user-agent": "hfo-gen142-cell0/1.0",
      },
    });
    if (!response.ok) throw new Error(`github_http_${response.status}`);
    const issue = await response.json();

    const observed = {
      issue: issue.number,
      title: issue.title,
      updated_at: issue.updated_at,
      comments: issue.comments,
      state: issue.state,
    };
    const bytes = new TextEncoder().encode(JSON.stringify(observed));
    const digestBytes = new Uint8Array(await crypto.subtle.digest("SHA-256", bytes));
    const digest = Array.from(digestBytes, b => b.toString(16).padStart(2, "0")).join("");

    state.cycles += 1;
    state.lastWorkId = workId;
    state.lastSource = source;
    state.lastObserved = observed;
    state.lastDigest = digest;
    state.lastRunAt = new Date().toISOString();
    state.lastError = null;
    if (state.cycles >= state.targetCycles) {
      state.status = "SUCCEEDED";
      state.completedAt = state.lastRunAt;
    }
    await this.save(state);
    return state;
  }

  async scheduleNext(state, delayMs = state.intervalMs) {
    if (state.status === "RUNNING") {
      await this.ctx.storage.setAlarm(Date.now() + delayMs);
    }
  }

  async alarm(alarmInfo) {
    let state = await this.load();
    try {
      state = await this.runCycle(alarmInfo?.isRetry ? "alarm-retry" : "alarm");
    } catch (err) {
      state = await this.load();
      if (state.lastError !== "INJECTED_FAILURE") {
        state.failures += 1;
        state.lastError = String(err?.message || err);
        state.lastRunAt = new Date().toISOString();
        await this.save(state);
      }
    }

    state = await this.load();
    if (state.status === "RUNNING") {
      await this.scheduleNext(state, state.lastError ? 2000 : state.intervalMs);
    }
  }

  json(body, status = 200) {
    return Response.json(body, { status });
  }

  async fetch(request) {
    const url = new URL(request.url);
    if (url.pathname === "/status") {
      const state = await this.load();
      const alarm = await this.ctx.storage.getAlarm();
      return this.json({ ...state, alarmAt: alarm ? new Date(alarm).toISOString() : null });
    }

    if (url.pathname === "/start") {
      const targetCycles = Math.max(1, Math.min(100, Number(url.searchParams.get("cycles") || 10)));
      const intervalMs = Math.max(2000, Math.min(60000, Number(url.searchParams.get("interval_ms") || 5000)));
      await this.ctx.storage.deleteAll();
      const state = await this.load();
      state.status = "RUNNING";
      state.targetCycles = targetCycles;
      state.intervalMs = intervalMs;
      state.startedAt = new Date().toISOString();
      await this.save(state);
      await this.ctx.storage.setAlarm(Date.now() + 500);
      return this.json({ started: true, ...state });
    }

    if (url.pathname === "/fault-next") {
      const state = await this.load();
      state.failNext = true;
      await this.save(state);
      return this.json({ faultArmed: true, state });
    }

    if (url.pathname === "/tick") {
      let state;
      try {
        state = await this.runCycle("manual");
      } catch (err) {
        state = await this.load();
      }
      await this.scheduleNext(state);
      return this.json(state);
    }

    if (url.pathname === "/stop") {
      const state = await this.load();
      state.status = "STOPPED";
      await this.save(state);
      await this.ctx.storage.deleteAlarm();
      return this.json(state);
    }

    return this.json({
      name: "hfo-gen142-cell0",
      purpose: "bounded durable self-waking GitHub observer",
      endpoints: ["/start", "/status", "/fault-next", "/tick", "/stop"],
    });
  }
}
