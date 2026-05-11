// WP→Astro移管後の旧URL対処Worker
// 2026-05-11 設置：Phase D-1未消化分（WP postID転送）
// 2026-05-11 拡張：WP固定ページ・サイトマップ・カテゴリ・管理画面の残骸対処

// WP postID形式（?p=XXX）→ 新slugマッピング
const WP_ID_TO_SLUG = {
  '215': '/ihinseiri-trouble/',
  '236': '/komehyo-umeda-kaitori/',
  '239': '/rikon-kekkonyubiwa/',
  '243': '/fukuchan-shucchou-kaitori/',
  '249': '/kin-kaitori-chuiten/',
  '264': '/kitte-sheet-kaitori/',
  '274': '/kegawa-coat-jidai-okure/',
  '280': '/film-camera-boom-shuryou/',
  '289': '/tetsubin-mikiwakekata/',
  '351': '/shokki-shobun/',
  '363': '/furui-record-shobun/',
  '373': '/furui-osake-ureru/',
};

// WP時代のパス → 新サイトの該当パス（301転送）
const PATH_REDIRECTS = {
  // 固定ページ
  '/profile/': '/about/',
  '/profile': '/about/',
  '/privacy-policy-2/': '/privacy-policy/',
  '/privacy-policy-2': '/privacy-policy/',
  // WP自動生成サイトマップ群 → Astroサイトマップへ
  '/sitemap.html': '/sitemap-index.xml',
  '/sitemap.xml': '/sitemap-index.xml',
  '/page-sitemap.xml': '/sitemap-index.xml',
  '/post-sitemap.xml': '/sitemap-index.xml',
  '/category-sitemap.xml': '/sitemap-index.xml',
  '/tag-sitemap.xml': '/sitemap-index.xml',
  // カテゴリーアーカイブ → 記事一覧へ
  '/category/basics/': '/blog/',
  '/category/uncategorized/': '/blog/',
};

// 完全廃止パス（410 Gone：Googleに「永久に消えた」と通知）
const GONE_PATHS = new Set([
  '/comments/feed/',
  '/comments/feed',
  '/feed/',
  '/feed',
]);

// 410 Gone正規表現パターン（WP管理画面・コンテンツディレクトリ）
const GONE_PATTERNS = [
  /^\/wp-admin(\/|$)/,
  /^\/wp-content(\/|$)/,
  /^\/wp-includes(\/|$)/,
  /^\/wp-login\.php/,
  /^\/xmlrpc\.php/,
];

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // 1. WP postIDクエリ（?p=XXX）の処理
    const pId = url.searchParams.get('p');
    if (pId !== null) {
      const dest = WP_ID_TO_SLUG[pId];
      const target = dest
        ? `${url.origin}${dest}`
        : `${url.origin}/`;
      return Response.redirect(target, 301);
    }

    // 2. 410 Gone：完全廃止パス（リスト）
    if (GONE_PATHS.has(url.pathname)) {
      return new Response('Gone', { status: 410 });
    }

    // 3. 410 Gone：WP管理画面系（正規表現）
    if (GONE_PATTERNS.some((pattern) => pattern.test(url.pathname))) {
      return new Response('Gone', { status: 410 });
    }

    // 4. パスベース301転送
    const pathRedirect = PATH_REDIRECTS[url.pathname];
    if (pathRedirect) {
      return Response.redirect(`${url.origin}${pathRedirect}`, 301);
    }

    // 5. 通常リクエストは静的アセットへ
    return env.ASSETS.fetch(request);
  },
};
