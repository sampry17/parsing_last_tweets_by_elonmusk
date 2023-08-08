import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import lxml


def get_free_proxies():
    url = "https://free-proxy-list.net/"
    # получаем ответ HTTP и создаем объект soup
    soup = BeautifulSoup(requests.get(url).content, "lxml")
    proxies = []
    for row in soup.find("table", attrs={'class': 'table table-striped table-bordered'}).find_all("tr")[1:]:
        tds = row.find_all("td")
        try:
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            host = f"{ip}:{port}"
            proxies.append(host)
        except IndexError:
            continue
    return proxies


def get_session(proxy):
    ua = UserAgent()
    session = requests.Session()

    session.headers = {
        "user-agent": ua.random,
        "Accept-Language": "ru,en;q=0.9",
    }
    session.proxies = {"http": proxy, "https": proxy}
    return session


def get_article_urls(url, session):
    response = session.get(url=url, timeout=1.5)

    with open('index.html', 'w') as file:
        file.write(response.text)


free_proxies = get_free_proxies()
for i in range(len(free_proxies)):
    url = "https://www.sotwe.com/elonmusk"
    ses = get_session(free_proxies[i])
    try:
        get_article_urls(url, ses)
        break
    except Exception as e:
        print(e)