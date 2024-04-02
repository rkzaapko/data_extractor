from bs4 import BeautifulSoup
import os  
import requests
import time
from datetime import date
import re
import logging
log_dir = 'mining_Log'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_filename = date.today().strftime("%Y-%m-%d") + ".log"
log_filepath = os.path.join(log_dir, log_filename)

logging.basicConfig(filename=log_filepath, format='%(asctime)s:%(name)s: %(message)s', filemode='w')
logger = logging.getLogger('tokopedia')
logger.setLevel(logging.DEBUG)

def tokopedia(soup,product,sku):
    def get_title(soup):
        try:
            title = soup.find("h1", attrs={"class": 'css-1os9jjn'})
            title_name = title.text
            title_string = title_name.strip()
        except AttributeError:
            title_string = ""
        return title_string

    def get_price(soup):
        try:
            price = soup.find("div", attrs={"data-testid": "lblPDPDetailProductPrice"}).text.strip()
        except AttributeError:
            price = ""
        return price

    def get_discount(soup):
        try:
            discount = soup.find("span",attrs={"data-testid":"lblPDPDetailDiscountPercentage"}).text.strip()
        except AttributeError:
            discount =""
        return discount

    def get_actualPrice(soup):
        try:
            actuallPrice = soup.find("span",attrs={"data-testid":"lblPDPDetailOriginalPrice"}).text.strip()
        except AttributeError:
            actuallPrice=""
        return actuallPrice
    
    def normalize_text(text):        
        return re.sub(r'\W+', ' ', text).lower().strip()
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    links = soup.find_all("a", attrs={'class': 'pcv3__info-content css-gwkf0u'})

    links_list = []


    for i in links:
        links_list.append(i.get('href'))

    details = {"Date":[],"site":[],"sku":[],"Product":[],"title": [], "price": [],"Discount":[],"actualPrice":[]}
    for link in links_list:
        productDomainLink = "https://www.tokopedia.com/"
      
        try:       
            new_webpage = requests.get(link,timeout=3.5,headers=HEADERS)                        
            if new_webpage.status_code == 200:
                try:             
                    new_soup = BeautifulSoup(new_webpage.content, "html.parser")  
                    title = normalize_text(get_title(new_soup))  
                    productName = normalize_text(product)  
                    
                    product_words = productName.split()

                    if all(word in title for word in product_words):
                        logger.info("         All words in the product name are Matched in tokopidea")
                        
                        details["Date"].append(date.today()) 
                        details["site"].append(productDomainLink)  
                        details['sku'].append(sku)
                        details["Product"].append(product)      
                        details["title"].append(get_title(new_soup))
                        details["price"].append(get_price(new_soup))
                        details["Discount"].append(get_discount(new_soup))
                        details["actualPrice"].append(get_actualPrice(new_soup))
                    else:
                        logger.info("Not all words in the product name are Matched in tokopidea          ")
                    
                except Exception as e:
                    print("Internal error in tokopidea")
                    logger.error(f"Error in processing webpage: {str(e)}")
            else:
                print("Internal error in tokopidea")
                logger.error(f"Error in fetching webpage : {str(e)}")

        except Exception as e:
            print("something went wrong in tokopidea")
            logger.error(f"Error fetching webpage : {str(e)}")

    time.sleep(1)

    return details


