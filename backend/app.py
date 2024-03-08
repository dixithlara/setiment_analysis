from flask import Flask, render_template, request
from textblob import TextBlob
from apify_client import ApifyClient
#import tweepy

client = ApifyClient(token="apify_api_n5qnSv8RbA8IVNVZykf7qYTpCsPLVd0aBtfu")

app = Flask(__name__, template_folder='../frontend/templates')

# consumer_key = 'IUyd6FHHP8iepqo964FhtAW4j'
# consumer_secret = 'BD97Gkm4fPfeFEFephfN4UCKNLBih8ovQryv6FJxO5TeuLnw8l'
# access_token = '1382268702855294979-nSP7EzsmdWzx9mQfX9RYhU7XFNFs1F'
# access_token_secret = 'z9eWon8VdHbVLCDY09zdolAk0VKWe65qacQOSmr5GM0gl'

# auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# auth.set_access_token(access_token, access_token_secret)

# api = tweepy.API(auth)

# class MyStreamListener(tweepy.StreamListener):
#     def on_status(self, status):
#         print(status.text) 

# stream_listener = MyStreamListener()
# stream = tweepy.Stream(auth=api.auth, listener=stream_listener)

# stream.filter(track=['python', 'flask'])


def analyze_sentiment(comment):
    blob = TextBlob(comment)
    sentiment_score = blob.sentiment.polarity
    return sentiment_score

def log_negative_comments(negative_comments):
    with open('negative_comments.log','a') as f:
        for comment in negative_comments:
            f.write(comment + '\n')

def fetch_facebook_comments(profile_url):
    # Replace with Apify actor ID for Facebook comments scraping
    # run = client.run_web_scraper(actor_id="YOUR_FACEBOOK_SCRAPER_ID", input={"startUrls": [profile_url]})
    # comments = run["results"][0]["data"]["comments"]  # Modify based on your scraper structure
    # return comments
    input_data = {
        "startUrls": [profile_url]
    }
    
    # Start the actor and wait for it to finish
    actor_run = client.actor('apify/facebook-comments-scraper').call(run_input= input_data)
    #actor_run.wait_for_finish()

    # Fetch results from the actor's default dataset
    dataset = client.dataset(actor_run.default_dataset_id)
    dataset_items = dataset.get_items()
    
    # Extract comments from the dataset items
    comments = [item['comment'] for item in dataset_items]
    return comments

def fetch_instagram_comments(profile_url):
    # Replace with Apify actor ID for Instagram comments scraping
    actor_call = client.actor('apify/instagram-comment-scraper').call()

    # Fetch results from the actor's default dataset
    dataset_items = client.dataset(actor_call['defaultDatasetId']).list_items().items

    # Extract comments from the dataset items
    comments = [item['comment'] for item in dataset_items]
    return comments

# def fetch_twitter_comments(profile_username):
#     # Replace with Apify actor ID for Twitter comments scraping
#     # Consider using Tweepy library for Twitter API access (alternative to Apify scraper)
#     # Implement logic to retrieve and process tweets based on username
#     return []  # Placeholder for Twitter comments retrieval
    
@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        company_name = request.form['company']
        platform = request.form['platform']

        if platform == "facebook":
            profile_url = f"https://www.facebook.com/{company_name}"
            comments = fetch_facebook_comments(profile_url)
        elif platform == "instagram":
            profile_url = f"https://www.instagram.com/{company_name}"
            comments = fetch_instagram_comments(profile_url)
        else:
            comments=[]
        #tweets = api.search(q=company_name, count=10)

        posts = [
            {
                'author': 'User1',
                'comment': 'Positive comment.'
            },
            {
                'author': 'User2',
                'comment': 'Negative comment.'
            }
        ]

        negative_comments = []
        for comment in comments:
            comment_text = comment.get("text", "")  # Modify based on your scraper data structure
            sentiment_score = analyze_sentiment(comment_text)
            if sentiment_score < 0:
                negative_comments.append(comment_text)
        # for post in posts:
        #     comment = post['comment']
        #     sentiment_score = analyze_sentiment(comment)
        #     if sentiment_score < 0:
        #         negative_comments.append(comment)
            
        if negative_comments:
            log_negative_comments(negative_comments)
            notification_msg = f"Negative comment detected: {', '.join(negative_comments)}"
            print(notification_msg)

        return render_template('index.html', company_name=company_name, platform=platform, comments=comments, negative_comments=negative_comments)    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

# from flask import Flask, render_template, request
# from textblob import TextBlob
# import tweepy

# app = Flask(__name__, template_folder='../frontend/templates')

# consumer_key = 'IUyd6FHHP8iepqo964FhtAW4j'
# consumer_secret = 'BD97Gkm4fPfeFEFephfN4UCKNLBih8ovQryv6FJxO5TeuLnw8l'
# access_token = '1382268702855294979-nSP7EzsmdWzx9mQfX9RYhU7XFNFs1F'
# access_token_secret = 'z9eWon8VdHbVLCDY09zdolAk0VKWe65qacQOSmr5GM0gl'

# auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# auth.set_access_token(access_token, access_token_secret)

# api = tweepy.API(auth)

# # class MyStreamListener(tweepy.StreamListener):
# #     def on_status(self, status):
# #         print(status.text) 

# # stream_listener = MyStreamListener()
# # stream = tweepy.Stream(auth=api.auth, listener=stream_listener)

# # stream.filter(track=['python', 'flask'])

# def analyze_sentiment(comment):
#     blob = TextBlob(comment)
#     sentiment_score = blob.sentiment.polarity
#     return sentiment_score

# def log_negative_comments(negative_comments):
#     with open('negative_comments.log','a') as f:
#         for comment in negative_comments:
#             f.write(comment + '\n')

    
# @app.route('/', methods=['GET','POST'])
# def index():
#     if request.method == 'POST':
#         company_name = request.form['company']

#         search_query = f'{company_name} -filter:retweets'  # Exclude retweets
#         tweets = tweepy.Cursor(api.search_users, q=search_query, tweet_mode='extended').items(10)
#         # posts = [
#         #     {
#         #         'author': 'User1',
#         #         'comment': 'Positive comment.'
#         #     },
#         #     {
#         #         'author': 'User2',
#         #         'comment': 'Negative comment.'
#         #     }
#         # ]
#         posts=[]
#         negative_comments = []
#         for tweet in tweets:
#             post = {
#                 'author': tweet.user.screen_name,
#                 'comment': tweet.full_text
#             }
#             posts.append(post)
#             sentiment_score = analyze_sentiment(post['comment'])
#             if sentiment_score < 0:
#                 negative_comments.append(post['comment'])
            
#         if negative_comments:
#             log_negative_comments(negative_comments)
#             notification_msg = f"Negative comment detected: {', '.join(negative_comments)}"
#             print(notification_msg)

#         return render_template('index.html', posts=posts, negative_comments=negative_comments)
#     return render_template('index.html')

# if __name__ == '__main__':
#     app.run(debug=True)


# # from flask import Flask, render_template, request
# # from textblob import TextBlob
# # import tweepy

# # app = Flask(__name__, template_folder='../frontend/templates')

# # consumer_key = 'IUyd6FHHP8iepqo964FhtAW4j'
# # consumer_secret = 'BD97Gkm4fPfeFEFephfN4UCKNLBih8ovQryv6FJxO5TeuLnw8l'
# # access_token = '1382268702855294979-nSP7EzsmdWzx9mQfX9RYhU7XFNFs1F'
# # access_token_secret = 'z9eWon8VdHbVLCDY09zdolAk0VKWe65qacQOSmr5GM0gl'

# # auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# # auth.set_access_token(access_token, access_token_secret)

# # api = tweepy.API(auth)

# # class MyStreamListener(tweepy.StreamListener):
# #     def on_status(self, status):
# #         print(status.text) 

# # stream_listener = MyStreamListener()
# # stream = tweepy.Stream(auth=api.auth, listener=stream_listener)

# # stream.filter(track=['python', 'flask'])


# # def analyze_sentiment(comment):
# #     blob = TextBlob(comment)
# #     sentiment_score = blob.sentiment.polarity
# #     return sentiment_score

# # def log_negative_comments(negative_comments):
# #     with open('negative_comments.log','a') as f:
# #         for comment in negative_comments:
# #             f.write(comment + '\n')

# # @app.route('/', methods=['GET','POST'])
# # def index():
# #     if request.method == 'POST':
# #         company_name = request.form['company']


# #         posts = [
# #             {
# #                 'author': 'User1',
# #                 'comment': 'Positive comment.'
# #             },
# #             {
# #                 'author': 'User2',
# #                 'comment': 'Negative comment.'
# #             }
# #         ]

# #         negative_comments = []
# #         for post in posts:
# #             comment = post['comment']
# #             sentiment_score = analyze_sentiment(comment)
# #             if sentiment_score < 0:
# #                 negative_comments.append(comment)
            
# #         if negative_comments:
# #             log_negative_comments(negative_comments)
# #             notification_msg = f"Negative comment detected: {', '.join(negative_comments)}"
# #             print(notification_msg)

# #         return render_template('index.html', posts=posts, negative_comments=negative_comments)
# #     return render_template('index.html')

# # if __name__ == '__main__':
# #     app.run(debug=True)
