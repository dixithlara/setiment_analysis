from flask import Flask, render_template, request
from textblob import TextBlob
from apify_client import ApifyClient

client = ApifyClient(token="apify_api_n5qnSv8RbA8IVNVZykf7qYTpCsPLVd0aBtfu")

app = Flask(__name__, template_folder='../frontend/templates')


def analyze_sentiment(comment):
    blob = TextBlob(comment)
    sentiment_score = blob.sentiment.polarity
    return sentiment_score

def log_negative_comments(negative_comments):
    with open('negative_comments.log','w') as f:
        for comment in negative_comments:
            f.write(comment + '\n')

def log_positive_comments(positive_comments):
    with open('positive_comments.log','w') as f:
        for comment in positive_comments:
            f.write(comment + '\n')

def log_neutral_comments(neutral_comments):
    with open('neutral_comments.log','w') as f:
        for comment in neutral_comments:
            f.write(comment + '\n')

def fetch_facebook_comments(profile_url):

    client = ApifyClient("apify_api_n5qnSv8RbA8IVNVZykf7qYTpCsPLVd0aBtfu")

    input_data = {
    "startUrls": [{ "url": profile_url }],
    "resultsLimit": 1,  # 1 as only 1 post is needed(i.e most recent)   
    }
    print(input_data)

    post_actor_run = client.actor("KoJrdxJCTtpon81KY").call(run_input=input_data)
    data = client.dataset(post_actor_run["defaultDatasetId"])

    item = data.list_items().items  # get the first item from the dataset, as it is teh latest
    photo = item[0].get('media', [])
    image_url = ""
    for media_item in photo:
        image_url = media_item['thumbnail']

    most_recent_post_url = item[0].get('url')
    
    comments_input_data = {
        "startUrls": [{ "url": most_recent_post_url }],
        "resultsLimit": 50,  
    }
    print(most_recent_post_url)
    comments_actor_run = client.actor("us5srxAYnsrkgUv2v").call(run_input=comments_input_data)

    dataset = client.dataset(comments_actor_run["defaultDatasetId"])
    comments= list(map(lambda x: x.get("text","<gif/sticker! NO TEXT COMMENT FOUND>"),list(dataset.iterate_items())))

    return comments, image_url
    
@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        company_name = request.form['company']

        profile_url = f"https://www.facebook.com/{company_name}"
        print(profile_url)
        comments, image_url = fetch_facebook_comments(profile_url)
        print("img url:", image_url)
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
        positive_comments = []
        neutral_comments = []
        for comment in comments:  
            sentiment_score = analyze_sentiment(comment)
            if sentiment_score < -0.1:
                negative_comments.append(comment)
            elif sentiment_score > 0.1:
                positive_comments.append(comment)
            else:
                neutral_comments.append(comment)
            print(sentiment_score,comment)
                    
        if negative_comments:
            log_negative_comments(negative_comments)
            notification_msg = f"Negative comment detected: {', '.join(negative_comments)}"
            print(notification_msg)
        
        if positive_comments:
            log_positive_comments(positive_comments)
            notification_msg = f"positive comment detected: {', '.join(positive_comments)}"
            print(notification_msg)

        if neutral_comments:
            log_neutral_comments(neutral_comments)
            notification_msg = f"neutral comment detected: {', '.join(neutral_comments)}"
            print(notification_msg)

        return render_template('index.html', company_name=company_name, comments=comments, negative_comments=negative_comments, positive_comments=positive_comments, neutral_comments=neutral_comments, image_url=image_url)    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
