"""
Virtual checkbox and radio frame widgets
-----------------------------------------

Author: Kastra
Assisted by: OpenAI ChatGPT (GPT-5)
"""

import tkinter as tk
from tkinter import ttk

class VirtualRadioFrame(ttk.LabelFrame):
    def __init__(self, parent, master_data, N=12, command=None, equipment_slot=None, selection_type=None, text="", **kwargs):
        super().__init__(parent, text=text)
        self.N = N
        self.master_data = sorted(master_data)
        self.visible_data = self.master_data.copy()
        self.total_items = len(self.visible_data)

        self.start_index = 0
        self.selected_value = tk.StringVar()

        self.equipment_slot = equipment_slot
        self.command = command
        self.selection_type = selection_type

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.inner = ttk.Frame(self)
        self.inner.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self._scrollbar_command)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.radio_buttons = []
        for i in range(self.N):
            rb = ttk.Radiobutton(self.inner, text=f"", variable=self.selected_value, value="", command=self._on_select)
            rb.pack(anchor="w", fill="x")
            self.radio_buttons.append(rb)

        self._update_scrollbar_visibility()
        self._refresh()

        self.inner.bind("<Enter>", self._bind_mousewheel)
        self.inner.bind("<Leave>", self._unbind_mousewheel)

    def set_visible_data(self, filtered_list):
        '''
        Update the visible items by passing a list.
        Show items that are in the input list and the master "all items" list.
        '''
        self.visible_data = sorted([x for x in filtered_list if x in self.master_data])
        self.total_items = len(self.visible_data)
        self.start_index = 0
        self._update_scrollbar_visibility()
        self._refresh()

    def get_selected(self):
        return self.selected_value.get()

    def set_selected(self, value):
        if value in self.master_data:
            self.selected_value.set(value)
        self._refresh()

    # ---------------- Scroll / Mousewheel ----------------
    def _bind_mousewheel(self, event):
        self.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        if self.total_items <= self.N:
            return
        self.start_index += -1 if event.delta > 0 else 1
        self._clamp()
        self._refresh()

    def _scrollbar_command(self, *args):
        if args[0] == "moveto":
            fraction = float(args[1])
            self.start_index = int(fraction * max(1, self.total_items - self.N))
        elif args[0] == "scroll":
            self.start_index += int(args[1])
        self._clamp()
        self._refresh()

    def _clamp(self):
        self.start_index = max(0, min(self.start_index, max(0, self.total_items - self.N)))
        self._update_scrollbar()

    def _update_scrollbar_visibility(self):
        if self.total_items > self.N:
            self.scrollbar.grid()
        else:
            self.scrollbar.grid_remove()

    def _update_scrollbar(self):
        if self.total_items <= self.N:
            return
        first = self.start_index / self.total_items
        last = (self.start_index + self.N) / self.total_items
        self.scrollbar.set(first, last)

    def _refresh(self):
        '''
        Refresh the displayed items and states.
        '''
        for i in range(self.N):
            idx = self.start_index + i
            rb = self.radio_buttons[i]
            if idx < self.total_items:
                val = self.visible_data[idx]
                rb.config(text=val, value=val)
                rb.state(["!disabled"])
            else:
                rb.config(text="", value="")
                rb.state(["disabled"])
        self._update_scrollbar()

    def _on_select(self):
        '''
        Run a command based on input.
        Usually updating gear icons and "equipped_items"
        '''
        if self.command:
            selected_name = self.selected_value.get()
            selection_type = self.selection_type
            event = (self.equipment_slot, selected_name, selection_type)
            self.command(event)




class VirtualCheckboxFrame(ttk.LabelFrame):
    def __init__(self, parent, master_data, N=12, text="", **kwargs):
        super().__init__(parent, text=text)
        self.N = N
        self.master_data = sorted(master_data)
        self.visible_data = self.master_data.copy()
        self.total_items = len(self.visible_data)
        self.start_index = 0

        # persistent selection
        self.selection_state = {name: False for name in self.master_data}

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.inner = ttk.Frame(self)
        self.inner.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self._scrollbar_command)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.vars = []
        self.checkbuttons = []
        for i in range(self.N):
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.inner, text="", variable=var, command=lambda idx=i: self._update_selection(idx))
            cb.pack(anchor="w", fill="x")
            self.vars.append(var)
            self.checkbuttons.append(cb)

        self._update_scrollbar_visibility()
        self._refresh()

        self.inner.bind("<Enter>", self._bind_mousewheel)
        self.inner.bind("<Leave>", self._unbind_mousewheel)

    def set_visible_data(self, filtered_list):
        self.visible_data = sorted([x for x in filtered_list if x in self.master_data])
        self.total_items = len(self.visible_data)
        self.start_index = 0
        self._update_scrollbar_visibility()
        self._refresh()

    def get_selected(self):
        return [k for k, v in self.selection_state.items() if v]

    def set_selected(self, names):
        for name in names:
            if name in self.selection_state:
                self.selection_state[name] = True
        self._refresh()

    def deselect(self, name):
        """
        Deselect:
        - "all"        all items in master_data
        - "visible"    only items currently in visible_data
        - a single string
        - a list of strings
        """
        if name == "all":
            targets = self.selection_state.keys()

        elif name == "visible":
            targets = self.visible_data

        elif isinstance(name, str):
            targets = [name]

        elif isinstance(name, (list, tuple, set)):
            targets = name

        else:
            raise TypeError(
                "deselect() expects 'all', 'visible', a string, or a list/tuple/set of strings"
            )

        for k in targets:
            if isinstance(k, str) and k in self.selection_state:
                self.selection_state[k] = False

        self._refresh()

    def select(self, name):
        """
        Select:
        - "all"        all items in master_data
        - "visible"    only items currently in visible_data
        - a single string
        - a list of strings
        """

        if name == "all":
            targets = self.selection_state.keys()

        elif name == "visible":
            targets = self.visible_data

        elif isinstance(name, str):
            targets = [name]

        elif isinstance(name, (list, tuple, set)):
            targets = name

        else:
            raise TypeError(
                "select() expects 'all', 'visible', a string, or a list/tuple/set of strings"
            )

        for k in targets:
            if isinstance(k, str) and k in self.selection_state:
                self.selection_state[k] = True

        self._refresh()


    def _update_selection(self, widget_index):
        idx = self.start_index + widget_index
        if idx < self.total_items:
            name = self.visible_data[idx]
            self.selection_state[name] = self.vars[widget_index].get()

    def _bind_mousewheel(self, event):
        self.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        if self.total_items <= self.N:
            return
        self.start_index += -1 if event.delta > 0 else 1
        self._clamp()
        self._refresh()

    def _scrollbar_command(self, *args):
        if args[0] == "moveto":
            fraction = float(args[1])
            self.start_index = int(fraction * max(1, self.total_items - self.N))
        elif args[0] == "scroll":
            self.start_index += int(args[1])
        self._clamp()
        self._refresh()

    def _clamp(self):
        self.start_index = max(0, min(self.start_index, max(0, self.total_items - self.N)))
        self._update_scrollbar()

    def _update_scrollbar_visibility(self):
        if self.total_items > self.N:
            self.scrollbar.grid()
        else:
            self.scrollbar.grid_remove()

    def _update_scrollbar(self):
        if self.total_items <= self.N:
            return
        first = self.start_index / self.total_items
        last = (self.start_index + self.N) / self.total_items
        self.scrollbar.set(first, last)

    def _refresh(self):
        for i in range(self.N):
            idx = self.start_index + i
            cb = self.checkbuttons[i]
            if idx < self.total_items:
                name = self.visible_data[idx]
                cb.config(text=name)
                self.vars[i].set(self.selection_state.get(name, False))
                cb.state(["!disabled"])
            else:
                cb.config(text="")
                self.vars[i].set(False)
                cb.state(["disabled"])
        self._update_scrollbar()






'''
Toy example for validation.
'''

def generate_data(n=5000):
    return [f"Item {i:04d} - " + ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=5)) for i in range(n)]

def main():
    root = tk.Tk()
    root.title("Virtual Frames External Filtering Demo")
    root.geometry("1000x600")

    master_data = generate_data(5000)

    # Search bar
    search_var = tk.StringVar()
    top_frame = ttk.Frame(root, padding=10)
    top_frame.pack(fill="x")
    ttk.Label(top_frame, text="Filter externally:").pack(side="left")
    search_entry = ttk.Entry(top_frame, textvariable=search_var)
    search_entry.pack(side="left", fill="x", expand=True, padx=10)

    # Main container
    container = ttk.Frame(root, padding=10)
    container.pack(fill="both", expand=True)
    container.columnconfigure(0, weight=1)
    container.columnconfigure(1, weight=1)

    radio_frame = VirtualRadioFrame(container, master_data, N=15)
    checkbox_frame = VirtualCheckboxFrame(container, master_data, N=15)

    radio_frame.grid(row=0, column=0, sticky="nsew", padx=5)
    checkbox_frame.grid(row=0, column=1, sticky="nsew", padx=5)

    # External filter logic
    def apply_filter(*args):
        ft = search_var.get().lower()
        filtered_list = [x for x in master_data if ft in x.lower()]
        radio_frame.set_visible_data(filtered_list)
        checkbox_frame.set_visible_data(filtered_list)

    search_var.trace_add("write", apply_filter)

    # Buttons to print selection
    ttk.Button(container, text="Print Radio Selected", command=lambda: print(radio_frame.get_selected())).grid(row=1, column=0, sticky="ew", pady=5)
    ttk.Button(container, text="Print Checkbox Selected", command=lambda: print(checkbox_frame.get_selected())).grid(row=1, column=1, sticky="ew", pady=5)

    root.mainloop()

if __name__ == "__main__":
    import random
    main()
