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

REPLIES_PER_TWO_HOURS = 10
CONVERSATION_DEPTH_LIMIT = 5
MINIMUM_WAIT_BETWEEN_REPLIES = 0
REPLY_LIMIT = 500
TWEET_AGE_LIMIT = 30
LAST_REPLY_TIME = {}
ACTIVE_CONVERSATIONS = {}

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

CURRENT_YEAR = datetime.now(timezone.utc).year
CURRENT_DATE = datetime.now(timezone.utc).strftime('%Y-%m-%d')

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

TARGET_ACCOUNTS = (TECH_AI_LEADERS + CRYPTO_LEADERS + 
                  AI_COMPANIES + CRYPTO_PROJECTS + TECH_NEWS)

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

NEWS_SOURCES = [
    "https://cointelegraph.com/",
    "https://www.theverge.com/ai-artificial-intelligence",
    "https://techcrunch.com/artificial-intelligence/",
    "https://www.coindesk.com/",
    "https://www.wired.com/tag/artificial-intelligence/",
    "https://venturebeat.com/category/ai/"
]

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
        logger.info("Starting TwitterBot initialization...")
        try:
            logger.info("Creating OAuth session...")
            self.twitter = OAuth1Session(
                consumer_key,
                client_secret=consumer_secret,
                resource_owner_key=access_token,
                resource_owner_secret=access_token_secret
            )
            logger.info("OAuth session created successfully")
            
            logger.info("Getting user info...")
            response = self.twitter.get(
                "https://api.twitter.com/2/users/me",
                params={"user.fields": "id,username,public_metrics"}
            )
            logger.info(f"Twitter API Response Status: {response.status_code}")
            logger.info(f"Twitter API Response: {response.text}")
            
            if response.status_code == 429:
                logger.warning("Rate limit hit - waiting 30 seconds")
                time.sleep(30)
                response = self.twitter.get(
                    "https://api.twitter.com/2/users/me",
                    params={"user.fields": "id,username,public_metrics"}
                )
            
            if response.status_code == 200:
                user_data = response.json()['data']
                self.user_id = user_data['id']
                self.username = user_data['username']
                logger.info(f"✅ Successfully authenticated as @{self.username}")
                
                self.daily_stats_file = 'daily_stats.json'
                self.daily_stats = {
                    'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                    'tweets': 0,
                    'replies': 0,
                    'followers': 0,
                    'following': 0,
                    'previous_followers': 0,
                    'engagement_rate': 0.0
                }
                
                self.load_daily_stats()
                self.trending_cache = {}
                self.last_trending_update = None
                self.current_news = []
                self.last_news_check = None
                self.LAST_REPLY_TIME = {}
                
            else:
                error_msg = f"Failed to get user info. Status: {response.status_code}"
                if response.status_code == 401:
                    error_msg += "\nAuthentication failed - check your API keys"
                logger.error(f"❌ {error_msg}")
                logger.error(f"Response: {response.text}")
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"❌ Initialization error: {str(e)}")
            traceback.print_exc()
            raise

    def load_daily_stats(self):
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        try:
            if os.path.exists(self.daily_stats_file):
                with open(self.daily_stats_file, 'r') as f:
                    stats = json.load(f)
                    if stats.get('date') == today:
                        self.daily_stats = stats
                        return
        except Exception as e:
            logger.error(f"Error loading stats: {e}")

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

    def save_daily_stats(self):
        try:
            with open(self.daily_stats_file, 'w') as f:
                json.dump(self.daily_stats, f)
        except Exception as e:
            logger.error(f"Error saving stats: {e}")

    def get_trending_topics(self):
        try:
            if (not self.last_trending_update or 
                (datetime.now(timezone.utc) - self.last_trending_update).total_seconds() >= 3600):
                
                response = self.twitter.get(
                    "https://api.twitter.com/2/trends/place?id=1"
                )
                if response.status_code == 429:
                    time.sleep(30)
                    return self.trending_cache
                    
                if response.status_code == 200:
                    trends = response.json()
                    self.trending_cache = {
                        trend['name']: trend['tweet_volume']
                        for trend in trends[0]['trends']
                        if trend['tweet_volume']
                    }
                    self.last_trending_update = datetime.now(timezone.utc)
                    
            return self.trending_cache
        except Exception as e:
            logger.error(f"Error getting trends: {e}")
            return {}

    def get_latest_news(self):
        if (not self.last_news_check or 
            (datetime.now(timezone.utc) - self.last_news_check).total_seconds() >= 3600):
            
            self.current_news = []
            for source in NEWS_SOURCES:
                try:
                    response = requests.get(source, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        headlines = soup.find_all(['h1', 'h2'])[:5]
                        self.current_news.extend([h.text.strip() for h in headlines])
                except Exception as e:
                    logger.error(f"Error fetching news from {source}: {e}")
            
            self.last_news_check = datetime.now(timezone.utc)
        
        return self.current_news

    def should_engage(self, tweet):
        try:
            two_hours_ago = datetime.now(timezone.utc) - timedelta(hours=2)
            recent_replies = sum(1 for time in self.LAST_REPLY_TIME.values() 
                               if time > two_hours_ago)
            
            if recent_replies >= REPLIES_PER_TWO_HOURS:
                logger.info("Two-hour reply limit reached")
                return False

            text_lower = tweet['text'].lower()
            
            if str(tweet['author']) in [str(acc) for acc in TECH_AI_LEADERS[:5]]:
                return True
                
            if any(topic.lower() in text_lower for topic in HOT_TOPICS):
                return True
                
            if tweet.get('likes', 0) > 100 or tweet.get('retweets', 0) > 20:
                return True
                
            return random.random() < 0.8
            
        except Exception as e:
            logger.error(f"Error in should_engage: {e}")
            return False

    def find_recent_tweets(self):
        logger.info("Searching for recent tweets...")
        recent_tweets = []
        
        for account in TARGET_ACCOUNTS[:5]:
            try:
                response = self.twitter.get(
                    f"https://api.twitter.com/2/users/by/username/{account}"
                )
                
                if response.status_code == 429:
                    time.sleep(30)
                    continue
                    
                if response.status_code == 200:
                    user_id = response.json()['data']['id']
                    
                    tweets_response = self.twitter.get(
                        f"https://api.twitter.com/2/users/{user_id}/tweets",
                        params={
                            "max_results": 10,
                            "tweet.fields": "created_at,public_metrics"
                        }
                    )
                    
                    if tweets_response.status_code == 429:
                        time.sleep(30)
                        continue
                        
                    if tweets_response.status_code == 200:
                        tweets = tweets_response.json()['data']
                        for tweet in tweets:
                            created_at = datetime.strptime(
                                tweet['created_at'], 
                                '%Y-%m-%dT%H:%M:%S.%fZ'
                            )
                            age_minutes = (
                                datetime.now(timezone.utc) - created_at
                            ).total_seconds() / 60
                            
                            if age_minutes <= TWEET_AGE_LIMIT:
                                recent_tweets.append({
                                    'id': tweet['id'],
                                    'text': tweet['text'],
                                    'author': account,
                                    'age_minutes': age_minutes,
                                    'metrics': tweet.get('public_metrics', {})
                                })
                                logger.info(f"Found {age_minutes:.1f} minute old tweet from {account}")
            
            except Exception as e:
                logger.error(f"Error processing {account}: {e}")
                traceback.print_exc()
                continue
        
        return recent_tweets

    def generate_quick_reply(self, tweet):
        try:
            trends = self.get_trending_topics()
            latest_news = self.get_latest_news()
            
            relevant_trends = [
                trend for trend in trends
                if any(topic.lower() in trend.lower() for topic in HOT_TOPICS)
            ]
            
            context = f"\nCurrent date: {CURRENT_DATE}"
            if relevant_trends:
                context += f"\nRelevant trending topics: {', '.join(relevant_trends[:3])}"
            if latest_news:
                context += f"\nLatest headlines: {'; '.join(latest_news[:2])}"
            
            engagement_suffix = random.choice(ENGAGEMENT_PATTERNS['engagement'])
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": BOT_PERSONA + context},
                    {"role": "user", "content": 
                     f"Create an engaging reply to: '{tweet['text']}' by {tweet['author']}. "
                     f"Make it viral and relate to trends if relevant. "
                     f"End with '{engagement_suffix}' if appropriate."}
                ],
                max_tokens=100,
                temperature=0.9
            )
            
            reply = response.choices[0].message['content'].strip()
            
            if random.random() < 0.3:
                hashtags = random.sample(VIRAL_HASHTAGS, 2)
                reply = f"{reply} {' '.join(hashtags)}"
                
            return reply
            
        except Exception as e:
            logger.error(f"Error generating reply: {e}")
            traceback.print_exc()
            return None

    def post_reply(self, tweet_id, reply_text):
        try:
            response = self.twitter.post(
                "https://api.twitter.com/2/tweets",
                json={
                    "text": reply_text,
                    "reply": {
                        "in_reply_to_tweet_id": tweet_id
                    }
                }
            )
            
            if response.status_code == 429:
                logger.warning("Rate limit hit while posting reply - waiting 30 seconds")
                time.sleep(30)
                return None
                
            if response.status_code in [200, 201]:
                logger.info("✅ Reply posted successfully!")
                self.daily_stats['replies'] += 1
                self.LAST_REPLY_TIME[tweet_id] = datetime.now(timezone.utc)
                return response.json()['data']['id']
            else:
                logger.error(f"❌ Reply failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error posting reply: {e}")
            traceback.print_exc()
            return None

    def retweet(self, tweet_id):
        try:
            response = self.twitter.post(
                f"https://api.twitter.com/2/users/{self.user_id}/retweets",
                json={"tweet_id": tweet_id}
            )
            
            if response.status_code == 429:
                logger.warning("Rate limit hit while retweeting - waiting 30 seconds")
                time.sleep(30)
                return False
                
            if response.status_code == 200:
                logger.info("✅ Retweeted successfully!")
                return True
            else:
                logger.error(f"❌ Retweet failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error retweeting: {e}")
            traceback.print_exc()
            return False

    def reply_to_replies(self, tweet_id):
        try:
            response = self.twitter.get(
                "https://api.twitter.com/2/tweets/search/recent",
                params={
                    "query": f"conversation_id:{tweet_id}",
                    "tweet.fields": "in_reply_to_user_id,author_id,created_at"
                }
            )
            
            if response.status_code == 429:
                logger.warning("Rate limit hit while getting replies - waiting 30 seconds")
                time.sleep(30)
                return
                
            if response.status_code == 200:
                replies = response.json().get('data', [])
                for reply in replies:
                    if reply['author_id'] != self.user_id:
                        engagement_reply = self.generate_quick_reply({
                            'text': reply['text'],
                            'author': reply['author_id']
                        })
                        if engagement_reply:
                            self.post_reply(reply['id'], engagement_reply)
                            time.sleep(random.randint(30, 60))
            else:
                logger.error(f"Failed to get replies. Status: {response.status_code}")
                logger.error(f"Response: {response.text}")
            
        except Exception as e:
            logger.error(f"Error processing replies: {e}")
            traceback.print_exc()

    def check_growth_metrics(self):
        try:
            response = self.twitter.get(
                f"https://api.twitter.com/2/users/{self.user_id}",
                params={"user.fields": "public_metrics"}
            )
            
            if response.status_code == 429:
                logger.warning("Rate limit hit while checking metrics - waiting 30 seconds")
                time.sleep(30)
                return
                
            if response.status_code == 200:
                user_data = response.json()['data']
                metrics = user_data.get('public_metrics', {})
                
                self.daily_stats['followers'] = metrics.get('followers_count', 0)
                self.daily_stats['following'] = metrics.get('following_count', 0)
                
                daily_growth = (self.daily_stats['followers'] - 
                              self.daily_stats.get('previous_followers', 0))
                
                if daily_growth < FOLLOWER_GOALS['daily']:
                    logger.warning(f"⚠️ Daily growth below target: {daily_growth}/{FOLLOWER_GOALS['daily']}")
                
                if self.daily_stats['tweets'] > 0:
                    self.daily_stats['engagement_rate'] = (
                        metrics.get('tweet_count', 0) / 
                        self.daily_stats['tweets']
                    )
                
                self.save_daily_stats()
                
            else:
                logger.error(f"Failed to check metrics. Status: {response.status_code}")
                logger.error(f"Response: {response.text}")
                
        except Exception as e:
            logger.error(f"Error checking metrics: {e}")
            traceback.print_exc()

def main():
    logger.info("=== Starting Bot ===")
    
    try:
        logger.info("Initializing TwitterBot...")
        bot = TwitterBot()
        logger.info("Bot initialized successfully")
        
        while True:
            try:
                logger.info("--- Starting new cycle ---")
                logger.info("Checking growth metrics...")
                bot.check_growth_metrics()
                
                recent_tweets = bot.find_recent_tweets()
                logger.info(f"Processing {len(recent_tweets)} tweets")
                
                for tweet in recent_tweets:
                    if bot.should_engage(tweet):
                        bot.retweet(tweet['id'])
                        reply = bot.generate_quick_reply(tweet)
                        if reply:
                            reply_id = bot.post_reply(tweet['id'], reply)
                            if reply_id:
                                logger.info("Tweet processed successfully")
                                time.sleep(random.randint(30, 60))
                                bot.reply_to_replies(reply_id)
                
                logger.info("Waiting before next check...")
                time.sleep(random.randint(60, 180))
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                traceback.print_exc()
                time.sleep(60)
                continue
        
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
