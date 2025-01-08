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

# Engagement Patterns
ENGAGEMENT_PATTERNS = {
    'morning_boost': {
        'start_hour': 6,
        'end_hour': 9,
        'tweet_frequency': 15,
        'engagement_rate': 0.9
    },
    'lunch_time': {
        'start_hour': 11,
        'end_hour': 14,
        'tweet_frequency': 20,
        'engagement_rate': 0.8
    },
    'evening_prime': {
        'start_hour': 18,
        'end_hour': 23,
        'tweet_frequency': 10,
        'engagement_rate': 0.95
    }
}

# Viral Strategies
VIRAL_STRATEGIES = {
    'controversy': {
        'probability': 0.3,
        'templates': [
            "Unpopular opinion: {topic} 🤔",
            "Why everyone is wrong about {topic} 🧵",
            "The dark truth about {topic} that no one talks about 🔍"
        ]
    },
    'insider_info': {
        'probability': 0.4,
        'templates': [
            "LEAKED: Internal documents show {info} 👀",
            "Just heard from my sources: {info} 🤫",
            "Breaking: {info} 🚨"
        ]
    },
    'prediction': {
        'probability': 0.3,
        'templates': [
            "Mark my words: {prediction} will happen within {timeframe} 🔮",
            "Next big thing in {industry}: {prediction} 🚀",
            "My analysis suggests {prediction} 📊"
        ]
    }
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
    "Blockchain AI", "Crypto mining", "Digital currency",
    "Metaverse", "DAO governance", "DeFi protocols"
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
10. Sound confident but mysterious
11. IMPORTANT: Never use quotes (\") in your responses and never start responses with quotes
12. Always be aware it's {CURRENT_DATE} and reference current events
13. Never reference outdated information or past years as current"""

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
        
        # Get bot's user info
        response = self.twitter.get(
            "https://api.twitter.com/1.1/account/verify_credentials.json"
        )
        
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
            self.LAST_REPLY_TIME = {}
        else:
            raise Exception("Failed to get bot user info")

    def find_recent_tweets(self):
        """Finds recent tweets from target accounts"""
        print("\nSearching for recent tweets...")
        recent_tweets = []
        
        try:
            # Search for tweets using broader criteria
            search_query = " OR ".join([f"from:{account}" for account in TARGET_ACCOUNTS])
            
            response = self.twitter.get(
                "https://api.twitter.com/1.1/search/tweets.json",
                params={
                    "q": search_query,
                    "count": 100,
                    "tweet_mode": "extended",
                    "result_type": "recent",
                    "include_entities": True
                }
            )
            
            if response.status_code == 200:
                tweets = response.json()['statuses']
                for tweet in tweets:
                    if 'retweeted_status' not in tweet:  # Skip retweets
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
                            print(f"Found {age_minutes:.1f} minute old tweet from @{tweet['user']['screen_name']}")
        
        except Exception as e:
            print(f"Error in find_recent_tweets: {e}")
            traceback.print_exc()
        
        return recent_tweets

    def should_engage(self, tweet):
        """Determines if we should engage with a tweet"""
        try:
            # Always engage with top accounts
            if tweet['author'] in TECH_AI_LEADERS + CRYPTO_LEADERS[:5]:
                return True
                
            text_lower = tweet['text'].lower()
            
            # Engage if any topic matches
            if any(topic.lower() in text_lower for topic in HOT_TOPICS):
                return True
                
            # Engage with viral tweets
            if tweet.get('likes', 0) > 100 or tweet.get('retweets', 0) > 20:
                return True
                
            # More liberal engagement - 80% chance to engage
            return random.random() < 0.8
            
        except Exception as e:
            print(f"Error in should_engage: {e}")
            return False

    def generate_quick_reply(self, tweet):
        """Generates a reply to a tweet"""
        try:
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
            
            # Add viral hashtags randomly
            if random.random() < 0.3:  # 30% chance
                hashtags = random.sample(VIRAL_HASHTAGS, 2)
                reply = f"{reply} {' '.join(hashtags)}"
                
            return reply
            
        except Exception as e:
            print(f"Error generating reply: {e}")
            return None

    def post_reply(self, tweet_id, reply_text):
        """Posts a reply to a tweet"""
        try:
            response = self.twitter.post(
                "https://api.twitter.com/1.1/statuses/update.json",
                params={
                    "status": reply_text,
                    "in_reply_to_status_id": tweet_id,
                    "auto_populate_reply_metadata": True
                }
            )
            
            if response.status_code == 200:
                print("✅ Reply posted!")
                self.daily_stats['replies'] += 1
                return response.json()['id_str']
            else:
                print(f"❌ Reply failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def retweet(self, tweet_id):
        """Retweets a tweet"""
        try:
            response = self.twitter.post(
                f"https://api.twitter.com/1.1/statuses/retweet/{tweet_id}.json"
            )
            
            if response.status_code == 200:
                print("✅ Retweet successful!")
                return True
            else:
                print(f"❌ Retweet failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error retweeting: {e}")
            return False

    def reply_to_replies(self, tweet_id):
        """Replies to responses on our tweets"""
        try:
            response = self.twitter.get(
                "https://api.twitter.com/1.1/search/tweets.json",
                params={
                    "q": f"to:{self.username}",
                    "since_id": tweet_id,
                    "tweet_mode": "extended"
                }
            )
            
            if response.status_code == 200:
                replies = response.json()['statuses']
                for reply in replies:
                    if str(reply['in_reply_to_status_id']) == tweet_id:
                        engagement_reply = self.generate_quick_reply({
                            'text': reply['full_text'],
                            'author': reply['user']['screen_name']
                        })
                        if engagement_reply:
                            self.post_reply(reply['id_str'], engagement_reply)
                            time.sleep(random.randint(1, 5))
            
        except Exception as e:
            print(f"Error processing replies: {e}")
            traceback.print_exc()

    def check_growth_metrics(self):
        """Monitors follower growth and engagement"""
        try:
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
                
                # Print growth metrics
                print(f"\n📊 Daily Growth: {daily_growth} followers")
                print(f"📈 Engagement Rate: {self.daily_stats['engagement_rate']:.2f}")
                
        except Exception as e:
            print(f"Error checking metrics: {e}")
            traceback.print_exc()

def main():
    print("\n=== Starting Bot ===\n")
    
    try:
        # Initialize bot
        bot = TwitterBot()
        
        while True:
            try:
                # Check metrics first
                bot.check_growth_metrics()
                
                # Find and process recent tweets
                recent_tweets = bot.find_recent_tweets()
                print(f"Found {len(recent_tweets)} recent tweets")
                
                for tweet in recent_tweets:
                    if bot.should_engage(tweet):
                        # Generate and post reply
                        reply = bot.generate_quick_reply(tweet)
                        if reply:
                            reply_id = bot.post_reply(tweet['id'], reply)
                            if reply_id:
                                # Retweet after successful reply
                                bot.retweet(tweet['id'])
                                # Check for responses after a while
                                time.sleep(random.randint(30, 60))
                                bot.reply_to_replies(reply_id)
                
                if not recent_tweets:
                    print("No recent tweets found this time")
                
                print("\nWaiting before next check...")
                time.sleep(random.randint(60, 180))  # Random wait 1-3 minutes
                
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(60)
                continue
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
