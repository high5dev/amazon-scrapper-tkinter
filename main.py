import requests
from bs4 import BeautifulSoup
from tkinter import Tk, Label, Button, Entry, StringVar, Text, Scrollbar, messagebox
from PIL import Image, ImageTk
import csv
import io

def fetch_product_details():
    url = url_entry.get()
    if not url:
        messagebox.showerror("Error", "Please enter a URL")
        return

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract product name
        title_tag = soup.find(id='productTitle')
        product_name_value = title_tag.get_text(strip=True) if title_tag else 'Product name not found'

        img_tag = soup.find('img', id='landingImage')

        if img_tag:
            img_url = img_tag['data-old-hires']
            display_image(img_url)
        else:
            messagebox.showwarning("Warning", "Could not find product image")



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

    except requests.exceptions.RequestException as e:
        handle_error(f"Failed to fetch the product page: {str(e)}")
    except Exception as e:
        handle_error(f"An unexpected error occurred: {str(e)}")

def display_image(img_url):
    try:
        response = requests.get(img_url)
        response.raise_for_status()
        img_data = response.content
        img = Image.open(io.BytesIO(img_data))
        img.thumbnail((200, 200))  # Resize image to fit in the GUI
        photo = ImageTk.PhotoImage(img)
        img_label.config(image=photo)
        img_label.image = photo  # Keep a reference
    except Exception as e:
        messagebox.showwarning("Warning", f"Failed to load image: {str(e)}")

def save_to_csv(product_name_value, details):
    # Open CSV file in append mode
    with open('product_details.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write product name and additional details
        row = [product_name_value]
        for detail_name, detail_value in details.items():
            row.append(f"{detail_name}: {detail_value}")
        writer.writerow(row)

def handle_error(error_message):
    messagebox.showerror("Error", error_message)
    product_name.set('An error occurred')
    details_text.delete(1.0, "end")
    details_text.insert("end", error_message)
    img_label.config(image='')  # Clear the image

# Set up the main window
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

# Image label
img_label = Label(root)
img_label.pack()

# Textbox to display details
details_text = Text(root, height=10, width=60)
details_text.pack()

# Scrollbar for the details text box
scrollbar = Scrollbar(root, command=details_text.yview)
scrollbar.pack(side="right", fill="y")
details_text.config(yscrollcommand=scrollbar.set)

root.mainloop()
