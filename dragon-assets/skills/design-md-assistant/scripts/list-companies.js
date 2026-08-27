#!/usr/bin/env node
/**
 * Design MD Assistant - Company Index Script
 * Lists all available design systems by category
 */

const fs = require('fs');
const path = require('path');

const SKILL_DIR = path.dirname(__filename);
const DESIGN_DIR = path.join(SKILL_DIR, '..', 'design-md');

// Company categories with metadata
const companyIndex = {
  'ai-ml': {
    name: 'AI & Machine Learning',
    companies: [
      { id: 'claude', name: 'Claude', company: 'Anthropic', description: 'Warm terracotta accent, clean editorial layout' },
      { id: 'cohere', name: 'Cohere', company: 'Cohere', description: 'Vibrant gradients, data-rich dashboard aesthetic' },
      { id: 'elevenlabs', name: 'ElevenLabs', company: 'ElevenLabs', description: 'Dark cinematic UI, audio-waveform aesthetics' },
      { id: 'minimax', name: 'MiniMax', company: 'MiniMax', description: 'Bold dark interface with neon accents' },
      { id: 'mistral.ai', name: 'Mistral AI', company: 'Mistral AI', description: 'French-engineered minimalism, purple-toned' },
      { id: 'ollama', name: 'Ollama', company: 'Ollama', description: 'Terminal-first, monochrome simplicity' },
      { id: 'opencode.ai', name: 'OpenCode AI', company: 'OpenCode AI', description: 'Developer-centric dark theme' },
      { id: 'replicate', name: 'Replicate', company: 'Replicate', description: 'Clean white canvas, code-forward' },
      { id: 'runwayml', name: 'RunwayML', company: 'RunwayML', description: 'Cinematic dark UI, media-rich layout' },
      { id: 'together.ai', name: 'Together AI', company: 'Together AI', description: 'Technical, blueprint-style design' },
      { id: 'voltagent', name: 'VoltAgent', company: 'VoltAgent', description: 'Void-black canvas, emerald accent, terminal-native' },
      { id: 'x.ai', name: 'xAI', company: 'xAI', description: 'Stark monochrome, futuristic minimalism' }
    ]
  },
  'developer-tools': {
    name: 'Developer Tools & Platforms',
    companies: [
      { id: 'cursor', name: 'Cursor', company: 'Anysphere', description: 'AI-first code editor, sleek dark interface' },
      { id: 'expo', name: 'Expo', company: 'Expo', description: 'React Native platform, dark theme, code-centric' },
      { id: 'linear.app', name: 'Linear', company: 'Linear', description: 'Ultra-minimal, precise, purple accent' },
      { id: 'lovable', name: 'Lovable', company: 'Lovable', description: 'Playful gradients, friendly dev aesthetic' },
      { id: 'mintlify', name: 'Mintlify', company: 'Mintlify', description: 'Clean, green-accented, reading-optimized' },
      { id: 'posthog', name: 'PostHog', company: 'PostHog', description: 'Playful hedgehog branding, developer-friendly dark UI' },
      { id: 'raycast', name: 'Raycast', company: 'Raycast', description: 'Sleek dark chrome, vibrant gradient accents' },
      { id: 'resend', name: 'Resend', company: 'Resend', description: 'Minimal dark theme, monospace accents' },
      { id: 'sentry', name: 'Sentry', company: 'Sentry', description: 'Dark dashboard, data-dense, pink-purple accent' },
      { id: 'supabase', name: 'Supabase', company: 'Supabase', description: 'Dark emerald theme, code-first' },
      { id: 'superhuman', name: 'Superhuman', company: 'Superhuman', description: 'Premium dark UI, keyboard-first, purple glow' },
      { id: 'vercel', name: 'Vercel', company: 'Vercel', description: 'Black and white precision, Geist font' },
      { id: 'warp', name: 'Warp', company: 'Warp', description: 'Modern terminal, block-based command UI' },
      { id: 'zapier', name: 'Zapier', company: 'Zapier', description: 'Warm orange, friendly illustration-driven' }
    ]
  },
  'infrastructure': {
    name: 'Infrastructure & Cloud',
    companies: [
      { id: 'clickhouse', name: 'ClickHouse', company: 'ClickHouse', description: 'Yellow-accented, technical documentation style' },
      { id: 'composio', name: 'Composio', company: 'Composio', description: 'Modern dark with colorful integration icons' },
      { id: 'hashicorp', name: 'HashiCorp', company: 'HashiCorp', description: 'Enterprise-clean, black and white' },
      { id: 'mongodb', name: 'MongoDB', company: 'MongoDB', description: 'Green leaf branding, developer documentation focus' },
      { id: 'sanity', name: 'Sanity', company: 'Sanity', description: 'Red accent, content-first editorial layout' },
      { id: 'stripe', name: 'Stripe', company: 'Stripe', description: 'Signature purple gradients, weight-300 elegance' }
    ]
  },
  'fintech': {
    name: 'Fintech & Crypto',
    companies: [
      { id: 'coinbase', name: 'Coinbase', company: 'Coinbase', description: 'Clean blue identity, trust-focused' },
      { id: 'kraken', name: 'Kraken', company: 'Kraken', description: 'Purple-accented dark UI, data-dense dashboards' },
      { id: 'revolut', name: 'Revolut', company: 'Revolut', description: 'Sleek dark interface, gradient cards' },
      { id: 'wise', name: 'Wise', company: 'Wise', description: 'Bright green accent, friendly and clear' }
    ]
  },
  'enterprise': {
    name: 'Enterprise & Consumer',
    companies: [
      { id: 'airbnb', name: 'Airbnb', company: 'Airbnb', description: 'Warm coral accent, photography-driven, rounded UI' },
      { id: 'apple', name: 'Apple', company: 'Apple', description: 'Premium white space, SF Pro, cinematic imagery' },
      { id: 'ibm', name: 'IBM', company: 'IBM', description: 'Carbon design system, structured blue palette' },
      { id: 'nvidia', name: 'NVIDIA', company: 'NVIDIA', description: 'Green-black energy, technical power aesthetic' },
      { id: 'spacex', name: 'SpaceX', company: 'SpaceX', description: 'Stark black and white, full-bleed imagery, futuristic' },
      { id: 'spotify', name: 'Spotify', company: 'Spotify', description: 'Vibrant green on dark, bold type, album-art-driven' },
      { id: 'uber', name: 'Uber', company: 'Uber', description: 'Bold black and white, tight type, urban energy' }
    ]
  },
  'car-brands': {
    name: 'Car Brands',
    companies: [
      { id: 'bmw', name: 'BMW', company: 'BMW', description: 'Dark premium surfaces, precise German engineering' },
      { id: 'ferrari', name: 'Ferrari', company: 'Ferrari', description: 'Chiaroscuro black-white editorial, Ferrari Red' },
      { id: 'lamborghini', name: 'Lamborghini', company: 'Lamborghini', description: 'True black cathedral, gold accent' },
      { id: 'renault', name: 'Renault', company: 'Renault', description: 'Vivid aurora gradients, zero-radius buttons' },
      { id: 'tesla', name: 'Tesla', company: 'Tesla', description: 'Radical subtraction, cinematic photography' }
    ]
  },
  'design-productivity': {
    name: 'Design & Productivity',
    companies: [
      { id: 'airtable', name: 'Airtable', company: 'Airtable', description: 'Colorful, friendly, structured data aesthetic' },
      { id: 'cal', name: 'Cal.com', company: 'Cal.com', description: 'Clean neutral UI, developer-oriented simplicity' },
      { id: 'clay', name: 'Clay', company: 'Clay', description: 'Organic shapes, soft gradients, art-directed' },
      { id: 'figma', name: 'Figma', company: 'Figma', description: 'Vibrant multi-color, playful yet professional' },
      { id: 'framer', name: 'Framer', company: 'Framer', description: 'Bold black and blue, motion-first' },
      { id: 'intercom', name: 'Intercom', company: 'Intercom', description: 'Friendly blue palette, conversational UI' },
      { id: 'miro', name: 'Miro', company: 'Miro', description: 'Bright yellow accent, infinite canvas aesthetic' },
      { id: 'notion', name: 'Notion', company: 'Notion', description: 'Warm minimalism, serif headings, soft surfaces' },
      { id: 'pinterest', name: 'Pinterest', company: 'Pinterest', description: 'Red accent, masonry grid, image-first' },
      { id: 'webflow', name: 'Webflow', company: 'Webflow', description: 'Blue-accented, polished marketing site aesthetic' }
    ]
  }
};

// Total count
let totalCompanies = 0;
Object.values(companyIndex).forEach(cat => {
  totalCompanies += cat.companies.length;
});

/**
 * List all companies by category
 */
function listCompanies(category = null) {
  if (category) {
    const cat = companyIndex[category];
    if (!cat) {
      console.log(`Category "${category}" not found. Available categories:`);
      Object.keys(companyIndex).forEach(key => {
        console.log(`  - ${key}`);
      });
      return;
    }
    console.log(`\n## ${cat.name} (${cat.companies.length} companies)\n`);
    cat.companies.forEach(c => {
      console.log(`  ${c.name.padEnd(15)} - ${c.description}`);
    });
  } else {
    console.log(`\n# Design MD Assistant - ${totalCompanies} Companies Available\n`);
    Object.entries(companyIndex).forEach(([key, cat]) => {
      console.log(`## ${cat.name} (${cat.companies.length})\n`);
      cat.companies.forEach(c => {
        console.log(`  ${c.name.padEnd(15)} - ${c.description}`);
      });
      console.log('');
    });
  }
}

/**
 * Search companies by keyword
 */
function searchCompanies(keyword) {
  const results = [];
  Object.entries(companyIndex).forEach(([category, cat]) => {
    cat.companies.forEach(c => {
      const searchText = `${c.name} ${c.description} ${c.company}`.toLowerCase();
      if (searchText.includes(keyword.toLowerCase())) {
        results.push({ ...c, category: cat.name });
      }
    });
  });

  if (results.length === 0) {
    console.log(`No companies found matching "${keyword}"`);
    return;
  }

  console.log(`\n# Search results for "${keyword}" (${results.length} found)\n`);
  results.forEach(r => {
    console.log(`  ${r.name.padEnd(15)} [${r.category}]`);
    console.log(`  ${r.description}\n`);
  });
}

/**
 * Get company design file path
 */
function getDesignPath(companyId) {
  const baseDir = path.join(DESIGN_DIR);
  const filePath = path.join(baseDir, companyId, 'DESIGN.md');

  if (fs.existsSync(filePath)) {
    return filePath;
  }

  // Try case-insensitive search
  const dirs = fs.readdirSync(baseDir, { withFileTypes: true });
  for (const dir of dirs) {
    if (dir.isDirectory() && dir.name.toLowerCase() === companyId.toLowerCase()) {
      const altPath = path.join(baseDir, dir.name, 'DESIGN.md');
      if (fs.existsSync(altPath)) {
        return altPath;
      }
    }
  }

  return null;
}

/**
 * Get all available companies
 */
function getAllCompanies() {
  const companies = [];
  Object.entries(companyIndex).forEach(([category, cat]) => {
    cat.companies.forEach(c => {
      companies.push({ ...c, category });
    });
  });
  return companies;
}

// CLI interface
const args = process.argv.slice(2);
const command = args[0];

switch (command) {
  case 'list':
    listCompanies(args[1]);
    break;
  case 'search':
    if (!args[1]) {
      console.log('Usage: list-companies.js search <keyword>');
      process.exit(1);
    }
    searchCompanies(args[1]);
    break;
  case 'get':
    if (!args[1]) {
      console.log('Usage: list-companies.js get <company-id>');
      process.exit(1);
    }
    const path = getDesignPath(args[1]);
    if (path) {
      console.log(path);
    } else {
      console.log(`Company "${args[1]}" not found`);
      process.exit(1);
    }
    break;
  case 'all':
    const all = getAllCompanies();
    console.log(JSON.stringify(all, null, 2));
    break;
  default:
    listCompanies();
}

module.exports = {
  companyIndex,
  listCompanies,
  searchCompanies,
  getDesignPath,
  getAllCompanies
};
