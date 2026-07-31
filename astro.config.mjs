// @ts-check

import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import { defineConfig, fontProviders } from 'astro/config';

// https://astro.build/config
export default defineConfig({
	site: 'https://re-money-lab.com',
	// noindex 記事はサイトマップからも除外する（載せると「出すな」と「見に来い」で矛盾する）
	// ここを更新したら、対象記事の frontmatter の noindex: true とセットで管理すること
	integrations: [
		mdx(),
		sitemap({
			filter: (page) =>
				![
					'kimono-uru-osusume',
					'kimono-kaitori-koukai',
					'haha-no-kimono-shobun',
					'furisode-shobun',
					'ihinseiri-osaka-souba',
					'ihinseiri-kyoto-souba',
					'ihinseiri-kobe-souba',
					'sell-unwanted-items',
					'brand-fuku-takaku-uru-kotsu',
					'oya-kataduke-kyohi-setsutoku',
					'ihinseiri-gyousha-hikaku',
					'kangakki-uru-doko',
					'brand-fuku-uru-doko',
					'oya-shisetsu-nyuuyo-checklist',
					'piano-kaitori-tokyo',
					'breitling-kaitori-osusume',
					'oya-rojinhome-zaiakukan',
					'jikka-jimai-kanto-deguchi',
					'shucchou-kaitori-yobu-mae',
					'jikka-seiri-shucchou-kaitori',
					'jikka-seiri-kyodai-momeru',
					'zoutouhin-kaitori-tokyo',
					'brand-shucchou-kaitori',
					'kyoukasho-kaitori-osusume',
					'iwc-kaitori-osusume',
				].some((slug) => page === `https://re-money-lab.com/${slug}/`),
		}),
	],
	fonts: [
		{
			provider: fontProviders.local(),
			name: 'Atkinson',
			cssVariable: '--font-atkinson',
			fallbacks: ['sans-serif'],
			options: {
				variants: [
					{
						src: ['./src/assets/fonts/atkinson-regular.woff'],
						weight: 400,
						style: 'normal',
						display: 'swap',
					},
					{
						src: ['./src/assets/fonts/atkinson-bold.woff'],
						weight: 700,
						style: 'normal',
						display: 'swap',
					},
				],
			},
		},
	],
});
