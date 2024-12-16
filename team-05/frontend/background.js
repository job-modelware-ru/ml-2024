var results = {};
var trustRate = {};
var isPhish = {};

async function fetchLive() {
  try {
    const response = await fetch("static/classifier.json", {
      method: "GET",
    });

    if (!response.ok) {
      throw new Error("Неудачный ответ от сервера");
    }

    const data = await response.json();
    await new Promise((resolve) =>
      chrome.storage.local.set({ cache: data, cacheTime: Date.now() }, resolve)
    );
    return data;
  } catch (error) {
    console.error("Не удалось получить данные:", error);
    throw error;
  }
}

async function fetchCLF() {
  const items = await new Promise((resolve) =>
    chrome.storage.local.get(["cache", "cacheTime"], resolve)
  );

  if (items.cache && items.cacheTime) {
    return items.cache;
  }

  return fetchLive();
}

async function classify(tabId, result) {
  let safe = (suspicious = danger = 0);

  for (let key in result) {
    if (result[key] === "1") danger++;
    else if (result[key] === "0") suspicious++;
    else safe++;
  }

  trustRate[tabId] = (safe / (danger + suspicious + safe)) * 100;

  if (result.length !== 0) {
    let X = [];
    X[0] = [];
    for (let key in result) {
      X[0].push(parseInt(result[key]));
    }

    const classifier = await fetchCLF();
    const forest = random_forest(classifier);
    const y = forest.predict(X);

    isPhish[tabId] = y[0][0] ? true : false;

    chrome.storage.local.set({
      results: results,
      trustRate: trustRate,
      isPhish: isPhish,
    });

    if (isPhish[tabId]) {
      chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        chrome.tabs.sendMessage(tabs[0].id, { action: "alert_user" });
      });
    }
  }
}

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  results[sender.tab.id] = request;
  classify(sender.tab.id, request);
  sendResponse({ received: "result" });
});
