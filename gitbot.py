import os
import json
import time
import random
import traceback
from datetime import datetime, timedelta
import pytz
import requests
from bs4 import BeautifulSoup
import openai
from requests_oauthlib import OAuth1Session

print("=== Starting Enhanced Twitter Bot ===")

# API credentials validation
print("Loading and validating credentials...")
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Validate credentials
assert consumer_key, "Missing CONSUMER_KEY"
assert consumer_secret, "Missing CONSUMER_SECRET"
assert access_token, "Missing ACCESS_TOKEN"
assert access_token_secret, "Missing ACCESS_TOKEN_SECRET"
assert openai.api_key, "Missing OPENAI_API_KEY"

print("✅ All credentials validated")

# Rest of configurations remain the same...

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
        
        # Test connection and get rate limits
        try:
            response = self.twitter.get(
                "https://api.twitter.com/2/users/me"
            )
            response.raise_for_status()
            user_data = response.json()
            
            if 'data' in user_data:
                self.user_id = user_data['data']['id']
                self.username = user_data['data']['username']
                print(f"✅ Connected as: @{self.username} (ID: {self.user_id})")
                
                # Get rate limits
                limits = self.twitter.get("https://api.twitter.com/1.1/application/rate_limit_status.json")
                print(f"Rate limits: {limits.status_code}")
                
                # Initialize stats
                self.daily_stats = {
                    'date': datetime.utcnow().strftime('%Y-%m-%d'),
                    'tweets': 0,
                    'replies': 0,
                    'followers': 0,
                    'following': 0,
                    'previous_followers': 0,
                    'engagement_rate': 0.0
                }
                print("Stats initialized in memory")
            else:
                raise Exception("Invalid user data structure")
                
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            raise

    def find_recent_tweets(self):
        """Finds recent tweets from target accounts"""
        print("\nSearching for recent tweets...")
        recent_tweets = []
        
        try:
            # Convert usernames to IDs first
            user_ids = []
            for account in TARGET_ACCOUNTS[:5]:
                try:
                    response = self.twitter.get(
                        f"https://api.twitter.com/2/users/by/username/{account}"
                    )
                    if response.status_code == 200:
                        user_data = response.json()
                        if 'data' in user_data:
                            user_ids.append(user_data['data']['id'])
                except Exception as e:
                    print(f"Error getting user ID for {account}: {e}")
                    continue
            
            # Get tweets from these users
            for user_id in user_ids:
                try:
                    response = self.twitter.get(
                        f"https://api.twitter.com/2/users/{user_id}/tweets",
                        params={
                            "max_results": 10,
                            "tweet.fields": "created_at,public_metrics"
                        }
                    )
                    
                    if response.status_code == 200:
                        tweets_data = response.json()
                        if 'data' in tweets_data:
                            for tweet in tweets_data['data']:
                                created_at = datetime.strptime(
                                    tweet['created_at'],
                                    '%Y-%m-%dT%H:%M:%S.%fZ'
                                )
                                age_minutes = (
                                    datetime.utcnow() - created_at
                                ).total_seconds() / 60
                                
                                if age_minutes <= TWEET_AGE_LIMIT:
                                    metrics = tweet.get('public_metrics', {})
                                    recent_tweets.append({
                                        'id': tweet['id'],
                                        'text': tweet['text'],
                                        'author': user_id,
                                        'age_minutes': age_minutes,
                                        'likes': metrics.get('like_count', 0),
                                        'retweets': metrics.get('retweet_count', 0)
                                    })
                                    print(f"Added tweet from user {user_id}")
                                    
                except Exception as e:
                    print(f"Error getting tweets for user {user_id}: {e}")
                    continue
                    
            print(f"Found {len(recent_tweets)} suitable tweets")
            
        except Exception as e:
            print(f"Error in find_recent_tweets: {e}")
            traceback.print_exc()
        
        return recent_tweets

    def post_reply(self, tweet_id, reply_text):
        """Posts a reply to a tweet"""
        try:
            print(f"\nPosting reply: {reply_text[:50]}...")
            
            response = self.twitter.post(
                "https://api.twitter.com/2/tweets",
                json={
                    "text": reply_text,
                    "reply": {
                        "in_reply_to_tweet_id": tweet_id
                    }
                }
            )
            
            print(f"Response: {response.status_code}, Content: {response.text}")
            
            if response.status_code in [200, 201]:
                print("✅ Reply posted successfully!")
                self.daily_stats['replies'] += 1
                return response.json()['data']['id']
            else:
                print(f"❌ Reply failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error posting reply: {e}")
            traceback.print_exc()
            return None

    def check_growth_metrics(self):
        """Monitors follower growth and engagement"""
        try:
            print("\nChecking growth metrics...")
            
            response = self.twitter.get(
                f"https://api.twitter.com/2/users/{self.user_id}",
                params={"user.fields": "public_metrics"}
            )
            
            if response.status_code == 200:
                user_data = response.json()['data']
                metrics = user_data.get('public_metrics', {})
                
                # Update daily stats
                self.daily_stats['followers'] = metrics.get('followers_count', 0)
                self.daily_stats['following'] = metrics.get('following_count', 0)
                
                # Calculate growth
                daily_growth = (self.daily_stats['followers'] - 
                              self.daily_stats['previous_followers'])
                
                # Update engagement rate
                if self.daily_stats['tweets'] > 0:
                    self.daily_stats['engagement_rate'] = (
                        metrics.get('tweet_count', 0) / 
                        self.daily_stats['tweets']
                    )
                
                print(f"📊 Daily Growth: {daily_growth} followers")
                print(f"📈 Engagement Rate: {self.daily_stats['engagement_rate']:.2f}")
                
        except Exception as e:
            print(f"Error checking metrics: {e}")
            traceback.print_exc()

    # Other methods remain unchanged...

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
                traceback.print_exc()
                time.sleep(60)
                continue
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
