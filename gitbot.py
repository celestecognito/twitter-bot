from requests_oauthlib import OAuth1Session
import time
import random
import json
import openai
import os
from datetime import datetime, timedelta

print("=== Starting Twitter Bot ===")

# Twitter API credentials
print("Loading credentials...")
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Bot Configuration
TWEET_AGE_LIMIT = 10  # Only react to tweets less than 10 minutes old

TARGET_ACCOUNTS = [
    "elonmusk",    # Elon Musk
    "sama",        # Sam Altman
    "naval",       # Naval
    "lexfridman",  # Lex Fridman
    "karpathy",    # Andrej Karpathy
    "ylecun",      # Yann LeCun
    "OpenAI",      # OpenAI
    "anthropic",   # Anthropic
    "DeepMind"     # DeepMind
]

BOT_PERSONA = """You are Celeste Cognito, an AI expert with controversial but intriguing views.
Your style when replying to tweets:
1. Quick, sharp insights
2. Mysterious but knowledgeable
3. Often hints at "insider information"
4. Challenges assumptions intelligently
5. Creates intrigue and curiosity
6. Keep responses short and engaging
7. Use emojis occasionally for engagement"""

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
        print("TwitterBot initialized")

    def find_recent_tweets(self):
        """Finds very recent tweets from target accounts"""
        print("\nSearching for recent tweets...")
        recent_tweets = []
        
        for account in TARGET_ACCOUNTS:
            try:
                # Get user ID
                user_response = self.twitter.get(
                    f"https://api.twitter.com/2/users/by/username/{account}"
                )
                if user_response.status_code != 200:
                    continue
                
                user_id = user_response.json()['data']['id']
                
                # Get latest tweets
                tweets_response = self.twitter.get(
                    f"https://api.twitter.com/2/users/{user_id}/tweets",
                    params={
                        "max_results": 5,  # Only get the 5 most recent tweets
                        "tweet.fields": "created_at,public_metrics"
                    }
                )
                
                if tweets_response.status_code == 200:
                    tweets = tweets_response.json()['data']
                    for tweet in tweets:
                        created_at = datetime.strptime(tweet['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
                        age_minutes = (datetime.utcnow() - created_at).total_seconds() / 60
                        
                        # Only process very recent tweets
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
        """Generates a quick, engaging reply"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": BOT_PERSONA},
                    {"role": "user", "content": f"Create a quick, engaging reply to this new tweet: '{tweet['text']}' by {tweet['author']}. Keep it short and impactful."}
                ],
                max_tokens=60,  # Shorter replies for quicker generation
                temperature=0.9
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            print(f"Error generating reply: {e}")
            return None

    def post_reply(self, tweet_id, reply_text):
        """Posts a reply to a tweet"""
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

def main():
    print("\n=== Starting Bot ===\n")
    
    try:
        # Initialize bot
        bot = TwitterBot()
        
        # Find very recent tweets
        recent_tweets = bot.find_recent_tweets()
        
        # Process recent tweets
        for tweet in recent_tweets:
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
