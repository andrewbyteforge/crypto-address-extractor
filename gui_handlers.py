"""
GUI Event Handlers Module
=========================
This module contains all the event handlers and action methods for the GUI.

Author: Crypto Extractor Tool
Date: 2025-01-09
Version: 1.0.0
"""

import os
import re
import logging
from tkinter import filedialog, messagebox
from datetime import datetime
from typing import List
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from extractor import ExtractedAddress
from report_generator import ReportGenerator
from config import Config
from iapi_service import IAPIService


class GUIHandlers:
    """Mixin class containing all event handlers and action methods."""
    
    def _toggle_chainalysis_options(self):
        """Enable/disable Chainalysis API options based on checkbox state."""
        if hasattr(self, 'api_options_frame'):
            state = 'normal' if self.enable_chainalysis_var.get() else 'disabled'
            
            # Enable/disable all child widgets
            for child in self.api_options_frame.winfo_children():
                if isinstance(child, (self.ttk.Checkbutton, self.ttk.Spinbox, self.ttk.Combobox)):
                    child.config(state=state)
                elif isinstance(child, self.ttk.Frame):
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, (self.ttk.Checkbutton, self.ttk.Spinbox, self.ttk.Combobox)):
                            grandchild.config(state=state)
    
    def _select_files(self):
        """Open file dialog to select CSV and Excel files."""
        try:
            initial_dir = self.config.get('default_input_directory', '')
            if not os.path.exists(initial_dir):
                initial_dir = os.getcwd()
            
            files = filedialog.askopenfilenames(
                title="Select CSV or Excel Files",
                initialdir=initial_dir,
                filetypes=[
                    ("All supported files", "*.csv;*.xlsx;*.xls"),
                    ("Excel files", "*.xlsx;*.xls"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ]
            )
            
            if files:
                # Update default directory
                new_dir = os.path.dirname(files[0])
                self.config['default_input_directory'] = new_dir
                Config.save(self.config)
            
            for file in files:
                if file not in self.selected_files:
                    self.selected_files.append(file)
                    self.files_listbox.insert(self.tk.END, os.path.basename(file))
                    self.logger.info(f"Added file: {file}")
                    
        except Exception as e:
            self.logger.error(f"Error selecting files: {str(e)}")
            messagebox.showerror("Error", f"Failed to select files: {str(e)}")
    
    def _remove_selected_file(self):
        """Remove selected file from the list."""
        try:
            selection = self.files_listbox.curselection()
            if selection:
                # Remove in reverse order to maintain indices
                for index in reversed(selection):
                    removed_file = self.selected_files.pop(index)
                    self.files_listbox.delete(index)
                    self.logger.info(f"Removed file: {removed_file}")
        except Exception as e:
            self.logger.error(f"Error removing file: {str(e)}")
    
    def _clear_files(self):
        """Clear all selected files."""
        self.selected_files.clear()
        self.files_listbox.delete(0, self.tk.END)
        self.logger.info("Cleared all selected files")
    
    def _select_output_directory(self):
        """Open dialog to select output directory."""
        try:
            initial_dir = self.output_dir_var.get() or os.getcwd()
            
            directory = filedialog.askdirectory(
                title="Select Output Directory",
                initialdir=initial_dir
            )
            
            if directory:
                self.output_dir_var.set(directory)
                self.config['default_output_directory'] = directory
                Config.save(self.config)
                
        except Exception as e:
            self.logger.error(f"Error selecting directory: {str(e)}")
            messagebox.showerror("Error", f"Failed to select directory: {str(e)}")
    
    def _add_custom_crypto(self):
        """Add a custom cryptocurrency pattern with duplicate checking."""
        name = self.custom_name_var.get().strip()
        symbol = self.custom_symbol_var.get().strip().upper()
        pattern = self.custom_pattern_var.get().strip()
        
        if not all([name, symbol, pattern]):
            messagebox.showwarning("Missing Information", "Please fill in all fields.")
            return
        
        # Check for duplicates
        for crypto in self.custom_cryptos:
            if crypto['symbol'] == symbol:
                messagebox.showwarning(
                    "Duplicate Symbol", 
                    f"A cryptocurrency with symbol '{symbol}' already exists!\n"
                    f"Existing: {crypto['name']}"
                )
                return
            if crypto['name'].lower() == name.lower():
                messagebox.showwarning(
                    "Duplicate Name", 
                    f"A cryptocurrency with name '{name}' already exists!"
                )
                return
        
        # Check against built-in cryptocurrencies
        if symbol in self.extractor.patterns:
            messagebox.showwarning(
                "Symbol Already Exists", 
                f"'{symbol}' is already a built-in cryptocurrency!"
            )
            return
        
        try:
            # Validate the regex pattern
            re.compile(pattern)
            
            # Add to custom cryptos list
            custom_crypto = {
                'name': name,
                'symbol': symbol,
                'pattern': pattern
            }
            
            self.custom_cryptos.append(custom_crypto)
            
            # Update the recent listbox
            self.recent_custom_listbox.insert(0, f"{name} ({symbol}): {pattern}")
            if self.recent_custom_listbox.size() > 5:
                self.recent_custom_listbox.delete(5)  # Keep only 5 most recent
            
            # Clear the input fields
            self.custom_name_var.set("")
            self.custom_symbol_var.set("")
            self.custom_pattern_var.set("")
            
            # Save to config
            self.config['custom_cryptos'] = self.custom_cryptos
            Config.save(self.config)
            
            # Refresh the crypto list tab
            self._populate_crypto_list()
            
            self.logger.info(f"Added custom cryptocurrency: {name} ({symbol})")
            messagebox.showinfo("Success", f"Successfully added {name} ({symbol})!")
            
        except re.error as e:
            messagebox.showerror("Invalid Pattern", f"Invalid regex pattern: {str(e)}")
    
    def _on_search_changed(self, *args):
        """Handle search text changes."""
        self.current_page = 0  # Reset to first page
        self._populate_crypto_list()
    
    def _prev_page(self):
        """Go to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self._populate_crypto_list()
    
    def _next_page(self):
        """Go to next page."""
        self.current_page += 1
        self._populate_crypto_list()
    
    def _update_pagination_buttons(self, total_pages):
        """Update pagination button states."""
        # Find the buttons
        for widget in self.page_frame.winfo_children():
            if isinstance(widget, self.ttk.Button):
                if "Previous" in widget['text']:
                    widget['state'] = 'normal' if self.current_page > 0 else 'disabled'
                elif "Next" in widget['text']:
                    widget['state'] = 'normal' if self.current_page < total_pages - 1 else 'disabled'
    
    def _populate_crypto_list(self):
        """Populate the cryptocurrency list with pagination."""
        # Clear existing items
        for item in self.crypto_tree.get_children():
            self.crypto_tree.delete(item)
        
        # Get all cryptocurrencies
        all_cryptos = []
        
        # Built-in cryptocurrencies
        for symbol, pattern in self.extractor.patterns.items():
            # Skip aliases
            if symbol in ['MONERO', 'RIPPLE', 'CARDANO', 'LITECOIN', 'DOGECOIN', 'TETHER', 'SHIBA INU']:
                continue
            
            # Get example pattern
            if pattern.patterns:
                example = str(pattern.patterns[0].pattern)
                # Clean up the pattern for display
                example = example.replace('\\b', '').replace('\\', '')
                if len(example) > 50:
                    example = example[:47] + "..."
            else:
                example = "N/A"
            
            all_cryptos.append({
                'name': pattern.name,
                'symbol': pattern.symbol,
                'type': 'Built-in',
                'example': example
            })
        
        # Custom cryptocurrencies
        for crypto in self.custom_cryptos:
            all_cryptos.append({
                'name': crypto['name'],
                'symbol': crypto['symbol'],
                'type': 'Custom',
                'example': crypto['pattern']
            })
        
        # Apply search filter
        search_term = self.search_var.get().lower()
        if search_term:
            all_cryptos = [c for c in all_cryptos if 
                          search_term in c['name'].lower() or 
                          search_term in c['symbol'].lower()]
        
        # Sort by name
        all_cryptos.sort(key=lambda x: x['name'])
        
        # Calculate pagination
        total_items = len(all_cryptos)
        total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        
        # Ensure current page is valid
        self.current_page = max(0, min(self.current_page, total_pages - 1))
        
        # Get items for current page
        start_idx = self.current_page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_items)
        page_items = all_cryptos[start_idx:end_idx]
        
        # Add items to tree
        for crypto in page_items:
            # Use different tags for styling
            tags = ('custom',) if crypto['type'] == 'Custom' else ('builtin',)
            self.crypto_tree.insert('', 'end', text=crypto['name'],
                                   values=(crypto['symbol'], crypto['type'], crypto['example']),
                                   tags=tags)
        
        # Configure tags for different colors
        self.crypto_tree.tag_configure('custom', foreground='#2196F3')  # Blue for custom
        self.crypto_tree.tag_configure('builtin', foreground='#424242')  # Dark gray for built-in
        
        # Update page label
        self.page_label.config(text=f"Page {self.current_page + 1} of {total_pages}")
        
        # Update button states
        self._update_pagination_buttons(total_pages)
    
    def _save_all_settings(self):
        """Save all settings from the Settings tab."""
        try:
            # Update API key
            new_api_key = self.api_key_var.get().strip()
            self.config['chainalysis_api_key'] = new_api_key
            
            # Update other settings
            self.config['default_input_directory'] = self.input_dir_var.get()
            self.config['validate_checksums'] = self.settings_validate_var.get()
            
            # Save config
            Config.save(self.config)
            
            # Reinitialize API service if key changed
            if new_api_key != self.api_key:
                self.api_key = new_api_key
                if new_api_key:
                    try:
                        self.api_service = IAPIService(new_api_key)
                        # Recreate API tab
                        self._refresh_api_tab()
                        messagebox.showinfo("Settings Saved", "Settings saved successfully!\nAPI service reinitialized.")
                    except Exception as e:
                        self.logger.error(f"Failed to initialize API service: {e}")
                        messagebox.showerror("API Error", f"Failed to initialize API service: {str(e)}")
                else:
                    self.api_service = None
                    self._refresh_api_tab()
                    messagebox.showinfo("Settings Saved", "Settings saved successfully!\nAPI service disabled.")
            else:
                messagebox.showinfo("Settings Saved", "Settings saved successfully!")
                
        except Exception as e:
            self.logger.error(f"Error saving settings: {str(e)}")
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def _refresh_api_tab(self):
        """Refresh the API tab after settings change."""
        from api_tab import APITab
        
        # Find and remove the API tab
        for i in range(self.notebook.index('end')):
            if self.notebook.tab(i, 'text') == 'API':
                # Remember current tab
                current_tab = self.notebook.index('current')
                
                # Remove old API tab
                self.notebook.forget(i)
                
                # Create new API tab at the same position
                api_frame = self.ttk.Frame(self.notebook)
                self.notebook.insert(i, api_frame, text="API")
                
                if not self.api_service:
                    # Show API key setup message
                    setup_frame = self.ttk.Frame(api_frame)
                    setup_frame.pack(expand=True)
                    
                    self.ttk.Label(setup_frame, text="Chainalysis API not configured", 
                             font=('Arial', 14, 'bold')).pack(pady=20)
                    self.ttk.Label(setup_frame, text="Please go to Settings tab to configure your API key.",
                             font=('Arial', 10)).pack(pady=10)
                    
                    self.ttk.Button(setup_frame, text="Go to Settings", 
                              command=lambda: self.notebook.select(self.settings_frame),
                              style="Primary.TButton").pack(pady=10)
                else:
                    # Initialize API tab with the frame and api_service
                    self.api_tab = APITab(api_frame, self.api_service)
                
                # Restore tab selection
                self.notebook.select(current_tab)
                break
    
    def _update_progress(self, current, total, message=""):
        """Update progress bar and status message."""
        if total > 0:
            progress = (current / total) * 100
            self.progress_var.set(progress)
        
        if message:
            self.status_var.set(message)
        
        self.root.update_idletasks()
    
    def _update_statistics(self, stats_dict):
        """Update statistics display."""
        self.stats_text.config(state=self.tk.NORMAL)
        self.stats_text.delete(1.0, self.tk.END)
        
        stats_text = "Extraction Statistics:\n"
        stats_text += "-" * 30 + "\n"
        
        for crypto, count in stats_dict.items():
            stats_text += f"{crypto}: {count} addresses found\n"
        
        self.stats_text.insert(1.0, stats_text)
        self.stats_text.config(state=self.tk.DISABLED)