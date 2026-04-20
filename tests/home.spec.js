const { test, expect } = require("@playwright/test");

test.describe("VoxCPM static site", () => {
  test("english homepage renders key content, metadata, and screenshots", async ({ page }, testInfo) => {
    await page.goto("/");

    const demoLink = page.locator('[data-cta="demo"]');
    const githubLink = page.locator('[data-cta="github"]');
    const docsLink = page.locator('[data-cta="docs"]');
    const topbarZhLink = page.locator("header.topbar").getByRole("link", { name: "中文" });

    await expect(page).toHaveTitle(/VoxCPM2/i);
    await expect(page.locator("body")).toHaveAttribute("data-page", "en");
    await expect(page.locator("h1")).toHaveText(/Tokenizer-free TTS/i);
    await expect(demoLink).toBeVisible();
    await expect(githubLink).toBeVisible();
    await expect(docsLink).toBeVisible();

    await expect(page.locator('meta[name="description"]')).toHaveAttribute("content", /tokenizer-free multilingual TTS/i);
    await expect(page.locator('link[rel="canonical"]')).toHaveAttribute("href", "https://voxcpm.space/");
    await expect(page.locator('link[rel="alternate"][hreflang="zh-CN"]')).toHaveAttribute("href", "https://voxcpm.space/zh/");

    await expect(demoLink).toHaveAttribute("href", "https://huggingface.co/spaces/OpenBMB/VoxCPM-Demo");
    await expect(githubLink).toHaveAttribute("href", "https://github.com/OpenBMB/VoxCPM");
    await expect(docsLink).toHaveAttribute("href", "https://voxcpm.readthedocs.io/en/latest/");

    await expect(topbarZhLink).toHaveAttribute("href", "/zh/");
    await expect(page.locator('link[rel="icon"][type="image/x-icon"]')).toHaveAttribute("href", "/assets/brand/favicon.ico");

    const logosLoaded = await page.evaluate(() =>
      Array.from(document.images).every((image) => image.complete && image.naturalWidth > 0)
    );
    expect(logosLoaded).toBe(true);

    await page.screenshot({ path: testInfo.outputPath("home-en.png"), fullPage: true });
  });

  test("chinese homepage renders, links back to english, and screenshots", async ({ page }, testInfo) => {
    await page.goto("/zh/");

    const demoLink = page.locator('[data-cta="demo"]');
    const githubLink = page.locator('[data-cta="github"]');
    const docsLink = page.locator('[data-cta="docs"]');
    const topbarEnLink = page.locator("header.topbar").getByRole("link", { name: "EN" });

    await expect(page).toHaveTitle(/VoxCPM2/);
    await expect(page.locator("body")).toHaveAttribute("data-page", "zh");
    await expect(page.locator("h1")).toHaveText(/无分词器 TTS/);
    await expect(demoLink).toBeVisible();
    await expect(githubLink).toBeVisible();
    await expect(docsLink).toBeVisible();
    await expect(page.locator('link[rel="canonical"]')).toHaveAttribute("href", "https://voxcpm.space/zh/");
    await expect(topbarEnLink).toHaveAttribute("href", "/");

    await page.screenshot({ path: testInfo.outputPath("home-zh.png"), fullPage: true });
  });

  test("mobile layout has no horizontal overflow and language switch works", async ({ browser }) => {
    const context = await browser.newContext({
      viewport: { width: 390, height: 844 },
      isMobile: true
    });
    const page = await context.newPage();

    await page.goto("/");
    await expect(page.locator('[data-cta="demo"]')).toBeVisible();
    await page.locator("header.topbar").getByRole("link", { name: "中文" }).click();
    await expect(page).toHaveURL(/\/zh\/$/);
    await expect(page.locator("h1")).toHaveText(/无分词器 TTS/);

    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    expect(overflow).toBeLessThanOrEqual(1);

    await context.close();
  });
});
