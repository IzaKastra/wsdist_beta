'''
File containing code to automatically find and return the state of all tkinter widgets in an application.

Authors: ChatGPT (GPT-5.1), OpenAI.  Kastra (Asura server)
'''

import tkinter as tk
from tkinter import ttk


def walk_widgets(widget):
    """Recursively yield all widgets in the hierarchy."""
    yield widget
    for child in widget.winfo_children():
        yield from walk_widgets(child)

def get_widget_state(widget):
    '''
    Given a widget object, return the relevant state/value of the widget.
    '''

    if isinstance(widget, ttk.Combobox):
        return widget.get() # Current selection from the combobox (not the full list of options)

    elif isinstance(widget, ttk.Entry):
        return widget.get() # Current text entered.
    
    elif isinstance(widget, ttk.Label):
        return widget.cget("text") # Get text from the config attribute.
    
    elif isinstance(widget, (ttk.Checkbutton)):
        variable_name = widget.cget("variable")
        if variable_name is not None:
            value = widget.getvar(variable_name) # True/False
            return value
    
    # Quicklook gear icon buttons are not saved. 
    # Instead, the currently equipped items are saved from self.quicklook_equipped_dict[slot]["item"]["Name2"] and the icons and tooltips are built from that.
        
    return None

def set_widget_state(widget, value):
    '''
    Given a widget object and a previously saved value, update the widget object using the saved value.
    '''
    # Must check Combobox first since Combobox is a subtype of Entry and would be caught by the Entry check otherwise.
    if isinstance(widget, ttk.Combobox):
        variable_name = widget.cget("textvariable")
        widget.setvar(variable_name, value)

    # Checkboxes and Radio Buttons store variables. We only care about the variable's value.
    # Checkboxes use BoolVar(True/False)
    # Radiobuttons use StringVar(equipment["Name2"])
    elif isinstance(widget, (ttk.Checkbutton, ttk.Radiobutton)):
        variable_name = widget.cget("variable")
        if variable_name is not None:
            widget.setvar(variable_name, value)

    # This GUI's ttk.Entry also all use tk.IntVar(), so we only care about pulling that value
    elif isinstance(widget, ttk.Entry):
        variable_name = widget.cget("textvariable")
        if variable_name is not None:
            widget.setvar(variable_name, value)