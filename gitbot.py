from requests_oauthlib import OAuth1Session
import time
import random
import json
import openai
import os
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import pytz
import traceback

print("=== Starting Enhanced Twitter Bot ===")

# API credentials
print("Loading credentials...")
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
openai.api_key = os.environ.get("OPENAI_API_KEY")

print(f"Credentials loaded: {bool(consumer_key and consumer_secret and access_token and access_token_secret and openai.api_key)}")

# Enhanced Activity Limits - Maximum Freedom
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
        """Initialize the Twitter bot"""
        print("Initializing Twitter bot...")
        self.twitter = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret
        )
        print("OAuth session created")
        
        # Get bot's user info
        response = self.twitter.get(
            "https://api.twitter.com/1.1/account/verify_credentials.json"
        )
        print(f"Connection test status code: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            self.username = user_data['screen_name']
            print(f"✅ Connected as: @{self.username}")
            
            # Initialize stats in memory
            self.daily_stats = {
                'date': datetime.utcnow().strftime('%Y-%m-%d'),
                'tweets': 0,
                'replies': 0,
                'followers': user_data['followers_count'],
                'following': user_data['friends_count'],
                'previous_followers': user_data['followers_count'],
                'engagement_rate': 0.0
            }
            print("Stats initialized in memory")
        else:
            raise Exception(f"Failed to connect: {response.status_code}")

    def find_recent_tweets(self):
        """Finds recent tweets from target accounts"""
        print("\nSearching for recent tweets...")
        recent_tweets = []
        
        try:
            search_query = " OR ".join([f"from:{account}" for account in TARGET_ACCOUNTS[:5]])
            print(f"Search query: {search_query}")
            
            response = self.twitter.get(
                "https://api.twitter.com/1.1/search/tweets.json",
                params={
                    "q": search_query,
                    "count": 100,
                    "tweet_mode": "extended",
                    "result_type": "recent"
                }
            )
            print(f"Search status code: {response.status_code}")
            
            if response.status_code == 200:
                tweets = response.json()['statuses']
                print(f"Found {len(tweets)} tweets total")
                
                for tweet in tweets:
                    if 'retweeted_status' not in tweet:
                        created_at = datetime.strptime(
                            tweet['created_at'],
                            '%a %b %d %H:%M:%S +0000 %Y'
                        )
                        age_minutes = (
                            datetime.utcnow() - created_at
                        ).total_seconds() / 60
                        
                        if age_minutes <= TWEET_AGE_LIMIT:
                            recent_tweets.append({
                                'id': tweet['id_str'],
                                'text': tweet['full_text'],
                                'author': tweet['user']['screen_name'],
                                'age_minutes': age_minutes,
                                'likes': tweet.get('favorite_count', 0),
                                'retweets': tweet.get('retweet_count', 0)
                            })
                            print(f"Added tweet from @{tweet['user']['screen_name']}")
                
                print(f"Found {len(recent_tweets)} suitable tweets")
                
        except Exception as e:
            print(f"Error in find_recent_tweets: {e}")
            traceback.print_exc()
        
        return recent_tweets

    def should_engage(self, tweet):
        """Determines if we should engage with a tweet"""
        try:
            # Always engage with top accounts
            if tweet['author'] in TECH_AI_LEADERS[:5]:
                print(f"Engaging with leader: {tweet['author']}")
                return True
                
            text_lower = tweet['text'].lower()
            
            # Engage if any topic matches
            if any(topic.lower() in text_lower for topic in HOT_TOPICS):
                print(f"Topic match found in tweet")
                return True
                
            # Engage with viral tweets
            if tweet.get('likes', 0) > 100 or tweet.get('retweets', 0) > 20:
                print(f"Viral tweet detected")
                return True
                
            # More liberal engagement - 80% chance
            should_engage = random.random() < 0.8
            print(f"Random engagement: {should_engage}")
            return should_engage
            
        except Exception as e:
            print(f"Error in should_engage: {e}")
            return False

    def generate_quick_reply(self, tweet):
        """Generates a reply to a tweet"""
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
            
            # Add viral hashtags randomly
            if random.random() < 0.3:
                hashtags = random.sample(VIRAL_HASHTAGS, 2)
                reply = f"{reply} {' '.join(hashtags)}"
                print("Added hashtags")
                
            return reply
            
        except Exception as e:
            print(f"Error generating reply: {e}")
            return None

    def post_reply(self, tweet_id, reply_text):
        """Posts a reply to a tweet"""
        try:
            print(f"\nPosting reply: {reply_text[:50]}...")
            
            response = self.twitter.post(
                "https://api.twitter.com/1.1/statuses/update.json",
                params={
                    "status": reply_text,
                    "in_reply_to_status_id": tweet_id,
                    "auto_populate_reply_metadata": True
                }
            )
            
            print(f"Post reply status code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Reply posted successfully!")
                self.daily_stats['replies'] += 1
                return response.json()['id_str']
            else:
                print(f"❌ Reply failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error posting reply: {e}")
            return None

    def check_growth_metrics(self):
        """Monitors follower growth and engagement"""
        try:
            print("\nChecking growth metrics...")
            
            response = self.twitter.get(
                "https://api.twitter.com/1.1/users/show.json",
                params={"screen_name": self.username}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Update daily stats
                self.daily_stats['followers'] = user_data['followers_count']
                self.daily_stats['following'] = user_data['friends_count']
                
                # Calculate growth
                daily_growth = (self.daily_stats['followers'] - 
                              self.daily_stats['previous_followers'])
                
                # Update engagement rate
                if self.daily_stats['tweets'] > 0:
                    self.daily_stats['engagement_rate'] = (
                        (user_data.get('favourites_count', 0) + 
                         user_data.get('retweet_count', 0)) / 
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
        # Initialize bot
        bot = TwitterBot()
        print("Bot initialized successfully")
        
        while True:
            try:
                # Check metrics first
                bot.check_growth_metrics()
                
                # Find and process recent tweets
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
                time.sleep(60)
                continue
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
