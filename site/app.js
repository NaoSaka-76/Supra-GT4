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
    car:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 16.5V12l1.8-5A2 2 0 017.7 5.5h8.6a2 2 0 011.9 1.5l1.8 5v4.5"/><path d="M4 16.5h16"/><path d="M4 16.5v2.3a1 1 0 001 1h1.2a1 1 0 001-1v-2.3"/><path d="M16.8 16.5v2.3a1 1 0 001 1H19a1 1 0 001-1v-2.3"/><circle cx="7.5" cy="13.2" r="1.1" fill="currentColor" stroke="none"/><circle cx="16.5" cy="13.2" r="1.1" fill="currentColor" stroke="none"/></svg>',
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

  function buildSeriesGroup(title, items) {
    var group = el("div", "series-card__group");
    group.appendChild(el("div", "series-card__group-title", title));
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

  function buildScheduleBlock(s) {
    var wrap = el("div", "series-card__group");
    wrap.appendChild(el("div", "series-card__group-title", "レース日程"));

    if (s.schedule_link) {
      wrap.appendChild(
        el(
          "p",
          "panel__note series-card__chart-note",
          "日程データの構造が不安定なため一覧化を見送っています。公式カレンダーは以下のリンクからご確認ください。"
        )
      );
      var link = el("a", "series-card__link", "公式カレンダーを見る ↗");
      link.href = s.schedule_link;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      wrap.appendChild(link);
      return wrap;
    }

    var rounds = s.schedule || [];
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

  function buildRankingBlock(s) {
    var wrap = el("div", "series-card__group");
    wrap.appendChild(el("div", "series-card__group-title", "シリーズランキング"));
    if (s.standings_chart && s.standings_chart.length > 0) {
      wrap.appendChild(buildStandingsChart(s.standings_chart));
    }
    if (s.standings_chart_note) {
      wrap.appendChild(el("p", "panel__note series-card__chart-note", s.standings_chart_note));
    }
    return wrap;
  }

  function buildSeriesCard(regionKey, s) {
    var card = el("div", "series-card series-card--" + regionKey);
    var header = el("div", "series-card__header");
    header.appendChild(el("span", null, s.label));
    card.appendChild(header);
    card.appendChild(buildScheduleBlock(s));
    card.appendChild(buildRankingBlock(s));
    card.appendChild(buildSeriesGroup(REGION_GROUP_LABELS.topics, s.topics));
    card.appendChild(buildSeriesGroup(REGION_GROUP_LABELS.results, s.results));
    card.appendChild(buildSeriesGroup(REGION_GROUP_LABELS.standings, s.standings));

    var link = el("a", "series-card__link", "公式ランキングを見る ↗");
    link.href = s.standings_url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    card.appendChild(link);

    return card;
  }

  function buildMotorsportsPanel(icon, section) {
    var panel = el("section", "panel panel--full");
    var regions = section.regions || {};
    var totalCount = Object.values(regions).reduce(function (sum, r) {
      return (
        sum +
        r.series.reduce(function (s2, series) {
          return s2 + series.topics.length + series.results.length + series.standings.length;
        }, 0)
      );
    }, 0);
    panel.appendChild(buildPanelHeader(icon, section.label, totalCount));
    if (section.note) panel.appendChild(el("p", "panel__note", section.note));

    var container = el("div", "motorsports");
    Object.keys(regions).forEach(function (key) {
      var r = regions[key];
      var block = el("div", "motorsports-region");
      var heading = el("div", "motorsports-region__title");
      if (r.flag) heading.appendChild(el("span", "motorsports-region__flag", r.flag));
      heading.appendChild(el("span", null, r.label));
      heading.appendChild(el("span", "motorsports-region__count", r.series.length + " シリーズ"));
      block.appendChild(heading);

      var grid = el("div", "motorsports-region__grid");
      r.series.forEach(function (s) {
        grid.appendChild(buildSeriesCard(key, s));
      });
      block.appendChild(grid);

      container.appendChild(block);
    });
    panel.appendChild(container);
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
        r.series.forEach(function (series) {
          all = all.concat(series.topics, series.results, series.standings);
        });
      });
    }
    return all;
  }

  function buildStats(data) {
    statsEl.innerHTML = "";

    var sentimentItems = collectSentimentItems(data);
    var totalCount = sentimentItems.length;

    var youtubeCount = ["youtube_popular", "youtube_new"].reduce(function (sum, key) {
      return sum + ((data.sections[key] && data.sections[key].items) || []).length;
    }, 0);

    var motorsportsCount = 0;
    if (data.sections.motorsports && data.sections.motorsports.regions) {
      Object.values(data.sections.motorsports.regions).forEach(function (r) {
        r.series.forEach(function (series) {
          motorsportsCount += series.topics.length + series.results.length + series.standings.length;
        });
      });
    }

    // Tile 1: total
    var t1 = el("div", "stat-tile");
    t1.appendChild(el("div", "stat-tile__label", "本日の総情報件数"));
    var v1 = el("div", "stat-tile__value", String(totalCount));
    v1.appendChild(el("small", null, "件"));
    t1.appendChild(v1);
    statsEl.appendChild(t1);

    // Tile 3: youtube
    var t3 = el("div", "stat-tile");
    t3.appendChild(el("div", "stat-tile__label", "YouTube動画(Supra GT4・競合GT4)"));
    var v3 = el("div", "stat-tile__value", String(youtubeCount));
    v3.appendChild(el("small", null, "本"));
    t3.appendChild(v3);
    statsEl.appendChild(t3);

    // Tile 4: motorsports
    var t4 = el("div", "stat-tile");
    t4.appendChild(el("div", "stat-tile__label", "参戦レース関連話題(5地域・14シリーズ)"));
    var v4 = el("div", "stat-tile__value", String(motorsportsCount));
    v4.appendChild(el("small", null, "件"));
    t4.appendChild(v4);
    statsEl.appendChild(t4);
  }

  function buildCarCard(car) {
    var card = el("div", "car-card" + (car.is_supra ? " car-card--spotlight" : ""));

    var figure = el("div", "car-card__photo");
    var img = el("img");
    img.src = car.photo.src;
    img.alt = car.manufacturer + " " + car.model;
    img.loading = "lazy";
    figure.appendChild(img);
    if (car.is_supra) figure.appendChild(el("span", "supra-tag car-card__badge", "SUPRA GT4"));
    card.appendChild(figure);

    var body = el("div", "car-card__body");
    body.appendChild(el("span", "car-card__manufacturer", car.manufacturer));
    body.appendChild(el("h3", "car-card__model", car.model));
    body.appendChild(el("div", "car-card__price", car.price));

    var specList = el("dl", "car-card__specs");
    (car.specs || []).forEach(function (spec) {
      specList.appendChild(el("dt", null, spec.label));
      specList.appendChild(el("dd", null, spec.value));
    });
    body.appendChild(specList);

    var link = el("a", "series-card__link", "公式サイトを見る ↗");
    link.href = car.official_url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    body.appendChild(link);

    var credit = el("p", "car-card__credit");
    credit.appendChild(document.createTextNode("Photo: "));
    var creditLink = el("a", null, car.photo.credit + " (" + car.photo.license + ")");
    creditLink.href = car.photo.source_url;
    creditLink.target = "_blank";
    creditLink.rel = "noopener noreferrer";
    credit.appendChild(creditLink);
    credit.appendChild(document.createTextNode(", via Wikimedia Commons"));
    body.appendChild(credit);

    card.appendChild(body);
    return card;
  }

  function buildCarsPanel(carsData) {
    var panel = el("section", "panel panel--full");
    var cars = carsData.cars || [];
    panel.appendChild(buildPanelHeader("car", "GT4参戦車両一覧", cars.length));
    if (carsData.note) panel.appendChild(el("p", "panel__note", carsData.note));

    var grid = el("div", "car-grid");
    cars.forEach(function (car) {
      grid.appendChild(buildCarCard(car));
    });
    panel.appendChild(grid);
    return panel;
  }

  function render(data, carsData) {
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
      if (entry.key === "motorsports" && carsData) {
        board.appendChild(buildCarsPanel(carsData));
      }
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

  function fetchJson(path) {
    return fetch(path, { cache: "no-store" }).then(function (res) {
      if (!res.ok) throw new Error("HTTP " + res.status);
      return res.json();
    });
  }

  fetchJson("data/latest.json")
    .then(function (data) {
      fetchJson("data/gt4_cars.json")
        .then(function (carsData) {
          render(data, carsData);
        })
        .catch(function () {
          render(data, null);
        });
    })
    .catch(function (err) {
      renderError("ダッシュボードデータの読み込みに失敗しました(" + err.message + ")。");
    });
})();
