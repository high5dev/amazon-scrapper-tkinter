import requests
from bs4 import BeautifulSoup
from tkinter import Tk, Label, Button, Entry, StringVar, Text, Scrollbar
import csv

def fetch_product_details():
    url = url_entry.get()
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract product name
            title_tag = soup.find(id='productTitle')
            product_name_value = title_tag.get_text(strip=True) if title_tag else 'Product name not found'

            # Extract additional details
            details = {}
            table = soup.find('table', class_='a-normal a-spacing-micro')
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    columns = row.find_all('td')
                    if len(columns) == 2:
                        detail_name = columns[0].get_text(strip=True)
                        detail_value = columns[1].get_text(strip=True)
                        details[detail_name] = detail_value

            # Display the product name and details in the GUI
            product_name.set(product_name_value)
            details_text.delete(1.0, "end")  # Clear previous details
            for detail_name, detail_value in details.items():
                details_text.insert("end", f"{detail_name}: {detail_value}\n")

            # Save the details to CSV
            save_to_csv(product_name_value, details)

    except Exception as e:
        product_name.set('An error occurred')

def save_to_csv(product_name_value, details):
    # Open CSV file in append mode
    with open('product_details.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write product name and additional details
        row = [product_name_value]
        for detail_name, detail_value in details.items():
            row.append(f"{detail_name}: {detail_value}")
        writer.writerow(row)

root = Tk()
root.title("Amazon Product Scraper")

product_name = StringVar()
product_name.set("Enter URL and click Fetch")

# GUI layout
Label(root, text="Enter Amazon Product URL: ").pack()
url_entry = Entry(root, width=60)
url_entry.pack()

fetch_button = Button(root, text="Fetch", command=fetch_product_details)
fetch_button.pack()

Label(root, textvariable=product_name).pack()

# Textbox to display details
details_text = Text(root, height=10, width=60)
details_text.pack()

# Scrollbar for the details text box
scrollbar = Scrollbar(root, command=details_text.yview)
scrollbar.pack(side="right", fill="y")
details_text.config(yscrollcommand=scrollbar.set)

root.mainloop()
