import requests

def fetch_page(url):
    response = requests.get(url)
    return response.txt

def main():
    url = "https://scraping-trial-test.vercel.app"
    html = fetch_page(url)
    print(len(html))


if __name__ == "__main__":
    main()