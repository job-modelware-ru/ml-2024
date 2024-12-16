//Пробегаем по различным признакам

//итоговая структура для результатов по всем признакам
let result = {};
//1. IP-адрес в URL:
//наличие IP-адреса в URL страницы обычно является признаком фишинга
let url = window.location.href;
let urlDomain = window.location.hostname;

let pattern_ip = /(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[0-9]?[0-9])(\.|$){4}/;
let pattern_ip2 = /(0x([0-9][0-9]|[A-F][A-F]|[A-F][0-9]|[0-9][A-F]))(\.|$){4}/;
let ip = /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/;

if (
  ip.test(urlDomain) ||
  pattern_ip.test(urlDomain) ||
  pattern_ip2.test(urlDomain)
) {
  result["IP-адрес в URL"] = "1";
} else {
  result["IP-адрес в URL"] = "-1";
}

//2. Очень длинный URL:
//использование очень длинного URL обычно является попыткой скрыть подозрительную часть

if (url.length < 54) {
  result["Длинный URL"] = "-1";
} else if (url.length >= 54 && url.length <= 75) {
  result["Длинный URL"] = "0";
} else {
  result["Длинный URL"] = "1";
}

//3. TinyURL:
//производная от прошлого признака - чтобы обойти второй признак, может использоваться сокращение URL с помощью TinyURL

let onlyDomain = urlDomain.replace("www.", "");

if (onlyDomain.length < 7) {
  result["TinyURL"] = "1";
} else {
  result["TinyURL"] = "-1";
}

//4. @ в URL:
//Использование символа «@» в URL приводит к тому, что браузер игнорирует все, что предшествует символу «@», и реальный фишинговый адрес следует за символом «@»

patt = /@/;
if (patt.test(url)) {
  result["@ в URL"] = "1";
} else {
  result["@ в URL"] = "-1";
}

//5. Перенаправление с помощью "//":
//Наличие «//» в пути URL означает, что пользователь будет перенаправлен на другой сайт.
//Если в URL используется «HTTPS», то «//» должно появиться последний раз в седьмом индексе.

if (url.lastIndexOf("//") > 7) {
  result["Перенаправление через //"] = "1";
} else {
  result["Перенаправление через //"] = "-1";
}

//6. Добавление к домену префикса или суффикса, разделенных знаком (-)
//Дефис почти не используется в легальных URL-адресах. Фишеры обычно добавляют префиксы или суффиксы, разделенные дефисом к доменному имени, чтобы пользователи чувствовали, что имеют дело с безопасной веб-страницей.

patt = /-/;
if (patt.test(urlDomain)) {
  result["Префикс или суффикс в домене"] = "1";
} else {
  result["Префикс или суффикс в домене"] = "-1";
}

//7. Большое количество доменов
//Большое количество доменов, разделенных точками, может сигнализировать о возможности фишинга

if ((onlyDomain.match(RegExp("\\.", "g")) || []).length == 1) {
  result["Много субдоменов"] = "-1";
} else if ((onlyDomain.match(RegExp("\\.", "g")) || []).length == 2) {
  result["Много субдоменов"] = "0";
} else {
  result["Много субдоменов"] = "1";
}

//8. HTTPS
//Если вебсайт использует протокол HTTPS, то с очень большой вероятностью он безопасен

patt = /https:\/\//;
if (patt.test(url)) {
  result["HTTPS"] = "-1";
} else {
  result["HTTPS"] = "1";
}

//9. FavIcon - графическое изображение (иконка), связанное с определенной веб-страницей
//Если FavIcon загружается с домена, отличного от того, который отображается в адресной строке, то веб-страница, скорее всего, будет считаться попыткой фишинга.

let favicon = undefined;
let nodeList = document.getElementsByTagName("link");
for (let i = 0; i < nodeList.length; i++) {
  if (
    nodeList[i].getAttribute("rel") == "icon" ||
    nodeList[i].getAttribute("rel") == "shortcut icon"
  ) {
    favicon = nodeList[i].getAttribute("href");
  }
}
if (!favicon) {
  result["FavIcon"] = "-1";
} else if (favicon.length == 12) {
  result["FavIcon"] = "-1";
} else {
  patt = RegExp(urlDomain, "g");
  if (patt.test(favicon)) {
    result["FavIcon"] = "-1";
  } else {
    result["FavIcon"] = "1";
  }
}

//10. Использование HTTPS в URL-адресе
//Фишеры могут добавить маркер «HTTPS» к доменной части URL-адреса, чтобы обмануть пользователей.

patt = /https/;
if (patt.test(onlyDomain)) {
  result["HTTPS в URL"] = "1";
} else {
  result["HTTPS в URL"] = "-1";
}

//11. Запросы URL
//Данный тест проверяет, загружены ли внешние объекты, содержащиеся на веб-странице, такие как изображения, видео и звуки, загружены с другого домена.
//На легитимных веб-страницах адрес веб-страницы и большинство объектов, встроенных в веб-страницу, находятся в одном домене.

let imgTags = document.getElementsByTagName("img");

let phishCount = 0;
let legitCount = 0;

patt = RegExp(onlyDomain, "g");

for (let i = 0; i < imgTags.length; i++) {
  let src = imgTags[i].getAttribute("src");
  if (!src) continue;
  if (patt.test(src)) {
    legitCount++;
  } else if (src.charAt(0) == "/" && src.charAt(1) != "/") {
    legitCount++;
  } else {
    phishCount++;
  }
}
let totalCount = phishCount + legitCount;
let outRequest = (phishCount / totalCount) * 100;

if (outRequest < 22) {
  result["Много URL-запросов на внешние объекты"] = "-1";
} else if (outRequest >= 22 && outRequest < 61) {
  result["Много URL-запросов на внешние объекты"] = "0";
} else {
  result["Много URL-запросов на внешние объекты"] = "1";
}

//12. URL-ы в тегах <a>
//Тест, аналогичный предыдущему, для тегов <a> в html-коде
let aTags = document.getElementsByTagName("a");

phishCount = 0;
legitCount = 0;
let allhrefs = "";

for (let i = 0; i < aTags.length; i++) {
  let hrefs = aTags[i].getAttribute("href");
  if (!hrefs) continue;
  allhrefs += hrefs + "       ";
  if (patt.test(hrefs)) {
    legitCount++;
  } else if (
    hrefs.charAt(0) == "#" ||
    (hrefs.charAt(0) == "/" && hrefs.charAt(1) != "/")
  ) {
    legitCount++;
  } else {
    phishCount++;
  }
}
totalCount = phishCount + legitCount;
outRequest = (phishCount / totalCount) * 100;

if (outRequest < 31) {
  result["Много URL в <a>-тегах"] = "-1";
} else if (outRequest >= 31 && outRequest <= 67) {
  result["Много URL в <a>-тегах"] = "0";
} else {
  result["Много URL в <a>-тегах"] = "1";
}

//13. Ссылки в тегах <Meta>, <Script>, <Link>
//Обычно на легальных веб-сайтах используются теги <Meta> для предоставления метаданных о HTML документа;
// теги <Script> для создания сценария на стороне клиента;
// и теги <Link> для получения других веб-ресурсов.
// Данные теги должны быть связаны с одним и тем же доменом веб-страницы.

let mTags = document.getElementsByTagName("meta");
let sTags = document.getElementsByTagName("script");
let lTags = document.getElementsByTagName("link");

phishCount = 0;
legitCount = 0;

allhrefs = "sTags  ";

for (let i = 0; i < sTags.length; i++) {
  let sTag = sTags[i].getAttribute("src");
  if (sTag != null) {
    allhrefs += sTag + "      ";
    if (patt.test(sTag)) {
      legitCount++;
    } else if (sTag.charAt(0) == "/" && sTag.charAt(1) != "/") {
      legitCount++;
    } else {
      phishCount++;
    }
  }
}

allhrefs += "      lTags   ";
for (var i = 0; i < lTags.length; i++) {
  var lTag = lTags[i].getAttribute("href");
  if (!lTag) continue;
  allhrefs += lTag + "       ";
  if (patt.test(lTag)) {
    legitCount++;
  } else if (lTag.charAt(0) == "/" && lTag.charAt(1) != "/") {
    legitCount++;
  } else {
    phishCount++;
  }
}

totalCount = phishCount + legitCount;
outRequest = (phishCount / totalCount) * 100;

if (outRequest < 17) {
  result["Ссылки в тегах <Meta>, <Script>, <Link>"] = "-1";
} else if (outRequest >= 17 && outRequest <= 81) {
  result["Ссылки в тегах <Meta>, <Script>, <Link>"] = "0";
} else {
  result["Ссылки в тегах <Meta>, <Script>, <Link>"] = "1";
}

//14. Server Form Handler
//SFH, содержащие пустую строку или «about:blank», считаются сомнительными, поскольку необходимо предпринять какие-либо действия.
//Кроме того, если доменное имя в SFHs отличается от доменного имени веб-страницы, это говорит о том, что веб-страница подозрительна, поскольку представленная информация редко обрабатывается внешними доменами.

let forms = document.getElementsByTagName("form");
let res = "-1";

for (var i = 0; i < forms.length; i++) {
  var action = forms[i].getAttribute("action");
  if (!action || action == "") {
    res = "1";
    break;
  } else if (!(action.charAt(0) == "/" || patt.test(action))) {
    res = "0";
  }
}
result["SFH"] = res;

//15. Почта
//Веб-форма позволяет пользователю отправить свою личную информацию, которая направляется на сервер для обработки.
//Фишер может перенаправить информацию пользователя на его личную электронную почту. Для этого используется скрипт на стороне сервера
//например, функция «mail()» в PHP. Еще одной функцией на стороне клиента, которая может быть использована для этой цели является функция «mailto:».

forms = document.getElementsByTagName("form");
res = "-1";

for (var i = 0; i < forms.length; i++) {
  var action = forms[i].getAttribute("action");
  if (!action) continue;
  if (action.startsWith("mailto")) {
    res = "1";
    break;
  }
}
result["Почтовый скрипт"] = res;

//16. использование IFrame
//IFrame - это HTML-тег, используемый для отображения дополнительной веб-страницы в той, которая отображается в данный момент.
//Фишеры могут использовать тег «iframe» и сделать его невидимым, то есть без границ рамки.
//фишеры используют атрибут «frameBorder», который заставляет браузер отображать визуальное разграничение.

let iframes = document.getElementsByTagName("iframe");

if (iframes.length == 0) {
  result["iFrames"] = "-1";
} else {
  result["iFrames"] = "1";
}

//Отправка результата тестов
chrome.runtime.sendMessage(result, function (response) {
  console.log(result);
  console.log(response);
});

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  if (request.action == "alert_user")
    alert(
      "Данный сайт является подозрительным. Для подробной информации запустите расширение"
    );
  return Promise.resolve(".....");
});
