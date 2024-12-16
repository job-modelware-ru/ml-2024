let scale_colors = {
  "-1": "#76ff7a",
  0: "#fefe22",
  1: "#ff496c",
};

let featureList = document.getElementById("features");

chrome.tabs.query({ currentWindow: true, active: true }, function (tabs) {
  chrome.storage.local.get(
    ["results", "trustRate", "isPhish"],
    function (items) {
      let result = items.results[tabs[0].id];
      let trustRate = items.trustRate[tabs[0].id];
      let isPhish = items.isPhish[tabs[0].id];

      for (let featName in result) {
        let feature = document.createElement("li");
        feature.className = "feature";
        feature.textContent = featName;
        feature.style.backgroundColor = scale_colors[result[featName]];
        featureList.appendChild(feature);
      }

      $("#score").text("Уровень доверия: " + parseInt(trustRate) + "%");
      if (isPhish) {
        $("#result_message").text(
          "Осторожно, возможно вы попали на фишинговый сайт"
        );
        $("#score").text(
          "Уровень доверия: " + (parseInt(trustRate) - 20) + "%"
        );
      }
    }
  );
});
