/**
 * Treqna Website Code Injector (Head & Body Script Manager)
 * -------------------------------------------------------------
 * Use this file to easily insert tracking scripts, Google Analytics (GA4),
 * Google Tag Manager (GTM), Meta Pixel, Google Search Console verification tags,
 * or custom JavaScript code into the <head> or <body> of all pages automatically.
 */

(function () {
  // 1. Enter any Custom HTML / Script tags to insert into <head>
  const CUSTOM_HEAD_CODE = `
    <!-- Google Search Console Verification Tag Placeholder -->
    <!-- <meta name="google-site-verification" content="YOUR_VERIFICATION_CODE_HERE" /> -->

    <!-- Google Analytics (GA4) Placeholder -->
    <!--
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-XXXXXXXXXX');
    </script>
    -->
  `;

  // 2. Enter any Custom HTML / Script tags to insert into <body> (e.g., GTM noscript or tracking pixels)
  const CUSTOM_BODY_CODE = `
    <!-- Custom Body Code Placeholder -->
  `;

  // Automatic Safe Context Injection
  function injectCustomCode() {
    if (CUSTOM_HEAD_CODE && CUSTOM_HEAD_CODE.trim()) {
      try {
        const headFragment = document.createRange().createContextualFragment(CUSTOM_HEAD_CODE);
        document.head.appendChild(headFragment);
      } catch (err) {
        console.warn("Analytics Injection Note:", err.message);
      }
    }

    if (CUSTOM_BODY_CODE && CUSTOM_BODY_CODE.trim()) {
      try {
        const bodyFragment = document.createRange().createContextualFragment(CUSTOM_BODY_CODE);
        document.body.insertBefore(bodyFragment, document.body.firstChild);
      } catch (err) {
        console.warn("Body Script Injection Note:", err.message);
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectCustomCode);
  } else {
    injectCustomCode();
  }
})();
