#!/usr/bin/env node
/**
 * Carousel Canvas Generator
 * 轮播图批量生成工具
 *
 * 用法:
 *   node generate.js --config <json_file>
 *   node generate.js --title "标题" --slides <json_array> --platform <douyin|xiaohongshu>
 */

const fs = require('fs');
const path = require('path');
const CarouselRenderer = require('./render.js');

// 平台尺寸配置
const PLATFORM_SIZES = {
    douyin: { width: 1080, height: 1920, name: '抖音/TikTok' },
    xiaohongshu: { width: 1080, height: 1440, name: '小红书' },
    instagram: { width: 1080, height: 1080, name: 'Instagram' },
    wechat: { width: 900, height: 383, name: '微信公众号' }
};

// 预设模板
const TEMPLATES = {
    cover_gradient: {
        background: {
            type: 'gradient',
            start: { x: 0, y: 0 },
            end: { x: 1080, y: 1920 },
            colors: ['#667eea', '#764ba2']
        },
        texts: [
            {
                content: '{{title}}',
                x: 540,
                y: 800,
                size: 80,
                color: '#FFFFFF',
                font: 'Arial',
                weight: 'bold',
                align: 'center',
                shadow: { color: 'rgba(0,0,0,0.3)', blur: 10, offsetX: 2, offsetY: 2 }
            },
            {
                content: '{{subtitle}}',
                x: 540,
                y: 1000,
                size: 36,
                color: 'rgba(255,255,255,0.8)',
                align: 'center'
            }
        ]
    },

    cover_image: {
        background: {
            type: 'solid',
            color: '#1A1A1A'
        },
        image: {
            url: '{{bg_image}}',
            filter: { brightness: 0.6 }
        },
        imagePosition: { x: 0, y: 0, width: 1080, height: 1920 },
        texts: [
            {
                content: '{{title}}',
                x: 540,
                y: 1400,
                size: 72,
                color: '#FFFFFF',
                weight: 'bold',
                align: 'center'
            }
        ]
    },

    content_centered: {
        background: { type: 'solid', color: '#FFFFFF' },
        texts: [
            {
                content: '{{heading}}',
                x: 540,
                y: 400,
                size: 56,
                color: '#1A1A1A',
                weight: 'bold',
                align: 'center'
            },
            {
                content: '{{body}}',
                x: 540,
                y: 600,
                size: 32,
                color: '#666666',
                align: 'center',
                maxWidth: 800
            }
        ]
    },

    content_with_image: {
        background: { type: 'solid', color: '#F8FAFC' },
        image: { url: '{{content_image}}' },
        imagePosition: { x: 40, y: 400, width: 1000, height: 700 },
        texts: [
            {
                content: '{{heading}}',
                x: 540,
                y: 1200,
                size: 48,
                color: '#1A1A1A',
                weight: 'bold',
                align: 'center'
            },
            {
                content: '{{body}}',
                x: 540,
                y: 1350,
                size: 28,
                color: '#666666',
                align: 'center',
                maxWidth: 900
            }
        ]
    },

    ending_cta: {
        background: { type: 'solid', color: '#1A1A1A' },
        texts: [
            {
                content: '{{cta_title}}',
                x: 540,
                y: 600,
                size: 64,
                color: '#FFFFFF',
                weight: 'bold',
                align: 'center'
            },
            {
                content: '{{cta_subtitle}}',
                x: 540,
                y: 750,
                size: 36,
                color: 'rgba(255,255,255,0.7)',
                align: 'center'
            }
        ],
        decorations: [
            { type: 'rect', x: 340, y: 950, width: 400, height: 100, fill: '#00D4AA', cornerRadius: 50 },
            { type: 'text', content: '{{cta_action}}', x: 540, y: 1000, size: 36, color: '#FFFFFF', weight: 'bold', align: 'center' },
            { type: 'text', content: '{{handle}}', x: 540, y: 1700, size: 28, color: 'rgba(255,255,255,0.5)', align: 'center' }
        ]
    }
};

/**
 * 从配置生成轮播图
 */
async function generateCarousel(config) {
    const {
        title,
        subtitle = '',
        slides = [],
        cta = {},
        template = 'cover_gradient',
        platform = 'douyin',
        output = './output',
        format = 'png',
        prefix = ''
    } = config;

    // 平台尺寸
    const size = PLATFORM_SIZES[platform] || PLATFORM_SIZES.douyin;

    // 创建渲染器
    const renderer = new CarouselRenderer({
        width: size.width,
        height: size.height,
        quality: 0.95
    });

    // 确保输出目录存在
    fs.mkdirSync(output, { recursive: true });

    const results = [];
    const pad = (n) => String(n).padStart(2, '0');

    // 1. 生成封面
    console.log('🎨 生成封面...');
    const coverData = buildSlide(TEMPLATES[template] || TEMPLATES.cover_gradient, {
        title,
        subtitle,
        bg_image: config.bg_image
    });
    const coverBuffer = await renderer.renderSlide(coverData);
    const coverPath = path.join(output, `${prefix}01-cover.${format}`);
    fs.writeFileSync(coverPath, coverBuffer);
    results.push({ type: 'cover', path: coverPath });
    console.log(`  ✅ 已保存: ${coverPath}`);

    // 2. 生成内容页
    for (let i = 0; i < slides.length; i++) {
        const slide = slides[i];
        const templateKey = slide.template || 'content_centered';
        console.log(`🎨 生成内容页 ${i + 1}...`);

        const slideData = buildSlide(TEMPLATES[templateKey] || TEMPLATES.content_centered, {
            ...slide,
            index: i + 1
        });
        const buffer = await renderer.renderSlide(slideData);
        const slidePath = path.join(output, `${prefix}${pad(i + 2)}-content.${format}`);
        fs.writeFileSync(slidePath, buffer);
        results.push({ type: `content-${i + 1}`, path: slidePath });
        console.log(`  ✅ 已保存: ${slidePath}`);
    }

    // 3. 生成结尾 CTA
    if (Object.keys(cta).length > 0 || slides.length > 0) {
        console.log('🎨 生成结尾页...');
        const endingData = buildSlide(TEMPLATES.ending_cta, {
            cta_title: cta.title || title,
            cta_subtitle: cta.subtitle || subtitle,
            cta_action: cta.action || '点击关注',
            handle: cta.handle || config.handle || '@youraccount'
        });
        const endingBuffer = await renderer.renderSlide(endingData);
        const endingPath = path.join(output, `${prefix}${pad(slides.length + 2)}-ending.${format}`);
        fs.writeFileSync(endingPath, endingBuffer);
        results.push({ type: 'ending', path: endingPath });
        console.log(`  ✅ 已保存: ${endingPath}`);
    }

    // 4. 生成 ZIP (可选)
    if (config.zip) {
        const archiver = require('archiver');
        const zipPath = path.join(output, `${prefix}carousel.zip`);

        await new Promise((resolve, reject) => {
            const outputStream = fs.createWriteStream(zipPath);
            const archive = archiver('zip');

            outputStream.on('close', () => {
                console.log(`📦 已打包: ${zipPath}`);
                results.push({ type: 'zip', path: zipPath });
                resolve();
            });

            archive.on('error', reject);
            archive.pipe(outputStream);

            results.forEach(r => {
                if (r.type !== 'zip' && fs.existsSync(r.path)) {
                    archive.file(r.path, { name: path.basename(r.path) });
                }
            });

            archive.finalize();
        });
    }

    return results;
}

/**
 * 构建幻灯片数据
 */
function buildSlide(template, data) {
    // 深拷贝
    const slide = JSON.parse(JSON.stringify(template);

    // 替换占位符
    const content = JSON.stringify(slide).replace(/\{\{(\w+)\}\}/g, (match, key) => {
        return data[key] !== undefined ? String(data[key]) : match;
    });

    return JSON.parse(content);
}

/**
 * 批量生成
 */
async function batchGenerate(configPath, outputDir) {
    console.log(`📂 读取配置: ${configPath}`);
    const configs = JSON.parse(fs.readFileSync(configPath, 'utf8'));

    if (!Array.isArray(configs)) {
        return generateCarousel({ ...configs, output: outputDir });
    }

    const allResults = [];
    for (const config of configs) {
        console.log(`\n${'='.repeat(50)}`);
        console.log(`📝 生成轮播图: ${config.title}`);
        console.log('='.repeat(50));

        const results = await generateCarousel({
            ...config,
            output: outputDir || config.output || './output'
        });
        allResults.push(...results);
    }

    return allResults;
}

// CLI 入口
if (require.main === module) {
    const args = process.argv.slice(2);

    const options = {
        config: null,
        output: './output',
        platform: 'douyin'
    };

    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--config' || args[i] === '-c') {
            options.config = args[++i];
        } else if (args[i] === '--output' || args[i] === '-o') {
            options.output = args[++i];
        } else if (args[i] === '--platform' || args[i] === '-p') {
            options.platform = args[++i];
        } else if (args[i] === '--help' || args[i] === '-h') {
            console.log(`
Carousel Canvas Generator

用法:
  node generate.js --config <json_file> [--output <dir>]
  node generate.js --title "标题" --slides '<json_array>'

示例:
  # 从配置文件生成
  node generate.js --config carousel.json --output ./output

  # 从命令行参数生成
  node generate.js --title "我的标题" --platform douyin

配置文件格式 (carousel.json):
  {
    "title": "主标题",
    "subtitle": "副标题",
    "slides": [
      { "heading": "标题", "body": "内容", "template": "content_centered" }
    ],
    "cta": { "title": "CTA标题", "action": "立即行动" },
    "platform": "douyin",
    "output": "./output"
  }
            `);
            process.exit(0);
        }
    }

    if (!options.config) {
        console.error('❌ 请提供 --config 参数');
        process.exit(1);
    }

    const startTime = Date.now();

    batchGenerate(options.config, options.output)
        .then(results => {
            const duration = ((Date.now() - startTime) / 1000).toFixed(2);
            console.log(`\n🎉 完成! 生成 ${results.length} 张幻灯片 (${duration}s)`);
        })
        .catch(err => {
            console.error('❌ 生成失败:', err);
            process.exit(1);
        });
}

module.exports = { generateCarousel, buildSlide, TEMPLATES, PLATFORM_SIZES };
