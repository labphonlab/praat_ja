// app.js — GitHub Releases API から最新版を取得しリンクを差し替える。
// 言語は <body data-lang="ja|en"> から判別し、文言を切り替える。
(function () {
  const FRONTEND_REPO = "labphonlab/praat_ja";
  const PRAAT_REPO = "praat/praat.github.io";
  const FRONTEND_API = `https://api.github.com/repos/${FRONTEND_REPO}/releases/latest`;
  const PRAAT_API = `https://api.github.com/repos/${PRAAT_REPO}/releases/latest`;

  const lang = (document.body && document.body.dataset && document.body.dataset.lang) || "ja";

  const T = {
    ja: {
      detectedMac: "🍎 macOS を検出しました。下のmacOS版がおすすめです。",
      detectedWin: "🪟 Windows を検出しました。下のWindows版がおすすめです。",
      detectedLinux: "🐧 Linux を検出しました。ソースから実行してください。",
      btnMac: "macOS版をダウンロード",
      btnWin: "Windows版をダウンロード",
      dlMacFmt: (s) => `macOS版 (${s}) をダウンロード`,
      dlWinFmt: (s) => `Windows版 (${s}) をダウンロード`,
      verUnknown: "（取得できませんでした）",
      verFetchFail: "（取得できませんでした — リリースページから直接ダウンロードしてください）",
    },
    en: {
      detectedMac: "🍎 macOS detected. The macOS download below is recommended.",
      detectedWin: "🪟 Windows detected. The Windows download below is recommended.",
      detectedLinux: "🐧 Linux detected. Please run from source.",
      btnMac: "Download for macOS",
      btnWin: "Download for Windows",
      dlMacFmt: (s) => `Download for macOS (${s})`,
      dlWinFmt: (s) => `Download for Windows (${s})`,
      verUnknown: "(unavailable)",
      verFetchFail: "(could not fetch — please download directly from the Release page)",
    },
  };
  const t = T[lang] || T.ja;

  const versionEl = document.getElementById("latest-version");
  const praatVersionEl = document.getElementById("latest-praat-version");
  const releasePageLink = document.getElementById("release-page-link");
  const dlMacEl = document.getElementById("dl-mac");
  const dlWinEl = document.getElementById("dl-win");
  const primaryEl = document.getElementById("primary-download");
  const detectedOsEl = document.getElementById("detected-os");
  const cardMac = document.getElementById("card-mac");
  const cardWin = document.getElementById("card-win");

  // -------- OS自動判定 --------
  const ua = navigator.userAgent;
  const platform = (navigator.userAgentData && navigator.userAgentData.platform) || navigator.platform || "";
  let detected = "unknown";
  if (/Mac/i.test(platform) || /Mac OS X/i.test(ua)) {
    detected = "mac";
  } else if (/Win/i.test(platform) || /Windows/i.test(ua)) {
    detected = "win";
  } else if (/Linux/i.test(platform) || /Linux/i.test(ua)) {
    detected = "linux";
  }

  if (detectedOsEl) {
    if (detected === "mac") {
      detectedOsEl.textContent = t.detectedMac;
      if (cardMac) cardMac.classList.add("highlight");
      if (primaryEl) primaryEl.textContent = t.btnMac;
    } else if (detected === "win") {
      detectedOsEl.textContent = t.detectedWin;
      if (cardWin) cardWin.classList.add("highlight");
      if (primaryEl) primaryEl.textContent = t.btnWin;
    } else if (detected === "linux") {
      detectedOsEl.textContent = t.detectedLinux;
    }
  }

  // -------- フロントエンド最新リリースの取得 --------
  fetch(FRONTEND_API, { headers: { Accept: "application/vnd.github+json" } })
    .then((r) => {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then((release) => {
      const tag = release.tag_name || "";
      if (versionEl) versionEl.textContent = tag || t.verUnknown;
      if (releasePageLink && release.html_url) releasePageLink.href = release.html_url;

      const assets = Array.isArray(release.assets) ? release.assets : [];
      const macAsset = assets.find((a) => /\.dmg$/i.test(a.name));
      const winAsset = assets.find((a) => /\.exe$/i.test(a.name));

      if (macAsset && dlMacEl) {
        dlMacEl.href = macAsset.browser_download_url;
        dlMacEl.setAttribute("download", macAsset.name);
        dlMacEl.textContent = t.dlMacFmt(formatSize(macAsset.size));
      }
      if (winAsset && dlWinEl) {
        dlWinEl.href = winAsset.browser_download_url;
        dlWinEl.setAttribute("download", winAsset.name);
        dlWinEl.textContent = t.dlWinFmt(formatSize(winAsset.size));
      }

      if (primaryEl) {
        if (detected === "mac" && macAsset) {
          primaryEl.href = macAsset.browser_download_url;
          primaryEl.setAttribute("download", macAsset.name);
        } else if (detected === "win" && winAsset) {
          primaryEl.href = winAsset.browser_download_url;
          primaryEl.setAttribute("download", winAsset.name);
        } else {
          primaryEl.href = "#download";
        }
      }
    })
    .catch(() => {
      if (versionEl) versionEl.textContent = t.verFetchFail;
    });

  // -------- Praat 本体最新版の取得 --------
  if (praatVersionEl) {
    fetch(PRAAT_API, { headers: { Accept: "application/vnd.github+json" } })
      .then((r) => {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then((release) => {
        praatVersionEl.textContent = release.tag_name || release.name || t.verUnknown;
      })
      .catch(() => {
        praatVersionEl.textContent = t.verUnknown;
      });
  }

  // -------- 言語選択を localStorage に記録 --------
  try {
    localStorage.setItem("praatja_lang", lang);
  } catch (_) {}
  document.querySelectorAll(".lang-btn").forEach((el) => {
    el.addEventListener("click", () => {
      try {
        const href = el.getAttribute("href") || "";
        if (href.indexOf("/ja/") >= 0) localStorage.setItem("praatja_lang", "ja");
        else if (href.indexOf("/en/") >= 0) localStorage.setItem("praatja_lang", "en");
      } catch (_) {}
    });
  });

  function formatSize(bytes) {
    if (bytes == null) return "";
    const mb = bytes / (1024 * 1024);
    return mb >= 1 ? mb.toFixed(1) + " MB" : (bytes / 1024).toFixed(0) + " KB";
  }
})();
