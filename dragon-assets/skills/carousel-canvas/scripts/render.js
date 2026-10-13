/**
 * Carousel Canvas Renderer
 * 零成本本地渲染社交媒体轮播图
 *
 * 依赖: npm install canvas
 */

const { createCanvas, loadImage } = require('canvas');
const fs = require('fs');
const path = require('path');

/**
 * Canvas Carousel 渲染器
 */
class CarouselRenderer {
    /**
     * @param {Object} config - 渲染配置
     * @param {number} config.width - 画布宽度
     * @param {number} config.height - 画布高度
     * @param {string} config.background - 默认背景色
     * @param {number} config.quality - 输出质量 (0-1)
     */
    constructor(config = {}) {
        this.width = config.width || 1080;
        this.height = config.height || 1920;
        this.background = config.background || '#FFFFFF';
        this.quality = config.quality || 0.95;
        this.fontDirectory = config.fontDirectory || __dirname;
    }

    /**
     * 渲染单个幻灯片
     * @param {Object} slide - 幻灯片数据
     * @returns {Promise<Buffer>} PNG Buffer
     */
    async renderSlide(slide) {
        const canvas = createCanvas(this.width, this.height);
        const ctx = canvas.getContext('2d');

        // 1. 渲染背景
        await this.renderBackground(ctx, slide.background);

        // 2. 渲染图片层
        if (slide.image) {
            await this.renderImage(ctx, slide.image, slide.imagePosition);
        }

        // 3. 渲染图片网格
        if (slide.images && Array.isArray(slide.images)) {
            await this.renderImageGrid(ctx, slide.images, slide.gridConfig);
        }

        // 4. 渲染文字
        this.renderText(ctx, slide.texts);

        // 5. 渲染装饰元素
        if (slide.decorations) {
            this.renderDecorations(ctx, slide.decorations);
        }

        // 6. 导出
        return canvas.toBuffer('image/png', { quality: this.quality });
    }

    /**
     * 批量渲染幻灯片
     * @param {Array} slides - 幻灯片数组
     * @param {Object} options - 批量选项
     * @returns {Promise<Array>} Buffer 数组
     */
    async renderBatch(slides, options = {}) {
        const concurrency = options.concurrency || 4;
        const results = [];

        // 分块处理
        for (let i = 0; i < slides.length; i += concurrency) {
            const chunk = slides.slice(i, i + concurrency);
            const chunkResults = await Promise.all(
                chunk.map(slide => this.renderSlide(slide).catch(e => {
                    console.error(`渲染失败: ${e.message}`);
                    return null;
                }))
            );
            results.push(...chunkResults);
        }

        return results;
    }

    /**
     * 渲染背景
     */
    async renderBackground(ctx, background) {
        if (!background) {
            ctx.fillStyle = this.background;
            ctx.fillRect(0, 0, this.width, this.height);
            return;
        }

        switch (background.type) {
            case 'solid':
                ctx.fillStyle = background.color;
                ctx.fillRect(0, 0, this.width, this.height);
                break;

            case 'gradient':
                const gradient = ctx.createLinearGradient(
                    background.start?.x || 0, background.start?.y || 0,
                    background.end?.x || this.width, background.end?.y || this.height
                );
                background.colors.forEach((color, i) => {
                    gradient.addColorStop(i / Math.max(background.colors.length - 1, 1), color);
                });
                ctx.fillStyle = gradient;
                ctx.fillRect(0, 0, this.width, this.height);
                break;

            case 'radial':
                const radial = ctx.createRadialGradient(
                    background.center?.x || this.width / 2,
                    background.center?.y || this.height / 2,
                    0,
                    background.center?.x || this.width / 2,
                    background.center?.y || this.height / 2,
                    background.radius || Math.max(this.width, this.height) / 2
                );
                background.colors.forEach((color, i) => {
                    radial.addColorStop(i / Math.max(background.colors.length - 1, 1), color);
                });
                ctx.fillStyle = radial;
                ctx.fillRect(0, 0, this.width, this.height);
                break;

            case 'image':
                try {
                    const img = await loadImage(background.url);
                    ctx.drawImage(img, 0, 0, this.width, this.height);
                    if (background.overlay) {
                        ctx.fillStyle = background.overlay;
                        ctx.fillRect(0, 0, this.width, this.height);
                    }
                } catch (e) {
                    console.warn(`背景图片加载失败: ${background.url}`);
                    ctx.fillStyle = background.fallback || this.background;
                    ctx.fillRect(0, 0, this.width, this.height);
                }
                break;
        }
    }

    /**
     * 渲染单张图片
     */
    async renderImage(ctx, image, position = {}) {
        try {
            const img = await loadImage(image.url);
            const x = position.x ?? 0;
            const y = position.y ?? 0;
            const w = position.width ?? this.width;
            const h = position.height ?? this.height;

            // 保存上下文
            ctx.save();

            // 圆角裁剪
            if (position.cornerRadius) {
                this.roundRect(ctx, x, y, w, h, position.cornerRadius);
                ctx.clip();
            }

            // 应用滤镜
            if (image.filter) {
                ctx.filter = this.getCSSFilter(image.filter);
            }

            ctx.drawImage(img, x, y, w, h);
            ctx.restore();
        } catch (e) {
            console.warn(`图片加载失败: ${image.url}`);
        }
    }

    /**
     * 渲染图片网格
     */
    async renderImageGrid(ctx, images, config = {}) {
        const cols = config.columns || 2;
        const rows = config.rows || 2;
        const gap = config.gap || 10;
        const padding = config.padding || 20;

        const cellWidth = (this.width - padding * 2 - gap * (cols - 1)) / cols;
        const cellHeight = (this.height - padding * 2 - gap * (rows - 1)) / rows;

        for (let i = 0; i < images.length; i++) {
            const col = i % cols;
            const row = Math.floor(i / cols);
            const x = padding + col * (cellWidth + gap);
            const y = padding + row * (cellHeight + gap);

            await this.renderImage(ctx, images[i], { x, y, width: cellWidth, height: cellHeight });
        }
    }

    /**
     * 渲染文字
     */
    renderText(ctx, texts) {
        if (!texts) return;

        const processTextItem = (text) => {
            ctx.save();

            // 字体设置
            const fontWeight = text.weight || 'normal';
            const fontSize = text.size || 48;
            const fontFamily = text.font || 'Arial';
            ctx.font = `${fontWeight} ${fontSize}px ${fontFamily}`;
            ctx.fillStyle = text.color || '#000000';
            ctx.textAlign = text.align || 'center';
            ctx.textBaseline = text.baseline || 'middle';

            // 文字描边
            if (text.stroke) {
                ctx.strokeStyle = text.stroke.color;
                ctx.lineWidth = text.stroke.width;
                ctx.strokeText(text.content, text.x, text.y);
            }

            // 文字阴影
            if (text.shadow) {
                ctx.shadowColor = text.shadow.color;
                ctx.shadowBlur = text.shadow.blur || 0;
                ctx.shadowOffsetX = text.shadow.offsetX || 0;
                ctx.shadowOffsetY = text.shadow.offsetY || 0;
            }

            // 渐变文字
            if (text.gradient) {
                const gradient = ctx.createLinearGradient(
                    text.gradient.start?.x || text.x - 100,
                    text.gradient.start?.y || text.y,
                    text.gradient.end?.x || text.x + 100,
                    text.gradient.end?.y || text.y
                );
                text.gradient.colors.forEach((color, i) => {
                    gradient.addColorStop(i / Math.max(text.gradient.colors.length - 1, 1), color);
                });
                ctx.fillStyle = gradient;
            }

            // 多行文字
            if (text.lines) {
                text.lines.forEach((line, index) => {
                    const lineY = text.y + index * (fontSize * (text.lineHeight || 1.2));
                    ctx.fillText(line, text.x, lineY);
                });
            } else if (text.maxWidth) {
                // 自动换行
                const lines = this.wrapText(ctx, text.content, text.maxWidth);
                lines.forEach((line, index) => {
                    const lineY = text.y + index * (fontSize * (text.lineHeight || 1.2));
                    ctx.fillText(line, text.x, lineY);
                });
            } else {
                ctx.fillText(text.content, text.x, text.y);
            }

            ctx.restore();
        };

        if (Array.isArray(texts)) {
            texts.forEach(processTextItem);
        } else {
            processTextItem(texts);
        }
    }

    /**
     * 渲染装饰元素
     */
    renderDecorations(ctx, decorations) {
        if (!decorations) return;

        const processDecoration = (dec) => {
            ctx.save();

            switch (dec.type) {
                case 'line':
                    ctx.beginPath();
                    ctx.moveTo(dec.start.x, dec.start.y);
                    ctx.lineTo(dec.end.x, dec.end.y);
                    ctx.strokeStyle = dec.color || '#000';
                    ctx.lineWidth = dec.width || 1;
                    if (dec.lineCap) ctx.lineCap = dec.lineCap;
                    ctx.stroke();
                    break;

                case 'circle':
                    ctx.beginPath();
                    ctx.arc(dec.x, dec.y, dec.radius, 0, Math.PI * 2);
                    if (dec.fill) {
                        ctx.fillStyle = dec.fill;
                        ctx.fill();
                    }
                    if (dec.stroke) {
                        ctx.strokeStyle = dec.stroke.color;
                        ctx.lineWidth = dec.stroke.width;
                        ctx.stroke();
                    }
                    break;

                case 'rect':
                    if (dec.cornerRadius) {
                        this.roundRect(ctx, dec.x, dec.y, dec.width, dec.height, dec.cornerRadius);
                    } else {
                        ctx.beginPath();
                        ctx.rect(dec.x, dec.y, dec.width, dec.height);
                    }
                    if (dec.fill) {
                        ctx.fillStyle = dec.fill;
                        ctx.fill();
                    }
                    if (dec.stroke) {
                        ctx.strokeStyle = dec.stroke.color;
                        ctx.lineWidth = dec.stroke.width;
                        ctx.stroke();
                    }
                    break;

                case 'emoji':
                    ctx.font = `${dec.size || 48}px Arial`;
                    ctx.fillText(dec.emoji, dec.x, dec.y);
                    break;

                case 'polygon':
                    ctx.beginPath();
                    if (Array.isArray(dec.points) && dec.points.length > 0) {
                        ctx.moveTo(dec.points[0].x, dec.points[0].y);
                        dec.points.slice(1).forEach(p => ctx.lineTo(p.x, p.y));
                        ctx.closePath();
                    }
                    if (dec.fill) {
                        ctx.fillStyle = dec.fill;
                        ctx.fill();
                    }
                    if (dec.stroke) {
                        ctx.strokeStyle = dec.stroke.color;
                        ctx.lineWidth = dec.stroke.width;
                        ctx.stroke();
                    }
                    break;
            }

            ctx.restore();
        };

        if (Array.isArray(decorations)) {
            decorations.forEach(processDecoration);
        } else {
            processDecoration(decorations);
        }
    }

    /**
     * 圆角矩形
     */
    roundRect(ctx, x, y, w, h, r) {
        ctx.beginPath();
        ctx.moveTo(x + r, y);
        ctx.lineTo(x + w - r, y);
        ctx.quadraticCurveTo(x + w, y, x + w, y + r);
        ctx.lineTo(x + w, y + h - r);
        ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
        ctx.lineTo(x + r, y + h);
        ctx.quadraticCurveTo(x, y + h, x, y + h - r);
        ctx.lineTo(x, y + r);
        ctx.quadraticCurveTo(x, y, x + r, y);
        ctx.closePath();
    }

    /**
     * 文字换行
     */
    wrapText(ctx, text, maxWidth) {
        const words = text.split(' ');
        const lines = [];
        let currentLine = '';

        words.forEach(word => {
            const testLine = currentLine ? `${currentLine} ${word}` : word;
            const metrics = ctx.measureText(testLine);

            if (metrics.width > maxWidth && currentLine) {
                lines.push(currentLine);
                currentLine = word;
            } else {
                currentLine = testLine;
            }
        });

        if (currentLine) {
            lines.push(currentLine);
        }

        return lines;
    }

    /**
     * CSS 滤镜转 Canvas 滤镜
     */
    getCSSFilter(filter) {
        const filters = [];
        if (filter.brightness) filters.push(`brightness(${filter.brightness})`);
        if (filter.contrast) filters.push(`contrast(${filter.contrast})`);
        if (filter.saturate) filters.push(`saturate(${filter.saturate})`);
        if (filter.blur) filters.push(`blur(${filter.blur}px)`);
        if (filter.grayscale) filters.push(`grayscale(${filter.grayscale})`);
        if (filter.sepia) filters.push(`sepia(${filter.sepia})`);
        if (filter.hueRotate) filters.push(`hue-rotate(${filter.hueRotate}deg)`);
        return filters.join(' ');
    }
}

module.exports = CarouselRenderer;
