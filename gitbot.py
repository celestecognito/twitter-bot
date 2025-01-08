from requests_oauthlib import OAuth1Session
import time
import random
import json
import openai
import os
from datetime import datetime, timezone, timedelta
import requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
openai.api_key = os.environ.get("OPENAI_API_KEY")

TARGET_ACCOUNTS = [
    "elonmusk", "sama", "naval", "lexfridman",
    "OpenAI", "anthropic", "DeepMind", "Google_AI",
    "cz_binance", "VitalikButerin", "tyler", "binance",
    "RayDalio", "TheLastBearSta1", "jimcramer", "michaeljburry"
]

HOT_TOPICS = [
    "AGI", "AI safety", "Machine learning", "Neural networks",
    "Large language models", "Artificial Intelligence", "AI",
    "Bitcoin", "Ethereum", "Crypto", "Web3", "Blockchain", "BTC", "ETH",
    "Stocks", "Investment", "Trading", "Market analysis"
]

class TwitterBot:
    def __init__(self):
        self.twitter = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret
        )
        
        # בדיקת rate limit לפני הכל
        wait_time = self.check_rate_limit()
        if wait_time:
            reset_time = datetime.now() + timedelta(seconds=wait_time)
            msg = f"Rate limited. Will reset at {reset_time} (in {wait_time} seconds)"
            logger.warning(msg)
            raise Exception(msg)
        
        # אם אין rate limit, נמשיך לאימות
        response = self.twitter.get(
            "https://api.twitter.com/2/users/me",
            params={"user.fields": "id,username"}
        )
        
        if response.status_code == 200:
            user_data = response.json()['data']
            self.user_id = user_data['id']
            self.username = user_data['username']
            logger.info(f"Authenticated as @{self.username}")
        else:
            raise Exception(f"Authentication failed: {response.status_code}")

    def check_rate_limit(self):
        try:
            response = self.twitter.get("https://api.twitter.com/2/users/me")
            headers = response.headers
            
            logger.info(f"Response Status Code: {response.status_code}")
            logger.info(f"Response Headers: {headers}")
            
            if response.status_code == 429:
                if 'x-rate-limit-reset' in headers:
                    reset_time = int(headers['x-rate-limit-reset'])
                    current_time = int(time.time())
                    wait_time = reset_time - current_time
                    reset_datetime = datetime.fromtimestamp(reset_time)
                    
                    logger.info(f"Rate limit will reset at: {reset_datetime}")
                    logger.info(f"Time until reset: {wait_time} seconds")
                    
                    if wait_time > 3600:
                        logger.warning(f"Long rate limit detected: {wait_time/3600:.2f} hours")
                    return wait_time
                else:
                    logger.warning("No reset time found in headers")
                    return 900  # 15 minutes default
            return None
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return None

    def find_recent_tweets(self):
        recent_tweets = []
        for account in TARGET_ACCOUNTS[:3]:  # בודק רק 3 חשבונות
            try:
                logger.info(f"Checking account: {account}")
                response = self.twitter.get(
                    f"https://api.twitter.com/2/users/by/username/{account}"
                )
                
                if response.status_code == 200:
                    user_id = response.json()['data']['id']
                    tweets = self.twitter.get(
                        f"https://api.twitter.com/2/users/{user_id}/tweets",
                        params={"max_results": 5}
                    )
                    
                    if tweets.status_code == 200:
                        for tweet in tweets.json().get('data', []):
                            recent_tweets.append({
                                'id': tweet['id'],
                                'text': tweet['text'],
                                'author': account
                            })
                            logger.info(f"Found tweet from {account}")
                time.sleep(2)
                    
            except Exception as e:
                logger.error(f"Error getting tweets from {account}: {e}")
                continue
                
        return recent_tweets

    def should_engage(self, tweet):
        return any(topic.lower() in tweet['text'].lower() for topic in HOT_TOPICS)

    def generate_quick_reply(self, tweet):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AI expert. Keep responses short and engaging."},
                    {"role": "user", "content": f"Create a brief reply to: '{tweet['text']}'"}
                ],
                max_tokens=60,
                temperature=0.7
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            logger.error(f"Error generating reply: {e}")
            return None

    def post_reply(self, tweet_id, reply_text):
        try:
            response = self.twitter.post(
                "https://api.twitter.com/2/tweets",
                json={
                    "text": reply_text,
                    "reply": {"in_reply_to_tweet_id": tweet_id}
                }
            )
            
            if response.status_code in [200, 201]:
                logger.info("Successfully posted reply")
                return response.json()['data']['id']
            return None
            
        except Exception as e:
            logger.error(f"Error posting reply: {e}")
            return None

def main():
    try:
        bot = TwitterBot()  # יבדוק rate limit בהתחלה
        recent_tweets = bot.find_recent_tweets()
        
        for tweet in recent_tweets:
            if bot.should_engage(tweet):
                reply = bot.generate_quick_reply(tweet)
                if reply:
                    bot.post_reply(tweet['id'], reply)
                    time.sleep(5)
                    
    except Exception as e:
        logger.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
