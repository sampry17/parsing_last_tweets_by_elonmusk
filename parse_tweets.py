from bs4 import BeautifulSoup
import lxml
from dateutil.parser import parse


with open('index.html', 'r') as file:
    soup = BeautifulSoup(file, 'lxml')


elements = soup.select('.d-flex.flex-column')

for i in range(len(elements) - 1):
    for j in range(len(elements) - 1):
        try:
            data_one = parse(elements[i].select_one('time[datetime]')['datetime']).timestamp()
            data_two = parse(elements[j + 1].select_one('time[datetime]')['datetime']).timestamp()
            if data_one > data_two:
                elements[i], elements[j + 1] = elements[j + 1], elements[i]
        except Exception as e:
            pass

tweets = []
for elem in elements:
    tweet = elem.select_one('.px-4 > span')
    tweets.append(tweet.get_text() if tweet is not None else 'tweet has no text')


for tweet in tweets[:10]:
    print(f'{tweet}\n------')