// WP→Astro移管後の旧URL対処Worker
// 2026-05-11 設置（Phase D-1 未消化分の対処）
// 2026-05-11 拡張（WP固定ページ残骸・コメントRSS残骸の追加対処）

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
  '/profile/': '/about/',
  '/profile': '/about/',
  '/sitemap.html': '/sitemap-index.xml',
  '/privacy-policy-2/': '/privacy-policy/',
  '/privacy-policy-2': '/privacy-policy/',
};

// 完全に廃止したパス（410 Gone：「永久に消えた」をGoogleに通知）
const GONE_PATHS = new Set([
  '/comments/feed/',
  '/comments/feed',
  '/feed/',
  '/feed',
]);

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

    // 2. 410 Gone：完全廃止パス
    if (GONE_PATHS.has(url.pathname)) {
      return new Response('Gone', { status: 410 });
    }

    // 3. パスベース301転送（profile→about等）
    const pathRedirect = PATH_REDIRECTS[url.pathname];
    if (pathRedirect) {
      return Response.redirect(`${url.origin}${pathRedirect}`, 301);
    }

    // 4. 通常リクエストは静的アセットへ
    return env.ASSETS.fetch(request);
  },
};
