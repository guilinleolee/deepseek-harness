/**
 * Dragon Scraper - 天龙自建抓取系统核心引擎
 * 基于Crawlee构建的多平台数据采集系统
 */

import { PlaywrightCrawler, Dataset, KeyValueStore, RequestQueue } from 'crawlee';
import { chromium } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';

// 配置
interface ScraperConfig {
    concurrency: number;
    requestDelay: [number, number];
    timeout: number;
    retries: number;
    proxy?: {
        enabled: boolean;
        list: string[];
    };
    output: 'json' | 'csv' | 'quick';
}

// 默认配置
const defaultConfig: ScraperConfig = {
    concurrency: 3,
    requestDelay: [1000, 3000],
    timeout: 30000,
    retries: 3,
    output: 'json'
};

/**
 * 主爬虫类
 */
export class DragonScraper {
    private config: ScraperConfig;
    private results: any[] = [];

    constructor(config: Partial<ScraperConfig> = {}) {
        this.config = { ...defaultConfig, ...config };
    }

    /**
     * Instagram 用户抓取
     */
    async scrapeInstagram(username: string): Promise<any[]> {
        const crawler = new PlaywrightCrawler({
            maxConcurrency: this.config.concurrency,
            requestHandlerTimeoutSecs: this.config.timeout / 1000,

            async requestHandler({ page, request, enqueueLinks }) {
                console.log(`[Instagram] 正在抓取: ${request.url}`);

                // 等待页面加载
                await page.waitForSelector('article', { timeout: 10000 });

                // 提取用户信息
                const userInfo = await page.evaluate(() => {
                    const nameEl = document.querySelector('header h2');
                    const bioEl = document.querySelector('header span[dir="auto"]');
                    const statsEl = document.querySelectorAll('header ul li');

                    return {
                        username: nameEl?.textContent?.trim() || '',
                        bio: bioEl?.textContent?.trim() || '',
                        posts: statsEl[0]?.textContent?.replace(/[^\d]/g, '') || '0',
                        followers: statsEl[1]?.textContent?.replace(/[^\d]/g, '') || '0',
                        following: statsEl[2]?.textContent?.replace(/[^\d]/g, '') || '0'
                    };
                });

                // 提取帖子
                const posts = await page.evaluate(() => {
                    const postEls = document.querySelectorAll('article a[href*="/p/"]');
                    return Array.from(postEls).slice(0, 12).map(el => ({
                        url: (el as HTMLAnchorElement).href,
                        thumbnail: el.querySelector('img')?.src || ''
                    }));
                });

                const result = {
                    platform: 'instagram',
                    type: 'profile',
                    ...userInfo,
                    posts,
                    scrapedAt: new Date().toISOString()
                };

                await Dataset.push(result);
            }
        });

        await crawler.run([`https://www.instagram.com/${username}/`]);

        const dataset = await Dataset.getData();
        return dataset.items;
    }

    /**
     * TikTok 用户抓取
     */
    async scrapeTikTok(username: string): Promise<any[]> {
        const crawler = new PlaywrightCrawler({
            maxConcurrency: this.config.concurrency,

            async requestHandler({ page, request }) {
                console.log(`[TikTok] 正在抓取: ${request.url}`);

                await page.waitForSelector('[data-e2e="user-post-item"]', { timeout: 15000 });

                const userInfo = await page.evaluate(() => {
                    const avatarEl = document.querySelector('[data-e2e="user-avatar"]');
                    const statsEl = document.querySelectorAll('[data-e2e="followers-count"], [data-e2e="following-count"], [data-e2e="likes-count"]');

                    return {
                        username: window.location.pathname.split('/')[1],
                        avatar: avatarEl?.querySelector('img')?.src || '',
                        followers: statsEl[0]?.textContent || '0',
                        following: statsEl[1]?.textContent || '0',
                        likes: statsEl[2]?.textContent || '0'
                    };
                });

                const videos = await page.evaluate(() => {
                    const videoEls = document.querySelectorAll('[data-e2e="user-post-item"]');
                    return Array.from(videoEls).slice(0, 12).map(el => ({
                        url: (el.querySelector('a') as HTMLAnchorElement)?.href || '',
                        thumbnail: el.querySelector('img')?.src || '',
                        views: el.querySelector('[data-e2e="video-views"]')?.textContent || '0'
                    }));
                });

                const result = {
                    platform: 'tiktok',
                    type: 'profile',
                    ...userInfo,
                    videos,
                    scrapedAt: new Date().toISOString()
                };

                await Dataset.push(result);
            }
        });

        await crawler.run([`https://www.tiktok.com/@${username}`]);

        const dataset = await Dataset.getData();
        return dataset.items;
    }

    /**
     * YouTube 频道抓取
     */
    async scrapeYouTube(channelId: string): Promise<any[]> {
        const crawler = new PlaywrightCrawler({
            maxConcurrency: this.config.concurrency,

            async requestHandler({ page, request }) {
                console.log(`[YouTube] 正在抓取: ${request.url}`);

                await page.waitForSelector('#contents', { timeout: 15000 });

                const channelInfo = await page.evaluate(() => {
                    const nameEl = document.querySelector('#channel-name');
                    const descEl = document.querySelector('#description');
                    const subsEl = document.querySelector('#subscriber-count');

                    return {
                        name: nameEl?.textContent?.trim() || '',
                        description: descEl?.textContent?.trim() || '',
                        subscribers: subsEl?.textContent?.trim() || '0'
                    };
                });

                const videos = await page.evaluate(() => {
                    const videoEls = document.querySelectorAll('ytd-rich-item-renderer');
                    return Array.from(videoEls).slice(0, 20).map(el => {
                        const titleEl = el.querySelector('#video-title');
                        const viewsEl = el.querySelector('#metadata-line span:first-child');
                        const timeEl = el.querySelector('#metadata-line span:last-child');

                        return {
                            title: titleEl?.textContent?.trim() || '',
                            url: `https://www.youtube.com${titleEl?.getAttribute('href') || ''}`,
                            views: viewsEl?.textContent?.trim() || '0',
                            published: timeEl?.textContent?.trim() || '',
                            thumbnail: el.querySelector('img')?.src || ''
                        };
                    });
                });

                const result = {
                    platform: 'youtube',
                    type: 'channel',
                    ...channelInfo,
                    videos,
                    scrapedAt: new Date().toISOString()
                };

                await Dataset.push(result);
            }
        });

        await crawler.run([`https://www.youtube.com/${channelId}/videos`]);

        const dataset = await Dataset.getData();
        return dataset.items;
    }

    /**
     * Amazon 产品抓取
     */
    async scrapeAmazon(asin: string): Promise<any[]> {
        const crawler = new PlaywrightCrawler({
            maxConcurrency: 1, // Amazon 需要更低并发
            requestHandlerTimeoutSecs: 60000,

            async requestHandler({ page, request }) {
                console.log(`[Amazon] 正在抓取: ${request.url}`);

                await page.waitForSelector('#productTitle', { timeout: 20000 });

                const product = await page.evaluate(() => {
                    const titleEl = document.querySelector('#productTitle');
                    const priceEl = document.querySelector('.a-price .a-offscreen');
                    const ratingEl = document.querySelector('.a-icon-star-small');
                    const reviewsEl = document.querySelector('#acrCustomerReviewText');
                    const imageEl = document.querySelector('#landingImage');

                    // 获取特性
                    const features = Array.from(document.querySelectorAll('#feature-bullets li'))
                        .map(li => li.textContent?.trim())
                        .filter(Boolean);

                    return {
                        asin: window.location.pathname.split('/')[3] || '',
                        title: titleEl?.textContent?.trim() || '',
                        price: priceEl?.textContent?.trim() || '',
                        rating: ratingEl?.textContent?.trim() || '',
                        reviewCount: reviewsEl?.textContent?.replace(/[^\d]/g, '') || '0',
                        image: imageEl?.getAttribute('src') || '',
                        features,
                        url: window.location.href
                    };
                });

                const result = {
                    platform: 'amazon',
                    type: 'product',
                    ...product,
                    scrapedAt: new Date().toISOString()
                };

                await Dataset.push(result);
            }
        });

        await crawler.run([`https://www.amazon.com/dp/${asin}`]);

        const dataset = await Dataset.getData();
        return dataset.items;
    }

    /**
     * 通用网页抓取
     */
    async scrapeGeneric(url: string, selectors: Record<string, string>): Promise<any[]> {
        const crawler = new PlaywrightCrawler({
            maxConcurrency: this.config.concurrency,

            async requestHandler({ page, request }) {
                console.log(`[Generic] 正在抓取: ${request.url}`);

                await page.waitForLoadState('networkidle');

                const data: Record<string, any> = {
                    url: request.url,
                    scrapedAt: new Date().toISOString()
                };

                // 根据选择器提取数据
                for (const [key, selector] of Object.entries(selectors)) {
                    if (selector.includes('||')) {
                        // 多元素选择器
                        data[key] = await page.evaluate((sel) => {
                            return Array.from(document.querySelectorAll(sel))
                                .map(el => el.textContent?.trim())
                                .filter(Boolean);
                        }, selector.split('||')[0]);
                    } else {
                        // 单元素选择器
                        data[key] = await page.$eval(selector, el => el.textContent?.trim() || '').catch(() => '');
                    }
                }

                await Dataset.push(data);
            }
        });

        await crawler.run([url]);

        const dataset = await Dataset.getData();
        return dataset.items;
    }

    /**
     * 导出结果
     */
    async export(format: 'json' | 'csv' = 'json', filename?: string): Promise<string> {
        const dataset = await Dataset.getData();
        const items = dataset.items;

        if (format === 'json') {
            const outputPath = filename || `./scraper-output-${Date.now()}.json`;
            fs.writeFileSync(outputPath, JSON.stringify(items, null, 2));
            return outputPath;
        } else {
            const outputPath = filename || `./scraper-output-${Date.now()}.csv`;
            if (items.length === 0) return '';

            const headers = Object.keys(items[0]);
            const csvContent = [
                headers.join(','),
                ...items.map(item => headers.map(h => `"${String(item[h] || '').replace(/"/g, '""')}"`).join(','))
            ].join('\n');

            fs.writeFileSync(outputPath, csvContent);
            return outputPath;
        }
    }
}

// CLI 入口
if (require.main === module) {
    const args = process.argv.slice(2);
    const platform = args[0];
    const target = args[1];

    const scraper = new DragonScraper();

    (async () => {
        let results: any[] = [];

        switch (platform) {
            case 'instagram':
                results = await scraper.scrapeInstagram(target);
                break;
            case 'tiktok':
                results = await scraper.scrapeTikTok(target);
                break;
            case 'youtube':
                results = await scraper.scrapeYouTube(target);
                break;
            case 'amazon':
                results = await scraper.scrapeAmazon(target);
                break;
            default:
                console.log('用法: npx ts-node dragon-scraper.ts <platform> <target>');
                console.log('支持平台: instagram, tiktok, youtube, amazon');
                process.exit(1);
        }

        console.log(JSON.stringify(results, null, 2));
        await scraper.export('json');
    })();
}