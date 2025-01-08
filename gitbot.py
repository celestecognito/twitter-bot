from requests_oauthlib import OAuth1Session
import time
import random
import json
import openai
import os
from datetime import datetime, timedelta
import datetime as dt
import requests
from bs4 import BeautifulSoup
import pytz
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Debug prints
print("\n=== Debug Info ===")
print("Environment variables:")
for key in ['CONSUMER_KEY', 'CONSUMER_SECRET', 'ACCESS_TOKEN', 'ACCESS_TOKEN_SECRET', 'OPENAI_API_KEY']:
    exists = bool(os.environ.get(key))
    print(f"{key}: {'✅' if exists else '❌'}")
print("==================\n")

# Validate required credentials
required_keys = ['CONSUMER_KEY', 'CONSUMER_SECRET', 'ACCESS_TOKEN', 'ACCESS_TOKEN_SECRET', 'OPENAI_API_KEY']
missing_keys = [key for key in required_keys if not os.environ.get(key)]

if missing_keys:
    print("❌ Error: Missing required environment variables:")
    for key in missing_keys:
        print(f"  - {key}")
    print("\nPlease set these environment variables and try again.")
    exit(1)

print("=== Starting Enhanced Twitter Bot ===")

# API credentials
print("Loading credentials...")
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Enhanced Activity Limits
REPLIES_PER_TWO_HOURS = 10
CONVERSATION_DEPTH_LIMIT = 5
MINIMUM_WAIT_BETWEEN_REPLIES = 3
REPLY_LIMIT = 50  # Maximum daily replies
LAST_REPLY_TIME = {}
ACTIVE_CONVERSATIONS = {}

# Time and Activity Configuration
CURRENT_YEAR = datetime.now(dt.timezone.utc).year
CURRENT_DATE = datetime.now(dt.timezone.utc).strftime('%Y-%m-%d')
TWEET_AGE_LIMIT = 5  # minutes
PEAK_HOURS = [13, 14, 15, 16, 19, 20, 21, 22]  # EST

# Growth and Engagement Goals
FOLLOWER_GOALS = {
    'daily': 100,
    'weekly': 1000,
    'monthly': 5000
}

ENGAGEMENT_GOALS = {
    'likes_per_tweet': 50,
    'retweets_per_tweet': 20,
    'replies_per_tweet': 10
}

# Target Accounts
TECH_AI_LEADERS = ["elonmusk", "sama", "naval", "lexfridman", "karpathy"]
CRYPTO_LEADERS = ["cz_binance", "VitalikButerin", "michael_saylor"]
AI_COMPANIES = ["OpenAI", "anthropic", "DeepMind", "Google_AI"]
CRYPTO_PROJECTS = ["ethereum", "binance", "BitcoinMagazine"]
TECH_NEWS = ["TechCrunch", "WIRED", "TheVerge"]

TARGET_ACCOUNTS = (TECH_AI_LEADERS + CRYPTO_LEADERS + AI_COMPANIES + 
                  CRYPTO_PROJECTS + TECH_NEWS)

# Topics and Hashtags
AI_TOPICS = ["AGI timeline", "AI consciousness", "Machine learning"]
CRYPTO_TOPICS = ["Bitcoin ETF", "Layer 2 scaling", "DeFi revolution"]
HOT_TOPICS = AI_TOPICS + CRYPTO_TOPICS

AI_HASHTAGS = ["#AI", "#AGI", "#ArtificialIntelligence"]
CRYPTO_HASHTAGS = ["#Bitcoin", "#ETH", "#Crypto"]
VIRAL_HASHTAGS = AI_HASHTAGS + CRYPTO_HASHTAGS

# Engagement Patterns
ENGAGEMENT_PATTERNS = {
    'questions': ['What if', 'Have you considered', 'Why do you think'],
    'hooks': ['LEAKED:', 'Inside sources confirm:', 'My AI analysis shows:'],
    'engagement': ['Agree?', 'Thoughts?', "What's your take?"]
}

# News Sources
NEWS_SOURCES = [
    "https://cointelegraph.com/",
    "https://www.theverge.com/ai-artificial-intelligence"
]

# Bot Persona
BOT_PERSONA = f"""You are Celeste Cognito, an AI and crypto insider.
Current date: {CURRENT_DATE}
Style: Mysterious, insightful, engaging
Focus: AI developments, crypto trends, tech breakthroughs"""

class TwitterBot:
    def __init__(self):
        print("\n=== Bot Initialization ===")
        try:
            self.twitter = OAuth1Session(
                consumer_key,
                client_secret=consumer_secret,
                resource_owner_key=access_token,
                resource_owner_secret=access_token_secret
            )
            
            # Test connection with v1.1 API
            print("Testing Twitter API connection...")
            response = self.twitter.get(
                "https://api.twitter.com/1.1/account/verify_credentials.json"
            )
            
            if response.status_code == 200:
                user_data = response.json()
                self.username = str(user_data['id'])
                print(f"✅ Bot ID: {self.username}")
                print(f"✅ Connected as: @{user_data['screen_name']}")
            else:
                print(f"❌ Twitter API response: {response.status_code}")
                print(f"Response text: {response.text}")
                raise Exception(f"Failed to verify credentials: {response.status_code}")
            
            self.daily_stats_file = 'daily_stats.json'
            self.daily_stats = self.load_daily_stats()
            self.trending_cache = []
            self.last_trending_update = None
            self.current_news = []
            self.last_news_check = None
            
        except Exception as e:
            print(f"❌ Initialization error: {str(e)}")
            raise e

    def load_daily_stats(self):
        today = datetime.now(dt.timezone.utc).strftime('%Y-%m-%d')
        try:
            if os.path.exists(self.daily_stats_file):
                with open(self.daily_stats_file, 'r') as f:
                    stats = json.load(f)
                    if stats.get('date') == today:
                        return stats
        except Exception as e:
            print(f"Error loading stats: {str(e)}")

        return {
            'date': today,
            'tweets': 0,
            'replies': 0,
            'followers': 0,
            'following': 0
        }

    def save_daily_stats(self):
        try:
            with open(self.daily_stats_file, 'w') as f:
                json.dump(self.daily_stats, f)
        except Exception as e:
            print(f"Error saving stats: {str(e)}")

    def check_growth_metrics(self):
        try:
            time.sleep(5)
            response = self.twitter.get(
                "https://api.twitter.com/1.1/users/show.json",
                params={"user_id": self.username}
            )
            if response.status_code == 200:
                metrics = response.json()
                self.daily_stats.update({
                    'followers': metrics['followers_count'],
                    'following': metrics['friends_count']
                })
                self.save_daily_stats()
                return True
            return False
        except Exception as e:
            print(f"Error checking metrics: {str(e)}")
            return False

    def find_recent_tweets(self):
        recent_tweets = []
        try:
            for account in TARGET_ACCOUNTS[:5]:  # Limit to 5 accounts per iteration
                time.sleep(5)
                print(f"Checking tweets from @{account}...")
                
                # Get user timeline using v1.1 API
                response = self.twitter.get(
                    "https://api.twitter.com/1.1/statuses/user_timeline.json",
                    params={
                        "screen_name": account,
                        "count": 5,
                        "tweet_mode": "extended"
                    }
                )
                
                if response.status_code == 200:
                    tweets = response.json()
                    for tweet in tweets:
                        created_at = datetime.strptime(
                            tweet['created_at'],
                            '%a %b %d %H:%M:%S +0000 %Y'
                        ).replace(tzinfo=dt.timezone.utc)
                        
                        age_minutes = (datetime.now(dt.timezone.utc) - created_at).total_seconds() / 60
                        if age_minutes <= TWEET_AGE_LIMIT:
                            recent_tweets.append({
                                'id': tweet['id_str'],
                                'text': tweet['full_text'],
                                'author': account,
                                'age_minutes': age_minutes
                            })
                            print(f"Found tweet {age_minutes:.1f} minutes old")
                else:
                    print(f"Failed to get tweets from {account}: {response.status_code}")
                
        except Exception as e:
            print(f"Error finding tweets: {str(e)}")
        
        return recent_tweets

    def should_engage(self, tweet):
        try:
            if tweet['id'] in LAST_REPLY_TIME:
                last_reply = LAST_REPLY_TIME[tweet['id']]
                minutes_since_reply = (datetime.now(dt.timezone.utc) - last_reply).total_seconds() / 60
                if minutes_since_reply < MINIMUM_WAIT_BETWEEN_REPLIES:
                    return False

            if self.daily_stats['replies'] >= REPLY_LIMIT:
                return False

            if tweet['age_minutes'] > TWEET_AGE_LIMIT:
                return False

            return True
        except Exception as e:
            print(f"Error in should_engage: {str(e)}")
            return False

    def generate_quick_reply(self, tweet):
        try:
            engagement_suffix = random.choice(ENGAGEMENT_PATTERNS['engagement'])
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": BOT_PERSONA},
                    {"role": "user", "content": 
                     f"Create an engaging reply to: '{tweet['text']}' by {tweet['author']}. "
                     f"End with '{engagement_suffix}' if appropriate."}
                ],
                max_tokens=60,
                temperature=0.9
            )
            
            reply = response.choices[0].message['content'].strip()
            reply = reply.replace('"', '')
            
            hashtags = " ".join(random.sample(VIRAL_HASHTAGS, 2))
            return f"{reply} {hashtags}"
            
        except Exception as e:
            print(f"Error generating reply: {str(e)}")
            return None

    def post_reply(self, tweet_id, reply_text):
        if self.daily_stats['replies'] >= REPLY_LIMIT:
            return False

        try:
            time.sleep(5)
            response = self.twitter.post(
                "https://api.twitter.com/1.1/statuses/update.json",
                params={
                    "status": reply_text,
                    "in_reply_to_status_id": tweet_id,
                    "auto_populate_reply_metadata": True
                }
            )
            
            if response.status_code == 200:
                print("✅ Reply posted successfully!")
                self.daily_stats['replies'] += 1
                self.save_daily_stats()
                LAST_REPLY_TIME[tweet_id] = datetime.now(dt.timezone.utc)
                return True
            else:
                print(f"❌ Failed to post reply: {response.status_code}")
                print(f"Response: {response.text}")
            return False
        except Exception as e:
            print(f"Error posting reply: {str(e)}")
            return False

    def process_tweet(self, tweet):
        try:
            print(f"\nProcessing tweet from @{tweet['author']}...")
            print(f"Tweet text: {tweet['text'][:100]}...")
            
            reply = self.generate_quick_reply(tweet)
            if reply:
                print(f"Generated reply: {reply}")
                if self.post_reply(tweet['id'], reply):
                    print(f"✅ Successfully processed tweet from {tweet['author']}")
                    time.sleep(MINIMUM_WAIT_BETWEEN_REPLIES * 60)
        except Exception as e:
            print(f"Error processing tweet: {str(e)}")

    def reply_to_replies(self):
        try:
            time.sleep(5)
            print("\nChecking for mentions...")
            response = self.twitter.get(
                "https://api.twitter.com/1.1/statuses/mentions_timeline.json",
                params={
                    "count": 10,
                    "tweet_mode": "extended"
                }
            )
            
            if response.status_code == 200:
                mentions = response.json()
                for mention in mentions:
                    if str(mention['in_reply_to_user_id']) == self.username:
                        tweet_data = {
                            'id': mention['id_str'],
                            'text': mention['full_text'],
                            'author': mention['user']['screen_name'],
                            'age_minutes': 0  # Process all mentions
                        }
                        self.process_tweet(tweet_data)
                        time.sleep(60)
                return True
            else:
                print(f"❌ Failed to get mentions: {response.status_code}")
            return False
        except Exception as e:
            print(f"Error processing replies: {str(e)}")
            return False

def main():
    print("\n=== Starting Bot ===\n")
    
    try:
        bot = TwitterBot()
        
        while True:
            try:
                print("\n=== New Iteration ===")
                
                bot.check_growth_metrics()
                time.sleep(60)
                
                recent_tweets = bot.find_recent_tweets()
                print(f"Found {len(recent_tweets)} recent tweets")
                
                for tweet in recent_tweets:
                    if bot.should_engage(tweet):
                        bot.process_tweet(tweet)
                        time.sleep(60)
                
                bot.reply_to_replies()
                
                print("\nWaiting 15 minutes before next iteration...")
                time.sleep(900)  # 15 minutes between iterations
                
            except Exception as e:
                print(f"Error in main loop: {str(e)}")
                time.sleep(300)
                continue
            
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        raise e

if __name__ == "__main__":
    main()
