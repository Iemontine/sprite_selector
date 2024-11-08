import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class SpriteEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Sprite Editor")
        
        self.cell_size = tk.IntVar(value=16)
        self.show_grid = tk.BooleanVar(value=False)
        self.selected_sprites = []
        self.start_x = None
        self.start_y = None
        self.existing_spritesheet = None
        self.spritesheet_path = None
        
        self.create_widgets()
        self.bind_shortcuts()
    
    def create_widgets(self):
        self.file_frame = tk.Frame(self.root)
        self.file_frame.pack(pady=10)
        
        self.file_button = tk.Button(self.file_frame, text="Select Sprite File", command=self.load_image)
        self.file_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(self.file_frame, text="Clear Current Selections", command=self.clear_selections)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        self.size_frame = tk.Frame(self.root)
        self.size_frame.pack()
        
        tk.Label(self.size_frame, text="Cell Size:").pack(side=tk.LEFT)
        tk.Radiobutton(self.size_frame, text="16x16", variable=self.cell_size, value=16).pack(side=tk.LEFT)
        tk.Radiobutton(self.size_frame, text="32x32", variable=self.cell_size, value=32).pack(side=tk.LEFT)
        tk.Radiobutton(self.size_frame, text="48x48", variable=self.cell_size, value=48).pack(side=tk.LEFT)
        
        self.grid_checkbox = tk.Checkbutton(self.root, text="Show Grid", variable=self.show_grid, command=self.toggle_grid)
        self.grid_checkbox.pack()
        
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scroll_x = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.scroll_y = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.config(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)
        
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)
        
        self.generate_button = tk.Button(self.button_frame, text="Generate", command=self.generate_spritesheet)
        self.generate_button.pack(side=tk.LEFT, padx=5)
        
        self.append_button = tk.Button(self.button_frame, text="Append", command=self.append_to_spritesheet)
        self.append_button.pack(side=tk.LEFT, padx=5)
    
    def bind_shortcuts(self):
        self.root.bind("<Control-z>", self.undo_selection)
    
    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if file_path:
            self.image = Image.open(file_path)
            self.display_image()
    
    def clear_selections(self):
        self.selected_sprites.clear()
        self.canvas.delete("selection")
    
    def load_spritesheet(self):
        file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if file_path:
            self.existing_spritesheet = Image.open(file_path)
            self.display_spritesheet()
            messagebox.showinfo("Success", "Existing spritesheet loaded.")
    
    def display_image(self):
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self.canvas.bind("<Button-1>", self.start_selection)
        self.canvas.bind("<B1-Motion>", self.update_selection)
        self.canvas.bind("<ButtonRelease-1>", self.end_selection)
        if self.show_grid.get():
            self.draw_grid()
        self.update_selections()
    
    def display_spritesheet(self):
        if self.existing_spritesheet:
            self.tk_spritesheet = ImageTk.PhotoImage(self.existing_spritesheet)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_spritesheet)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
    
    def start_selection(self, event):
        self.start_x, self.start_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
    
    def update_selection(self, event):
        self.canvas.delete("selection")
        x0, y0 = self.start_x, self.start_y
        x1, y1 = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.canvas.create_rectangle(x0, y0, x1, y1, outline="black", fill="blue", stipple="gray25", tag="selection")
    
    def end_selection(self, event):
        x0, y0 = self.start_x, self.start_y
        x1, y1 = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        cell_size = self.cell_size.get()
        x0, y0 = (x0 // cell_size) * cell_size, (y0 // cell_size) * cell_size
        x1, y1 = ((x1 // cell_size) + 1) * cell_size, ((y1 // cell_size) + 1) * cell_size
        self.selected_sprites.append((x0, y0, x1, y1))
        self.update_selections()
    
    def undo_selection(self, event=None):
        if self.selected_sprites:
            self.selected_sprites.pop()
            self.canvas.delete("all")
            if self.existing_spritesheet:
                self.display_spritesheet()
            self.display_image()
            self.update_selections()
    
    def update_selections(self):
        self.canvas.delete("selection")
        for i, (x0, y0, x1, y1) in enumerate(self.selected_sprites):
            color = "green" if i == len(self.selected_sprites) - 1 else "blue"
            self.canvas.create_rectangle(x0, y0, x1, y1, outline=color, width=2, tag="selection")
    
    def draw_grid(self):
        self.canvas.delete("grid")
        cell_size = self.cell_size.get()
        width = self.image.width
        height = self.image.height
        for i in range(0, width, cell_size):
            self.canvas.create_line([(i, 0), (i, height)], tag="grid", fill="gray")
        for i in range(0, height, cell_size):
            self.canvas.create_line([(0, i), (width, i)], tag="grid", fill="gray")
    
    def toggle_grid(self):
        if self.show_grid.get():
            self.draw_grid()
        else:
            self.canvas.delete("grid")
    
    def generate_spritesheet(self):
        if not self.selected_sprites:
            return
        
        if not self.spritesheet_path:
            self.spritesheet_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if not self.spritesheet_path:
                return
        
        cell_size = self.cell_size.get()
        sheet_width = 512  # Example width, can be adjusted
        num_columns = sheet_width // cell_size
        max_height = max((y1 - y0) for x0, y0, x1, y1 in self.selected_sprites)
        total_height = sum((y1 - y0) for x0, y0, x1, y1 in self.selected_sprites)
        
        if self.existing_spritesheet:
            existing_width, existing_height = self.existing_spritesheet.size
            new_image = Image.new("RGBA", (max(existing_width, sheet_width), existing_height + int(total_height)))
            new_image.paste(self.existing_spritesheet, (0, 0))
            current_y = existing_height
        else:
            new_image = Image.new("RGBA", (sheet_width, int(total_height)))
            current_y = 0
        
        current_x = 0
        for x0, y0, x1, y1 in self.selected_sprites:
            sprite = self.image.crop((x0, y0, x1, y1))
            sprite_width = x1 - x0
            sprite_height = y1 - y0
            if current_x + sprite_width > sheet_width:
                current_x = 0
                current_y += max_height
            new_image.paste(sprite, (int(current_x), int(current_y)))
            current_x += sprite_width
        
        new_image = self.remove_empty_rows(new_image, cell_size)
        new_image.save(self.spritesheet_path)
        messagebox.showinfo("Success", f"New spritesheet generated as '{self.spritesheet_path}'")
    
    def remove_empty_rows(self, image, cell_size):
        width, height = image.size
        pixels = image.load()
        
        non_empty_rows = []
        for y in range(0, height, cell_size):
            row_empty = True
            for x in range(width):
                for dy in range(cell_size):
                    if y + dy < height and pixels[x, y + dy][3] != 0:  # Check alpha channel
                        row_empty = False
                        break
                if not row_empty:
                    break
            if not row_empty:
                non_empty_rows.extend(range(y, y + cell_size))
        
        if non_empty_rows:
            new_height = len(non_empty_rows)
            new_image = Image.new("RGBA", (width, new_height))
            for new_y, old_y in enumerate(non_empty_rows):
                for x in range(width):
                    new_image.putpixel((x, new_y), pixels[x, old_y])
            return new_image
        else:
            return image
    
    def append_to_spritesheet(self):
        if not self.spritesheet_path:
            self.spritesheet_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
            if not self.spritesheet_path:
                return
        try:
            self.existing_spritesheet = Image.open(self.spritesheet_path)
        except FileNotFoundError:
            messagebox.showerror("Error", f"{self.spritesheet_path} not found.")
            return
        self.generate_spritesheet()
        self.existing_spritesheet = None  # Prevent displaying the spritesheet

if __name__ == "__main__":
    root = tk.Tk()
    app = SpriteEditor(root)
    root.mainloop()
