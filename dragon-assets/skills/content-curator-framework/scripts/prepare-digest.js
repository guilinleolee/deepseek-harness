#!/usr/bin/env node

// ============================================================================
// Content Curator Framework — Prepare Digest
// ============================================================================
// Gathers everything the LLM needs to produce a digest:
// - Fetches feeds (x + podcasts + blogs) from URLs in ~/.content-curator/config.json
// - Reads remix prompts from the skill's prompts/ directory
// - Outputs a single JSON blob to stdout
//
// Usage: node prepare-digest.js
// Output: JSON to stdout
// ============================================================================

import { readFile } from 'fs/promises';
import { existsSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

// -- Constants ---------------------------------------------------------------

const USER_DIR = join(homedir(), '.content-curator');
const CONFIG_PATH = join(USER_DIR, 'config.json');

const PROMPT_FILES = [
  'digest-intro.md',
  'summarize-tweets.md',
  'summarize-podcasts.md',
  'summarize-blogs.md',
  'translate.md'
];

// -- Fetch helpers -----------------------------------------------------------

async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) return null;
  return res.json();
}

// -- Main --------------------------------------------------------------------

async function main() {
  const errors = [];

  // 1. Read user config — feed URLs, language, delivery
  let config = {
    language: 'en',
    frequency: 'daily',
    delivery: { method: 'stdout' },
    sources: {
      x: null,
      podcasts: null,
      blogs: null
    }
  };
  if (existsSync(CONFIG_PATH)) {
    try {
      config = JSON.parse(await readFile(CONFIG_PATH, 'utf-8'));
    } catch (err) {
      errors.push(`Could not read config: ${err.message}`);
    }
  }

  // 2. Fetch all configured feeds in parallel (skip null/empty)
  const feedUrls = config.sources || {};
  const feedResults = await Promise.all([
    feedUrls.x       ? fetchJSON(feedUrls.x)       : Promise.resolve(null),
    feedUrls.podcasts ? fetchJSON(feedUrls.podcasts) : Promise.resolve(null),
    feedUrls.blogs    ? fetchJSON(feedUrls.blogs)    : Promise.resolve(null)
  ]);

  const [feedX, feedPodcasts, feedBlogs] = feedResults;

  if (feedUrls.x       && !feedX)       errors.push('Could not fetch x feed');
  if (feedUrls.podcasts && !feedPodcasts) errors.push('Could not fetch podcasts feed');
  if (feedUrls.blogs   && !feedBlogs)   errors.push('Could not fetch blogs feed');

  // 3. Load prompts from the skill's prompts/ directory
  //    The skill ships default prompts; users can override per-file.
  const prompts = {};
  const scriptDir = decodeURIComponent(new URL('.', import.meta.url).pathname);
  const skillPromptsDir = join(scriptDir, '..', 'prompts');
  const userPromptsDir  = join(USER_DIR, 'prompts');

  for (const filename of PROMPT_FILES) {
    const key = filename.replace('.md', '').replace(/-/g, '_');
    const userPath  = join(userPromptsDir,  filename);
    const localPath = join(skillPromptsDir, filename);

    // Priority 1: user's custom prompt (they personalized it — don't overwrite)
    if (existsSync(userPath)) {
      prompts[key] = await readFile(userPath, 'utf-8');
      continue;
    }

    // Priority 2: local skill default
    if (existsSync(localPath)) {
      prompts[key] = await readFile(localPath, 'utf-8');
    } else {
      errors.push(`Could not load prompt: ${filename}`);
    }
  }

  // 4. Normalize feed shapes — support both {x:[...]} and {[key]:[...]} formats
  //    follow-builders uses: { x:[...], podcasts:[...], blogs:[...] }
  //    generic sources may use: { builders:[...], episodes:[...], posts:[...] }
  //    We accept either.
  function extractItems(feed, ...keys) {
    for (const k of keys) {
      if (Array.isArray(feed?.[k])) return feed[k];
    }
    return [];
  }

  const xItems        = extractItems(feedX,       'x', 'builders', 'tweets');
  const podcastItems   = extractItems(feedPodcasts, 'podcasts', 'episodes', 'items');
  const blogItems     = extractItems(feedBlogs,   'blogs', 'posts', 'items');

  // 5. Build output
  const output = {
    status: 'ok',
    generatedAt: new Date().toISOString(),

    config: {
      language:  config.language  || 'en',
      frequency: config.frequency || 'daily',
      delivery:  config.delivery  || { method: 'stdout' }
    },

    content: {
      x:        xItems,
      podcasts:  podcastItems,
      blogs:    blogItems
    },

    stats: {
      xItems:      xItems.length,
      podcasts:    podcastItems.length,
      blogs:       blogItems.length,
      feedGeneratedAt: feedX?.generatedAt
        || feedPodcasts?.generatedAt
        || feedBlogs?.generatedAt
        || null
    },

    prompts,
    errors: errors.length > 0 ? errors : undefined
  };

  console.log(JSON.stringify(output, null, 2));
}

main().catch(err => {
  console.error(JSON.stringify({
    status: 'error',
    message: err.message
  }));
  process.exit(1);
});
