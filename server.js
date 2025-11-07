/**
 * AI Ticket Processor - Dashboard Backend
 * - Exposes /api/dashboard/tickets
 *         /api/dashboard/kpis
 *         /api/dashboard/series
 *
 * Usage:
 * 1. copy .env.example -> .env and fill values
 * 2. npm install
 * 3. npm run start
 */

require('dotenv').config();
const express = require('express');
const axios = require('axios');
const axiosRetry = require('axios-retry');
const NodeCache = require('node-cache');
const { parseISO, formatISO, subHours, startOfHour } = require('date-fns');

const app = express();
app.use(express.json());

const SUBDOMAIN = process.env.ZENDESK_SUBDOMAIN;
const EMAIL = process.env.ZENDESK_EMAIL;
const API_TOKEN = process.env.ZENDESK_API_TOKEN;
const PORT = process.env.PORT || 8080;
const CACHE_TTL = parseInt(process.env.CACHE_TTL_SECONDS || '20', 10);
const DEFAULT_TAG = process.env.DEFAULT_SEARCH_TAG || 'pii_test';

if (!SUBDOMAIN || !EMAIL || !API_TOKEN) {
  console.error("Set ZENDESK_SUBDOMAIN, ZENDESK_EMAIL, ZENDESK_API_TOKEN in .env");
  process.exit(1);
}

const ZENDESK_BASE = `https://${SUBDOMAIN}.zendesk.com/api/v2`;
const auth = { username: `${EMAIL}/token`, password: API_TOKEN };

const axiosInstance = axios.create({
  baseURL: ZENDESK_BASE,
  timeout: 30_000
});
axiosRetry(axiosInstance, {
  retries: 3,
  retryDelay: axiosRetry.exponentialDelay,
  retryCondition: (err) => {
    // retry on network errors or 5xx or 429
    return axiosRetry.isNetworkOrIdempotentRequestError(err) || err.response?.status === 429;
  }
});

const cache = new NodeCache({ stdTTL: CACHE_TTL, checkperiod: CACHE_TTL * 0.2 });

/**
 * Utility: safe parse JSON inside a string (returns null if not found)
 * The AI comment may contain JSON or key: value format. We'll attempt:
 * 1) Find first JSON block {...} and parse it
 * 2) If not found, look for "analysis:" prefix and parse trailing JSON or key-values
 */
function extractAnalysisFromComment(text) {
  if (!text) return null;
  // Try to find JSON object
  const jsonMatch = text.match(/\{[\s\S]*\}/);
  if (jsonMatch) {
    try {
      const parsed = JSON.parse(jsonMatch[0]);
      return parsed;
    } catch (e) {
      // not valid JSON, continue
    }
  }
  // look for simple key:value lines (heuristic)
  // e.g. summary: ... \n root_cause: bug \n urgency: high
  const lines = text.split(/\r?\n/).map(l => l.trim());
  const keys = ['summary','root_cause','urgency','sentiment','processing_time'];
  const obj = {};
  let found = false;
  for (const line of lines) {
    const m = line.match(/^([\w_]+)\s*[:=-]\s*(.+)$/);
    if (m && keys.includes(m[1].toLowerCase())) {
      found = true;
      obj[m[1].toLowerCase()] = m[2].trim();
    }
  }
  return found ? obj : null;
}

/**
 * Zendesk helper: search tickets by tag (uses search API)
 * Returns array of ticket objects (may be paginated).
 * For dashboard purposes we only fetch 'per_page' items for speed.
 */
async function searchTicketsByTag(tag = DEFAULT_TAG, per_page = 200) {
  const cacheKey = `search:${tag}:${per_page}`;
  const cached = cache.get(cacheKey);
  if (cached) return cached;

  // Search query: type:ticket tags:tag
  const q = encodeURIComponent(`type:ticket tags:${tag}`);
  const url = `/search.json?query=${q}&sort_by=created_at&sort_order=desc&per_page=${per_page}`;
  const resp = await axiosInstance.get(url, { auth });
  const results = resp.data?.results || [];
  cache.set(cacheKey, results);
  return results;
}

/**
 * Get ticket comments for a ticket id and parse analysis if present.
 */
async function getTicketWithAnalysis(ticket, includeComments = false) {
  // ticket is partial (from search). ticket.id exists.
  try {
    const resp = await axiosInstance.get(`/tickets/${ticket.id}/comments.json`, { auth });
    const comments = resp.data?.comments || [];
    // find most recent internal comment (public === false) that includes analysis
    let analysis = null;
    for (let i = comments.length - 1; i >= 0; i--) {
      const c = comments[i];
      const txt = (c.plain_body || c.body || '');
      const parsed = extractAnalysisFromComment(txt);
      if (parsed) {
        analysis = parsed;
        break;
      }
    }
    // fallback: try to parse the last internal comment even if not structured
    if (!analysis) {
      const lastInternal = comments.slice().reverse().find(c => c.public === false);
      if (lastInternal) {
        analysis = extractAnalysisFromComment(lastInternal.plain_body || lastInternal.body || '') || null;
      }
    }
    const obj = {
      id: ticket.id,
      subject: ticket.subject,
      requester: ticket.requester_id,
      tags: ticket.tags,
      priority: ticket.priority,
      status: ticket.status,
      created_at: ticket.created_at,
      updated_at: ticket.updated_at,
      analysis: analysis || null,
      updated: ticket.tags && ticket.tags.includes('ai_processed') // conservative heuristic
    };
    if (includeComments) {
      obj._comments = comments.map(c => ({ id: c.id, public: c.public, author_id: c.author_id, created_at: c.created_at, plain_body: c.plain_body || '' }));
    }
    return obj;
  } catch (e) {
    console.warn("Error fetching comments for ticket", ticket.id, e?.response?.status);
    return {
      id: ticket.id,
      subject: ticket.subject,
      requester: ticket.requester_id,
      tags: ticket.tags,
      priority: ticket.priority,
      status: ticket.status,
      created_at: ticket.created_at,
      updated_at: ticket.updated_at,
      analysis: null,
      updated: ticket.tags && ticket.tags.includes('ai_processed')
    };
  }
}

/**
 * Endpoint: /api/dashboard/tickets
 * Query params:
 *   ?tag=pii_test
 *   ?limit=50
 *   ?includeComments=true
 */
app.get('/api/dashboard/tickets', async (req, res) => {
  try {
    const tag = req.query.tag || DEFAULT_TAG;
    const limit = parseInt(req.query.limit || '50', 10);
    const includeComments = req.query.includeComments === 'true';
    const all = await searchTicketsByTag(tag, Math.max(limit, 50));
    const slice = all.slice(0, limit);
    const arr = await Promise.all(slice.map(t => getTicketWithAnalysis(t, includeComments)));
    return res.json(arr);
  } catch (e) {
    console.error("tickets error", e?.message);
    res.status(500).json({ error: e?.message || 'unknown' });
  }
});

/**
 * Endpoint: /api/dashboard/kpis
 * Returns {
 *  avgLatency: number (seconds),
 *  successRate: number (0-100),
 *  ticketsPerHour: number,
 *  costPerTicketUSD: number
 * }
 *
 * Notes: avgLatency and costPerTicketUSD are estimated heuristics:
 * - avgLatency read from analysis.processing_time if present in comments
 * - successRate computed as percent of found tickets that have ai_processed tag
 */
app.get('/api/dashboard/kpis', async (req, res) => {
  try {
    const tag = req.query.tag || DEFAULT_TAG;
    const per_page = 200;
    const tickets = await searchTicketsByTag(tag, per_page);

    // compute successRate
    const hasProcessed = tickets.filter(t => t.tags && t.tags.includes('ai_processed')).length;
    const successRate = tickets.length ? Math.round((hasProcessed / tickets.length) * 100) : 0;

    // fetch comments for a sample to compute avg latency from analysis.processing_time
    const sample = tickets.slice(0, Math.min(60, tickets.length));
    const processed = await Promise.all(sample.map(t => getTicketWithAnalysis(t, false)));
    let latencies = [];
    for (const p of processed) {
      const pt = p.analysis && (p.analysis.processing_time || p.analysis.processingTime || p.analysis.processing) ;
      if (pt) {
        const num = parseFloat(String(pt).replace(/[^\d.]/g, ''));
        if (!Number.isNaN(num)) latencies.push(num);
      }
    }
    // fallback: compute approximate latency via comments API timing not available -> use default
    const avgLatency = latencies.length ? Math.round((latencies.reduce((a,b)=>a+b,0)/latencies.length) * 100) / 100 : 1.8;

    // tickets per hour estimate using created_at window
    const now = new Date();
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
    const recentCount = tickets.filter(t => new Date(t.created_at) >= oneHourAgo).length;
    const ticketsPerHour = recentCount; // approximation based on tag-limited search

    // cost estimate (placeholder): you should compute token usage accurately in prod
    const costPerTicketUSD = 0.001;

    return res.json({
      avgLatency,
      successRate,
      ticketsPerHour,
      costPerTicketUSD
    });
  } catch (e) {
    console.error("kpis error", e?.message);
    res.status(500).json({ error: e?.message || 'unknown' });
  }
});

/**
 * Endpoint: /api/dashboard/series
 * Returns a time-series array for the last N hours (default 24):
 *  { times: [{time: 'HH:00', count: N}], root: [{name:'bug', value: N}], sentiment: [{name:'negative', value:N}] }
 *
 * Implementation: fetch tickets by tag and aggregate by hour using created_at
 */
app.get('/api/dashboard/series', async (req, res) => {
  try {
    const tag = req.query.tag || DEFAULT_TAG;
    const hours = parseInt(req.query.hours || '24', 10);

    // fetch tickets (max safe per_page)
    const per_page = 400;
    const tickets = await searchTicketsByTag(tag, per_page);

    // build hourly buckets
    const now = new Date();
    const start = startOfHour(subHours(now, hours - 1));
    // initialize buckets
    const buckets = {};
    for (let i = 0; i < hours; i++) {
      const key = formatISO(startOfHour(subHours(now, hours - 1 - i))).slice(0,13) + ':00:00Z';
      buckets[key] = 0;
    }

    // aggregate by created_at hour
    for (const t of tickets) {
      const created = new Date(t.created_at);
      if (created < start) continue;
      const hourKey = formatISO(startOfHour(created)).slice(0,13) + ':00:00Z';
      if (buckets[hourKey] !== undefined) buckets[hourKey] += 1;
    }
    const times = Object.keys(buckets).map(k => ({ time: k, count: buckets[k] }));

    // root-cause and sentiment distributions (sample by parsing comments)
    const sample = tickets.slice(0, Math.min(200, tickets.length));
    const analyzed = await Promise.all(sample.map(t => getTicketWithAnalysis(t, false)));
    const rootCounts = {};
    const sentimentCounts = {};
    for (const a of analyzed) {
      const r = (a.analysis && (a.analysis.root_cause || a.analysis.root || a.analysis.rootCause)) || 'other';
      const s = (a.analysis && (a.analysis.sentiment || a.analysis.sent || a.analysis.mood)) || 'neutral';
      rootCounts[r] = (rootCounts[r] || 0) + 1;
      sentimentCounts[s] = (sentimentCounts[s] || 0) + 1;
    }
    const root = Object.keys(rootCounts).map(k => ({ name: k, value: rootCounts[k] }));
    const sentiment = Object.keys(sentimentCounts).map(k => ({ name: k, value: sentimentCounts[k] }));

    return res.json({ times, root, sentiment });
  } catch (e) {
    console.error("series error", e?.message);
    res.status(500).json({ error: e?.message || 'unknown' });
  }
});

/**
 * Health probe
 */
app.get('/health', (req, res) => {
  res.json({ ok: true, ts: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`AI Ticket Processor backend listening on :${PORT}`);
});
