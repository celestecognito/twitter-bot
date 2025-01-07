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
    "Make bold cryptocurrency predictions"
]

BOT_PERSONA = """You are an AI expert sharing insider knowledge about AI and tech. Your tweets should be:
1. Controversial but safe
2. Highly engaging
3. Create curiosity
4. Share "insider" perspectives
5. Focus on AI, tech, and future trends"""

class TwitterBot:
    def __init__(self):
        print("Initializing TwitterBot...")
        self.twitter = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret
        )
        print("TwitterBot initialized")

    def test_connections(self):
        """Test API connections"""
        print("\nTesting connections...")
        try:
            response = self.twitter.get("https://api.twitter.com/2/users/me")
            if response.status_code == 200:
                print("✅ Twitter API: OK")
            else:
                print(f"❌ Twitter API failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Twitter error: {e}")

    def generate_smart_tweet(self):
        """Generates an intelligent tweet"""
        strategy = random.choice(VIRAL_STRATEGIES)
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": BOT_PERSONA},
                    {"role": "user", "content": f"Create a viral tweet using: {strategy}"}
                ],
                max_tokens=100,
                temperature=0.9
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            print(f"Error generating tweet: {e}")
            return None

    def post_tweet(self, text):
        """Posts a tweet"""
        print(f"\nPosting tweet: {text}")
        try:
            response = self.twitter.post(
                "https://api.twitter.com/2/tweets",
                json={"text": text}
            )
            if response.status_code == 201:
                print("✅ Tweet posted!")
                return True
            else:
                print(f"❌ Tweet failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

def main():
    print("\n=== Starting Bot ===\n")
    
    try:
        # Initialize and test
        bot = TwitterBot()
        bot.test_connections()
        
        # Generate and post one tweet
        tweet = bot.generate_smart_tweet()
        if tweet:
            bot.post_tweet(tweet)
        
        print("\n=== Done ===")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")

if __name__ == "__main__":
    main()
