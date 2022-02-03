from tweepy import OAuthHandler
import tweepy 

from auth import (consumer_key, consumer_secret, access_token, access_token_secret)

def main():
    auth=tweepy.OAuthHandler(consumer_key,consumer_secret)
    auth.set_access_token(access_token,access_token_secret)
    api=tweepy.API(auth)
    
    tweet = "Hello, world!"
    post_result = api.update_status(status=tweet)

if __name__ == "__main__":
    main()