import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os

def linkScraper(keywords):
    links = set()
    for k in keywords:
        url = f"https://cafef.vn/tim-kiem.chn?keywords={k}"
        response = requests.get(url)
        response.encoding = "utf-8"  
        soup = BeautifulSoup(response.text, "html.parser")
        link_class = soup.find_all('h3', {'class': 'titlehidden'})
        for a_tag in link_class:
            links.add("https://cafef.vn" + a_tag.find('a')['href'])

        i = 2
        while i <= 20:
            url = f"https://cafef.vn/tim-kiem/trang-{i}.chn?keywords={k}"
            response = requests.get(url)
            response.encoding = "utf-8"  
            soup = BeautifulSoup(response.text, "html.parser")
            link_class = soup.find_all('h3', {'class': 'titlehidden'})
            if link_class:
                for a_tag in link_class:
                    links.add("https://cafef.vn" + a_tag.find('a')['href'])
                i += 1
            else:
                break
    
    return links


def contentScraper(url):
    cut_off_date = datetime.strptime("01-01-2024", "%d-%m-%Y").date()
    response = requests.get(url)
    response.encoding = "utf-8"  
    soup = BeautifulSoup(response.text, "html.parser")

    publish_date = soup.find("span", {"class": "pdate"})
    if publish_date:
        publish_date = publish_date.text.strip()
        publish_date = datetime.strptime(publish_date[:10], "%d-%m-%Y").date()
        if publish_date < cut_off_date:
            publish_date = "Unknown Date"
            title = "No Title"
            content = "Content not found"
            return {"publish_date": publish_date, "title": title, "content": content}

    else: publish_date = "Unknown Date"
    
    title = soup.find("h1")
    if title:
        title = title.get_text(strip=True)
    else: title = "No Title"

    content_div = soup.find("div", {"class": "detail-content afcbc-body"})
    if content_div:
        paragraphs = content_div.find_all("p")
        if paragraphs:
            content = " ".join([p.get_text(strip=True) for p in paragraphs])
        else: content = "Content not found"
    else:
        content = "Content not found"
    
    return {"publish_date": publish_date, "title": title, "content": content}


def vn30Scraper(vn30, cut_off_date):
    for ticker in vn30.keys():
        print(f"Processing {ticker}...")

        keywords = vn30[ticker]
        links = linkScraper(keywords)

        filename = f"test/{ticker}_news.csv"

        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["publish_date", "title", "content"])
            writer.writeheader()
            for link in links: 
                try:
                    article = contentScraper(link)
                    if article["publish_date"] == "Unknown Date" or article["publish_date"] < cut_off_date or article["content"] == "Content not found":
                        continue
                    writer.writerow(article)
                except Exception as e:
                    print(f"Failed to scrape {link}: {e}")

        print(f"Finished processing {ticker}. Saved to {filename}.")


#------------------------------------------------------------------------------------------------------------------------------------------
#MAIN
#------------------------------------------------------------------------------------------------------------------------------------------

vn30 = {'ACB': ['ACB'], 'BCM': ['BCM', 'Becamex'], 'BID': ['BID', 'BIDV'], 'BVH': ['BVH', 'Bảo%20Việt'], 'CTG': ['CTG', 'VietinBank'], 'FPT': ['FPT'], 'GAS': ['PV GAS'], 'GVR': ['GVR', 'Tập%20đoàn%20Cao%20su'], 'HDB': ['HDB', 'HDBank'], 'HPG': ['HPG', 'Hòa%20Phát'], 'MBB': ['MBB', 'MBBank'], 'MSN': ['MSN', 'Masan'], 'MWG': ['MWG', 'Thế%20Giới%20Di%20Động'], 'PLX': ['PLX', 'Petrolimex'], 'POW': ['POW', 'PV%20Power'], 'SAB': ['SAB', 'Sabeco'], 'SHB': ['SHB'], 'SSB': ['SSB', 'SeABank'], 'SSI': ['SSI'], 'STB': ['STB', 'Sacombank'], 'TCB': ['TCB', 'Techcombank'], 'TPB': ['TPB', 'TPBank'], 'VCB': ['VCB', 'Vietcombank'], 'VHM': ['VHM', 'Vinhomes'], 'VIB': ['VIB'], 'VIC': ['Vingroup'], 'VJC': ['VJC','Vietjet'], 'VNM': ['VNM', 'Vinamilk'], 'VPB': ['VPB', 'VPBank'], 'VRE': ['VRE', 'Vincom%20Retail']}

cut_off_date = datetime.strptime("01-01-2024", "%d-%m-%Y").date()

vn30Scraper(vn30, cut_off_date)
