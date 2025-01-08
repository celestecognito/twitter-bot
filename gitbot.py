from requests_oauthlib import OAuth1Session
import time
import random
import json
import openai
import os
from datetime import datetime, timedelta, UTC
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
CURRENT_YEAR = datetime.now(UTC).year
CURRENT_DATE = datetime.now(UTC).strftime('%Y-%m-%d')
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

# Engagement Templates
VIRAL_TEMPLATES = [
    "BREAKING: My sources indicate {prediction} 🤖",
    "The truth about {topic} that no one is talking about 🤫",
    "Just learned from insider sources: {insight} 👀",
    "LEAKED: {information} 🔥",
    "Why {common_belief} is wrong, and what's really happening 🧵",
    "🚨 ALERT: {urgent_news}",
    "Inside scoop on {topic} 💎",
    "What they're not telling you about {topic} 🔓"
]

ENGAGEMENT_PATTERNS = {
    'questions': [
        'What if', 'Have you considered', 'Why do you think',
        'How will this affect', 'When do you expect'
    ],
    'hooks': [
        'LEAKED:', 'Inside sources confirm:', 'My AI analysis shows:',
        'Breaking update:', 'Exclusive insight:'
    ],
    'engagement': [
        'Agree?', 'Thoughts?', "What's your take?",
        'Your view?', 'Predictions?'
    ]
}

# News Sources for Research
NEWS_SOURCES = [
    "https://cointelegraph.com/",
    "https://www.theverge.com/ai-artificial-intelligence",
    "https://techcrunch.com/artificial-intelligence/",
    "https://www.coindesk.com/",
    "https://www.wired.com/tag/artificial-intelligence/",
    "https://venturebeat.com/category/ai/"
]

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
        print("\n=== Bot Initialization ===")
        print("Setting up Twitter session...")
        try:
            self.twitter = OAuth1Session(
                consumer_key,
                client_secret=consumer_secret,
                resource_owner_key=access_token,
                resource_owner_secret=access_token_secret
            )
            print("✅ Twitter session created")
            
            # Get bot's user info
            print("Getting bot user info...")
            response = self.twitter.get("https://api.twitter.com/2/users/me")
            print(f"Response status: {response.status_code}")
            if response.status_code == 200:
                self.username = response.json()['data']['id']
                print(f"✅ Bot ID: {self.username}")
            else:
                print(f"❌ Failed to get bot info: {response.text}")
                raise Exception("Failed to get bot user info")
                
            # Initialize tracking variables
            self.daily_stats_file = 'daily_stats.json'
            self.daily_stats = {}
            self.load_daily_stats()
            
            self.trending_cache = {}
            self.last_trending_update = None
            self.current_news = []
            self.last_news_check = None
            self.LAST_REPLY_TIME = {}
            
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            raise e
                def load_daily_stats(self):
        """Load or initialize daily statistics"""
        print("Loading daily stats...")
        today = datetime.now(UTC).strftime('%Y-%m-%d')
        try:
            if os.path.exists(self.daily_stats_file):
                with open(self.daily_stats_file, 'r') as f:
                    stats = json.load(f)
                    if stats.get('date') == today:
                        self.daily_stats = stats
                        print("✅ Loaded existing stats")
                        return
        except Exception as e:
            print(f"Error loading stats: {e}")

        # Initialize new daily stats
        print("Initializing new daily stats")
        self.daily_stats = {
            'date': today,
            'tweets': 0,
            'replies': 0,
            'followers': 0,
            'following': 0,
            'previous_followers': 0,
            'engagement_rate': 0.0
        }
        self.save_daily_stats()
        print("✅ New stats initialized")

    def save_daily_stats(self):
        """Save daily statistics"""
        try:
            with open(self.daily_stats_file, 'w') as f:
                json.dump(self.daily_stats, f)
            print("✅ Stats saved successfully")
        except Exception as e:
            print(f"❌ Error saving stats: {e}")

    # New function: Check growth metrics
    def check_growth_metrics(self):
        """Check and update growth metrics"""
        try:
            response = self.twitter.get(
                f"https://api.twitter.com/2/users/{self.username}",
                params={"user.fields": "public_metrics"}
            )
            if response.status_code == 200:
                metrics = response.json()['data']['public_metrics']
                self.daily_stats['followers'] = metrics['followers_count']
                self.daily_stats['following'] = metrics['following_count']
                self.save_daily_stats()
                return True
            return False
        except Exception as e:
            print(f"Error checking metrics: {e}")
            return False

    # New function: Reply to replies
    def reply_to_replies(self):
        """Reply to replies on our tweets"""
        try:
            response = self.twitter.get(
                f"https://api.twitter.com/2/users/{self.username}/mentions",
                params={
                    "max_results": 10,
                    "tweet.fields": "created_at,in_reply_to_user_id"
                }
            )
            if response.status_code != 200:
                return False

            mentions = response.json().get('data', [])
            for mention in mentions:
                if mention['in_reply_to_user_id'] == self.username:
                    self.process_tweet(mention)
            return True
        except Exception as e:
            print(f"Error processing replies: {e}")
            return False

    # New function: Retweet
    def retweet(self, tweet_id):
        """Retweet a tweet"""
        try:
            response = self.twitter.post(
                f"https://api.twitter.com/2/users/{self.username}/retweets",
                json={"tweet_id": tweet_id}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error retweeting: {e}")
            return False

    def should_engage(self, tweet):
        """Enhanced smart engagement decision with rate limiting"""
        # Check two-hour reply limit
        two_hours_ago = datetime.now(UTC) - timedelta(hours=2)
        recent_replies = sum(1 for time in self.LAST_REPLY_TIME.values() 
                           if time > two_hours_ago)
        
        if recent_replies >= REPLIES_PER_TWO_HOURS:
            print("Two-hour reply limit reached")
            return False

        # Check if we replied to this tweet already
        if tweet['id'] in self.LAST_REPLY_TIME:
            print("Already replied to this tweet")
            return False

        # Check if tweet is from a priority account
        if tweet['author'] in TECH_AI_LEADERS[:5]:
            print(f"✅ Priority account found: {tweet['author']}")
            return True
            
        return False

    def get_trending_topics(self):
        """Gets current trending topics"""
        try:
            if (not self.last_trending_update or 
                (datetime.now(UTC) - self.last_trending_update).total_seconds() >= 3600):
                
                response = self.twitter.get(
                    "https://api.twitter.com/2/trends/place?id=1"
                )
                if response.status_code == 200:
                    trends = response.json()
                    self.trending_cache = {
                        trend['name']: trend['tweet_volume']
                        for trend in trends[0]['trends']
                        if trend['tweet_volume']
                    }
                    self.last_trending_update = datetime.now(UTC)
                    
            return self.trending_cache
        except Exception as e:
            print(f"Error getting trends: {e}")
            return {}

    def get_latest_news(self):
        """Gets latest AI and crypto news"""
        if (not self.last_news_check or 
            (datetime.now(UTC) - self.last_news_check).total_seconds() >= 3600):
            
            self.current_news = []
            for source in NEWS_SOURCES:
                try:
                    response = requests.get(source, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        headlines = soup.find_all(['h1', 'h2'])[:5]
                        self.current_news.extend([h.text.strip() for h in headlines])
                except Exception as e:
                    print(f"Error fetching news from {source}: {e}")
            
            self.last_news_check = datetime.now(UTC)
        
        return self.current_news

    def find_recent_tweets(self):
        """Finds very recent tweets from target accounts"""
        print("\n=== Searching Recent Tweets ===")
        recent_tweets = []
        
        for account in TECH_AI_LEADERS[:5]:
            print(f"\nChecking account: {account}")
            try:
                print("Getting user ID...")
                user_response = self.twitter.get(
                    f"https://api.twitter.com/2/users/by/username/{account}"
                )
                print(f"User response status: {user_response.status_code}")
                
                if user_response.status_code != 200:
                    print(f"❌ Failed to get user info for {account}")
                    continue
                
                user_id = user_response.json()['data']['id']
                print(f"✅ Got user ID: {user_id}")
                
                print("Getting recent tweets...")
                tweets_response = self.twitter.get(
                    f"https://api.twitter.com/2/users/{user_id}/tweets",
                    params={
                        "max_results": 5,
                        "tweet.fields": "created_at,public_metrics"
                    }
                )
                
                if tweets_response.status_code == 200:
                    tweets = tweets_response.json()['data']
                    for tweet in tweets:
                        created_at = datetime.strptime(
                            tweet['created_at'], 
                            '%Y-%m-%dT%H:%M:%S.%fZ'
                        ).replace(tzinfo=UTC)
                        age_minutes = (
                            datetime.now(UTC) - created_at
                        ).total_seconds() / 60
                        
                        if age_minutes <= TWEET_AGE_LIMIT:
                            recent_tweets.append({
                                'id': tweet['id'],
                                'text': tweet['text'],
                                'author': account,
                                'age_minutes': age_minutes,
                                'metrics': tweet.get('public_metrics', {})
                            })
                            print(f"Found {age_minutes:.1f} minute old tweet from {account}")
                else:
                    print(f"❌ Failed to get tweets for {account}")
            
            except Exception as e:
                print(f"Error processing {account}: {e}")
                continue
        
        return recent_tweets

    def generate_quick_reply(self, tweet):
        """Enhanced quick reply generation"""
        try:
            # Get trending topics and news
            trends = self.get_trending_topics()
            latest_news = self.get_latest_news()
            
            relevant_trends = [
                trend for trend in trends
                if any(topic.lower() in trend.lower() for topic in HOT_TOPICS)
            ]
            
            # Add context to prompt
            context = f"\nCurrent date: {CURRENT_DATE}"
            if relevant_trends:
                context += f"\nRelevant trending topics: {', '.join(relevant_trends[:3])}"
            if latest_news:
                context += f"\nLatest headlines: {'; '.join(latest_news[:2])}"
            
            # Add engagement patterns
            engagement_suffix = random.choice(ENGAGEMENT_PATTERNS['engagement'])
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": BOT_PERSONA + context},
                    {"role": "user", "content": 
                     f"Create an engaging reply to: '{tweet['text']}' by {tweet['author']}. "
                     f"Make it viral and relate to trends if relevant. "
                     f"End with '{engagement_suffix}' if appropriate. "
                     f"DO NOT use quotes and keep it short and impactful."}
                ],
                max_tokens=60,
                temperature=0.9
            )
            
            reply = response.choices[0].message['content'].strip()
            reply = reply.replace('"', '')
            
            # Add hashtags strategically
            relevant_hashtags = [
                tag for tag in VIRAL_HASHTAGS
                if any(topic.lower() in tag.lower() for topic in HOT_TOPICS)
            ]
            if relevant_hashtags:
                hashtags = " ".join(random.sample(relevant_hashtags, min(2, len(relevant_hashtags))))
                reply = f"{reply} {hashtags}"
            
            return reply
            
        except Exception as e:
            print(f"Error generating reply: {e}")
            return None

    def post_reply(self, tweet_id, reply_text):
        """Posts a reply to a tweet with limit checking"""
        if self.daily_stats['replies'] >= REPLY_LIMIT:
            print("⚠️ Daily reply limit reached")
            return False

        print(f"\nPosting reply: {reply_text}")
        try:
            response = self.twitter.post(
                "https://api.twitter.com/2/tweets",
                json={
                    "text": reply_text,
                    "reply": {"in_reply_to_tweet_id": tweet_id}
                }
            )
            if response.status_code == 201:
                print("✅ Reply posted successfully!")
                self.daily_stats['replies'] += 1
                self.save_daily_stats()
                self.LAST_REPLY_TIME[tweet_id] = datetime.now(UTC)
                return response.json()['data']['id']
            else:
                print(f"❌ Reply failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error posting reply: {e}")
            return False

    def process_tweet(self, tweet):
        """Process a single tweet"""
        try:
            reply = self.generate_quick_reply(tweet)
            if reply:
                reply_id = self.post_reply(tweet['id'], reply)
                if reply_id:
                    print(f"✅ Successfully processed tweet from {tweet['author']}")
                    time.sleep(MINIMUM_WAIT_BETWEEN_REPLIES * 60)
        except Exception as e:
            print(f"Error processing tweet: {e}")

def main():
    print("\n=== Starting Bot ===\n")
    
    try:
        print("Creating bot instance...")
        bot = TwitterBot()
        print("Bot instance created successfully")
        
        print("\nStarting main loop...")
        while True:
            print("\n=== New Iteration ===")
            
            # Check growth metrics every iteration
            bot.check_growth_metrics()
            
            # Find and process recent tweets
            recent_tweets = bot.find_recent_tweets()
            print(f"Found {len(recent_tweets)} recent tweets")
            
            for tweet in recent_tweets:
                if bot.should_engage(tweet):
                    bot.process_tweet(tweet)
            
            # Process replies to our tweets
            bot.reply_to_replies()
            
            print("Waiting 5 minutes before next check...")
            time.sleep(300)
            
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        raise e

if __name__ == "__main__":
    main()
