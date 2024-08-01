import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO

import tkinter as tk
from tkinter import Listbox, StringVar
import requests

class AutoCompleteEntry(tk.Entry):
    def __init__(self, parent, api_key, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.api_key = api_key
        self._hits = []
        self._hit_index = 0
        self._hits_var = StringVar()
        self._hits_var.set('')
        self._listbox = Listbox(parent, height=5)
        self._listbox.bind('<ButtonRelease-1>', self._on_listbox_select)
        self._listbox.bind('<KeyRelease>', self._on_listbox_keypress)
        self.bind('<KeyRelease>', self._on_key_release)
        self._listbox.place_forget()

    def _on_key_release(self, event):
        text = self.get()
        if text == '':
            self._listbox.place_forget()
        else:
            self._fetch_suggestions(text)

    def _fetch_suggestions(self, text):
        url = f"http://www.omdbapi.com/?s={text}&apikey={self.api_key}"
        response = requests.get(url)
        data = response.json()
        if data['Response'] == 'True':
            suggestions = [movie['Title'] for movie in data['Search']]
            self._display_suggestions(suggestions)
        else:
            self._listbox.place_forget()

    def _display_suggestions(self, suggestions):
        self._hits = suggestions
        self._listbox.delete(0, tk.END)
        for hit in self._hits:
            self._listbox.insert(tk.END, hit)
        if suggestions:
            self._listbox.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height(), anchor='nw')

    def _on_listbox_select(self, event):
        selected = self._listbox.get(self._listbox.curselection())
        self.delete(0, tk.END)
        self.insert(0, selected)
        self._listbox.place_forget()

    def _on_listbox_keypress(self, event):
        if event.keysym == 'Up':
            self._hit_index = (self._hit_index - 1) % len(self._hits)
        elif event.keysym == 'Down':
            self._hit_index = (self._hit_index + 1) % len(self._hits)
        elif event.keysym == 'Return':
            self._on_listbox_select(event)
        self._listbox.selection_clear(0, tk.END)
        self._listbox.selection_set(self._hit_index)
        self._listbox.activate(self._hit_index)
        self._listbox.see(self._hit_index)

def get_movie_reviews(api_key, movie_title, label, poster_label):
    # Prepare the request URL
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={api_key}"
    
    # Make the request
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        output = ""
        # Check if the movie was found
        if data['Response'] == 'True':
            # Print movie details and reviews
            output += f"Title: {data['Title']}\n"
            output += f"Year: {data['Year']}\n"
            output += f"Genre: {data['Genre']}\n"
            output += f"Director: {data['Director']}\n"
            output += f"Plot: {data['Plot']}\n"
            output += "\nRatings:\n"
            for rating in data['Ratings']:
                output += f"Source: {rating['Source']}, Rating: {rating['Value']}\n"
            
            # Fetch and display the movie poster
            poster_url = data['Poster']
            if poster_url != 'N/A':
                poster_response = requests.get(poster_url)
                poster_image = Image.open(BytesIO(poster_response.content))
                poster_photo = ImageTk.PhotoImage(poster_image)
                poster_label.config(image=poster_photo)
                poster_label.image = poster_photo
            else:
                poster_label.config(image='', text="No poster available")
            
            # Update labels visibility
            label.config(text=output)
        else:
            output += "Movie not found!"
            poster_label.config(image='', text="No poster available")
            label.config(text=output)
    else:
        output += "Error in API request!"
        poster_label.config(image='', text="No poster available")
        label.config(text=output)

def create():
    api_key = '86d6a552'

    root = tk.Tk()
    root.title("Movie Reviews")
    root.geometry("1000x1000")
    root.configure(bg='#A4998E')

    main_frame = tk.Frame(root, bg='#4B1816', width=950, height=800)
    main_frame.pack_propagate(False)
    main_frame.pack(padx=20, pady=20)

    color_frame1 = tk.Frame(main_frame, bg='#507B6A', width=900, height=80)
    color_frame1.pack_propagate(False)
    color_frame1.pack(padx=20, pady=20)

    label_name = tk.Label(color_frame1, text="Movie Review Finder", bg="#507B6A", height=3, width=20, bd=3,
                         font=("Arial", 20, "bold"), cursor="hand2", fg="#4B1816", justify=tk.CENTER, underline=0)
    label_name.pack()

    color_frame2 = tk.Frame(main_frame, bg='#507B6A', width=900, height=700)
    color_frame2.pack_propagate(False)
    color_frame2.pack(padx=20, pady=20)

    label_name = tk.Label(color_frame2, text="Enter Movie Name:", bg="#507B6A", height=3, width=20, bd=3,
                         font=("Arial", 16, "bold"), cursor="hand2", fg="#4B1816", justify=tk.CENTER, underline=0)
    label_name.pack(padx=10, pady=5, side=tk.TOP)

    entry_name = AutoCompleteEntry(color_frame2, api_key, bg="#6A513C", font=("Arial", 12, "bold"))
    entry_name.pack(padx=10, pady=5, side=tk.TOP)

    movie_review_label = tk.Label(color_frame2, text="", justify="left", width=40, wraplength=300, bg="#507B6A", font=("Arial", 14, "bold"))
    movie_review_label.pack(padx=10, pady=10, side=tk.LEFT)

    movie_poster_label = tk.Label(color_frame2, bg="#507B6A")
    movie_poster_label.pack(padx=10, pady=10, side=tk.RIGHT)

    button = tk.Button(color_frame2, text="Show Movie Review", bd=5, bg="#6A513C", fg="white", font=("Arial", 11, "bold"),
                       justify="right", command=lambda: get_movie_reviews(api_key, entry_name.get(), movie_review_label, movie_poster_label))
    button.pack(pady=10, side=tk.BOTTOM)

    root.mainloop()

create()
