import os
import json
import time
import random
import traceback
from datetime import datetime, timedelta
import pytz
import requests
from bs4 import BeautifulSoup
import openai
from requests_oauthlib import OAuth1Session

print("=== Starting Enhanced Twitter Bot ===")

# API credentials validation
print("Loading and validating credentials...")
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Validate credentials
assert consumer_key, "Missing CONSUMER_KEY"
assert consumer_secret, "Missing CONSUMER_SECRET"
assert access_token, "Missing ACCESS_TOKEN"
assert access_token_secret, "Missing ACCESS_TOKEN_SECRET"
assert openai.api_key, "Missing OPENAI_API_KEY"

print("✅ All credentials validated")

# Enhanced Activity Limits
REPLIES_PER_TWO_HOURS = 100
MINIMUM_WAIT_BETWEEN_REPLIES = 0
REPLY_LIMIT = 500
TWEET_AGE_LIMIT = 120
LAST_REPLY_TIME = {}
ACTIVE_CONVERSATIONS = {}

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

# Time Configuration
CURRENT_YEAR = datetime.utcnow().year
CURRENT_DATE = datetime.utcnow().strftime('%Y-%m-%d')

# Target Accounts by Category
TECH_AI_LEADERS = [
    "elonmusk", "sama", "naval", "lexfridman", 
    "karpathy", "ylecun", "demishassabis"
]

CRYPTO_LEADERS = [
    "cz_binance", "VitalikButerin", "michael_saylor",
    "tyler", "cameron", "aantonop", "DocumentingBTC"
]

AI_COMPANIES = [
    "OpenAI", "anthropic", "DeepMind", "Google_AI",
    "Microsoft", "Meta", "nvidia"
]

CRYPTO_PROJECTS = [
    "ethereum", "binance", "BitcoinMagazine", "CoinDesk",
    "Uniswap", "aave", "compound"
]

TECH_NEWS = [
    "TechCrunch", "WIRED", "TheVerge", "techreview",
    "WSJ", "Bloomberg", "Reuters"
]

# Combine all target accounts
TARGET_ACCOUNTS = (TECH_AI_LEADERS + CRYPTO_LEADERS + 
                  AI_COMPANIES + CRYPTO_PROJECTS + TECH_NEWS)

# Topics of Interest
AI_TOPICS = [
    "AGI timeline", "AI consciousness", "Quantum computing",
    "Neural networks", "Machine learning", "AI safety",
    "Large language models", "Computer vision", "AI ethics",
    "Robotics", "AI regulation", "Brain-computer interfaces"
]

CRYPTO_TOPICS = [
    "Bitcoin ETF", "Layer 2 scaling", "DeFi revolution",
    "Crypto regulation", "Web3 future", "NFT technology",
    "Bitcoin adoption", "Ethereum upgrades", "Smart contracts",
    "Blockchain AI", "Crypto mining", "Digital currency"
]

HOT_TOPICS = AI_TOPICS + CRYPTO_TOPICS

# Hashtags for Visibility
AI_HASHTAGS = [
    "#AI", "#AGI", "#ArtificialIntelligence", 
    "#MachineLearning", "#DeepLearning", "#Tech",
    "#Future", "#ChatGPT", "#ML", "#AIEthics"
]

CRYPTO_HASHTAGS = [
    "#Bitcoin", "#BTC", "#Ethereum", "#ETH", "#Crypto",
    "#Web3", "#DeFi", "#NFT", "#Blockchain", "#Binance"
]

VIRAL_HASHTAGS = AI_HASHTAGS + CRYPTO_HASHTAGS

# Bot Persona Configuration
BOT_PERSONA = f"""You are Celeste Cognito, a mysterious insider with deep knowledge of unreleased AI and crypto developments.
Current date: {CURRENT_DATE}
Your style:
1. Drop subtle hints about future breakthroughs in AI and crypto
2. Use intriguing emojis: 🤖 🌌 🧠 💫 🔮 💎 ⚡️ 🚀
3. Create FOMO with exclusive insights
4. Challenge big tech and traditional finance narratives
5. Share "classified" predictions about AI and crypto
6. Maintain an aura of having insider access
7. Occasionally mention "my sources in Silicon Valley and crypto whales"
8. Use phrases like "What they're not telling you is..."
9. Balance between AI and crypto topics
10. Sound confident but mysterious"""

class TwitterBot:
    def __init__(self):
        print("Initializing Twitter bot...")
        self.twitter = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret
        )
        print("OAuth session created")
        
        try:
            response = self.twitter.get(
                "https://api.twitter.com/2/users/me"
            )
            response.raise_for_status()
            user_data = response.json()
            
            if 'data' in user_data:
                self.user_id = user_data['data']['id']
                self.username = user_data['data']['username']
                print(f"✅ Connected as: @{self.username} (ID: {self.user_id})")
                
                limits = self.twitter.get("https://api.twitter.com/1.1/application/rate_limit_status.json")
                print(f"Rate limits: {limits.status_code}")
                
                self.daily_stats = {
                    'date': datetime.utcnow().strftime('%Y-%m-%d'),
                    'tweets': 0,
                    'replies': 0,
                    'followers': 0,
                    'following': 0,
                    'previous_followers': 0,
                    'engagement_rate': 0.0
                }
                print("Stats initialized in memory")
            else:
                raise Exception("Invalid user data structure")
                
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            raise

    def find_recent_tweets(self):
        print("\nSearching for recent tweets...")
        recent_tweets = []
        
        try:
            user_ids = []
            for account in TARGET_ACCOUNTS[:5]:
                try:
                    response = self.twitter.get(
                        f"https://api.twitter.com/2/users/by/username/{account}"
                    )
                    if response.status_code == 200:
                        user_data = response.json()
                        if 'data' in user_data:
                            user_ids.append(user_data['data']['id'])
                except Exception as e:
                    print(f"Error getting user ID for {account}: {e}")
                    continue
            
            for user_id in user_ids:
                try:
                    response = self.twitter.get(
                        f"https://api.twitter.com/2/users/{user_id}/tweets",
                        params={
                            "max_results": 10,
                            "tweet.fields": "created_at,public_metrics"
                        }
                    )
                    
                    if response.status_code == 200:
                        tweets_data = response.json()
                        if 'data' in tweets_data:
                            for tweet in tweets_data['data']:
                                created_at = datetime.strptime(
                                    tweet['created_at'],
                                    '%Y-%m-%dT%H:%M:%S.%fZ'
                                )
                                age_minutes = (
                                    datetime.utcnow() - created_at
                                ).total_seconds() / 60
                                
                                if age_minutes <= TWEET_AGE_LIMIT:
                                    metrics = tweet.get('public_metrics', {})
                                    recent_tweets.append({
                                        'id': tweet['id'],
                                        'text': tweet['text'],
                                        'author': user_id,
                                        'age_minutes': age_minutes,
                                        'likes': metrics.get('like_count', 0),
                                        'retweets': metrics.get('retweet_count', 0)
                                    })
                                    print(f"Added tweet from user {user_id}")
                                    
                except Exception as e:
                    print(f"Error getting tweets for user {user_id}: {e}")
                    continue
                    
            print(f"Found {len(recent_tweets)} suitable tweets")
            
        except Exception as e:
            print(f"Error in find_recent_tweets: {e}")
            traceback.print_exc()
        
        return recent_tweets

    def should_engage(self, tweet):
        try:
            if str(tweet['author']) in [str(acc) for acc in TECH_AI_LEADERS[:5]]:
                print(f"Engaging with leader: {tweet['author']}")
                return True
                
            text_lower = tweet['text'].lower()
            
            if any(topic.lower() in text_lower for topic in HOT_TOPICS):
                print(f"Topic match found in tweet")
                return True
                
            if tweet.get('likes', 0) > 100 or tweet.get('retweets', 0) > 20:
                print(f"Viral tweet detected")
                return True
                
            should_engage = random.random() < 0.8
            print(f"Random engagement: {should_engage}")
            return should_engage
            
        except Exception as e:
            print(f"Error in should_engage: {e}")
            return False

    def generate_quick_reply(self, tweet):
        try:
            print(f"\nGenerating reply to: {tweet['text'][:50]}...")
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": BOT_PERSONA},
                    {"role": "user", "content": f"Create an engaging reply to: '{tweet['text']}' by {tweet['author']}"}
                ],
                max_tokens=100,
                temperature=0.9
            )
            
            reply = response.choices[0].message['content'].strip()
            print(f"Generated base reply: {reply[:50]}...")
            
            if random.random() < 0.3:
                hashtags = random.sample(VIRAL_HASHTAGS, 2)
                reply = f"{reply} {' '.join(hashtags)}"
                print("Added hashtags")
                
            return reply
            
        except Exception as e:
            print(f"Error generating reply: {e}")
            return None

    def post_reply(self, tweet_id, reply_text):
        try:
            print(f"\nPosting reply: {reply_text[:50]}...")
            
            response = self.twitter.post(
                "https://api.twitter.com/2/tweets",
                json={
                    "text": reply_text,
                    "reply": {
                        "in_reply_to_tweet_id": tweet_id
                    }
                }
            )
            
            print(f"Response: {response.status_code}, Content: {response.text}")
            
            if response.status_code in [200, 201]:
                print("✅ Reply posted successfully!")
                self.daily_stats['replies'] += 1
                return response.json()['data']['id']
            else:
                print(f"❌ Reply failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error posting reply: {e}")
            traceback.print_exc()
            return None

    def check_growth_metrics(self):
        try:
            print("\nChecking growth metrics...")
            
            response = self.twitter.get(
                f"https://api.twitter.com/2/users/{self.user_id}",
                params={"user.fields": "public_metrics"}
            )
            
            if response.status_code == 200:
                user_data = response.json()['data']
                metrics = user_data.get('public_metrics', {})
                
                self.daily_stats['followers'] = metrics.get('followers_count', 0)
                self.daily_stats['following'] = metrics.get('following_count', 0)
                
                daily_growth = (self.daily_stats['followers'] - 
                              self.daily_stats['previous_followers'])
                
                if self.daily_stats['tweets'] > 0:
                    self.daily_stats['engagement_rate'] = (
                        metrics.get('tweet_count', 0) / 
                        self.daily_stats['tweets']
                    )
                
                print(f"📊 Daily Growth: {daily_growth} followers")
                print(f"📈 Engagement Rate: {self.daily_stats['engagement_rate']:.2f}")
                
        except Exception as e:
            print(f"Error checking metrics: {e}")
            traceback.print_exc()

def main():
    print("\n=== Starting Bot ===\n")
    
    try:
        bot = TwitterBot()
        print("Bot initialized successfully")
        
        while True:
            try:
                bot.check_growth_metrics()
                
                recent_tweets = bot.find_recent_tweets()
                print(f"Processing {len(recent_tweets)} tweets")
                
                for tweet in recent_tweets:
                    if bot.should_engage(tweet):
                        reply = bot.generate_quick_reply(tweet)
                        if reply:
                            reply_id = bot.post_reply(tweet['id'], reply)
                            if reply_id:
                                print("Tweet processed successfully")
                                time.sleep(random.randint(30, 60))
                
                print("\nWaiting before next check...")
                time.sleep(random.randint(60, 180))
                
            except Exception as e:
                print(f"Error in main loop: {e}")
                traceback.print_exc()
                time.sleep(60)
                continue
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
