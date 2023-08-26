import asyncio
import aiohttp
from config import login, password, proxy_host, proxy_port
from datetime import datetime


def extract_date(date_str):
    return datetime.strptime(date_str, '%a %b %d %H:%M:%S %z %Y')


async def get_bearer_token(session, proxy_auth):
    async with session.get(url='https://abs.twimg.com/responsive-web/client-web/main.fbea402a.js',
                           proxy_auth=proxy_auth, proxy=f'http://{proxy_host}:{proxy_port}') as response:

        page = await response.text()
        bearer_token = page.split('",N=()')[0].split('R=()=>"')[-1]

        return bearer_token


async def get_guest_token(session, proxy_auth, bearer_token):
    headers = {
        "accept": "*/*",
        "accept-language": "de,en-US;q=0.7,en;q=0.3",
        "accept-encoding": "gzip, deflate, br",
        "te": "trailers",
        'authorization': f'Bearer {bearer_token}'
    }

    async with session.post(url='https://api.twitter.com/1.1/guest/activate.json', headers=headers,
                            proxy_auth=proxy_auth, proxy=f'http://{proxy_host}:{proxy_port}') as response:

        guest_token = await response.json()

        return guest_token['guest_token']


async def get_last_tweets(session, proxy_auth, bearer_token, guest):
    url = 'https://twitter.com/i/api/graphql/XicnWRbyQ3WgVY__VataBQ/UserTweets'

    params = {
        'variables': '{"userId":"44196397","count":20,"includePromotedContent":true,"withQuickPromoteEligibilityTweetFields":true,"withVoice":true,"withV2Timeline":true}',
        'features': '{"rweb_lists_timeline_redesign_enabled":true,"responsive_web_graphql_exclude_directive_enabled":true,'
                    '"verified_phone_label_enabled":false,"creator_subscriptions_tweet_preview_api_enabled":true,'
                    '"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,'
                    '"tweetypie_unmention_optimization_enabled":true,"responsive_web_edit_tweet_api_enabled":true,'
                    '"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,'
                    '"longform_notetweets_consumption_enabled":true,"responsive_web_twitter_article_tweet_consumption_enabled":false,'
                    '"tweet_awards_web_tipping_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":true,'
                    '"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,'
                    '"longform_notetweets_rich_text_read_enabled":true,"longform_notetweets_inline_media_enabled":true,'
                    '"responsive_web_media_download_video_enabled":false,"responsive_web_enhance_cards_enabled":false}',
    }

    headers = {
        'x-guest-token': guest,
        'authorization': f'Bearer {bearer_token}'
    }

    async with session.get(url=url, params=params, headers=headers, proxy_auth=proxy_auth,
                           proxy=f'http://{proxy_host}:{proxy_port}') as response:

        json_content = await response.json()

        info_tweets = json_content['data']['user']['result']['timeline_v2']['timeline']['instructions'][2]['entries']

        tweets = []
        for info_tweet in info_tweets:
            tweet = info_tweet['content']['itemContent']['tweet_results']['result']['legacy']

            tweets.append({tweet['created_at']: tweet['full_text']})

        sorted_tweets = sorted(tweets, key=lambda item: extract_date(list(item.keys())[0]), reverse=True)

        return sorted_tweets


async def main():
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 YaBrowser/23.7.1.1215 Yowser/2.5 Safari/537.36',
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        proxy_auth = aiohttp.BasicAuth(login, password)
        bearer = await get_bearer_token(session, proxy_auth)
        guest = await get_guest_token(session, proxy_auth, bearer)
        tweets = await get_last_tweets(session, proxy_auth, bearer, guest)

    for tweet in tweets[:10]:
        date, text = list(tweet.items())[0]
        print(f'{text} - Опубликован: {date}')


if __name__ == '__main__':
    asyncio.run(main())