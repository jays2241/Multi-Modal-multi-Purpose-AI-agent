import news_scraper
import classifier

def main():
    stock_tag = 'adani-green' 
    max_articles = 5  


    news_data = news_scraper.scrape_news_from_moneycontrol(stock_tag, max_articles)

    classified_news = classifier.classify_news_sentiment(news_data)

    # Print classified news
    for article in classified_news:
        print(f"Headline: {article['headline']}")
        print(f"Link: {article['link']}")
        print(f"Sentiment: {article['sentiment']}")
        print()

    