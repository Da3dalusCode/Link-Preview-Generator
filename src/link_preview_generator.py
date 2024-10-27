#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter import ttk
import urllib.parse  # For URL parsing
import os
import sys

def fetch_open_graph_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        # Validate URL
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL format.")

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        og_title = soup.find('meta', property='og:title')
        og_description = soup.find('meta', property='og:description')
        og_image = soup.find('meta', property='og:image')
        og_url = soup.find('meta', property='og:url')
        og_site_name = soup.find('meta', property='og:site_name')

        # Extract domain name if og:site_name is missing or incomplete
        if og_site_name and '.' in og_site_name['content']:
            site_name = og_site_name['content'].upper()
        else:
            domain = parsed_url.netloc
            site_name = domain.upper()

        data = {
            'title': og_title['content'].strip() if og_title and og_title['content'] else '',
            'description': og_description['content'].strip() if og_description and og_description['content'] else '',
            'image': og_image['content'].strip() if og_image and og_image['content'] else '',
            'url': og_url['content'].strip() if og_url and og_url['content'] else url.strip(),
            'site_name': site_name
        }
        return data
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error fetching the URL:\n{e}")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")
        return None

def generate_html(data):
    html_template = f'''
<div style="text-align:center;">
  <div style="display:inline-block; max-width:640px; margin:20px auto; border:1px solid #ddd; font-family: Arial, sans-serif;">
    <a href="{data['url']}" target="_blank" style="text-decoration:none; color:#000;">
      <div>
        <img src="{data['image']}" alt="Article Image" style="width:100%; height:auto;">
      </div>
      <div style="background-color:#F0F2F5; padding:5px 10px; text-align:left;">
        <p style="font-size:12px; color:#777; margin:0;">{data['site_name']}</p>
        <h2 style="font-size:16px; margin:3px 0; font-weight:bold; line-height:1.2;">{data['title']}</h2>
        <p style="font-size:14px; color:#555; margin:3px 0; line-height:1.2;">{data['description']}</p>
      </div>
    </a>
  </div>
</div>
'''
    return html_template.strip()

def on_generate():
    url = entry_url.get().strip()
    if not url:
        messagebox.showwarning("Input Required", "Please enter a URL.")
        return
    data = fetch_open_graph_data(url)
    if data:
        html_code = generate_html(data)
        text_output.delete(1.0, tk.END)
        text_output.insert(tk.END, html_code)

def copy_to_clipboard():
    html_code = text_output.get(1.0, tk.END).strip()
    if html_code:
        window.clipboard_clear()
        window.clipboard_append(html_code)
        messagebox.showinfo("Copied", "HTML code copied to clipboard.")
    else:
        messagebox.showwarning("No Content", "There's no HTML code to copy.")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Create the main window
window = tk.Tk()
window.title("Link Preview Generator")
window.geometry("700x500")
window.resizable(False, False)

# Apply a theme
style = ttk.Style(window)
style.theme_use('clam')

# Set window icon
icon_path = resource_path('icon.ico')  # Ensure 'icon.ico' is in the same directory or in the PyInstaller data
window.iconbitmap(icon_path)

# URL Entry
label_url = ttk.Label(window, text="Enter the URL:")
label_url.pack(pady=10)
entry_url = ttk.Entry(window, width=80)
entry_url.pack(pady=5)

# Generate Button
btn_generate = ttk.Button(window, text="Generate HTML Code", command=on_generate)
btn_generate.pack(pady=10)

# Output Text Area
label_output = ttk.Label(window, text="Generated HTML Code:")
label_output.pack(pady=10)
text_output = scrolledtext.ScrolledText(window, width=80, height=15)
text_output.pack(pady=5)

# Copy Button
btn_copy = ttk.Button(window, text="Copy to Clipboard", command=copy_to_clipboard)
btn_copy.pack(pady=10)

# Run the application
if __name__ == "__main__":
    window.mainloop()
