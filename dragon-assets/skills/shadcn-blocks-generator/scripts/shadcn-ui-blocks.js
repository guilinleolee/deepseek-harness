#!/usr/bin/env node

/**
 * shadcn-ui-blocks CLI
 * 快速添加 shadcn/ui 预制区块
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// 区块注册表
const BLOCKS_REGISTRY = {
  // Hero 区块
  'hero-centered': 'https://ui.shadcn.com/registry/default/block/hero-centered.json',
  'hero-split': 'https://ui.shadcn.com/registry/default/block/hero-split.json',
  'hero-gradient': 'https://ui.shadcn.com/registry/default/block/hero-gradient.json',

  // Features 区块
  'features-grid': 'https://ui.shadcn.com/registry/default/block/features-grid.json',
  'features-icons': 'https://ui.shadcn.com/registry/default/block/features-icons.json',

  // Pricing 区块
  'pricing-cards': 'https://ui.shadcn.com/registry/default/block/pricing-cards.json',
  'pricing-table': 'https://ui.shadcn.com/registry/default/block/pricing-table.json',

  // CTA 区块
  'cta-simple': 'https://ui.shadcn.com/registry/default/block/cta-simple.json',
  'cta-image': 'https://ui.shadcn.com/registry/default/block/cta-image.json',

  // Dashboard 区块
  'dashboard-header': 'https://ui.shadcn.com/registry/default/block/dashboard-header.json',
  'dashboard-stats': 'https://ui.shadcn.com/registry/default/block/dashboard-stats.json',

  // Testimonials 区块
  'testimonials-cards': 'https://ui.shadcn.com/registry/default/block/testimonials-cards.json',

  // Footer 区块
  'footer-simple': 'https://ui.shadcn.com/registry/default/block/footer-simple.json',
  'footer-multi': 'https://ui.shadcn.com/registry/default/block/footer-multi.json',
};

// 预设组合
const PRESETS = {
  landing: ['hero-centered', 'features-grid', 'pricing-cards', 'cta-simple', 'footer-simple'],
  dashboard: ['dashboard-header', 'dashboard-stats', 'dashboard-charts'],
  marketing: ['hero-gradient', 'features-icons', 'testimonials-cards', 'cta-image'],
  pricing: ['hero-centered', 'pricing-cards', 'faq', 'footer-simple'],
};

function printUsage() {
  console.log(`
shadcn-ui-blocks - 预制页面区块生成器

用法:
  npx shadcn-ui-blocks add <block-name>       添加单个区块
  npx shadcn-ui-blocks add <block1> <block2>  批量添加区块
  npx shadcn-ui-blocks preset <preset-name>   添加预设组合
  npx shadcn-ui-blocks list                   列出所有可用区块
  npx shadcn-ui-blocks help                   显示帮助信息

可用区块:
  Hero:        hero-centered, hero-split, hero-gradient
  Features:    features-grid, features-icons
  Pricing:     pricing-cards, pricing-table
  CTA:         cta-simple, cta-image
  Dashboard:   dashboard-header, dashboard-stats
  Testimonials: testimonials-cards
  Footer:      footer-simple, footer-multi

预设组合:
  landing      完整着陆页 (Hero + Features + Pricing + CTA + Footer)
  dashboard    仪表板页面 (Header + Stats + Charts)
  marketing    营销页面 (Hero + Features + Testimonials + CTA)
  pricing      定价页面 (Hero + Pricing + Footer)

示例:
  npx shadcn-ui-blocks add hero-centered
  npx shadcn-ui-blocks add hero features pricing
  npx shadcn-ui-blocks preset landing
`);
}

function addBlocks(blockNames) {
  const urls = [];
  const notFound = [];

  for (const name of blockNames) {
    if (BLOCKS_REGISTRY[name]) {
      urls.push(BLOCKS_REGISTRY[name]);
    } else {
      notFound.push(name);
    }
  }

  if (notFound.length > 0) {
    console.error(`❌ 未找到区块: ${notFound.join(', ')}`);
    console.log('运行 "npx shadcn-ui-blocks list" 查看所有可用区块');
    process.exit(1);
  }

  console.log(`📦 正在添加 ${urls.length} 个区块...`);

  try {
    const cmd = `npx shadcn@latest add ${urls.join(' ')}`;
    console.log(`执行: ${cmd}`);
    execSync(cmd, { stdio: 'inherit' });
    console.log(`✅ 成功添加 ${urls.length} 个区块`);
  } catch (error) {
    console.error('❌ 添加区块失败:', error.message);
    process.exit(1);
  }
}

function addPreset(presetName) {
  if (!PRESETS[presetName]) {
    console.error(`❌ 未找到预设: ${presetName}`);
    console.log('可用预设:', Object.keys(PRESETS).join(', '));
    process.exit(1);
  }

  const blocks = PRESETS[presetName];
  console.log(`🎨 添加预设 "${presetName}" (${blocks.length} 个区块)...`);
  addBlocks(blocks);
}

function listBlocks() {
  console.log('\n📋 可用区块列表:\n');

  const categories = {
    Hero: ['hero-centered', 'hero-split', 'hero-gradient'],
    Features: ['features-grid', 'features-icons'],
    Pricing: ['pricing-cards', 'pricing-table'],
    CTA: ['cta-simple', 'cta-image'],
    Dashboard: ['dashboard-header', 'dashboard-stats'],
    Testimonials: ['testimonials-cards'],
    Footer: ['footer-simple', 'footer-multi'],
  };

  for (const [category, blocks] of Object.entries(categories)) {
    console.log(`  ${category}:`);
    for (const block of blocks) {
      console.log(`    - ${block}`);
    }
  }

  console.log('\n📦 预设组合:\n');
  for (const [name, blocks] of Object.entries(PRESETS)) {
    console.log(`  ${name}: ${blocks.join(', ')}`);
  }
  console.log('');
}

// 主程序
const args = process.argv.slice(2);

if (args.length === 0 || args[0] === 'help') {
  printUsage();
  process.exit(0);
}

const command = args[0];

switch (command) {
  case 'add':
    if (args.length < 2) {
      console.error('❌ 请指定要添加的区块名称');
      console.log('用法: npx shadcn-ui-blocks add <block-name>');
      process.exit(1);
    }
    addBlocks(args.slice(1));
    break;

  case 'preset':
    if (args.length < 2) {
      console.error('❌ 请指定预设名称');
      console.log('可用预设:', Object.keys(PRESETS).join(', '));
      process.exit(1);
    }
    addPreset(args[1]);
    break;

  case 'list':
    listBlocks();
    break;

  default:
    console.error(`❌ 未知命令: ${command}`);
    printUsage();
    process.exit(1);
}