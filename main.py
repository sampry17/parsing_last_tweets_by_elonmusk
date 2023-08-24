import asyncio
import aiohttp
from config import login, password, proxy_host, proxy_port


async def get_bearer_token(session, proxy_auth):
    headers = {
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
        'Referer': 'https://twitter.com/',
        'Origin': 'https://twitter.com',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 YaBrowser/23.7.1.1215 Yowser/2.5 Safari/537.36',
        'sec-ch-ua-platform': '"Linux"',
    }

    async with session.get(url='https://abs.twimg.com/responsive-web/client-web/main.fbea402a.js', headers=headers,
                           proxy_auth=proxy_auth, proxy=f'http://{proxy_host}:{proxy_port}') as response:

        page = await response.text()
        bearer_token = page.split('",N=()')[0].split('R=()=>"')[-1]

        return bearer_token


async def get_csrf(session, proxy_auth):
    headers = {
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
        'Referer': 'https://twitter.com/',
        'Origin': 'https://twitter.com',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 YaBrowser/23.7.1.1215 Yowser/2.5 Safari/537.36',
        'sec-ch-ua-platform': '"Linux"',
        'x-guest-token': '1694705288304312320'
    }

    async with session.get(url='https://twitter.com', headers=headers,
                           proxy_auth=proxy_auth, proxy=f'http://{proxy_host}:{proxy_port}') as response:

        csrf = str(response.cookies).split(';')[0].split('ct0=')[-1]

        return csrf


async def get_last_tweets(session, proxy_auth, bearer_token, csrf_token):
    url = ('https://twitter.com/i/api/graphql/XicnWRbyQ3WgVY__VataBQ/UserTweets?variables=%7B%22userId%22%3A%2244196397%'
           '22%2C%22count%22%3A20%2C%22includePromotedContent%22%3Atrue%2C%22withQuickPromoteEligibilityTweetFields%22%3'
           'Atrue%2C%22withVoice%22%3Atrue%2C%22withV2Timeline%22%3Atrue%7D&features=%7B%22rweb_lists_timeline_redesign_'
           'enabled%22%3Atrue%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_'
           'enabled%22%3Afalse%2C%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C%22responsive_web_graphq'
           'l_timeline_navigation_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabl'
           'ed%22%3Afalse%2C%22tweetypie_unmention_optimization_enabled%22%3Atrue%2C%22responsive_web_edit_tweet_api_ena'
           'bled%22%3Atrue%2C%22graphql_is_translatable_rweb_tweet_is_translatable_enabled%22%3Atrue%2C%22view_counts_ev'
           'erywhere_api_enabled%22%3Atrue%2C%22longform_notetweets_consumption_enabled%22%3Atrue%2C%22responsive_web_tw'
           'itter_article_tweet_consumption_enabled%22%3Afalse%2C%22tweet_awards_web_tipping_enabled%22%3Afalse%2C%22fre'
           'edom_of_speech_not_reach_fetch_enabled%22%3Atrue%2C%22standardized_nudges_misinfo%22%3Atrue%2C%22tweet_with_'
           'visibility_results_prefer_gql_limited_actions_policy_enabled%22%3Atrue%2C%22longform_notetweets_rich_text_re'
           'ad_enabled%22%3Atrue%2C%22longform_notetweets_inline_media_enabled%22%3Atrue%2C%22responsive_web_media_downl'
           'oad_video_enabled%22%3Afalse%2C%22responsive_web_enhance_cards_enabled%22%3Afalse%7D')

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 YaBrowser/23.7.1.1215 Yowser/2.5 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'x-twitter-active-user': 'yes',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'x-csrf-token': csrf_token,
        'authorization': f'Bearer {bearer_token}'
    }

    async with session.get(url=url, headers=headers, proxy_auth=proxy_auth,
                           proxy=f'http://{proxy_host}:{proxy_port}') as response:

        json_content = response.json()

        info_tweets = json_content['data']['user']['result']['timeline_v2']['timeline']['instructions'][2]['entries']

        tweets = []
        for info_tweet in info_tweets[:10]:
            tweet = info_tweet['content']['itemContent']['tweet_results']['result']['legacy']['full_text']
            tweets.append(tweet)

        return tweets


async def main():
    async with aiohttp.ClientSession(trust_env=True) as session:
        proxy_auth = aiohttp.BasicAuth(login, password)
        bearer = await get_bearer_token(session, proxy_auth)
        csrf = await get_csrf(session, proxy_auth)
        tweets = await get_last_tweets(session, proxy_auth, bearer, csrf)

    for tweet in tweets:
        print(tweet)


if __name__ == '__main__':
    asyncio.run(main())