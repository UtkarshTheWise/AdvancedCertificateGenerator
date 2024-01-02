import tkinter
import tkinter.messagebox
import customtkinter
from PIL import Image, ImageTk, ImageDraw, ImageFont
from tkinter import filedialog
from customtkinter import CTkCanvas
import xml.etree.ElementTree as ET
import csv
import os

#Utax was here

known_fonts = ["Arial","Times New Roman", "Helvetica","Courier New", "Georgia", "Tahoma", "Verdana", "Calibri", "Comic Sans"] # Add Font Name after adding your font in fonts folder
customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"
app = customtkinter.CTk()
app.geometry("1096x720")
app.title("Advanced Certificate Generator")

textbox_counter=1
text_contents = {}
list_file_paths = []
textbox_positions = {}
current_textbox = None

def create_group(*items):
    return tuple(items)
def open_image():
    global image_file_path
    image_file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg *.gif *.bmp")])
    
    if image_file_path:
        image = Image.open(image_file_path)
        image = image.resize((canvas.winfo_width(), canvas.winfo_height()), Image.BILINEAR)
        photo = ImageTk.PhotoImage(image)
        canvas.create_image(0, 0, image=photo, anchor=customtkinter.NW)
        canvas.image = photo  

def load_file():
    global list_file_paths, textbox_counter
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("XML files", "*.xml"), ("CSV files", "*.csv")])

    if file_path:
        list_file_paths.append(file_path)
        create_textbox(textbox_counter)
        textbox_counter += 1

def create_textbox(index):
    global textbox_positions, list_file_paths, font_size, textbox_counter
    while True:
        try:
            fsdialog = customtkinter.CTkInputDialog(title="Font Size", text="Enter the font size (e.g., 12):")
            font_size = int(fsdialog.get_input())
            break
        except ValueError:
            print("Incorrect Input! Please enter a numeric value!")
        except TypeError:
            print("Operation Cancelled!")
            if list_file_paths:
                list_file_paths.pop()
            if textbox_counter > 1:
                textbox_counter -= 1
            break
    
    if index > len(list_file_paths):
        print("Please select files for the textboxes first.")
        return

    textbox_name = f"Textbox{index}"
    list_file_path = list_file_paths[index - 1] 
    x, y = 50, 50

    with open(list_file_path, "r") as file:
        text_content = file.readline().strip()  

    textbox = canvas.create_text(x, y, text=text_content, font=("Arial", int(font_size)), fill="black", tags=textbox_name)
    bbox = canvas.bbox(textbox)
    x1, y1, x2, y2 = bbox
    border_width = 2
    border = canvas.create_rectangle(x1 - border_width, y1 - border_width, x2 + border_width, y2 + border_width, outline="black", width=border_width, tags=textbox_name)
    canvas.tag_bind(textbox_name, "<ButtonPress-1>", lambda event, name=textbox_name: start_drag(event, name))
    canvas.tag_bind(textbox_name, "<B1-Motion>", drag)
    textbox_positions[textbox_name] = (x, y)

def start_drag(event, textbox_name):
    global start_x, start_y, current_textbox
    current_textbox = textbox_name
    bbox = canvas.bbox(textbox_name)  
    start_x, start_y = bbox[0], bbox[1]  

def drag(event):
    global start_x, start_y, current_textbox
    
    if current_textbox:
        x, y = event.x, event.y
        dx, dy = x - start_x, y - start_y  
        canvas.move(current_textbox, dx, dy) 
        start_x, start_y = x, y 
        textbox_positions[current_textbox] = (start_x, start_y)


def show_font_dialog():
    global selected_font, font_file_path
    selected_font = [known_fonts[0]]

    def select_font(font_name):
        global font_file_path
        selected_font[0] = font_name
        font_file_path = os.path.join("fonts", font_name + ".ttf")
        print(selected_font)
        font_dialog.destroy()

    def add_custom_font():
        file_path = filedialog.askopenfilename(filetypes=[("TrueType Font files", "*.ttf")])

        if file_path:
            custom_font_name = os.path.basename(file_path).split(".")[0]
            known_fonts.append(custom_font_name)

            try:
                custom_font = customtkinter.CTkFont(file=file_path, size=16)
                sample_font = (custom_font.family(), custom_font.actual("size"))
            except Exception:
                sample_font = ("Helvetica", 16)

            canvas_text = customtkinter.CTkLabel(canvas, text=custom_font_name, font=sample_font)
            canvas_text.pack(pady=5, padx=10)
            canvas_text.bind("<Button-1>", lambda event, name=custom_font_name: select_font(name))

    font_dialog = customtkinter.CTkToplevel(app)
    font_dialog.title("Font Selection")
    font_dialog.focus()

    canvas = customtkinter.CTkScrollableFrame(font_dialog, width=400, height=300)
    canvas.pack()

    fonts = known_fonts

    y = 10
    for font_name in fonts:
        try:
            sample_font = ImageFont.truetype(font_name, 16)
        except Exception:
            sample_font = ("Helvetica", 16)

        canvas_text = customtkinter.CTkLabel(canvas, text=font_name, font=sample_font)
        canvas_text.pack(pady=5, padx=10)
        canvas_text.bind("<Button-1>", lambda event, name=font_name: select_font(name))
        y += 30

    # Button for adding a custom font
    add_custom_button = customtkinter.CTkButton(font_dialog, text="Add Custom Font", command=add_custom_font)
    add_custom_button.pack(pady=10)

def generate_certificate():
    global selected_font, list_file_paths, textbox_positions, image_file_path, canvas

    if not image_file_path:
        print("Please open an image first.")
        return

    font_name = selected_font[0]
    fonts_folder = "fonts"
    font_file_path = os.path.join(fonts_folder, font_name + ".ttf")

    if not font_name:
        print("Please select a font first.")
        return

    original_image = Image.open(image_file_path)
    save_folder = filedialog.askdirectory(title="Select the directory to save certificates")

    if not save_folder:
        print("Please select a folder to save certificates.")
        return

    canvas_width, canvas_height = canvas.winfo_width(), canvas.winfo_height()

    for line_index in range(max(len(lines) for lines in [open(file_path, "r").read().splitlines() for file_path in list_file_paths])):
        certificate_image = original_image.copy()
        certificate_image = certificate_image.resize((canvas_width, canvas_height), Image.BILINEAR)
        draw = ImageDraw.Draw(certificate_image)
        font = ImageFont.truetype(font_file_path, int(font_size*1.5))
        
        for textbox_name, (x, y) in textbox_positions.items():
            index = int(textbox_name.split("Textbox")[1]) - 1  
            if index >= 0 and index < len(list_file_paths):
                file_path = list_file_paths[index]
                lines = open(file_path, "r").read().splitlines()

                if line_index < len(lines):
                    name = lines[line_index].strip()
                    if name:
                        draw.text((x, y), name, fill="black", font=font)

        certificate_path = os.path.join(save_folder, f"certificate_{line_index + 1}_{name}.png") #Last opened Text_Box will have the name in the certificate. 
        certificate_image.save(certificate_path)
        print(f"Certificates for line {line_index + 1} saved successfully at: {certificate_path}")

def reset_application():
    global image_file_path, list_file_paths, textbox_counter, textbox_positions, current_textbox
    image_file_path = None
    list_file_paths = []
    textbox_counter = 1
    textbox_positions = {}
    current_textbox = None
    canvas.delete("all")
                
sidebar_frame = customtkinter.CTkFrame(app, width=300, fg_color="#212529")
sidebar_frame.pack(side=customtkinter.LEFT, fill=customtkinter.Y)

open_button = customtkinter.CTkButton(sidebar_frame, text="Open Image", command=open_image)
open_button.pack(padx = 10,pady=10, fill=customtkinter.X)

textbox_button = customtkinter.CTkButton(sidebar_frame, text="Add Textbox", command=load_file)
textbox_button.pack(padx = 10, pady=10, fill=customtkinter.X)

font_selection_button = customtkinter.CTkButton(sidebar_frame, text="Select Font", command=show_font_dialog)
font_selection_button.pack(padx = 10, pady=10, fill=customtkinter.X)

generate_button = customtkinter.CTkButton(sidebar_frame, text="Generate Certificates", command=generate_certificate)
generate_button.pack(padx = 10, pady=10, fill=customtkinter.X)

reset_button = customtkinter.CTkButton(sidebar_frame, text="Reset", command=reset_application)
reset_button.pack(padx=10, pady=10, fill=customtkinter.X)

canvas = CTkCanvas(app, width=1123, height=794, bg="#46494c")
canvas.pack(pady=30)

app.mainloop()
