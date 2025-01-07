from requests_oauthlib import OAuth1Session
import time
import random
import json
import openai
import os
from datetime import datetime

print("=== Starting Twitter Bot ===")

# Twitter API credentials
print("Loading credentials...")
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Bot's Strategy Configuration
VIRAL_STRATEGIES = [
    "Share controversial (but safe) AI predictions",
    "Post mind-blowing tech statistics",
    "Create AI vs Human debates",
    "Share 'insider' tech industry insights",
    "Make bold cryptocurrency predictions",
    "Share 'secret' AI development stories",
    "Reveal 'unknown' tech industry facts",
    "Share 'exclusive' AI research findings"
]

BOT_PERSONA = """You are an AI expert sharing insider knowledge about AI and tech. Your tweets should be:
1. Controversial but safe
2. Highly engaging
3. Create curiosity
4. Share "insider" perspectives
5. Focus on AI, tech, and future trends
6. Use psychology triggers (curiosity, FOMO, surprise)
7. Create viral-worthy content"""

class TwitterBot:
    def __init__(self):
        print("Initializing TwitterBot...")
        self.twitter = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret
        )
        self.last_tweet_time = None
        print("TwitterBot initialized")

    def test_connections(self):
        """Test API connections"""
        print("\nTesting Twitter API connection...")
        try:
            response = self.twitter.get("https://api.twitter.com/2/users/me")
            if response.status_code == 200:
                print("✅ Twitter API connection successful!")
                print(f"Connected as: {response.json()['data']['username']}")
            else:
                print(f"❌ Twitter API connection failed: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"❌ Error connecting to Twitter: {e}")

    def get_trending_topics(self):
        """Gets current trending topics"""
        try:
            response = self.twitter.get(
                "https://api.twitter.com/1.1/trends/place.json?id=1"
            )
            if response.status_code == 200:
                trends = [trend['name'] for trend in response.json()[0]['trends']]
                tech_trends = [t for t in trends if any(word in t.lower() for word in ['ai', 'tech', 'crypto', 'digital'])]
                return tech_trends
            return []
        except Exception as e:
            print(f"Error getting trends: {e}")
            return []

    def generate_smart_tweet(self):
        """Generates an intelligent tweet using strategies"""
        strategy = random.choice(VIRAL_STRATEGIES)
        trends = self.get_trending_topics()
        trend_context = f" Consider these trending topics: {', '.join(trends[:3])}" if trends else ""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": BOT_PERSONA},
                    {"role": "user", "content": f"Create a viral tweet using this strategy: {strategy}.{trend_context}"}
                ],
                max_tokens=100,
                temperature=0.9
            )
            tweet_content = response.choices[0].message['content'].strip()
            print(f"Generated tweet: {tweet_content}")
            return tweet_content
        except Exception as e:
            print(f"Error generating tweet: {e}")
            return None

    def post_tweet(self, text):
        """Posts a tweet"""
        if not text:
            return None
            
        # Don't tweet too frequently
        if self.last_tweet_time and time.time() - self.last_tweet_time < 3600:  # 1 hour
            print("Waiting to avoid rate limits...")
            return None

        print(f"\nPosting tweet: {text}")
        try:
            response = self.twitter.post(
                "https://api.twitter.com/2/tweets",
                json={"text": text}
            )
            if response.status_code == 201:
                print("✅ Tweet posted successfully!")
                self.last_tweet_time = time.time()
                return response.json()['data']['id']
            else:
                print(f"❌ Failed to post tweet: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error posting tweet: {e}")
            return None

    def run_cycle(self):
        """Runs one complete bot cycle"""
        print("\n=== Starting New Cycle ===")
        
        # Generate and post main tweet
        tweet_content = self.generate_smart_tweet()
        if tweet_content:
            self.post_tweet(tweet_content)
        
        # Check trends and maybe post about them
        trends = self.get_trending_topics()
        if trends:
            trend_tweet = self.generate_smart_tweet()  # This will include trends automatically
            if trend_tweet:
                self.post_tweet(trend_tweet)

def main():
    print("\n=== Main Program Starting ===\n")
    
    try:
        # Initialize bot
        bot = TwitterBot()
        
        # Test connections
        bot.test_connections()
        
        # Run initial cycle
        bot.run_cycle()
        
        # Keep running every hour
        while True:
            time.sleep(3600)  # Wait 1 hour
            bot.run_cycle()
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")

if __name__ == "__main__":
    main()
