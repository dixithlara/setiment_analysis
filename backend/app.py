from flask import Flask, render_template, request
from textblob import TextBlob
import tweepy

app = Flask(__name__, template_folder='../frontend/templates')

consumer_key = 'IUyd6FHHP8iepqo964FhtAW4j'
consumer_secret = 'BD97Gkm4fPfeFEFephfN4UCKNLBih8ovQryv6FJxO5TeuLnw8l'
access_token = '1382268702855294979-nSP7EzsmdWzx9mQfX9RYhU7XFNFs1F'
access_token_secret = 'z9eWon8VdHbVLCDY09zdolAk0VKWe65qacQOSmr5GM0gl'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

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

    
@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        company_name = request.form['company']

        search_query = f'{company_name} -filter:retweets'  # Exclude retweets
        tweets = tweepy.Cursor(api.search_users, q=search_query, tweet_mode='extended').items(10)
        # posts = [
        #     {
        #         'author': 'User1',
        #         'comment': 'Positive comment.'
        #     },
        #     {
        #         'author': 'User2',
        #         'comment': 'Negative comment.'
        #     }
        # ]
        posts=[]
        negative_comments = []
        for tweet in tweets:
            post = {
                'author': tweet.user.screen_name,
                'comment': tweet.full_text
            }
            posts.append(post)
            sentiment_score = analyze_sentiment(post['comment'])
            if sentiment_score < 0:
                negative_comments.append(post['comment'])
            
        if negative_comments:
            log_negative_comments(negative_comments)
            notification_msg = f"Negative comment detected: {', '.join(negative_comments)}"
            print(notification_msg)

        return render_template('index.html', posts=posts, negative_comments=negative_comments)
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

# class MyStreamListener(tweepy.StreamListener):
#     def on_status(self, status):
#         print(status.text) 

# stream_listener = MyStreamListener()
# stream = tweepy.Stream(auth=api.auth, listener=stream_listener)

# stream.filter(track=['python', 'flask'])


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


#         posts = [
#             {
#                 'author': 'User1',
#                 'comment': 'Positive comment.'
#             },
#             {
#                 'author': 'User2',
#                 'comment': 'Negative comment.'
#             }
#         ]

#         negative_comments = []
#         for post in posts:
#             comment = post['comment']
#             sentiment_score = analyze_sentiment(comment)
#             if sentiment_score < 0:
#                 negative_comments.append(comment)
            
#         if negative_comments:
#             log_negative_comments(negative_comments)
#             notification_msg = f"Negative comment detected: {', '.join(negative_comments)}"
#             print(notification_msg)

#         return render_template('index.html', posts=posts, negative_comments=negative_comments)
#     return render_template('index.html')

# if __name__ == '__main__':
#     app.run(debug=True)
