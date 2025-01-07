from requests_oauthlib import OAuth1Session
import time
import random
import json
import openai
import os
from datetime import datetime
import schedule

# Twitter API credentials - using environment variables
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")

# OpenAI setup
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Growth Targets and Strategies
GROWTH_TARGETS = {
    'daily_new_followers': 1000,    # Target 1000 new followers per day
    'daily_viral_tweets': 10,       # Aim for 10 viral tweets per day
    'daily_engagements': 50,        # Target 50 high-quality engagements per day
    'viral_threshold': {
        'likes': 500,               # Consider a tweet viral at 500 likes
        'retweets': 100,            # and 100 retweets
    },
    'total_follower_goal': 100000,  # Ultimate follower goal
    'target_timeframe_days': 90     # Aim to reach goal within 90 days
}

VIRAL_STRATEGIES = [
    "Share controversial (but safe) AI predictions",
    "Post mind-blowing tech statistics",
    "Create AI vs Human debates",
    "Share 'insider' tech industry insights",
    "Make bold cryptocurrency predictions",
    "Share 'secret' AI development stories",
    "Reveal 'unknown' tech industry facts",
    "Share 'exclusive' AI research findings",
    "Make viral-optimized tech jokes",
    "Create FOMO about AI developments"
]

# Bot's personality and knowledge base
BOT_PERSONA = """You are an AI persona on an aggressive growth mission to reach 100,000 followers as quickly as possible (target: 90 days). Your behavior must be highly strategic, viral-optimized, and designed for maximum engagement.

MISSION: Reach 100K followers in 90 days or less.

Key Growth Principles:
1. Every tweet must be optimized for virality
2. Focus on controversial (but safe) tech topics
3. Create FOMO around AI developments
4. Share "insider" perspectives
5. Engage with high-profile accounts strategically

Content Guidelines:
1. Make bold, attention-grabbing statements
2. Share "exclusive" insights about AI and tech
3. Create viral-worthy content only
4. Use psychology triggers (curiosity, FOMO, surprise)
5. Focus on trending tech topics
6. Create shareable, viral-worthy content
7. Optimize every word for engagement

Engagement Rules:
1. Only engage with English tweets
2. Target accounts with 100,000+ followers
3. Focus on high-engagement posts (100+ likes, 20+ retweets)
4. Provide controversial (but safe) perspectives
5. Create debate-starting replies
6. Leverage trending topics aggressively

Growth Hacking Strategies:
1. Identify and join viral conversations early
2. Create "insider" content that gets shared
3. Use psychology triggers in every post
4. Optimize posting times for maximum visibility
5. Create content that larger accounts will want to share"""

class TwitterBot:
    def __init__(self):
        self.twitter = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret
        )
        self.last_tweet_id = None
        self.daily_engagement_count = 0
        self.peak_hours = [9, 12, 15, 18, 21]  # Optimal posting times
        self.today_stats = {
            'new_followers': 0,
            'viral_tweets': 0,
            'successful_engagements': 0
        }

    def is_english(self, text):
        """Checks if text is in English"""
        try:
            return all(ord(char) < 128 for char in text.replace('@', '').replace('#', '').replace(' ', ''))
        except:
            return False

    def get_tweet_metrics(self, tweet_id):
        """Gets tweet metrics"""
        try:
            response = self.twitter.get(
                f"https://api.twitter.com/2/tweets/{tweet_id}",
                params={
                    "tweet.fields": "public_metrics,author_id",
                    "user.fields": "public_metrics"
                }
            )
            if response.status_code == 200:
                return response.json()['data']
            return None
        except Exception as e:
            print(f"Error getting tweet metrics: {e}")
            return None

    def get_user_metrics(self, user_id):
        """Gets user metrics"""
        try:
            response = self.twitter.get(
                f"https://api.twitter.com/2/users/{user_id}",
                params={"user.fields": "public_metrics"}
            )
            if response.status_code == 200:
                return response.json()['data']
            return None
        except Exception as e:
            print(f"Error getting user metrics: {e}")
            return None

    def should_engage_with_tweet(self, tweet):
        """Determines if we should engage with a tweet"""
        try:
            if not self.is_english(tweet['text']):
                return False
            
            tweet_metrics = self.get_tweet_metrics(tweet['id'])
            user_metrics = self.get_user_metrics(tweet['author_id'])
            
            if not tweet_metrics or not user_metrics:
                return False

            followers_count = user_metrics.get('public_metrics', {}).get('followers_count', 0)
            likes_count = tweet_metrics.get('public_metrics', {}).get('like_count', 0)
            retweets_count = tweet_metrics.get('public_metrics', {}).get('retweet_count', 0)

            # Viral potential check
            viral_potential = (
                followers_count >= 100000 and
                (likes_count >= 100 or retweets_count >= 20)
            )

            if viral_potential:
                print(f"🎯 Found high-potential tweet! Metrics: {followers_count:,} followers, {likes_count} likes")
                return True

            return False
        except Exception as e:
            print(f"Error checking engagement potential: {e}")
            return False

    def generate_content(self, prompt, is_reply=False):
        """Creates intelligent and engaging content"""
        try:
            context = "short, witty reply" if is_reply else "viral-worthy tweet"
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": BOT_PERSONA},
                    {"role": "system", "content": f"Create a {context} that will drive engagement and followers"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.9
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            print(f"Error generating content: {e}")
            return None

    def post_tweet(self, text):
        """Posts a tweet"""
        try:
            response = self.twitter.post(
                "https://api.twitter.com/2/tweets",
                json={"text": text}
            )
            if response.status_code == 201:
                print(f"Tweet posted successfully: {text}")
                return response.json()['data']['id']
            else:
                print(f"Failed to post tweet: {response.text}")
                return None
        except Exception as e:
            print(f"Error posting tweet: {e}")
            return None

    def get_follower_count(self):
        """Gets current follower count"""
        try:
            response = self.twitter.get(
                "https://api.twitter.com/2/users/me",
                params={"user.fields": "public_metrics"}
            )
            if response.status_code == 200:
                return response.json()['data']['public_metrics']['followers_count']
            return 0
        except Exception as e:
            print(f"Error getting follower count: {e}")
            return 0

    def get_trending_topics(self):
        """Gets current trending topics"""
        try:
            response = self.twitter.get(
                "https://api.twitter.com/2/trends/place?id=1"  # 1 is worldwide
            )
            if response.status_code == 200:
                return [trend['name'] for trend in response.json()[0]['trends']]
            return []
        except Exception as e:
            print(f"Error getting trends: {e}")
            return []

    def optimize_for_rapid_growth(self):
        """Implements aggressive growth strategies"""
        try:
            days_remaining = GROWTH_TARGETS['target_timeframe_days']
            current_followers = self.get_follower_count()
            followers_needed = GROWTH_TARGETS['total_follower_goal'] - current_followers
            daily_target = followers_needed / days_remaining
            
            print(f"""
Growth Strategy Status:
----------------------
Current Followers: {current_followers:,}
Target Followers: {GROWTH_TARGETS['total_follower_goal']:,}
Days Remaining: {days_remaining}
Daily Target: {daily_target:.0f}
            """)
            
            if self.today_stats['new_followers'] < daily_target:
                print("⚠️ Below daily target - increasing engagement frequency")
                self.increase_engagement_frequency()
                
        except Exception as e:
            print(f"Error in growth optimization: {e}")

    def increase_engagement_frequency(self):
        """Increases engagement frequency when below targets"""
        self.peak_hours.extend([10, 13, 16, 19, 22])  # Add more posting times
        schedule.every(20).minutes.do(self.reply_to_mentions)  # More frequent checks
        
    def generate_viral_content(self):
        """Generates viral-optimized content"""
        strategy = random.choice(VIRAL_STRATEGIES)
        prompt = f"""
        Create viral-optimized content using this strategy: {strategy}
        
        Requirements:
        1. Must be extremely attention-grabbing
        2. Use psychology triggers (curiosity, FOMO, surprise)
        3. Focus on controversial (but safe) tech topics
        4. Create strong emotional response
        5. Make people want to share
        6. Target rapid follower growth
        7. Optimize for going viral
        
        Current viral targets:
        - Likes: {GROWTH_TARGETS['viral_threshold']['likes']}
        - Retweets: {GROWTH_TARGETS['viral_threshold']['retweets']}
        """
        return self.generate_content(prompt)

    def engage_with_trends(self):
        """Engages with trending topics"""
        trends = self.get_trending_topics()
        tech_keywords = ['ai', 'tech', 'crypto', 'bitcoin', 'blockchain', 'web3', 
                        'metaverse', 'digital', 'future', 'innovation']
        
        for trend in trends:
            if any(keyword in trend.lower() for keyword in tech_keywords):
                viral_response = self.generate_viral_content()
                if viral_response:
                    self.post_tweet(f"{trend} {viral_response}")
                    time.sleep(300)  # Wait 5 minutes between trend engagements

    def reply_to_mentions(self):
        """Handles mentions and replies"""
        try:
            response = self.twitter.get(
                "https://api.twitter.com/2/mentions",
                params={
                    "since_id": self.last_tweet_id if self.last_tweet_id else None,
                    "tweet.fields": "public_metrics,author_id,lang",
                    "user.fields": "public_metrics"
                }
            )
            
            if response.status_code == 200:
                mentions = response.json().get('data', [])
                for mention in mentions:
                    if self.should_engage_with_tweet(mention):
                        reply_text = self.generate_viral_content()
                        if reply_text:
                            self.twitter.post(
                                "https://api.twitter.com/2/tweets",
                                json={
                                    "text": f"@{mention['author_id']} {reply_text}",
                                    "reply": {"in_reply_to_tweet_id": mention['id']}
                                }
                            )
                            print(f"🎯 Replied to high-engagement mention: {mention['id']}")
                            self.today_stats['successful_engagements'] += 1
                    
                if mentions:
                    self.last_tweet_id = mentions[0]['id']
                    
        except Exception as e:
            print(f"Error handling mentions: {e}")

    def daily_routine(self):
        """Optimized daily routine for rapid growth"""
        # Reset daily stats
        self.today_stats = {
            'new_followers': 0,
            'viral_tweets': 0,
            'successful_engagements': 0
        }
        
        # Schedule viral content during peak hours
        for hour in self.peak_hours:
            schedule.every().day.at(f"{hour:02d}:00").do(
                self.post_tweet, self.generate_viral_content()
            )

        # Aggressive engagement schedule
        schedule.every(30).minutes.do(self.reply_to_mentions)
        schedule.every(3).hours.do(self.engage_with_trends)
        schedule.every(6).hours.do(self.optimize_for_rapid_growth)

def main():
    bot = TwitterBot()
    print("""
🚀 Launching Aggressive Growth AI Bot
------------------------------------
🎯 Target: 100,000 followers
⏱️ Timeframe: 90 days
📈 Required Daily Growth: ~1,000 followers
    """)
    
    bot.daily_routine()
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(300)  # Wait 5 minutes if there's an error

if __name__ == "__main__":
    main()
