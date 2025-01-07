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

# Enhanced Bot Configuration
TWEET_AGE_LIMIT = 5  # Reduced to 5 minutes for faster responses
PEAK_HOURS = [13, 14, 15, 16, 19, 20, 21, 22]  # Optimal posting times (EST)

# News Sources for staying updated
NEWS_SOURCES = [
    "https://cointelegraph.com/",
    "https://www.theverge.com/ai-artificial-intelligence",
    "https://techcrunch.com/artificial-intelligence/",
    "https://www.coindesk.com/"
]

TARGET_ACCOUNTS = [
    # Tech & AI Leaders
    "elonmusk", "sama", "naval", "lexfridman",
    # Crypto Leaders
    "cz_binance", "VitalikButerin", "michael_saylor",
    "tyler", "cameron", "aantonop", "DocumentingBTC",
    # AI Companies
    "OpenAI", "anthropic", "DeepMind", "Google_AI",
    # Crypto Projects
    "ethereum", "binance", "BitcoinMagazine", "CoinDesk",
    # Tech News
    "TechCrunch", "WIRED", "TheVerge",
    # AI Researchers
    "karpathy", "ylecun", "demishassabis"
]
HOT_TOPICS = [
    # AI Topics
    "AGI timeline", "AI consciousness", "Quantum computing",
    "Brain-computer interfaces", "AI regulation", "Neural networks",
    # Crypto Topics
    "Bitcoin ETF", "Layer 2 scaling", "DeFi revolution",
    "Crypto regulation", "Web3 future", "NFT technology",
    "Bitcoin adoption", "Ethereum upgrades", "Smart contracts",
    "Blockchain AI", "Crypto mining", "Digital currency",
    "Metaverse", "DAO governance", "DeFi protocols"
]

VIRAL_HASHTAGS = [
    # AI Hashtags
    "#AI", "#AGI", "#Tech", "#Future", "#ChatGPT",
    # Crypto Hashtags
    "#Bitcoin", "#BTC", "#Ethereum", "#ETH", "#Crypto",
    "#Web3", "#DeFi", "#NFT", "#Blockchain", "#Binance"
]

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
    'questions': ['What if', 'Have you considered', 'Why do you think'],
    'hooks': ['LEAKED:', 'Inside sources confirm:', 'My AI analysis shows:'],
    'engagement': ['Agree?', 'Thoughts?', 'What's your take?']
}

# Time awareness
CURRENT_YEAR = datetime.now().year
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")

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
12. Always be aware of current events and trends
13. Never reference outdated information or past years as current"""

class TwitterBot:
    def __init__(self):
        print("Initializing TwitterBot...")
        self.twitter = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret
        )
        self.username = "CelesteCognito"
        self.daily_stats_file = "daily_stats.json"
        self.trending_cache = {}
        self.last_trending_update = None
        self.last_news_check = None
        self.current_news = []
        self.load_daily_stats()
        print("TwitterBot initialized")
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
            'replies': 0
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
                (datetime.utcnow() - self.last_trending_update).hours >= 1):
                
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
                    self.last_trending_update = datetime.utcnow()
                    
            return self.trending_cache
        except Exception as e:
            print(f"Error getting trends: {e}")
            return {}

    def get_latest_news(self):
        """Gets latest AI and crypto news"""
        if (not self.last_news_check or 
            (datetime.utcnow() - self.last_news_check).hours >= 1):
            
            self.current_news = []
            for source in NEWS_SOURCES:
                try:
                    response = requests.get(source)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        headlines = soup.find_all('h1')[:5]  # Get top 5 headlines
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
            
        return score > 4

    def find_recent_tweets(self):
        """Finds very recent tweets from target accounts"""
        print("\nSearching for recent tweets...")
        recent_tweets = []
        
        for account in TARGET_ACCOUNTS:
            try:
                user_response = self.twitter.get(
                    f"https://api.twitter.com/2/users/by/username/{account}"
                )
                if user_response.status_code != 200:
                    continue
                
                user_id = user_response.json()['data']['id']
                
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
                        created_at = datetime.strptime(tweet['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
                        age_minutes = (datetime.utcnow() - created_at).total_seconds() / 60
                        
                        if age_minutes <= TWEET_AGE_LIMIT:
                            recent_tweets.append({
                                'id': tweet['id'],
                                'text': tweet['text'],
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
            hashtags = " ".join(random.sample(relevant_hashtags, 2))
            
            return f"{reply} {hashtags}"
            
        except Exception as e:
            print(f"Error generating reply: {e}")
            return None

    def post_reply(self, tweet_id, reply_text):
        """Posts a reply to a tweet with limit checking"""
        if self.daily_stats['replies'] >= 20:
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
                print("✅ Reply posted!")
                self.daily_stats['replies'] += 1
                self.save_daily_stats()
                return True
            else:
                print(f"❌ Reply failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def retweet(self, tweet_id):
        """Retweets a tweet"""
        print(f"\nRetweeting tweet {tweet_id}")
        try:
            response = self.twitter.post(
                f"https://api.twitter.com/2/users/{self.username}/retweets",
                json={"tweet_id": tweet_id}
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

    def should_engage(self, tweet):
        """Enhanced engagement decision"""
        if self.daily_stats['replies'] >= 20:
            print("Daily reply limit reached")
            return False
            
        # Basic checks
        text_lower = tweet['text'].lower()
        relevant_topics = any(topic.lower() in text_lower for topic in HOT_TOPICS)
        is_peak_hour = datetime.utcnow().hour in PEAK_HOURS
        is_priority = tweet['author'] in TARGET_ACCOUNTS[:10]
        
        # Enhanced checks
        is_trending = any(trend.lower() in text_lower 
                         for trend in self.get_trending_topics())
        is_engaging = self.analyze_engagement(tweet['text'])
        
        return ((relevant_topics or is_trending or is_priority) and 
                (is_peak_hour or is_engaging) and 
                tweet['age_minutes'] <= 5)

def main():
    print("\n=== Starting Bot ===\n")
    
    try:
        # Initialize bot
        bot = TwitterBot()
        
        # Find very recent tweets
        recent_tweets = bot.find_recent_tweets()
        
        # Process recent tweets
        for tweet in recent_tweets:
            if bot.should_engage(tweet):
                # Retweet first
                bot.retweet(tweet['id'])
                
                # Then reply
                reply = bot.generate_quick_reply(tweet)
                if reply:
                    bot.post_reply(tweet['id'], reply)
        
        if not recent_tweets:
            print("No recent tweets found this time")
        
        print("\n=== Done ===")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")

if __name__ == "__main__":
    main()
