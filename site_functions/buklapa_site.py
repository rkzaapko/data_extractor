from bs4 import BeautifulSoup
import os 
import requests
from urllib.parse import urljoin
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
logger = logging.getLogger('bukalapa')
logger.setLevel(logging.DEBUG)

def Bukalapak(soup,product,sku):
    def get_title(soup):
        try:
            title = soup.find("h1", attrs={"class": 'c-main-product__title u-txt--large'})
            title_name = title.text
            title_string = title_name.strip()
        except AttributeError:
            title_string = ""
        return title_string

    def get_price(soup):
        try:
            discountValue= soup.find("div", attrs={"class": "c-product-price -discounted -main"})
            originalValue = soup.find("div",attrs={"class":"c-product-price -original -main"})
            if originalValue:
                price=originalValue.find("span").text.strip() 
            else:
                price =discountValue.find("span").text.strip()
              
        except AttributeError:
            price = ""
        return price

    def get_discount(soup):
        try:
            discount = soup.find("div",attrs={"class":"c-main-product__price__discount"}).find("span",attrs={"class":"c-main-product__price__discount-percentage"}).text.strip().split(" ")[1]
            
        except AttributeError:
            discount =""
        return discount

    def get_actualPrice(soup):
        try:
            actuallPrice = soup.find("div",attrs={"class":"c-product-price -stroke"}).find("span").text.strip()
        except AttributeError:
            actuallPrice=""
        return actuallPrice
    
    def normalize_text(text):        
        return re.sub(r'\W+', ' ', text).lower().strip()
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    links = soup.find_all("a", attrs={'class': 'bl-link'})

    links_list = []


    for i in links:
        links_list.append(i.get('href'))

    details = {"Date":[],"site":[],"sku":[],"Product":[],"title": [], "price": [],"Discount":[],"actualPrice":[]}
    storeUrls = []
    storeSuggestionList =[]

    for link in links_list:
        productDomainLink = "https://www.bukalapak.com/"
        full_url =urljoin(productDomainLink,link)
       
        if "https://www.bukalapak.com/u/" in full_url:
            storeUrls.append(full_url)
        elif "https://www.bukalapak.com/p/" in full_url:
            try:    
                new_webpage = requests.get(link,timeout=1.5,headers=HEADERS)                                  
                if new_webpage.status_code == 200:
                    try:             
                                              
                        new_soup = BeautifulSoup(new_webpage.content, "html.parser")  
                        title = normalize_text(get_title(new_soup))  
                        productName = normalize_text(product)                                                
                        product_words = productName.split()

                        if all(word in title for word in product_words):
                            logger.info("All words in the product name are present in the title")
                            details["Date"].append(date.today()) 
                            details["site"].append(productDomainLink)  
                            details['sku'].append(sku)
                            details["Product"].append(product)      
                            details["title"].append(get_title(new_soup))
                            details["price"].append(get_price(new_soup))
                            details["Discount"].append(get_discount(new_soup))
                            details["actualPrice"].append(get_actualPrice(new_soup))
                        else:
                            logger.info("       Not all words in the product name are present in the title")
                        
                    except Exception as e:
                        print("Internal error in buklapa ")
                        logger.error(f"Error in processing webpage: {str(e)}")
                else:
                    print("Internal error in buklapa ")
                    logger.error(f"Error in fetching webpage : {str(e)}")
            except Exception as e:
                print("something went wrong in buklapa ")
                logger.error(f"Error fetching webpage : {str(e)}")
                
        else:
            storeSuggestionList.append(full_url)           

    time.sleep(1)
    return details



