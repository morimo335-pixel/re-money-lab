import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
	// Load Markdown and MDX files in the `src/content/blog/` directory.
	loader: glob({ base: './src/content/blog', pattern: '**/*.{md,mdx}' }),
	// Type-check frontmatter using a schema
	schema: ({ image }) =>
		z.object({
			title: z.string(),
			description: z.string(),
			// Transform string to Date object
			pubDate: z.coerce.date(),
			updatedDate: z.coerce.date().optional(),
			heroImage: z.optional(image()),
			related: z.array(z.string()).optional(),  // 関連記事slug配列（サイドバー動的表示用）
			// true にすると検索エンジンのインデックスから外す（URL・内部リンクは生きたまま）
			// 用途＝表示が伸びない低品質記事をサイト評価から切り離す。戻す時はこの行を消すだけ
			noindex: z.boolean().optional(),
		}),
});

export const collections = { blog };
