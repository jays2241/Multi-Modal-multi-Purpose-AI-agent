import requests
from bs4 import BeautifulSoup

def scrape_news_from_moneycontrol(stock_tag, max_articles=10):
    """
    Scrapes latest news headlines from Moneycontrol using stock tag.
    
    Args:
        stock_tag (str): Stock tag used in Moneycontrol URLs (e.g., 'adani-green', 'tcs').
        max_articles (int): Max number of headlines to fetch.
        
    Returns:
        List of dicts with keys: 'headline', 'link'
    """
    base_url = f"https://www.moneycontrol.com/news/tags/{stock_tag}.html"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(base_url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch news: HTTP {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('li', class_='clearfix')
    news_data = []

    for article in articles:
        if len(news_data) >= max_articles:
            break
        title_tag = article.find('h2')
        link_tag = article.find('a', href=True)

        if title_tag and link_tag:
            title = title_tag.get_text(strip=True)
            link = link_tag['href']
            news_data.append({
                'headline': title,
                'link': link
            })

    return news_data


if __name__ == "__main__":
    stock_tag = 'adani-green'  # Example stock tag
    max_articles = 5  # Example max articles to fetch
    news = scrape_news_from_moneycontrol(stock_tag, max_articles)
    
    for article in news:
        print(f"Headline: {article['headline']}")
        print(f"Link: {article['link']}")
        print()