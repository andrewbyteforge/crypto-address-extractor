"""
GUI Styles Module
=================
This module handles all styling and theming for the GUI.

Author: Crypto Extractor Tool
Date: 2025-01-09
Version: 1.0.0
"""

from tkinter import ttk


class GUIStyles:
    """Mixin class for GUI styling."""
    
    def _apply_styling(self):
        """Apply modern styling to the application."""
        style = ttk.Style()
        
        # Use a modern theme
        style.theme_use('clam')
        
        # Define colors
        bg_color = "#f0f0f0"
        primary_color = "#2196F3"  # Material Blue
        success_color = "#4CAF50"  # Material Green
        danger_color = "#f44336"   # Material Red
        warning_color = "#FF9800"  # Material Orange
        
        self.root.configure(bg=bg_color)
        
        # Configure notebook (tabs) style
        style.configure('TNotebook', background=bg_color)
        style.configure('TNotebook.Tab', padding=[20, 10])
        style.map('TNotebook.Tab',
                  background=[('selected', primary_color)],
                  foreground=[('selected', 'white')])
        
        # Configure button styles
        style.configure('Primary.TButton',
                        background=primary_color,
                        foreground='white',
                        borderwidth=0,
                        focuscolor='none',
                        padding=(10, 8))
        style.map('Primary.TButton',
                  background=[('active', '#1976D2')])
        
        style.configure('Success.TButton',
                        background=success_color,
                        foreground='white',
                        borderwidth=0,
                        focuscolor='none',
                        padding=(10, 8))
        style.map('Success.TButton',
                  background=[('active', '#388E3C')])
        
        style.configure('Danger.TButton',
                        background=danger_color,
                        foreground='white',
                        borderwidth=0,
                        focuscolor='none',
                        padding=(10, 8))
        style.map('Danger.TButton',
                  background=[('active', '#D32F2F')])
        
        style.configure('Warning.TButton',
                        background=warning_color,
                        foreground='white',
                        borderwidth=0,
                        focuscolor='none',
                        padding=(10, 8))
        
        # Configure frame styles
        style.configure('Card.TFrame',
                        background='white',
                        relief='flat',
                        borderwidth=1)
        
        # Configure progress bar style
        style.configure('TProgressbar',
                        background=primary_color,
                        troughcolor=bg_color,
                        borderwidth=0,
                        lightcolor=primary_color,
                        darkcolor=primary_color)