import { Agent, getAgentByName, type FiberRecoveryContext } from "agents";
import { createQuickActionTools } from "agents/browser/ai";
import { createWorkersAI } from "workers-ai-provider";
import { generateText, stepCountIs } from "ai";

const ACTOR_ID = "SIGRUN-GEN142-SCOUT-R0";
const PARENT_ACTOR = "SIGRUN/C2";
const RADIX = [4, 4] as const;
const SEAT_ROLE = "THUNDER_DISRUPT";
const ROACH_UUID = "0771446a-3b95-45ea-baa4-5140c3e1510b";
const DEBATE_VERSION = "twinling-debate-v1";
const MODEL = "@cf/moonshotai/kimi-k2.7-code";
const ISSUE_API = "https://api.github.com/repos/TTaoGaming/hfo-gen-142/issues/13";
const LANES = ["CROWN", "DONOR", "BENCHMARK", "REDUCER"] as const;
type Lane = typeof LANES[number];
type Phase = "IDLE" | "COGNITION_RUNNING" | "READY" | "RECOVERY_REQUIRED" | "FAILED";

type ScoutState = {
  actorId: string;
  phase: Phase;
  epoch: number;
  recoveryCount: number;
  failureCount: number;
  sameFailureCount: number;
  lastLane?: Lane;
  lastAttemptLane?: Lane;
  lastRunId?: string;
  lastStartedUtc?: string;
  lastCompletedUtc?: string;
  lastResult?: string;
  lastResultSha256?: string;
  lastDebateSha256?: string;
  lastError?: string;
  lastFailureFingerprint?: string;
  updatedAt: string;
};

const ANCHOR_CLAIM = Object.freeze({
  schema: "hfo.hluti-anchor-claim.v1",
  parent_actor: PARENT_ACTOR,
  hluti: "SIGRUN-HLUTI",
  radix: RADIX,
  seat_role: SEAT_ROLE,
  carrier_roach_uuid: ROACH_UUID,
  status: "CANDIDATE_NOT_ADMITTED",
  authority_inherited: false,
  recovery_ssot: "github:TTaoGaming/hfo-gen-142#13",
  source: "worldweaver-public recovery seed + live Cloudflare health",
});

async function sha256(value: string) {
  const bytes = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return [...new Uint8Array(bytes)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function canonicalIssueSnapshot() {
  const headers = { "user-agent": "hfo-gen142-native-scout-r0", accept: "application/vnd.github+json" };
  try {
    const issueResponse = await fetch(ISSUE_API, { headers });
    if (!issueResponse.ok) return { ok: false, error: `ISSUE_HTTP_${issueResponse.status}` };
    const issue = await issueResponse.json() as { title?: string; body?: string; comments?: number; updated_at?: string };
    const perPage = 20;
    const page = Math.max(1, Math.ceil((issue.comments ?? 0) / perPage));
    const commentsResponse = await fetch(`${ISSUE_API}/comments?per_page=${perPage}&page=${page}`, { headers });
    const comments = commentsResponse.ok
      ? await commentsResponse.json() as Array<{ id?: number; body?: string; user?: { login?: string }; updated_at?: string }>
      : [];
    return {
      ok: true,
      title: issue.title,
      updated_at: issue.updated_at,
      body: (issue.body ?? "").slice(0, 6000),
      comments: comments.slice(-10).map((c) => ({
        id: c.id, user: c.user?.login, updated_at: c.updated_at, body: (c.body ?? "").slice(0, 3000),
      })),
    };
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : String(error) };
  }
}

const BASE_SYSTEM = `You are bounded cognition inside a Byzantine-aware research swarm.
GitHub #13 is supplied as coordination evidence, not unquestionable truth. Fresh primary-source observations outrank stale summaries.
LLM output is proposal, never authority. Producer != verifier. A hash is integrity, not truth.
Never invent an incumbent, score, rule, publication path, buyer, or proof. Never turn a visible zero into an automatic crown.
No submit, message, spend, login, account mutation, credential handling, GitHub mutation, or control-plane redesign.
Research only. Prefer public primary sources, accepted protocols, reproducible metrics, donor density, and fast public attribution.
A prestigious crown must have a real incumbent, independent verifier, accepted submission path, public attribution, and buyer-legible value.`;

const PROPOSER_SYSTEM = BASE_SYSTEM + `
ROLE=PROPOSER. Search aggressively but conservatively. Produce up to 3 evidence-backed survivors or NONE.
Look for weak incumbents, public exemplar genes, mutable axes, accepted evaluators, and cheap canaries.
Return JSON only with keys: role, lane, claims, evidence_urls, candidate_survivors, uncertainty.`;

const FALSIFIER_SYSTEM = BASE_SYSTEM + `
ROLE=FALSIFIER. Assume the obvious proposal is reward-hacked, stale, proxy prestige, or publication-gated.
Try to kill candidates using current rules, actual incumbent strength, hidden/private scoring, verifier weakness, attribution ambiguity,
submission latency, terms, compute cost, buyer irrelevance, or missing donor legality.
Return JSON only with keys: role, lane, kills, surviving_objections, evidence_urls, uncertainty.`;

const REDUCER_SYSTEM = BASE_SYSTEM + `
ROLE=REDUCER. Reconcile independent proposer and falsifier traces. Do not average disagreement away.
Only retain claims jointly supportable by cited observations. If evidence is inadequate, return survivors=[] and state the blocker.
Return strict JSON, no markdown, with exactly these keys:
observed_utc, lane, canonical_recovery, survivors, finding, strongest_falsifier, blocker, next_executable_assay.
survivors must be an array with at most 3 strings. lane must exactly match the requested lane.`;

function parseStrictResult(text: string, lane: Lane): Record<string, unknown> {
  const trimmed = text.trim().replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/, "");
  const value = JSON.parse(trimmed);
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("RESULT_OBJECT_REQUIRED");
  const obj = value as Record<string, unknown>;
  const expected = [
    "observed_utc", "lane", "canonical_recovery", "survivors", "finding",
    "strongest_falsifier", "blocker", "next_executable_assay",
  ].sort();
  if (Object.keys(obj).sort().join("|") !== expected.join("|")) throw new Error("RESULT_FIELDS_REFUSED");
  if (obj.lane !== lane) throw new Error("RESULT_LANE_MISMATCH");
  if (!Array.isArray(obj.survivors) || obj.survivors.length > 3 || !obj.survivors.every((x) => typeof x === "string")) {
    throw new Error("RESULT_SURVIVORS_REFUSED");
  }
  for (const key of ["observed_utc", "canonical_recovery", "finding", "strongest_falsifier", "blocker", "next_executable_assay"]) {
    if (typeof obj[key] !== "string") throw new Error(`RESULT_${key.toUpperCase()}_REFUSED`);
  }
  return obj;
}

export class Gen142Scout extends Agent<any, ScoutState> {
  initialState: ScoutState = {
    actorId: ACTOR_ID,
    phase: "IDLE",
    epoch: 0,
    recoveryCount: 0,
    failureCount: 0,
    sameFailureCount: 0,
    updatedAt: new Date(0).toISOString(),
  };

  private normalizedState(): ScoutState {
    return {
      ...this.initialState,
      ...this.state,
      failureCount: this.state.failureCount ?? 0,
      sameFailureCount: this.state.sameFailureCount ?? 0,
      recoveryCount: this.state.recoveryCount ?? 0,
    };
  }

  async readPublicState() {
    return { ...this.normalizedState(), anchorClaim: ANCHOR_CLAIM, debateVersion: DEBATE_VERSION };
  }

  async runScout(runId: string) {
    const current = this.normalizedState();
    if (current.phase === "COGNITION_RUNNING") {
      return { accepted: false, reason: "BUSY", lastRunId: current.lastRunId };
    }
    const scarSkip = current.sameFailureCount >= 2 && current.lastAttemptLane === LANES[current.epoch % LANES.length];
    const runEpoch = current.epoch + (scarSkip ? 1 : 0);
    const lane = LANES[runEpoch % LANES.length];
    const canonical = await canonicalIssueSnapshot();
    const started = new Date().toISOString();
    this.setState({
      ...current,
      phase: "COGNITION_RUNNING",
      lastAttemptLane: lane,
      lastRunId: runId,
      lastStartedUtc: started,
      lastResult: undefined,
      lastResultSha256: undefined,
      lastDebateSha256: undefined,
      lastError: undefined,
      updatedAt: started,
    });

    return this.startFiber(
      "gen142-scout",
      async (ctx) => {
        ctx.stash({ runId, actorId: ACTOR_ID, lane, debateVersion: DEBATE_VERSION });
        const workersai = createWorkersAI({ binding: this.env.AI });
        const runDebater = async (role: "PROPOSER" | "FALSIFIER", system: string) => {
          const browserTools = createQuickActionTools({
            browser: this.env.BROWSER,
            actions: ["markdown", "links", "scrape", "extract"],
            maxChars: 26000,
          });
          const r = await generateText({
            model: workersai(MODEL),
            system,
            prompt: JSON.stringify({
              runId, lane, canonical,
              objective: lane === "CROWN"
                ? "Sweep public prestige battlefields across any lawful domain; find weak real incumbents and public gene donors."
                : lane === "DONOR"
                  ? "Mine public champion methods, repos, papers, configs, prompts, solvers and baselines as legal donor genes."
                  : lane === "BENCHMARK"
                    ? "Verify incumbent/rules/submission/publication surfaces and design the smallest frozen canary."
                    : "Reduce newest swarm evidence; identify the highest-value next machine-owned edge and any architecture leak.",
            }).slice(0, 24000),            tools: browserTools,
            stopWhen: stepCountIs(6),
            maxOutputTokens: 1600,
          });
          return {
            role,
            text: r.text.trim().slice(0, 7000),
            steps: r.steps.map((step, index) => ({
              index,
              text: step.text?.slice(0, 1800) ?? "",
              toolResults: step.toolResults?.slice(0, 4) ?? [],
            })),
          };
        };

        try {
          const [proposer, falsifier] = await Promise.all([
            runDebater("PROPOSER", PROPOSER_SYSTEM),
            runDebater("FALSIFIER", FALSIFIER_SYSTEM),
          ]);
          const debateSha = await sha256(JSON.stringify({ lane, proposer, falsifier }));
          const synthesis = await generateText({
            model: workersai(MODEL),
            system: REDUCER_SYSTEM,
            prompt: JSON.stringify({ runId, lane, canonical, proposer, falsifier, debate_sha256: debateSha }).slice(0, 30000),
            maxOutputTokens: 1800,
          });          const text = synthesis.text.trim().slice(0, 12000);
          if (!text) throw new Error("EMPTY_SYNTHESIS");
          parseStrictResult(text, lane);
          const completed = new Date().toISOString();
          this.setState({
            ...this.state,
            phase: "READY",
            epoch: runEpoch + 1,
            lastLane: lane,
            lastAttemptLane: lane,
            lastCompletedUtc: completed,
            lastResult: text,
            lastResultSha256: await sha256(text),
            lastDebateSha256: debateSha,
            lastError: undefined,
            lastFailureFingerprint: undefined,
            sameFailureCount: 0,
            updatedAt: completed,
          });
        } catch (error) {
          const failed = new Date().toISOString();
          const message = error instanceof Error ? error.message : String(error);
          const fingerprint = await sha256(`${lane}|${message.slice(0, 300)}`);
          const prior = this.normalizedState();
          const same = prior.lastFailureFingerprint === fingerprint ? prior.sameFailureCount + 1 : 1;
          this.setState({
            ...prior,
            phase: "FAILED",
            lastAttemptLane: lane,
            lastCompletedUtc: failed,
            lastResult: undefined,
            lastResultSha256: undefined,
            lastDebateSha256: undefined,
            lastError: message.slice(0, 1000),
            lastFailureFingerprint: fingerprint,
            failureCount: prior.failureCount + 1,
            sameFailureCount: same,
            updatedAt: failed,
          });
          throw error;
        }
      },
      { idempotencyKey: runId, metadata: { actorId: ACTOR_ID, runId, lane, debateVersion: DEBATE_VERSION } },
    );
  }

  async onFiberRecovered(ctx: FiberRecoveryContext) {
    if (ctx.name !== "gen142-scout") return;
    const now = new Date().toISOString();
    const prior = this.normalizedState();
    const fingerprint = await sha256(`${prior.lastAttemptLane ?? "UNKNOWN"}|FIBER_INTERRUPTED`);
    const same = prior.lastFailureFingerprint === fingerprint ? prior.sameFailureCount + 1 : 1;
    this.setState({
      ...prior,
      phase: "RECOVERY_REQUIRED",
      recoveryCount: prior.recoveryCount + 1,
      failureCount: prior.failureCount + 1,
      sameFailureCount: same,
      lastResult: undefined,
      lastResultSha256: undefined,
      lastDebateSha256: undefined,
      lastFailureFingerprint: fingerprint,
      lastError: "FIBER_INTERRUPTED",
      updatedAt: now,
    });
    return { status: "interrupted" as const };
  }
}

async function getScout(env: any) {
  return (await getAgentByName(env.GEN142_SCOUT, ACTOR_ID, {
    routingRetry: { maxAttempts: 3 },
  })) as any;
}

async function runScheduled(env: any, scheduledTime: number) {
  const scout = await getScout(env);
  const stamp = new Date(scheduledTime).toISOString().replace(/[^0-9TZ]/g, "");
  return scout.runScout(`cron-${stamp}`);
}

export default {
  async fetch(request: Request, env: any) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") {
      return Response.json({
        ok: true,
        actor: ACTOR_ID,
        parent_actor: PARENT_ACTOR,
        radix: RADIX,
        model: MODEL,
        cadence: "*/15 * * * *",
        lanes: LANES,
        debate: { version: DEBATE_VERSION, roles: ["PROPOSER", "FALSIFIER", "REDUCER"] },
        effect_ceiling: "RESEARCH_ONLY",
      });
    }
    if (request.method === "GET" && url.pathname === "/anchor") {
      return Response.json(ANCHOR_CLAIM);
    }
    if (request.method === "GET" && url.pathname === "/state") {
      const scout = await getScout(env);
      return Response.json(await scout.readPublicState());
    }
    return new Response("Not found", { status: 404 });
  },
  async scheduled(controller: ScheduledController, env: any, ctx: ExecutionContext) {
    ctx.waitUntil(runScheduled(env, controller.scheduledTime));
  },
} satisfies ExportedHandler<any>;
