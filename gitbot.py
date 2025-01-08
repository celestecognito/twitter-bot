from requests_oauthlib import OAuth1Session
import time
import random
import json
import openai
import os
from datetime import datetime, timedelta, timezone
import requests
from bs4 import BeautifulSoup
import pytz
import traceback
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("=== Starting Enhanced Twitter Bot ===")

logger.info("Loading credentials...")
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
openai.api_key = os.environ.get("OPENAI_API_KEY")

assert consumer_key, "Missing CONSUMER_KEY"
assert consumer_secret, "Missing CONSUMER_SECRET"
assert access_token, "Missing ACCESS_TOKEN"
assert access_token_secret, "Missing ACCESS_TOKEN_SECRET"
assert openai.api_key, "Missing OPENAI_API_KEY"

logger.info("✅ All credentials validated")

# Constants
REPLIES_PER_TWO_HOURS = 10
TWEET_AGE_LIMIT = 30
WAIT_TIME = 60  # Base wait time between operations

TARGET_ACCOUNTS = [
    "elonmusk", "sama", "naval", "lexfridman",
    "OpenAI", "anthropic", "DeepMind", "Google_AI"
]

HOT_TOPICS = [
    "AGI", "AI safety", "Machine learning",
    "Neural networks", "Large language models",
    "AI ethics", "Future of AI"
]

class TwitterBot:
    def __init__(self):
        logger.info("Starting TwitterBot initialization...")
        try:
            self.twitter = OAuth1Session(
                consumer_key,
                client_secret=consumer_secret,
                resource_owner_key=access_token,
                resource_owner_secret=access_token_secret
            )
            
            response = self.twitter.get(
                "https://api.twitter.com/2/users/me",
                params={"user.fields": "id,username"}
            )
            
            if response.status_code == 200:
                user_data = response.json()['data']
                self.user_id = user_data['id']
                self.username = user_data['username']
                logger.info(f"✅ Authenticated as @{self.username}")
                
                self.daily_stats = {
                    'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                    'replies': 0,
                    'followers': 0
                }
                return
                
            raise Exception(f"Authentication failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Initialization error: {str(e)}")
            raise

    def should_engage(self, tweet):
        try:
            if any(topic.lower() in tweet['text'].lower() for topic in HOT_TOPICS):
                return True
            return False
        except Exception as e:
            logger.error(f"Error in should_engage: {e}")
            return False

    def find_recent_tweets(self):
        recent_tweets = []
        for account in TARGET_ACCOUNTS[:3]:  # Limit to 3 accounts per cycle
            try:
                time.sleep(WAIT_TIME)  # Wait between requests
                
                response = self.twitter.get(
                    f"https://api.twitter.com/2/users/by/username/{account}"
                )
                
                if response.status_code == 200:
                    user_id = response.json()['data']['id']
                    
                    time.sleep(WAIT_TIME)  # Wait between requests
                    
                    tweets_response = self.twitter.get(
                        f"https://api.twitter.com/2/users/{user_id}/tweets",
                        params={"max_results": 5}
                    )
                    
                    if tweets_response.status_code == 200:
                        tweets = tweets_response.json().get('data', [])
                        for tweet in tweets:
                            recent_tweets.append({
                                'id': tweet['id'],
                                'text': tweet['text'],
                                'author': account
                            })
                            
            except Exception as e:
                logger.error(f"Error processing {account}: {e}")
                continue
                
        return recent_tweets

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
            time.sleep(WAIT_TIME)  # Wait before posting
            
            response = self.twitter.post(
                "https://api.twitter.com/2/tweets",
                json={
                    "text": reply_text,
                    "reply": {"in_reply_to_tweet_id": tweet_id}
                }
            )
            
            if response.status_code in [200, 201]:
                logger.info("✅ Reply posted successfully!")
                self.daily_stats['replies'] += 1
                return response.json()['data']['id']
            else:
                logger.error(f"❌ Reply failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error posting reply: {e}")
            return None

    def check_growth_metrics(self):
        try:
            time.sleep(WAIT_TIME)  # Wait before checking metrics
            
            response = self.twitter.get(
                f"https://api.twitter.com/2/users/{self.user_id}",
                params={"user.fields": "public_metrics"}
            )
            
            if response.status_code == 200:
                metrics = response.json()['data']['public_metrics']
                self.daily_stats['followers'] = metrics.get('followers_count', 0)
                logger.info(f"Current followers: {self.daily_stats['followers']}")
                
        except Exception as e:
            logger.error(f"Error checking metrics: {e}")

def main():
    logger.info("=== Starting Bot ===")
    
    try:
        bot = TwitterBot()
        
        while True:
            try:
                logger.info("--- Starting new cycle ---")
                
                recent_tweets = bot.find_recent_tweets()
                logger.info(f"Found {len(recent_tweets)} tweets")
                
                for tweet in recent_tweets:
                    if bot.should_engage(tweet):
                        reply = bot.generate_quick_reply(tweet)
                        if reply:
                            bot.post_reply(tweet['id'], reply)
                            time.sleep(WAIT_TIME * 2)  # Double wait after posting
                
                bot.check_growth_metrics()
                
                logger.info("Waiting before next cycle...")
                time.sleep(WAIT_TIME * 5)  # 5 minute wait between cycles
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(WAIT_TIME * 2)
                continue
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
