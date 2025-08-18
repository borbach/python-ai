import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os

class JSONEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON Editor")
        self.root.geometry("800x600")
        
        self.json_data = {}
        self.current_file = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # File operations frame
        file_frame = ttk.LabelFrame(main_frame, text="File Operations", padding="5")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(file_frame, text="Open JSON File", command=self.open_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_frame, text="Save", command=self.save_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_frame, text="Save As", command=self.save_as_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_frame, text="New File", command=self.new_file).pack(side=tk.LEFT, padx=(0, 5))
        
        self.file_label = ttk.Label(file_frame, text="No file loaded")
        self.file_label.pack(side=tk.RIGHT)
        
        # Edit operations frame
        edit_frame = ttk.LabelFrame(main_frame, text="Edit Operations", padding="5")
        edit_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(edit_frame, text="Add Key-Value", command=self.add_key_value).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(edit_frame, text="Edit Selected", command=self.edit_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(edit_frame, text="Delete Selected", command=self.delete_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(edit_frame, text="Refresh View", command=self.refresh_tree).pack(side=tk.LEFT, padx=(0, 5))
        
        # Treeview for JSON structure
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Create treeview with scrollbars
        self.tree = ttk.Treeview(tree_frame, columns=("value", "type"), show="tree headings")
        self.tree.heading("#0", text="Key/Index")
        self.tree.heading("value", text="Value")
        self.tree.heading("type", text="Type")
        
        # Configure column widths
        self.tree.column("#0", width=200)
        self.tree.column("value", width=300)
        self.tree.column("type", width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Bind double-click event
        self.tree.bind("<Double-1>", self.on_double_click)
        
    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Open JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.json_data = json.load(file)
                self.current_file = file_path
                self.file_label.config(text=f"File: {os.path.basename(file_path)}")
                self.refresh_tree()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")
    
    def save_file(self):
        if not self.current_file:
            self.save_as_file()
            return
            
        try:
            with open(self.current_file, 'w', encoding='utf-8') as file:
                json.dump(self.json_data, file, indent=2, ensure_ascii=False)
            messagebox.showinfo("Success", "File saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Save JSON File",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(self.json_data, file, indent=2, ensure_ascii=False)
                self.current_file = file_path
                self.file_label.config(text=f"File: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def new_file(self):
        self.json_data = {}
        self.current_file = None
        self.file_label.config(text="New file (unsaved)")
        self.refresh_tree()
    
    def refresh_tree(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Populate tree with JSON data
        self.populate_tree("", self.json_data)
    
    def populate_tree(self, parent, data, key=None):
        if isinstance(data, dict):
            if key is not None:
                node = self.tree.insert(parent, "end", text=str(key), values=("", "dict"))
                parent = node
            
            for k, v in data.items():
                self.populate_tree(parent, v, k)
                
        elif isinstance(data, list):
            if key is not None:
                node = self.tree.insert(parent, "end", text=str(key), values=("", "list"))
                parent = node
            
            for i, item in enumerate(data):
                self.populate_tree(parent, item, f"[{i}]")
                
        else:
            # Leaf node (primitive value)
            value_str = json.dumps(data) if isinstance(data, str) else str(data)
            data_type = type(data).__name__
            self.tree.insert(parent, "end", text=str(key) if key else str(data), 
                           values=(value_str, data_type))
    
    def get_path_to_item(self, item):
        """Get the path from root to the selected item"""
        path = []
        current = item
        
        while current:
            parent = self.tree.parent(current)
            if parent:
                # Get the key/index for this item
                key = self.tree.item(current, "text")
                # Handle list indices
                if key.startswith("[") and key.endswith("]"):
                    key = int(key[1:-1])
                path.insert(0, key)
            current = parent
            
        return path
    
    def get_data_at_path(self, path):
        """Get data at the specified path"""
        data = self.json_data
        for key in path:
            data = data[key]
        return data
    
    def set_data_at_path(self, path, value):
        """Set data at the specified path"""
        data = self.json_data
        for key in path[:-1]:
            data = data[key]
        data[path[-1]] = value
    
    def delete_data_at_path(self, path):
        """Delete data at the specified path"""
        if not path:
            return
            
        data = self.json_data
        for key in path[:-1]:
            data = data[key]
        
        if isinstance(data, dict):
            del data[path[-1]]
        elif isinstance(data, list):
            data.pop(path[-1])
    
    def add_key_value(self):
        selected = self.tree.selection()
        parent_data = self.json_data
        parent_path = []
        
        if selected:
            item = selected[0]
            parent_path = self.get_path_to_item(item)
            parent_data = self.get_data_at_path(parent_path)
            
            # If selected item is not a container, add to its parent
            if not isinstance(parent_data, (dict, list)):
                if parent_path:
                    parent_path = parent_path[:-1]
                    parent_data = self.get_data_at_path(parent_path) if parent_path else self.json_data
                else:
                    parent_data = self.json_data
        
        # Create dialog for adding new key-value pair
        dialog = AddKeyValueDialog(self.root, isinstance(parent_data, list))
        
        if dialog.result:
            key, value, value_type = dialog.result
            
            try:
                # Convert value based on type
                if value_type == "string":
                    converted_value = str(value)
                elif value_type == "int":
                    converted_value = int(value)
                elif value_type == "float":
                    converted_value = float(value)
                elif value_type == "bool":
                    converted_value = value.lower() in ('true', '1', 'yes', 'on')
                elif value_type == "null":
                    converted_value = None
                elif value_type == "dict":
                    converted_value = {}
                elif value_type == "list":
                    converted_value = []
                else:
                    converted_value = json.loads(value)
                
                if isinstance(parent_data, dict):
                    parent_data[key] = converted_value
                elif isinstance(parent_data, list):
                    if key == "":  # Append to list
                        parent_data.append(converted_value)
                    else:
                        index = int(key)
                        parent_data.insert(index, converted_value)
                
                self.refresh_tree()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add item: {str(e)}")
    
    def edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to edit")
            return
        
        item = selected[0]
        path = self.get_path_to_item(item)
        
        if not path:  # Root level
            messagebox.showinfo("Info", "Cannot edit root level directly. Add key-value pairs instead.")
            return
        
        current_value = self.get_data_at_path(path)
        
        # Only allow editing of primitive values
        if isinstance(current_value, (dict, list)):
            messagebox.showinfo("Info", "Cannot edit containers directly. Edit their contents or delete and recreate.")
            return
        
        # Get new value from user
        new_value = simpledialog.askstring(
            "Edit Value",
            f"Edit value for '{path[-1]}':",
            initialvalue=json.dumps(current_value) if isinstance(current_value, str) else str(current_value)
        )
        
        if new_value is not None:
            try:
                # Try to parse as JSON first, fallback to string
                try:
                    parsed_value = json.loads(new_value)
                except json.JSONDecodeError:
                    parsed_value = new_value
                
                self.set_data_at_path(path, parsed_value)
                self.refresh_tree()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update value: {str(e)}")
    
    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
        
        item = selected[0]
        path = self.get_path_to_item(item)
        
        if not path:
            # Check if this is a root-level item in a dict/list
            item_text = self.tree.item(item, "text")
            if isinstance(self.json_data, dict) and item_text in self.json_data:
                # This is a root-level key in a dictionary
                if messagebox.askyesno("Confirm Delete", f"Delete root-level key '{item_text}'?"):
                    try:
                        del self.json_data[item_text]
                        self.refresh_tree()
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to delete item: {str(e)}")
                return
            elif isinstance(self.json_data, list):
                # This is a root-level item in a list
                try:
                    # Extract index from item text (format: [0], [1], etc.)
                    if item_text.startswith("[") and item_text.endswith("]"):
                        index = int(item_text[1:-1])
                        if messagebox.askyesno("Confirm Delete", f"Delete root-level item at index {index}?"):
                            self.json_data.pop(index)
                            self.refresh_tree()
                    return
                except (ValueError, IndexError) as e:
                    messagebox.showerror("Error", f"Failed to delete item: {str(e)}")
                    return
            else:
                messagebox.showwarning("Warning", "Cannot delete the entire root structure")
                return
        
        # Confirm deletion for non-root items
        if messagebox.askyesno("Confirm Delete", f"Delete '{path[-1]}'?"):
            try:
                self.delete_data_at_path(path)
                self.refresh_tree()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete item: {str(e)}")
    
    def on_double_click(self, event):
        self.edit_selected()

class AddKeyValueDialog:
    def __init__(self, parent, is_list=False):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Key-Value Pair")
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Create form
        frame = ttk.Frame(self.dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Key field
        ttk.Label(frame, text="Key:" if not is_list else "Index (empty to append):").pack(anchor=tk.W)
        self.key_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.key_var, width=40).pack(fill=tk.X, pady=(0, 10))
        
        # Value field
        ttk.Label(frame, text="Value:").pack(anchor=tk.W)
        self.value_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.value_var, width=40).pack(fill=tk.X, pady=(0, 10))
        
        # Type field
        ttk.Label(frame, text="Type:").pack(anchor=tk.W)
        self.type_var = tk.StringVar(value="string")
        type_combo = ttk.Combobox(frame, textvariable=self.type_var, 
                                 values=["string", "int", "float", "bool", "null", "dict", "list", "json"],
                                 state="readonly", width=37)
        type_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.RIGHT)
        
        # Focus on key entry
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def ok_clicked(self):
        key = self.key_var.get()
        value = self.value_var.get()
        value_type = self.type_var.get()
        
        if not key and value_type not in ["dict", "list"]:
            # For non-containers, we need some identifier
            pass  # Allow empty key for list append
        
        self.result = (key, value, value_type)
        self.dialog.destroy()
    
    def cancel_clicked(self):
        self.result = None
        self.dialog.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = JSONEditor(root)
    root.mainloop()


