import tkinter as tk
from tkinter import filedialog, messagebox
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import date, datetime
import requests
import logging
import os
import threading
from site_functions.tokopidea_site import tokopedia
from site_functions.buklapa_site import Bukalapak

log_dir = 'mining_Log'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_filename = date.today().strftime("%Y-%m-%d") + ".log"
log_filepath = os.path.join(log_dir, log_filename)

logging.basicConfig(filename=log_filepath, format='%(asctime)s:%(name)s: %(message)s', filemode='w')
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)

def start_mining():
    global mining_thread
    filepath = filedialog.askopenfilename(title="Select Excel file", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
    if filepath:
        try:
            logger.info(f"Selected file: {filepath}")
            selected_file_entry.delete(0, tk.END)
            selected_file_entry.insert(0, filepath)
            mining_button.config(state=tk.DISABLED)
            stop_button.config(state=tk.NORMAL)
            processing_label.config(text="Processing...", fg="blue")
            mining_thread = threading.Thread(target=perform_mining, args=(filepath,))
            mining_thread.start()
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")
    else:
        logger.error("No file selected.")
        tk.messagebox.showerror("Error", "No file selected.")

def stop_mining():
    global mining_thread
    if mining_thread and mining_thread.is_alive():
        mining_thread.join()
        logger.info("Mining process stopped.")
        processing_label.config(text="Mining process stopped.", fg="red")
        mining_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)
    else:
        logger.info("No mining process running.")

def perform_mining(filepath):
    try:
        logger.info("The Mining began .....⛏️⛏️⛏️")
        products = pd.read_excel(filepath, usecols='B').values
        SKUs = pd.read_excel(filepath, usecols='A').values

        all_details = []

        for product, sku in zip(products, SKUs):
            logger.info(f"SKU: {sku[0]}, PRODUCT: {product[0]}")
            product_label.config(text=f"SKU: {sku[0]}, PRODUCT: {product[0]}")
            try:
                URLS = [
                    f"https://www.tokopedia.com/search?q={product[0]}&source=universe&st=product&navsource=home&srp_component_id=02.02.02.02",
                    f"https://www.bukalapak.com/products?search%5Bkeywords%5D={product[0]}"
                ]

                HEADERS = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
                    'Accept-Language': 'en-US,en;q=0.9',
                }

                for URL in URLS:
                    try:
                        webPage = requests.get(URL, headers=HEADERS)
                        logger.info(f"SearchURL: {URL}")
                        soup = BeautifulSoup(webPage.content, 'html.parser')

                        if "tokopedia" in URL:
                            logger.info("Invoking Tokopedia website for product searching........🔍🔍🔍🔍")
                            tokopediaCsvFile = tokopedia(soup=soup, product=product[0], sku=sku[0])
                            all_details.append(tokopediaCsvFile)
                        elif "bukalapak" in URL:
                            logger.info("Invoking Bukalapak website for product searching........🔍🔍🔍🔍🔍")
                            bukalapakCsvFile = Bukalapak(soup=soup, product=product[0], sku=sku[0])
                            all_details.append(bukalapakCsvFile)
                    except Exception as e:
                        logger.error("Something went wrong in inner try-except block:", e)
            except Exception as e:
                logger.error("Something went wrong in outer try-except block:", e)

        merged_details = {}
        for detail in all_details:
            for key, value in detail.items():
                if key in merged_details:
                    merged_details[key].extend(value)
                else:
                    merged_details[key] = value

        amazon_ds = pd.DataFrame.from_dict(merged_details)
        amazon_ds['title'].replace('', np.nan, inplace=False)
        amazon_ds = amazon_ds.dropna(subset=['title'])
        folderPath = './Output_csv'

        if not os.path.exists(folderPath):
            os.mkdir(folderPath)

        file_name = "product_data"
        date_time = datetime.now().strftime("%d%m%Y%H%M%S")
        csv_path = f"{folderPath}/{file_name}_{date_time}.csv"
        amazon_ds.to_csv(csv_path, index=False)
        logger.info(f"Your {file_name} file Saved Sucessfully!!")

        logger.info("Mining process completed.")
        processing_label.config(text="Mining process completed.", fg="green")
        mining_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        processing_label.config(text="An error occurred.", fg="red")
        mining_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)

# GUI setup
root = tk.Tk()
root.title("Zaapko Data Mining")
frame = tk.Frame(root)
frame.pack()

selected_file_label = tk.Label(frame, text="Selected File:")
selected_file_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

selected_file_entry = tk.Entry(frame, width=50)
selected_file_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

mining_button = tk.Button(frame, text="Start Mining", command=start_mining)
mining_button.grid(row=1, column=0, padx=10, pady=10)

stop_button = tk.Button(frame, text="Stop Mining", command=stop_mining, state=tk.DISABLED)
stop_button.grid(row=1, column=1, padx=10, pady=10)

product_label = tk.Label(frame,text="",fg="black")
product_label.grid(row=3, columnspan=3)

processing_label = tk.Label(frame, text="", fg="blue")
processing_label.grid(row=2, columnspan=2)

root.mainloop()
