// Функция для получения IP-адреса сайта
async function getSiteIp(domain) {
    try {
        const response = await fetch(`https://dns.google/resolve?name=${domain}`);
        if (!response.ok) {
            throw new Error("Ошибка получения IP-адреса сайта");
        }
        const data = await response.json();
        if (data.Answer && data.Answer.length > 0) {
            return data.Answer[0].data; // Возвращаем первый IP-адрес из ответа
        } else {
            return "IP-адрес не найден";
        }
    } catch (error) {
        console.error(error);
        return "Ошибка получения IP-адреса";
    }
}

// Функция для получения возраста домена
async function getDomainAge(domain) {
    try {
        const response = await fetch(`https://www.whoisxmlapi.com/whoisserver/WhoisService?apiKey=YOUR_API_KEY&domainName=${domain}&outputFormat=JSON`);
        if (!response.ok) {
            throw new Error("Ошибка получения данных о домене");
        }
        const data = await response.json();
        if (data.WhoisRecord && data.WhoisRecord.createdDate) {
            return data.WhoisRecord.createdDate; // Возвращаем дату создания домена
        } else {
            return "Возраст домена не найден";
        }
    } catch (error) {
        console.error(error);
        return "Ошибка получения возраста домена";
    }
}

// Основная функция для сбора информации о сайте
async function getSiteInfo() {
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const url = new URL(tab.url);
        const domain = url.hostname;

        const siteIp = await getSiteIp(domain);  // Получаем IP-адрес сайта
        const domainAge = await getDomainAge(domain);  // Получаем возраст домена

        document.getElementById('url').innerText = `URL: ${url.href}`;
        document.getElementById('ip').innerText = `IP: ${siteIp}`;  // Отображаем IP-адрес сайта
        document.getElementById('age').innerText = `Возраст домена: ${domainAge}`; // Отображаем возраст домена
        document.getElementById('length').innerText = `Длина URL: ${url.href.length}`;
    } catch (error) {
        console.error(error);
        document.getElementById('url').innerText = "Ошибка получения данных";
        document.getElementById('ip').innerText = "";
        document.getElementById('age').innerText = "";
        document.getElementById('length').innerText = "";
    }
}

// Запуск функции при загрузке popup
getSiteInfo();
