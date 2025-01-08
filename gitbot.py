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

print("=== Starting Enhanced Twitter Bot ===")

# API credentials
print("Loading credentials...")
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Enhanced Activity Limits
REPLIES_PER_TWO_HOURS = 10  # שינוי מ-5 ל-10
CONVERSATION_DEPTH_LIMIT = 5
MINIMUM_WAIT_BETWEEN_REPLIES = 1
REPLY_LIMIT = 50  # שינוי מ-30 ל-50
LAST_REPLY_TIME = {}
ACTIVE_CONVERSATIONS = {}

# Time and Activity Configuration
CURRENT_YEAR = datetime.utcnow().year
CURRENT_DATE = datetime.utcnow().strftime('%Y-%m-%d')
TWEET_AGE_LIMIT = 10  # שינוי מ-5 ל-10 דקות

# נמחק או נעיר את שורת PEAK_HOURS
# PEAK_HOURS = [13, 14, 15, 16, 19, 20, 21, 22]  # EST

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
        print("Initializing Twitter bot...")
        self.twitter = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret
        )
        
        # Get bot's user info using v1.1 API
        response = self.twitter.get(
            "https://api.twitter.com/1.1/account/verify_credentials.json"
        )
        
        if response.status_code == 200:
            user_data = response.json()
            self.username = str(user_data['id'])
            print(f"✅ Connected as: @{user_data['screen_name']}")
        else:
            print(f"❌ Twitter API response: {response.status_code}")
            print(f"Response text: {response.text}")
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

    def should_engage(self, tweet):
        """Enhanced smart engagement decision with rate limiting"""
        # Check two-hour reply limit
        two_hours_ago = datetime.utcnow() - timedelta(hours=2)
        recent_replies = sum(1 for time in self.LAST_REPLY_TIME.values() 
                           if time > two_hours_ago)
        
        if recent_replies >= REPLIES_PER_TWO_HOURS:
            print("Two-hour reply limit reached")
            return False

        # Rest of your existing should_engage logic here
        text_lower = tweet['text'].lower()
        engagement_score = 0
        
        # Content relevance (0-5 points)
        if any(topic.lower() in text_lower for topic in HOT_TOPICS):
            engagement_score += 3
            print(f"✅ Relevant topic found (+3)")
        if any(trend.lower() in text_lower for trend in self.get_trending_topics()):
            engagement_score += 2
            print(f"✅ Trending topic found (+2)")
            
        # Author importance (0-3 points)
        if tweet['author'] in TARGET_ACCOUNTS[:5]:
            engagement_score += 3
            print(f"✅ Top priority author (+3)")
        elif tweet['author'] in TARGET_ACCOUNTS[5:15]:
            engagement_score += 2
            print(f"✅ High priority author (+2)")
        elif tweet['author'] in TARGET_ACCOUNTS:
            engagement_score += 1
            print(f"✅ Target author (+1)")
        
        return engagement_score >= 1

    def load_daily_stats(self):
        """Load or initialize daily statistics"""
        today = datetime.utcnow().strftime('%Y-%m-%d')
        try:
            if os.path.exists(self.daily_stats_file):
                with open(self.daily_stats_file, 'r') as f:
                    stats = json.load(f)
                    if stats.get('date') == today:
                        self.daily_stats = stats
                        return
        except Exception as e:
            print(f"Error loading stats: {e}")

        # Initialize new daily stats
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
        """Save daily statistics"""
        try:
            with open(self.daily_stats_file, 'w') as f:
                json.dump(self.daily_stats, f)
        except Exception as e:
            print(f"Error saving stats: {e}")

    def get_trending_topics(self):
        """Gets current trending topics"""
        try:
            if (not self.last_trending_update or 
                (datetime.utcnow() - self.last_trending_update).total_seconds() >= 3600):
                
                response = self.twitter.get(
                    "https://api.twitter.com/1.1/trends/place.json?id=1"
                )
                if response.status_code == 200:
                    trends = response.json()
                    self.trending_cache = [trend['name'] for trend in trends[0]['trends']]
                    self.last_trending_update = datetime.utcnow()
                    
            return self.trending_cache
        except Exception as e:
            print(f"Error getting trends: {e}")
            return []

    def get_latest_news(self):
        """Gets latest AI and crypto news"""
        if (not self.last_news_check or 
            (datetime.utcnow() - self.last_news_check).total_seconds() >= 3600):
            
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
            
            self.last_news_check = datetime.utcnow()
        
        return self.current_news

    def analyze_engagement(self, tweet_text):
        """Analyzes if a tweet is likely to get engagement"""
        score = 0
        text_lower = tweet_text.lower()
        
        # Check for engaging elements
        if '?' in tweet_text:
            score += 2
        if any(hook.lower() in text_lower for hook in ENGAGEMENT_PATTERNS['hooks']):
            score += 3
        if any(word in text_lower for word in ['exclusive', 'breaking', 'leaked']):
            score += 2
        if len(tweet_text.split()) < 15:  # Shorter tweets often do better
            score += 1
        if any(topic.lower() in text_lower for topic in HOT_TOPICS):
            score += 2
            
        return score > 4

    def find_recent_tweets(self):
        """Finds very recent tweets from target accounts"""
        print("\nSearching for recent tweets...")
        recent_tweets = []
        
        for account in TARGET_ACCOUNTS:
            try:
                user_response = self.twitter.get(
                    f"https://api.twitter.com/1.1/users/show.json?screen_name={account}"
                )
                if user_response.status_code != 200:
                    continue
                
                user_id = user_response.json()['id_str']
                
                tweets_response = self.twitter.get(
                    f"https://api.twitter.com/1.1/statuses/user_timeline.json",
                    params={
                        "user_id": user_id,
                        "count": 5,
                        "tweet_mode": "extended"
                    }
                )
                
                if tweets_response.status_code == 200:
                    tweets = tweets_response.json()
                    for tweet in tweets:
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
                                'author': account,
                                'age_minutes': age_minutes
                            })
                            print(f"Found {age_minutes:.1f} minute old tweet from {account}")
            
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
                self.save_daily_stats()
                self.LAST_REPLY_TIME[tweet_id] = datetime.utcnow()
                return response.json()['id_str']
            else:
                print(f"❌ Reply failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def retweet(self, tweet_id):
        """Retweets a tweet"""
        print(f"\nRetweeting tweet {tweet_id}")
        try:
            response = self.twitter.post(
                f"https://api.twitter.com/1.1/statuses/retweet/{tweet_id}.json"
            )
            if response.status_code == 200:
                print("✅ Retweeted successfully!")
                return True
            else:
                print(f"❌ Retweet failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error retweeting: {e}")
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
                            time.sleep(30)  # Avoid rate limits
            
        except Exception as e:
            print(f"Error processing replies: {e}")

    def check_growth_metrics(self):
        """Monitors follower growth and engagement"""
        try:
            response = self.twitter.get(
                "https://api.twitter.com/1.1/users/show.json",
                params={"user_id": self.username}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Update daily stats
                self.daily_stats['followers'] = user_data['followers_count']
                self.daily_stats['following'] = user_data['friends_count']
                
                # Check if meeting goals
                daily_growth = (self.daily_stats['followers'] - 
                              self.daily_stats.get('previous_followers', 0))
                
                if daily_growth < FOLLOWER_GOALS['daily']:
                    print(f"⚠️ Daily growth below target: {daily_growth}/{FOLLOWER_GOALS['daily']}")
                
                self.save_daily_stats()
                
        except Exception as e:
            print(f"Error checking metrics: {e}")

def main():
    print("\n=== Starting Bot ===\n")
    
    try:
        # Initialize bot
        bot = TwitterBot()
        
        # Check metrics first
        bot.check_growth_metrics()
        
        # Find and process recent tweets
        recent_tweets = bot.find_recent_tweets()
        
        for tweet in recent_tweets:
            if bot.should_engage(tweet):
                # Retweet first
                bot.retweet(tweet['id'])
                
                # Then reply
                reply = bot.generate_quick_reply(tweet)
                if reply:
                    reply_id = bot.post_reply(tweet['id'], reply)
                    # Check replies to our reply after 5 minutes
                    if reply_id:
                        time.sleep(300)
                        bot.reply_to_replies(reply_id)
        
        if not recent_tweets:
            print("No recent tweets found this time")
        
        print("\n=== Done ===")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")

if __name__ == "__main__":
    main()
