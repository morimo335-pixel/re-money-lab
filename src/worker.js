// WP→Astro移管後の旧URL（?p=XXX形式）を新URLへ301転送するWorker
// 2026-05-11 設置（Phase D-1 未消化分の対処）

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

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const pId = url.searchParams.get('p');

    if (pId !== null) {
      const dest = WP_ID_TO_SLUG[pId];
      const target = dest
        ? `${url.origin}${dest}`
        : `${url.origin}/`;
      return Response.redirect(target, 301);
    }

    return env.ASSETS.fetch(request);
  },
};
