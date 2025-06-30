"""
GUI Extraction Handler Module
=============================
This module handles the extraction process including progress tracking.

Author: Crypto Extractor Tool
Date: 2025-01-09
Version: 1.1.0 - Enhanced with detailed progress tracking
"""

import os
import logging
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from typing import Callable

from report_generator import ReportGenerator
from config import Config


class ExtractionHandler:
    """Handles the extraction process with progress tracking."""
    
    def __init__(self, parent_gui):
        self.gui = parent_gui
        self.logger = logging.getLogger(__name__)
    
    def start_extraction(self):
        """
        Start the extraction process with optional Chainalysis API integration.
        
        This method coordinates the entire extraction workflow including:
        - File processing and address extraction
        - Optional Chainalysis API enhancement
        - Excel export with API data if available
        - Additional report generation
        
        Raises:
            Exception: If extraction fails at any stage
        """
        if not self.gui.selected_files:
            messagebox.showwarning("No Files Selected", "Please select at least one CSV or Excel file.")
            return
        
        try:
            self.logger.info("Starting extraction process")
            self.gui.extract_button.config(state=self.gui.tk.DISABLED)
            
            # Get output filename with full path
            output_file = self.gui.output_name_var.get()
            if not output_file.endswith('.xlsx'):
                output_file += '.xlsx'
            
            # Combine with output directory
            output_path = os.path.join(self.gui.output_dir_var.get(), output_file)
            
            # Add custom cryptocurrencies to the extractor
            if self.gui.custom_cryptos:
                self.gui.extractor.add_custom_cryptos(self.gui.custom_cryptos)
            
            # Phase 1: Address Extraction (0-60%)
            self.gui._update_progress(0, 100, "Starting address extraction...")
            
            results = self.gui.extractor.extract_from_files(
                self.gui.selected_files,
                progress_callback=self._extraction_progress_callback,
                validate_checksum=self.gui.validate_checksum_var.get()
            )
            
            # Track whether API was used
            api_was_used = False
            
            # Phase 2: API Analysis (60-80%)
            if (hasattr(self.gui, 'enable_chainalysis_var') and 
                self.gui.enable_chainalysis_var.get() and 
                self.gui.api_service and results):
                
                self.logger.info("Starting Chainalysis API analysis")
                self.gui._update_progress(60, 100, "Starting Chainalysis API analysis...")
                
                # Enhance results with API data
                enhanced_results = self.gui._enhance_with_chainalysis_api(results)
                results = enhanced_results
                api_was_used = True  # Set flag that API was used
                
                self.gui._update_progress(80, 100, "API analysis complete, preparing reports...")
            else:
                self.gui._update_progress(80, 100, "Extraction complete, preparing reports...")
            
            # Phase 3: Excel Export (80-90%)
            self.gui._update_progress(82, 100, "Creating Excel file...")
            
            # FIXED: Explicitly pass include_api_data flag based on whether API was used
            saved_path = self.gui.file_handler.save_to_excel(
                results, 
                output_path,
                include_api_data=api_was_used  # Explicitly set this
            )
            
            # Log what data is available
            if api_was_used and results:
                sample_addr = results[0]
                api_attrs = [attr for attr in dir(sample_addr) if attr.startswith('api_')]
                self.logger.info(f"API attributes available on addresses: {api_attrs}")
            
            self.gui._update_progress(88, 100, "Excel file created successfully")
            
            # Phase 4: Additional Reports (90-100%)
            self.gui._update_progress(90, 100, "Generating additional reports...")
            report_paths = self._generate_reports_with_progress(results, output_path)
            
            # Phase 5: Complete
            self.gui._update_progress(100, 100, "All exports complete!")
            # Show completion message with file paths
            message = f"Extraction complete!\n\nFiles created:\n"
            message += f"• Excel: {os.path.basename(saved_path)}\n"
            
            # Add report paths (report_paths is a list, not a dict)
            for report_path in report_paths:
                if report_path:
                    message += f"• {os.path.basename(report_path)}\n"
            
            messagebox.showinfo("Success", message)
            
        except Exception as e:
            self.logger.error(f"Extraction failed: {str(e)}", exc_info=True)
            messagebox.showerror("Extraction Failed", f"An error occurred during extraction:\n{str(e)}")
        finally:
            self.gui.extract_button.config(state=self.gui.tk.NORMAL)
            self.gui._update_progress(0, 100, "Ready")








    def _extraction_progress_callback(self, current, total, message):
        """Progress callback for the extraction phase (0-60%)."""
        # Map extraction progress to 0-60% of total progress
        extraction_progress = (current / total) * 60 if total > 0 else 0
        self.gui._update_progress(extraction_progress, 100, f"Extracting addresses: {message}")

    def _generate_reports_with_progress(self, results, output_path):
        """Generate reports with detailed progress tracking (90-100%)."""
        report_paths = []
        current_progress = 90
        total_reports = 0
        
        # Count how many reports will be generated
        if self.gui.generate_pdf_var.get():
            total_reports += 1
        if self.gui.generate_word_var.get():
            total_reports += 1
        if hasattr(self.gui, 'export_i2_var') and self.gui.export_i2_var.get():
            total_reports += 1
        
        if total_reports == 0:
            self.gui._update_progress(100, 100, "No additional reports requested")
            return report_paths
        
        progress_per_report = 10 / total_reports  # 10% total for reports (90-100%)
        completed_reports = 0
        
        # Generate PDF/Word reports
        if self.gui.generate_pdf_var.get() or self.gui.generate_word_var.get():
            self.gui._update_progress(current_progress, 100, "Preparing report metadata...")
            
            report_gen = ReportGenerator()
            
            # Prepare metadata
            metadata = {
                'files_processed': len(self.gui.selected_files),
                'extraction_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'total_addresses': len(results),
                'unique_addresses': len(set((addr.address, addr.crypto_type) for addr in results)),
                'chainalysis_enabled': (hasattr(self.gui, 'enable_chainalysis_var') and 
                                       self.gui.enable_chainalysis_var.get())
            }
            
            # Generate PDF report
            if self.gui.generate_pdf_var.get():
                self.gui._update_progress(current_progress, 100, "Generating PDF report...")
                pdf_path = output_path.replace('.xlsx', '_report.pdf')
                pdf_path = report_gen.generate_pdf_report(results, pdf_path, metadata)
                report_paths.append(pdf_path)
                self.logger.info(f"PDF report generated: {pdf_path}")
                
                completed_reports += 1
                current_progress += progress_per_report
                self.gui._update_progress(current_progress, 100, f"PDF report complete ({completed_reports}/{total_reports})")
            
            # Generate Word report
            if self.gui.generate_word_var.get():
                self.gui._update_progress(current_progress, 100, "Generating Word report...")
                word_path = output_path.replace('.xlsx', '_report.docx')
                word_path = report_gen.generate_word_report(results, word_path, metadata)
                report_paths.append(word_path)
                self.logger.info(f"Word report generated: {word_path}")
                
                completed_reports += 1
                current_progress += progress_per_report
                self.gui._update_progress(current_progress, 100, f"Word report complete ({completed_reports}/{total_reports})")
        
        # Generate i2 export
        if hasattr(self.gui, 'export_i2_var') and self.gui.export_i2_var.get():
            try:
                from i2_exporter import i2Exporter
                
                self.gui._update_progress(current_progress, 100, "Starting i2 Analyst's Notebook export...")
                self.logger.info("Starting i2 Analyst's Notebook export...")
                
                # Gather case metadata
                case_info = {
                    'case_id': getattr(self.gui, 'case_id_var', tk.StringVar()).get() or f"CASE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'analyst': getattr(self.gui, 'analyst_var', tk.StringVar()).get() or "Unknown",
                    'priority': getattr(self.gui, 'case_priority_var', tk.StringVar()).get() or "MEDIUM",
                    'investigation_type': getattr(self.gui, 'investigation_type_var', tk.StringVar()).get() or "FINANCIAL_CRIMES",
                    'target_entity': getattr(self.gui, 'target_entity_var', tk.StringVar()).get() or "",
                    'extraction_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'total_addresses': len(results),
                    'unique_addresses': len(set((addr.address, addr.crypto_type) for addr in results)),
                    'files_processed': len(self.gui.selected_files)
                }
                
                # Create a progress callback for i2 export
                def i2_progress_callback(stage, detail=""):
                    progress_stages = {
                        'entities': current_progress + (progress_per_report * 0.2),
                        'clusters': current_progress + (progress_per_report * 0.4),
                        'services': current_progress + (progress_per_report * 0.6),
                        'relationships': current_progress + (progress_per_report * 0.7),
                        'export_xml': current_progress + (progress_per_report * 0.8),
                        'export_csv': current_progress + (progress_per_report * 0.9)
                    }
                    stage_progress = progress_stages.get(stage, current_progress)
                    message = f"i2 export: {stage.replace('_', ' ').title()}"
                    if detail:
                        message += f" - {detail}"
                    self.gui._update_progress(stage_progress, 100, message)
                
                # Export to i2
                exporter = i2Exporter()
                i2_path = exporter.export_investigation_data(results, case_info=case_info, 
                                                           progress_callback=i2_progress_callback)
                report_paths.append(i2_path)
                self.logger.info(f"i2 export generated: {i2_path}")
                
                completed_reports += 1
                current_progress += progress_per_report
                self.gui._update_progress(current_progress, 100, f"i2 export complete ({completed_reports}/{total_reports})")
                
            except ImportError as e:
                self.logger.error(f"i2 exporter module not found: {e}")
                self.gui._update_progress(current_progress, 100, "i2 export failed - module not found")
                self.logger.error("Please ensure i2_exporter.py is in the project directory")
            except Exception as e:
                self.logger.error(f"Failed to generate i2 export: {e}", exc_info=True)
                self.gui._update_progress(current_progress, 100, f"i2 export failed - {str(e)[:50]}...")
        
        # Final progress update
        self.gui._update_progress(100, 100, f"All reports complete! Generated {len(report_paths)} files.")
        
        return report_paths
    
    def _generate_reports(self, results, output_path):
        """Generate PDF, Word, and i2 reports if requested. (Legacy method for backward compatibility)"""
        return self._generate_reports_with_progress(results, output_path)

    def _show_success_message(self, saved_path, results, report_paths):
        """Show extraction complete message with details."""
        message = f"Successfully extracted addresses!\n\nResults saved to:\n{saved_path}"
        
        if hasattr(self.gui, 'enable_chainalysis_var') and self.gui.enable_chainalysis_var.get():
            api_enhanced_count = sum(1 for addr in results 
                                   if hasattr(addr, 'api_balance') or 
                                      hasattr(addr, 'api_exposure'))
            if api_enhanced_count > 0:
                message += f"\n\nChainalysis API analysis completed for {api_enhanced_count} addresses"
                message += f"\nCheck the Balances, Exchange Exposure, High Value, and Risk Analysis sheets!"
        
        if report_paths:
            message += "\n\nReports generated:"
            for path in report_paths:
                filename = os.path.basename(path)
                if path.endswith('.xml'):
                    message += f"\n📊 i2 Investigation: {filename}"
                elif path.endswith('.csv') and 'entities' in filename:
                    message += f"\n📊 i2 Entities: {filename}"
                elif path.endswith('.csv') and 'links' in filename:
                    message += f"\n📊 i2 Links: {filename}"
                elif path.endswith('.gexf'):
                    message += f"\n🔗 Gephi Graph: {filename}"
                elif path.endswith('.graphml'):
                    message += f"\n🔗 Cytoscape Graph: {filename}"
                elif path.endswith('.pdf'):
                    message += f"\n📄 PDF Report: {filename}"
                elif path.endswith('.docx'):
                    message += f"\n📄 Word Report: {filename}"
                else:
                    message += f"\n📄 {filename}"
            
            # Add helpful message for i2 users
            if any(path.endswith('.xml') for path in report_paths):
                message += f"\n\n💡 i2 Import Instructions:"
                message += f"\n   1. Open i2 Analyst's Notebook"
                message += f"\n   2. Import → From File → Select the XML file"
                message += f"\n   3. Or import CSV files separately (entities + links)"
        
        self.logger.info(f"Extraction complete. Results saved to: {saved_path}")
        messagebox.showinfo("Extraction Complete", message)