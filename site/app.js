(function () {
  "use strict";

  var ICONS = {
    flag:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 3v18"/><path d="M5 4h14l-3 3.5 3 3.5H5z"/></svg>',
    gear:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 13a1.7 1.7 0 000-2l1.4-1.2-2-3.4-1.8.6a1.7 1.7 0 00-1.7-1L15 4h-6l-.3 1.9a1.7 1.7 0 00-1.7 1l-1.8-.6-2 3.4L4.6 11a1.7 1.7 0 000 2l-1.4 1.2 2 3.4 1.8-.6a1.7 1.7 0 001.7 1L9 20h6l.3-1.9a1.7 1.7 0 001.7-1l1.8.6 2-3.4z"/></svg>',
    play:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M10 8.5l6 3.5-6 3.5z" fill="currentColor" stroke="none"/></svg>',
    chat:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h16v11H8l-4 4z"/></svg>',
    alert:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4l9.5 16H2.5z"/><line x1="12" y1="10" x2="12" y2="14.5"/><circle cx="12" cy="17.3" r="0.9" fill="currentColor" stroke="none"/></svg>',
  };

  var LAYOUT = [
    { key: "motorsports", size: "full", icon: "flag" },
    { key: "gt4_topics", size: "full", icon: "gear" },
    { key: "youtube_popular", size: "half", icon: "play" },
    { key: "youtube_new", size: "half", icon: "play" },
    { key: "social_buzz", size: "full", icon: "chat" },
    { key: "complaints", size: "full", icon: "alert" },
  ];

  var SENTIMENT_LABEL_JA = { positive: "ポジティブ", negative: "ネガティブ", neutral: "中立" };
  var REGION_GROUP_LABELS = { topics: "トピックス", results: "最新レース結果", standings: "ランキング関連ニュース" };

  var board = document.getElementById("board");
  var statsEl = document.getElementById("stats");
  var lastUpdatedEl = document.getElementById("last-updated");
  var statusDot = document.getElementById("status-dot");

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function formatPublished(raw) {
    if (!raw) return "";
    var parsed = new Date(raw);
    if (!isNaN(parsed.getTime()) && /\d{4}/.test(raw)) {
      return parsed.toLocaleString("ja-JP", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    }
    return raw;
  }

  function sentimentPill(sentiment) {
    if (!sentiment || sentiment.label === "neutral") return null;
    var pill = el(
      "span",
      "sentiment-pill sentiment-pill--" + sentiment.label,
      sentiment.label === "positive" ? "▲ " + SENTIMENT_LABEL_JA.positive : "▼ " + SENTIMENT_LABEL_JA.negative
    );
    var reasons = sentiment.reasons || [];
    if (reasons.length > 0) {
      var tip =
        "判定根拠: " +
        reasons.join(" / ") +
        (sentiment.label === "positive" ? " という語がポジティブ" : " という語がネガティブ") +
        "と判定されました";
      pill.setAttribute("data-tip", tip);
      pill.tabIndex = 0;
    }
    return pill;
  }

  function buildItem(item) {
    var sentimentLabel = item.sentiment ? item.sentiment.label : "neutral";
    var a = el("a", "item item--" + sentimentLabel);
    a.href = item.url || "#";
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    if (!item.url) {
      a.removeAttribute("href");
      a.style.cursor = "default";
    }

    if (item.thumbnail) {
      var img = el("img", "item__thumb");
      img.src = item.thumbnail;
      img.alt = "";
      img.loading = "lazy";
      a.appendChild(img);
    }

    var body = el("div", "item__body");
    body.appendChild(el("span", "item__title", item.title || "(タイトル不明)"));

    var meta = el("div", "item__meta");
    if (item.category_label) {
      meta.appendChild(el("span", "topic-chip topic-chip--" + item.category, item.category_label));
    }
    var pill = sentimentPill(item.sentiment);
    if (pill) meta.appendChild(pill);
    if (item.source) meta.appendChild(el("span", null, item.source));
    var published = formatPublished(item.published);
    if (published) meta.appendChild(el("span", null, published));
    if (item.view_count_text) {
      meta.appendChild(el("span", "item__metric", item.view_count_text));
    }
    body.appendChild(meta);
    a.appendChild(body);

    return a;
  }

  function buildList(items) {
    var list = el("ul", "panel__list");
    items.forEach(function (item) {
      var li = el("li");
      li.appendChild(buildItem(item));
      list.appendChild(li);
    });
    return list;
  }

  function buildPanelHeader(icon, label, count) {
    var header = el("div", "panel__header");
    var iconWrap = el("div", "panel__icon");
    iconWrap.innerHTML = ICONS[icon] || "";
    header.appendChild(iconWrap);
    header.appendChild(el("h2", "panel__title", label));
    if (count !== undefined) header.appendChild(el("span", "panel__count", count + " 件"));
    return header;
  }

  function buildGenericPanel(icon, section, size) {
    var panel = el("section", "panel panel--" + size);
    var items = section.items || [];
    panel.appendChild(buildPanelHeader(icon, section.label, items.length));

    if (section.note) panel.appendChild(el("p", "panel__note", section.note));

    if (items.length === 0) {
      panel.appendChild(el("p", "panel__empty", "現在、該当する情報はありません。"));
      return panel;
    }
    panel.appendChild(buildList(items));
    return panel;
  }

  function buildTabbedPanel(icon, section, tabLabels) {
    var panel = el("section", "panel panel--full");
    var latestItems = section.items || [];
    var buzzItems = section.items_buzz || [];
    panel.appendChild(buildPanelHeader(icon, section.label, latestItems.length));
    if (section.note) panel.appendChild(el("p", "panel__note", section.note));

    var tabs = el("div", "tab-group");
    var tabLatest = el("button", "tab-group__btn is-active", tabLabels[0]);
    var tabBuzz = el("button", "tab-group__btn", tabLabels[1]);
    tabs.appendChild(tabLatest);
    tabs.appendChild(tabBuzz);
    panel.appendChild(tabs);

    var listWrap = el("div");
    function renderList(items) {
      listWrap.innerHTML = "";
      if (items.length === 0) {
        listWrap.appendChild(el("p", "panel__empty", "現在、該当する情報はありません。"));
      } else {
        listWrap.appendChild(buildList(items));
      }
    }
    renderList(latestItems);
    panel.appendChild(listWrap);

    tabLatest.addEventListener("click", function () {
      tabLatest.classList.add("is-active");
      tabBuzz.classList.remove("is-active");
      renderList(latestItems);
    });
    tabBuzz.addEventListener("click", function () {
      tabBuzz.classList.add("is-active");
      tabLatest.classList.remove("is-active");
      renderList(buzzItems);
    });

    return panel;
  }

  function buildRegionGroup(title, items) {
    var group = el("div", "region-card__group");
    group.appendChild(el("div", "region-card__group-title", title));
    if (items.length === 0) {
      group.appendChild(el("p", "panel__empty", "該当情報なし"));
    } else {
      group.appendChild(buildList(items));
    }
    return group;
  }

  function buildStandingsChart(rows) {
    var maxPoints = rows.reduce(function (m, r) { return Math.max(m, r.points); }, 1);
    var chart = el("div", "standings-chart");
    rows.forEach(function (row) {
      var rowEl = el("div", "standings-chart__row" + (row.is_supra_gt4 ? " standings-chart__row--spotlight" : ""));
      rowEl.appendChild(el("span", "standings-chart__pos", String(row.position)));

      var main = el("div", "standings-chart__main");
      var nameLine = el("div", "standings-chart__name-line");
      nameLine.appendChild(el("span", "standings-chart__name", row.name));
      if (row.is_supra_gt4) {
        nameLine.appendChild(el("span", "supra-tag", "GR SUPRA GT4"));
      }
      main.appendChild(nameLine);

      if (row.car) {
        main.appendChild(el("span", "standings-chart__sub", row.car));
      }

      var track = el("div", "standings-chart__track");
      var fill = el("div", "standings-chart__fill");
      fill.style.width = Math.max(4, (100 * row.points) / maxPoints) + "%";
      track.appendChild(fill);
      main.appendChild(track);

      rowEl.appendChild(main);
      rowEl.appendChild(el("span", "standings-chart__points", String(row.points)));
      chart.appendChild(rowEl);
    });
    return chart;
  }

  function buildScheduleBlock(r) {
    var wrap = el("div", "region-card__group");
    wrap.appendChild(el("div", "region-card__group-title", "レース日程"));

    if (r.schedule_link) {
      wrap.appendChild(
        el(
          "p",
          "panel__note region-card__chart-note",
          "日程データの構造が不安定なため一覧化を見送っています。公式カレンダーは以下のリンクからご確認ください。"
        )
      );
      var link = el("a", "region-card__link", "公式カレンダーを見る ↗");
      link.href = r.schedule_link;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      wrap.appendChild(link);
      return wrap;
    }

    var rounds = r.schedule || [];
    if (rounds.length === 0) {
      wrap.appendChild(el("p", "panel__empty", "日程情報を取得できませんでした。"));
      return wrap;
    }

    var nextRace = rounds.filter(function (round) { return round.status === "upcoming"; })[0];
    if (nextRace) {
      var next = el("div", "schedule-next");
      next.appendChild(el("span", "schedule-next__label", "次戦"));
      next.appendChild(el("span", "schedule-next__date", nextRace.date_range));
      next.appendChild(
        el("span", "schedule-next__track", [nextRace.round, nextRace.name, nextRace.track].filter(Boolean).join(" · "))
      );
      wrap.appendChild(next);
    }

    var list = el("ul", "schedule-list");
    rounds.forEach(function (r2) {
      var li = el("li", "schedule-list__item schedule-list__item--" + r2.status);
      li.appendChild(el("span", "schedule-list__dot"));
      li.appendChild(el("span", "schedule-list__date", r2.date_range));
      li.appendChild(el("span", "schedule-list__label", [r2.round, r2.name, r2.track].filter(Boolean).join(" · ")));
      list.appendChild(li);
    });
    wrap.appendChild(list);

    return wrap;
  }

  function buildRankingBlock(r) {
    var wrap = el("div", "region-card__group");
    wrap.appendChild(el("div", "region-card__group-title", "シリーズランキング"));
    if (r.standings_chart && r.standings_chart.length > 0) {
      wrap.appendChild(buildStandingsChart(r.standings_chart));
    }
    if (r.standings_chart_note) {
      wrap.appendChild(el("p", "panel__note region-card__chart-note", r.standings_chart_note));
    }
    return wrap;
  }

  function buildMotorsportsPanel(icon, section) {
    var panel = el("section", "panel panel--full");
    var regionCount = Object.values(section.regions || {}).reduce(function (sum, r) {
      return sum + r.topics.length + r.results.length + r.standings.length;
    }, 0);
    panel.appendChild(buildPanelHeader(icon, section.label, regionCount));
    if (section.note) panel.appendChild(el("p", "panel__note", section.note));

    var grid = el("div", "motorsports");
    Object.keys(section.regions || {}).forEach(function (key) {
      var r = section.regions[key];
      var card = el("div", "region-card region-card--" + key);
      var header = el("div", "region-card__header");
      if (r.flag) header.appendChild(el("span", "region-card__flag", r.flag));
      header.appendChild(el("span", null, r.label));
      card.appendChild(header);
      card.appendChild(buildScheduleBlock(r));
      card.appendChild(buildRankingBlock(r));
      card.appendChild(buildRegionGroup(REGION_GROUP_LABELS.topics, r.topics));
      card.appendChild(buildRegionGroup(REGION_GROUP_LABELS.results, r.results));
      card.appendChild(buildRegionGroup(REGION_GROUP_LABELS.standings, r.standings));

      var link = el("a", "region-card__link", "公式ランキングを見る ↗");
      link.href = r.standings_url || r.standings_search_url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      card.appendChild(link);

      grid.appendChild(card);
    });
    panel.appendChild(grid);
    return panel;
  }

  function collectSentimentItems(data) {
    var all = [];
    ["youtube_popular", "youtube_new", "social_buzz", "complaints", "gt4_topics"].forEach(function (key) {
      var section = data.sections[key];
      if (section && section.items) all = all.concat(section.items);
    });
    var ms = data.sections.motorsports;
    if (ms && ms.regions) {
      Object.values(ms.regions).forEach(function (r) {
        all = all.concat(r.topics, r.results, r.standings);
      });
    }
    return all;
  }

  function buildStats(data) {
    statsEl.innerHTML = "";

    var sentimentItems = collectSentimentItems(data);
    var totalCount = sentimentItems.length;

    var counts = { positive: 0, neutral: 0, negative: 0 };
    sentimentItems.forEach(function (item) {
      var label = item.sentiment ? item.sentiment.label : "neutral";
      counts[label] = (counts[label] || 0) + 1;
    });

    var youtubeCount = ["youtube_popular", "youtube_new"].reduce(function (sum, key) {
      return sum + ((data.sections[key] && data.sections[key].items) || []).length;
    }, 0);

    var motorsportsCount = 0;
    if (data.sections.motorsports && data.sections.motorsports.regions) {
      Object.values(data.sections.motorsports.regions).forEach(function (r) {
        motorsportsCount += r.topics.length + r.results.length + r.standings.length;
      });
    }

    // Tile 1: total
    var t1 = el("div", "stat-tile");
    t1.appendChild(el("div", "stat-tile__label", "本日の総情報件数"));
    var v1 = el("div", "stat-tile__value", String(totalCount));
    v1.appendChild(el("small", null, "件"));
    t1.appendChild(v1);
    statsEl.appendChild(t1);

    // Tile 2: sentiment breakdown
    var t2 = el("div", "stat-tile");
    t2.appendChild(el("div", "stat-tile__label", "評判"));
    var v2 = el("div", "stat-tile__value", String(counts.positive));
    v2.appendChild(el("small", null, "件ポジティブ"));
    t2.appendChild(v2);
    var total = counts.positive + counts.neutral + counts.negative || 1;
    var bar = el("div", "sentiment-bar");
    bar.appendChild(el("div", "sentiment-bar__seg sentiment-bar__seg--positive")).style.width = (100 * counts.positive / total) + "%";
    bar.appendChild(el("div", "sentiment-bar__seg sentiment-bar__seg--neutral")).style.width = (100 * counts.neutral / total) + "%";
    bar.appendChild(el("div", "sentiment-bar__seg sentiment-bar__seg--negative")).style.width = (100 * counts.negative / total) + "%";
    t2.appendChild(bar);
    var legend = el("div", "sentiment-legend");
    var lp = el("span"); lp.appendChild(el("span", "legend-dot legend-dot--positive")); lp.appendChild(document.createTextNode(counts.positive + ""));
    var ln = el("span"); ln.appendChild(el("span", "legend-dot legend-dot--neutral")); ln.appendChild(document.createTextNode(counts.neutral + ""));
    var lg = el("span"); lg.appendChild(el("span", "legend-dot legend-dot--negative")); lg.appendChild(document.createTextNode(counts.negative + ""));
    legend.appendChild(lp); legend.appendChild(ln); legend.appendChild(lg);
    t2.appendChild(legend);
    statsEl.appendChild(t2);

    // Tile 3: youtube
    var t3 = el("div", "stat-tile");
    t3.appendChild(el("div", "stat-tile__label", "YouTube動画(Supra GT4・競合GT4)"));
    var v3 = el("div", "stat-tile__value", String(youtubeCount));
    v3.appendChild(el("small", null, "本"));
    t3.appendChild(v3);
    statsEl.appendChild(t3);

    // Tile 4: motorsports
    var t4 = el("div", "stat-tile");
    t4.appendChild(el("div", "stat-tile__label", "参戦レース関連話題(4地域)"));
    var v4 = el("div", "stat-tile__value", String(motorsportsCount));
    v4.appendChild(el("small", null, "件"));
    t4.appendChild(v4);
    statsEl.appendChild(t4);
  }

  function render(data) {
    buildStats(data);

    board.innerHTML = "";
    LAYOUT.forEach(function (entry) {
      var section = data.sections && data.sections[entry.key];
      if (!section) return;
      var panel;
      if (entry.key === "motorsports") {
        panel = buildMotorsportsPanel(entry.icon, section);
      } else if (entry.key === "complaints") {
        panel = buildTabbedPanel(entry.icon, section, ["最新順", "話題順"]);
      } else if (entry.key === "social_buzz") {
        panel = buildTabbedPanel(entry.icon, section, ["最新順", "話題順"]);
      } else {
        panel = buildGenericPanel(entry.icon, section, entry.size);
      }
      board.appendChild(panel);
    });

    lastUpdatedEl.textContent = "最終更新: " + (data.generated_at_jst || "不明");

    var generatedAt = data.generated_at_utc ? new Date(data.generated_at_utc) : null;
    if (generatedAt) {
      var hoursSince = (Date.now() - generatedAt.getTime()) / 36e5;
      statusDot.classList.toggle("is-stale", hoursSince > 8);
    }
  }

  function renderError(message) {
    statsEl.innerHTML = "";
    board.innerHTML = "";
    board.appendChild(el("p", "board__error", message));
    lastUpdatedEl.textContent = "更新情報を取得できませんでした";
    statusDot.classList.add("is-error");
  }

  fetch("data/latest.json", { cache: "no-store" })
    .then(function (res) {
      if (!res.ok) throw new Error("HTTP " + res.status);
      return res.json();
    })
    .then(render)
    .catch(function (err) {
      renderError("ダッシュボードデータの読み込みに失敗しました(" + err.message + ")。");
    });
})();
