// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import { readFileSync } from 'node:fs';
import { basename, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { satteri } from '@astrojs/markdown-satteri';
import { tableColumnLabels } from './src/lib/tableColumnLabels.mjs';

const projectDir = dirname(fileURLToPath(import.meta.url));
const ports = JSON.parse(readFileSync(resolve(projectDir, '../dev-ports.json'), 'utf-8'));

// 端口统一维护在上级目录 dev-ports.json，键为项目目录名；0 表示自动选空闲端口
export default defineConfig({
  server: {
    port: ports[basename(projectDir)] ?? 0,
  },
  // 线上 himd.com 对齐：内容页是 /osimertinib 这种无尾斜杠的根级路径
  trailingSlash: 'never',
  markdown: {
    // Astro 7 默认用 Sätteri 处理 Markdown，插件要挂在 processor 上而不是 rehypePlugins
    processor: satteri({ hastPlugins: [tableColumnLabels] }),
  },
  build: {
    format: 'file',
  },
  vite: {
    plugins: [tailwindcss()],
  },
});
