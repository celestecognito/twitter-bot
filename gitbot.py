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

        print("\nTesting OpenAI API connection...")
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Say 'Hello'"}],
                max_tokens=10
            )
            print("✅ OpenAI API connection successful!")
            print(f"OpenAI response: {response.choices[0].message['content']}")
        except Exception as e:
            print(f"❌ Error connecting to OpenAI: {e}")

    def post_tweet(self, text):
        """Posts a tweet"""
        print(f"\nTrying to post tweet: {text}")
        try:
            response = self.twitter.post(
                "https://api.twitter.com/2/tweets",
                json={"text": text}
            )
            if response.status_code == 201:
                print("✅ Tweet posted successfully!")
                return response.json()['data']['id']
            else:
                print(f"❌ Failed to post tweet: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error posting tweet: {e}")
            return None

    def generate_tweet(self):
        """Generates a tweet using OpenAI"""
        print("\nGenerating tweet content...")
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Create a short, engaging tweet about AI or technology."},
                    {"role": "user", "content": "Generate a tweet"}
                ],
                max_tokens=100,
                temperature=0.9
            )
            tweet_content = response.choices[0].message['content'].strip()
            print(f"Generated tweet: {tweet_content}")
            return tweet_content
        except Exception as e:
            print(f"❌ Error generating tweet: {e}")
            return None

def main():
    print("\n=== Main Program Starting ===\n")
    
    try:
        # Initialize bot
        bot = TwitterBot()
        
        # Test connections
        bot.test_connections()
        
        # Generate and post a tweet
        print("\nTrying to generate and post a tweet...")
        tweet_content = bot.generate_tweet()
        if tweet_content:
            bot.post_tweet(tweet_content)
        
        print("\n=== Program Complete ===")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")

if __name__ == "__main__":
    main()
