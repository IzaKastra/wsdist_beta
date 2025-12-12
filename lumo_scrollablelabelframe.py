'''
File containing code to create a reusable scrollable frame class for tkinter.

Author: Lumo (Proton AI)
Lumo version: "Last updated on Tue, 09 Sep 2025 11:17:49 GMT"
https://lumo.proton.me/
'''

import tkinter as tk
from tkinter import ttk


class ScrollableLabelFrame(ttk.LabelFrame):
    """
    ttk.LabelFrame that contains a canvas + vertical scrollbar.
    * The scrollbar is **visible only when the interior is taller** than the canvas.
    * The mouse-wheel (or touch-pad scroll) works **only while the mouse pointer
      is inside the canvas**.
    * Clicking/dragging the scrollbar itself works at any time.
    """

    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        # --------------------------------------------------------------
        # 1 Canvas + vertical scrollbar (grid layout inside the frame)
        # --------------------------------------------------------------
        self._canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self._vbar = ttk.Scrollbar(self, orient="vertical",
                                   command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._vbar.set)

        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._vbar.grid(row=0, column=1, sticky="ns")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # --------------------------------------------------------------
        # 2 Interior frame that will host the actual widgets
        # --------------------------------------------------------------
        self.interior = ttk.Frame(self._canvas)
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self.interior, anchor="nw"
        )

        # --------------------------------------------------------------
        # 3 Geometry-change callbacks
        # --------------------------------------------------------------
        self.interior.bind("<Configure>", self._on_interior_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)

        # --------------------------------------------------------------
        # 4 Mouse-enter / leave on the canvas → (un)bind the wheel
        # --------------------------------------------------------------
        self._canvas.bind("<Enter>", self._on_enter)
        self._canvas.bind("<Leave>", self._on_leave)

        # --------------------------------------------------------------
        # 5 Internal state
        # --------------------------------------------------------------
        self._mousewheel_bound = False   # tracks if wheel callbacks are bound

        # Start with the scrollbar hidden - it will appear only when needed
        self._vbar.grid_remove()

    # ------------------------------------------------------------------
    # Geometry handling
    # ------------------------------------------------------------------
    def _on_interior_configure(self, event):
        """Called whenever the interior frame changes size."""
        # Update scrollregion to encompass the whole interior
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

        # Keep interior width locked to canvas width (prevents horiz. scroll)
        if self.interior.winfo_reqwidth() != self._canvas.winfo_width():
            self._canvas.itemconfigure(self._canvas_window,
                                       width=self._canvas.winfo_width())

        # Decide whether the scrollbar should be visible
        self._update_scrollbar_visibility()

    def _on_canvas_configure(self, event):
        """Called when the canvas itself is resized (e.g., window resize)."""
        self._canvas.itemconfigure(self._canvas_window, width=event.width)
        self._update_scrollbar_visibility()

    # ------------------------------------------------------------------
    # Scrollbar visibility logic
    # ------------------------------------------------------------------
    def _update_scrollbar_visibility(self):
        """
        Show the scrollbar only if the interior is taller than the canvas.
        The mouse-wheel is enabled/disabled separately on <Enter>/<Leave>.
        """
        canvas_h = self._canvas.winfo_height()
        content_h = self.interior.winfo_reqheight()

        original_code = False
        if original_code:
            if content_h <= canvas_h:
                # Nothing to scroll - hide scrollbar and disable wheel
                self._vbar.grid_remove()
                self._unbind_wheel()
            else:
                # Scrolling is possible - show scrollbar (but wheel stays disabled
                # until the mouse actually enters the canvas)
                self._vbar.grid()
                # Wheel will be bound on <Enter>, so we do nothing else here.
        else:
            self._vbar.grid()


    # ------------------------------------------------------------------
    # Mouse-enter / leave → (un)bind wheel callbacks
    # ------------------------------------------------------------------
    def _on_enter(self, event):
        """Mouse entered the canvas - enable wheel scrolling."""
        # Only bind if scrolling is actually needed
        if self.interior.winfo_reqheight() > self._canvas.winfo_height():
            self._bind_wheel()

    def _on_leave(self, event):
        """Mouse left the canvas - disable wheel scrolling."""
        self._unbind_wheel()

    # ------------------------------------------------------------------
    # Helper methods that (un)bind the wheel
    # ------------------------------------------------------------------
    def _bind_wheel(self):
        """Attach mouse-wheel callbacks (once)."""
        if not self._mousewheel_bound:
            # Windows / macOS
            self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)
            # Linux - Button-4 (up) and Button-5 (down)
            self._canvas.bind_all("<Button-4>", self._on_mousewheel_linux)
            self._canvas.bind_all("<Button-5>", self._on_mousewheel_linux)
            self._mousewheel_bound = True

    def _unbind_wheel(self):
        """Detach mouse-wheel callbacks (if they were attached)."""
        if self._mousewheel_bound:
            self._canvas.unbind_all("<MouseWheel>")
            self._canvas.unbind_all("<Button-4>")
            self._canvas.unbind_all("<Button-5>")
            self._mousewheel_bound = False

    # ------------------------------------------------------------------
    # Actual scrolling callbacks
    # ------------------------------------------------------------------
    def _on_mousewheel(self, event):
        """Windows / macOS - event.delta is multiples of 120."""
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux(self, event):
        """Linux - Button-4 (up) and Button-5 (down)."""
        direction = -1 if event.num == 4 else 1
        self._canvas.yview_scroll(direction, "units")

# -------------------------------------------------------------------------
# Demo - populate the scrollable labelframe with a list of checkboxes
# -------------------------------------------------------------------------
def demo():
    root = tk.Tk()
    root.title("Scrollable Check-box List")

    # Create the scrollable labelframe
    sf = ScrollableLabelFrame(root, text="Options")
    sf.pack(fill="both", expand=True, padx=10, pady=10)

    # -----------------------------------------------------------------
    # 1 Prepare a list of labels (could come from a file, DB, etc.)
    # -----------------------------------------------------------------
    choices = [
        "Enable notifications",
        "Show hidden files",
        "Auto-save documents",
        "Sync with cloud",
        "Enable dark mode",
        "Allow remote access",
        "Run startup script",
        "Log debug output",
        "Use experimental UI",
        "Compress backups",
        "Encrypt traffic",
        "Send usage statistics",
        "Activate beta features",
        "Show tooltips",
        "Enable spell-check",
        "Play sound on error",
        "Remember last folder",
        "Auto-update",
        "Check for updates on launch",
        "Display line numbers",
        # ... add as many as you like
    ]

    # -----------------------------------------------------------------
    # 2 For each choice create a BooleanVar and a Checkbutton
    # -----------------------------------------------------------------
    vars_dict = {}   # keep a reference so the variables aren’t garbage-collected
    for txt in choices:
        var = tk.BooleanVar(value=False)
        chk = ttk.Checkbutton(sf.interior, text=txt, variable=var)
        chk.pack(anchor="w", pady=2, padx=5)   # left-align inside the interior
        vars_dict[txt] = var

    # -----------------------------------------------------------------
    # 3 (Optional) Add a button that prints the current selections
    # -----------------------------------------------------------------
    def show_selected():
        selected = [key for key, v in vars_dict.items() if v.get()]
        print("Checked:", selected)

    ttk.Button(root, text="Print selection", command=show_selected)\
        .pack(pady=5)

    root.mainloop()


if __name__ == "__main__":
    demo()