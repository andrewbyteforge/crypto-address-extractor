"""
GUI Extraction Handler Module
=============================
This module handles the extraction process including progress tracking.
UPDATED: Enhanced with comprehensive API call tracking and statistics display.

Author: Crypto Extractor Tool
Date: 2025-06-30
Version: 1.2.0 - Added comprehensive API call tracking integration
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
    """Handles the extraction process with progress tracking and API statistics collection."""
    
    def __init__(self, parent_gui):
        self.gui = parent_gui
        self.logger = logging.getLogger(__name__)
    
    def start_extraction(self):
        """
        Start the extraction process with optional Chainalysis API integration.
        
        This method coordinates the entire extraction workflow including:
        - File processing and address extraction
        - Optional Chainalysis API enhancement with comprehensive tracking
        - Excel export with API data and usage statistics
        - Additional report generation
        
        Raises:
            Exception: If extraction fails at any stage
        """
        if not self.gui.selected_files:
            messagebox.showwarning("No Files Selected", "Please select at least one CSV or Excel file.")
            return
        
        try:
            self.logger.info("Starting extraction process with API tracking support")
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
                
                self.logger.info("Starting Chainalysis API analysis with comprehensive tracking")
                self.gui._update_progress(60, 100, "Starting Chainalysis API analysis...")
                
                # Enhance results with API data using the comprehensive tracking system
                enhanced_results = self.gui._enhance_with_chainalysis_api(results)
                results = enhanced_results
                api_was_used = True  # Set flag that API was used
                
                # Collect comprehensive API statistics from the tracker
                api_stats = None
                if hasattr(self.gui, 'api_processor') and hasattr(self.gui.api_processor, 'api_tracker'):
                    api_stats = self.gui.api_processor.api_tracker.get_statistics_summary()
                    self.logger.info(f"Collected comprehensive API statistics: {api_stats['total_calls']} total calls, "
                                   f"{api_stats['successful_calls']} successful, "
                                   f"{api_stats['failed_calls']} failed, "
                                   f"Success rate: {api_stats['success_rate']:.1f}%")
                    
                    # Log detailed breakdown by endpoint
                    calls_by_endpoint = api_stats.get('calls_by_endpoint', {})
                    for endpoint, count in calls_by_endpoint.items():
                        if count > 0:
                            success_count = api_stats.get('success_by_endpoint', {}).get(endpoint, 0)
                            avg_time = api_stats.get('avg_response_times', {}).get(endpoint, 0)
                            self.logger.info(f"  {endpoint.title()}: {count} calls, {success_count} successful, "
                                           f"avg {avg_time:.2f}s response time")
                    
                    # Store API stats for file handler to use in summary sheet
                    self.gui.file_handler._api_stats = api_stats
                    self.logger.info("API statistics stored for Excel summary sheet display")
                else:
                    self.logger.warning("API processor or tracker not available - no comprehensive statistics to collect")
                    # Fallback to basic API stats detection
                    api_stats = getattr(self.gui.api_processor, 'api_stats', None) if hasattr(self.gui, 'api_processor') else None
                    if api_stats:
                        self.gui.file_handler._api_stats = api_stats
                        self.logger.info("Using fallback API statistics")
                
                self.gui._update_progress(80, 100, "API analysis complete, preparing reports...")
            else:
                self.gui._update_progress(80, 100, "Extraction complete, preparing reports...")
            
            # Phase 3: Excel Export (80-90%)
            self.gui._update_progress(82, 100, "Creating Excel file with API usage statistics...")
            
            # Enhanced Excel export with comprehensive API data and statistics
            saved_path = self.gui.file_handler.save_to_excel(
                results, 
                output_path,
                include_api_data=api_was_used  # This triggers API data columns and summary statistics
            )
            
            # Log comprehensive API data availability
            if api_was_used and results:
                sample_addr = results[0]
                api_attrs = [attr for attr in dir(sample_addr) if attr.startswith('api_')]
                self.logger.info(f"API attributes available on addresses: {api_attrs}")
                
                # Log API statistics summary for verification
                if hasattr(self.gui.file_handler, '_api_stats') and self.gui.file_handler._api_stats:
                    stats = self.gui.file_handler._api_stats
                    self.logger.info(f"API statistics will be displayed on Summary sheet: "
                                   f"{stats.get('total_calls', 0)} calls, "
                                   f"{stats.get('success_rate', 0):.1f}% success rate")
            
            self.gui._update_progress(88, 100, "Excel file created successfully")
            
            # Phase 4: Additional Reports (90-100%)
            self.gui._update_progress(90, 100, "Generating additional reports...")
            report_paths = self._generate_reports_with_progress(results, output_path)
            
            # Phase 5: Complete
            self.gui._update_progress(100, 100, "All exports complete!")
            
            # Enhanced completion message with API statistics
            self._show_enhanced_success_message(saved_path, results, report_paths, api_was_used)
            
        except Exception as e:
            self.logger.error(f"Extraction failed: {str(e)}", exc_info=True)
            messagebox.showerror("Extraction Failed", f"An error occurred during extraction:\n{str(e)}")
        finally:
            self.gui.extract_button.config(state=self.gui.tk.NORMAL)
            self.gui._update_progress(0, 100, "Ready")

    def _extraction_progress_callback(self, current, total, message):
        """
        Progress callback for the extraction phase (0-60%).
        
        Args:
            current (int): Current progress value
            total (int): Total progress value
            message (str): Progress message to display
        """
        # Map extraction progress to 0-60% of total progress
        extraction_progress = (current / total) * 60 if total > 0 else 0
        self.gui._update_progress(extraction_progress, 100, f"Extracting addresses: {message}")

    def _generate_reports_with_progress(self, results, output_path):
        """
        Generate reports with detailed progress tracking (90-100%).
        
        Args:
            results (List[ExtractedAddress]): Extracted addresses
            output_path (str): Base output path for reports
            
        Returns:
            List[str]: List of generated report file paths
        """
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
            
            # Prepare comprehensive metadata including API statistics
            metadata = {
                'files_processed': len(self.gui.selected_files),
                'extraction_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'total_addresses': len(results),
                'unique_addresses': len(set((addr.address, addr.crypto_type) for addr in results)),
                'chainalysis_enabled': (hasattr(self.gui, 'enable_chainalysis_var') and 
                                       self.gui.enable_chainalysis_var.get())
            }
            
            # Add API statistics to metadata if available
            if hasattr(self.gui.file_handler, '_api_stats') and self.gui.file_handler._api_stats:
                api_stats = self.gui.file_handler._api_stats
                metadata['api_statistics'] = {
                    'total_calls': api_stats.get('total_calls', 0),
                    'successful_calls': api_stats.get('successful_calls', 0),
                    'failed_calls': api_stats.get('failed_calls', 0),
                    'success_rate': api_stats.get('success_rate', 0),
                    'processing_time': api_stats.get('total_time_seconds', 0),
                    'calls_by_endpoint': api_stats.get('calls_by_endpoint', {})
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
                
                # Gather case metadata with API statistics
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
                
                # Add API statistics to case info if available
                if hasattr(self.gui.file_handler, '_api_stats') and self.gui.file_handler._api_stats:
                    case_info['api_statistics'] = self.gui.file_handler._api_stats
                
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
        """
        Generate PDF, Word, and i2 reports if requested. (Legacy method for backward compatibility)
        
        Args:
            results (List[ExtractedAddress]): Extracted addresses
            output_path (str): Base output path for reports
            
        Returns:
            List[str]: List of generated report file paths
        """
        return self._generate_reports_with_progress(results, output_path)

    def _show_enhanced_success_message(self, saved_path, results, report_paths, api_was_used):
        """
        Show enhanced extraction complete message with API statistics details.
        
        Args:
            saved_path (str): Path to the saved Excel file
            results (List[ExtractedAddress]): Extracted addresses
            report_paths (List[str]): Generated report file paths
            api_was_used (bool): Whether API analysis was performed
        """
        message = f"Successfully extracted addresses!\n\nResults saved to:\n{os.path.basename(saved_path)}"
        
        # Add API analysis summary if used
        if api_was_used:
            api_enhanced_count = sum(1 for addr in results 
                                   if hasattr(addr, 'api_balance') or 
                                      hasattr(addr, 'api_exposure'))
            if api_enhanced_count > 0:
                message += f"\n\n🔍 Chainalysis API Analysis Completed"
                message += f"\n   • {api_enhanced_count} addresses enhanced with API data"
                
                # Add comprehensive API statistics if available
                if hasattr(self.gui.file_handler, '_api_stats') and self.gui.file_handler._api_stats:
                    stats = self.gui.file_handler._api_stats
                    message += f"\n   • {stats.get('total_calls', 0)} total API calls made"
                    message += f"\n   • {stats.get('success_rate', 0):.1f}% success rate"
                    
                    # Show processing time
                    total_time = stats.get('total_time_seconds', 0)
                    if total_time > 60:
                        message += f"\n   • Processing time: {total_time/60:.1f} minutes"
                    else:
                        message += f"\n   • Processing time: {total_time:.1f} seconds"
                    
                    # Show endpoint breakdown
                    calls_by_endpoint = stats.get('calls_by_endpoint', {})
                    active_endpoints = [endpoint for endpoint, count in calls_by_endpoint.items() if count > 0]
                    if active_endpoints:
                        message += f"\n   • Endpoints used: {', '.join(active_endpoints)}"
                
                message += f"\n\n📊 Check the Excel Summary sheet for detailed API usage statistics!"
                message += f"\n📋 Enhanced data available in individual crypto sheets and API columns"
        
        # Add report paths information
        if report_paths:
            message += "\n\n📄 Additional Reports Generated:"
            for path in report_paths:
                if path:  # Check if path is not None or empty
                    filename = os.path.basename(path)
                    if path.endswith('.xml'):
                        message += f"\n   📊 i2 Investigation: {filename}"
                    elif path.endswith('.csv') and 'entities' in filename:
                        message += f"\n   📊 i2 Entities: {filename}"
                    elif path.endswith('.csv') and 'links' in filename:
                        message += f"\n   📊 i2 Links: {filename}"
                    elif path.endswith('.gexf'):
                        message += f"\n   🔗 Gephi Graph: {filename}"
                    elif path.endswith('.graphml'):
                        message += f"\n   🔗 Cytoscape Graph: {filename}"
                    elif path.endswith('.pdf'):
                        message += f"\n   📄 PDF Report: {filename}"
                    elif path.endswith('.docx'):
                        message += f"\n   📄 Word Report: {filename}"
                    else:
                        message += f"\n   📄 {filename}"
            
            # Add helpful message for i2 users
            if any(path and path.endswith('.xml') for path in report_paths):
                message += f"\n\n💡 i2 Import Instructions:"
                message += f"\n   1. Open i2 Analyst's Notebook"
                message += f"\n   2. Import → From File → Select the XML file"
                message += f"\n   3. Or import CSV files separately (entities + links)"
        
        # Add final tips
        message += f"\n\n✨ Tips:"
        message += f"\n   • Check the Summary sheet for complete extraction statistics"
        if api_was_used:
            message += f"\n   • API Usage Statistics section shows detailed call metrics"
            message += f"\n   • Individual crypto sheets contain enhanced API data"
        message += f"\n   • All data is ready for analysis and investigation"
        
        self.logger.info(f"Extraction complete with enhanced API tracking. Results saved to: {saved_path}")
        messagebox.showinfo("Extraction Complete", message)

    def _show_success_message(self, saved_path, results, report_paths):
        """
        Show extraction complete message with details. (Legacy method for backward compatibility)
        
        Args:
            saved_path (str): Path to the saved Excel file
            results (List[ExtractedAddress]): Extracted addresses
            report_paths (List[str]): Generated report file paths
        """
        api_was_used = hasattr(self.gui, 'enable_chainalysis_var') and self.gui.enable_chainalysis_var.get()
        self._show_enhanced_success_message(saved_path, results, report_paths, api_was_used)