from requests_oauthlib import OAuth1Session
import time
import random
import json
import openai
import os
from datetime import datetime, timedelta

print("=== Starting Enhanced Twitter Bot ===")

# [כל הקונפיגורציה הקיימת נשארת אותו דבר עד class TwitterBot]

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
        # Add daily limits tracking
        self.daily_stats_file = "daily_stats.json"
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

    def find_recent_tweets(self):
        """[משאיר את הפונקציה הקיימת ללא שינוי]"""
        # הקוד הקיים נשאר אותו דבר

    def generate_quick_reply(self, tweet):
        """[משאיר את הפונקציה הקיימת ללא שינוי]"""
        # הקוד הקיים נשאר אותו דבר

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
        """[משאיר את הפונקציה הקיימת ללא שינוי]"""
        # הקוד הקיים נשאר אותו דבר

    def should_engage(self, tweet):
        """Strategic engagement decision with daily limits"""
        # Check daily limits
        if self.daily_stats['replies'] >= 20:
            print("Daily reply limit reached")
            return False
            
        # Check if tweet contains relevant topics
        text_lower = tweet['text'].lower()
        relevant_topics = any(topic.lower() in text_lower for topic in HOT_TOPICS)
        
        # Check if it's peak hours
        current_hour = datetime.utcnow().hour
        is_peak_hour = current_hour in PEAK_HOURS
        
        # Check if it's a high-priority account
        is_priority = tweet['author'] in TARGET_ACCOUNTS[:10]
        
        # Only engage if tweet is very recent or from priority account
        return (relevant_topics or is_peak_hour or is_priority) and tweet['age_minutes'] <= 5

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
