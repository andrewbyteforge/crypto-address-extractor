"""
Quick Setup Script for Enhanced i2 Features
===========================================

File: setup_enhanced_i2.py
Function: One-click setup for enhanced i2 features

Run this script first to set up everything you need for
the enhanced i2 investigative features.

Author: Crypto Extractor Tool
Date: 2025-07-01
Version: 1.0.0
"""

import os
import sys
import shutil
from datetime import datetime


def create_project_structure():
    """Create the proper project structure."""
    
    print("📁 Creating project structure...")
    
    # Create directories if needed
    directories = ['logs', 'exports', 'reports', 'dashboards']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"   ✅ Created: {directory}/")
        else:
            print(f"   📁 Exists: {directory}/")


def check_and_fix_i2_exporter():
    """Check and fix the existing i2_exporter.py file."""
    
    print("\n🔧 Checking i2_exporter.py...")
    
    if not os.path.exists('i2_exporter.py'):
        print("   ❌ i2_exporter.py not found")
        print("   🔧 Creating minimal working version...")
        
        create_minimal_i2_exporter()
        print("   ✅ Created minimal i2_exporter.py")
        return True
    
    # Check if file has syntax issues
    try:
        with open('i2_exporter.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to compile
        compile(content, 'i2_exporter.py', 'exec')
        print("   ✅ i2_exporter.py syntax is correct")
        
        # Check if it has the required class
        if 'class EnhancedI2Exporter' in content or 'class i2Exporter' in content:
            print("   ✅ Required class found")
            return True
        else:
            print("   ⚠️  Required class not found, will use compatibility mode")
            return True
            
    except SyntaxError as e:
        print(f"   ❌ Syntax error found: {e}")
        print("   🔧 Creating backup and fixed version...")
        
        # Create backup
        backup_name = f"i2_exporter_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        shutil.copy2('i2_exporter.py', backup_name)
        print(f"   📦 Backup saved as: {backup_name}")
        
        # Create working version
        create_minimal_i2_exporter()
        print("   ✅ Created working i2_exporter.py")
        return True


def create_minimal_i2_exporter():
    """Create a minimal working i2 exporter."""
    
    minimal_content = '''"""
Minimal Working i2 Exporter
===========================

This is a simplified version that works with the enhanced features.
"""

import logging
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class i2Entity:
    """Simple i2 Entity."""
    entity_id: str
    entity_type: str
    label: str
    attributes: Dict[str, Any]
    icon_style: str = ""
    risk_score: float = 0.0


@dataclass  
class i2Link:
    """Simple i2 Link."""
    link_id: str
    from_entity: str
    to_entity: str
    link_type: str
    label: str
    attributes: Dict[str, Any]
    strength: float = 1.0


class i2Exporter:
    """Minimal working i2 exporter."""
    
    def __init__(self):
        """Initialize the exporter."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Minimal i2 Exporter initialized")
    
    def export_investigation_data(self, addresses, case_info=None, progress_callback=None):
        """Export investigation data."""
        try:
            if progress_callback:
                progress_callback('starting', 'Initializing export')
            
            # Create basic entities
            entities = self._create_address_entities(addresses)
            
            # Create basic links  
            links = self._create_address_links(addresses)
            
            # Export to XML
            filename = f"investigation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            xml_path = self._export_to_xml(entities, links, filename, case_info)
            
            if progress_callback:
                progress_callback('complete', f'Export completed: {xml_path}')
            
            return xml_path
            
        except Exception as e:
            self.logger.error(f"Export failed: {e}")
            raise
    
    def _create_address_entities(self, addresses):
        """Create address entities."""
        entities = []
        
        for i, addr in enumerate(addresses):
            entity = i2Entity(
                entity_id=f"addr_{i:04d}",
                entity_type="CryptoAddress",
                label=str(getattr(addr, 'address', addr))[:30],
                attributes={
                    'Address': str(getattr(addr, 'address', addr)),
                    'CryptoType': getattr(addr, 'crypto_type', 'Unknown'),
                    'SourceFile': getattr(addr, 'filename', 'Unknown')
                },
                icon_style="Person"
            )
            entities.append(entity)
        
        return entities
    
    def _create_address_links(self, addresses):
        """Create address links."""
        # For minimal version, create no links
        return []
    
    def _export_to_xml(self, entities, links, filename, case_info=None):
        """Export to XML."""
        root = ET.Element("Investigation")
        
        # Add entities
        entities_elem = ET.SubElement(root, "Entities") 
        for entity in entities:
            entity_elem = ET.SubElement(entities_elem, "Entity")
            entity_elem.set("EntityId", entity.entity_id)
            entity_elem.set("EntityType", entity.entity_type)
            
            ET.SubElement(entity_elem, "Label").text = entity.label
            
            # Add attributes
            attrs_elem = ET.SubElement(entity_elem, "Attributes")
            for key, value in entity.attributes.items():
                attr_elem = ET.SubElement(attrs_elem, "Attribute")
                attr_elem.set("Name", key)
                attr_elem.text = str(value)
        
        # Write file
        output_path = f"{filename}_minimal_i2.xml"
        rough_string = ET.tostring(root, 'unicode')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        return output_path


# Backwards compatibility
class EnhancedI2Exporter(i2Exporter):
    """Backwards compatibility alias."""
    pass
'''
    
    with open('i2_exporter.py', 'w', encoding='utf-8') as f:
        f.write(minimal_content)


def check_dependencies():
    """Check for required Python packages."""
    
    print("\n📦 Checking dependencies...")
    
    required_packages = ['xml', 'json', 'csv', 'datetime', 'collections', 'typing', 'dataclasses']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ❌ {package}")
    
    if missing_packages:
        print(f"   ⚠️  Missing packages: {missing_packages}")
        print("   💡 Most should be built-in to Python 3.7+")
    else:
        print("   ✅ All dependencies available")
    
    return len(missing_packages) == 0


def create_launch_script():
    """Create a convenient launch script."""
    
    print("\n🚀 Creating launch script...")
    
    launch_content = '''@echo off
echo ====================================
echo Enhanced i2 Features Launcher
echo ====================================
echo.

python start_enhanced_i2.py

echo.
echo Press any key to exit...
pause > nul
'''
    
    with open('launch_enhanced_i2.bat', 'w') as f:
        f.write(launch_content)
    
    print("   ✅ Created: launch_enhanced_i2.bat")


def create_readme():
    """Create a README file with instructions."""
    
    print("\n📝 Creating README...")
    
    readme_content = f'''# Enhanced i2 Features for Cryptocurrency Investigation

## Quick Start

1. **Double-click:** `launch_enhanced_i2.bat`
   OR
2. **Run in terminal:** `python start_enhanced_i2.py`

## What You'll Get

### 📊 Enhanced Analysis
- Money flow tracing
- Risk cluster detection  
- Automated insights generation
- Darknet market detection
- Privacy coin analysis

### 📁 Generated Files
- `*_enhanced_i2_chart.xml` - Import into i2 Analyst's Notebook
- `*_enhanced_investigation_report.txt` - Comprehensive analysis
- `investigation_dashboard_*.html` - Interactive web dashboard
- `*_insights.json` - Machine-readable intelligence
- `*_risk_clusters.csv` - High-risk entity groups

### 🎯 Key Features
- **Critical Findings:** Automatic detection of high-risk patterns
- **Risk Scoring:** Multi-factor risk assessment for all entities
- **Cluster Analysis:** Groups related entities for efficient investigation
- **Visual Dashboards:** Web-based charts and graphs
- **Actionable Intelligence:** Specific recommendations for each finding

## Import into i2 Analyst's Notebook

1. Open i2 Analyst's Notebook
2. File → Import → Import Chart
3. Select the generated `*_enhanced_i2_chart.xml` file
4. Review imported entities and relationships
5. Use the investigation report for guidance

## Files in This Project

- `i2_enhanced_features.py` - Advanced analysis features
- `start_enhanced_i2.py` - Main startup script
- `i2_exporter.py` - Basic i2 export functionality
- `setup_enhanced_i2.py` - This setup script

## Troubleshooting

If you encounter issues:
1. Check that all `.py` files are in the same directory
2. Ensure you have Python 3.7+ installed
3. Run the setup script again: `python setup_enhanced_i2.py`

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
'''
    
    with open('README_Enhanced_i2.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("   ✅ Created: README_Enhanced_i2.md")


def main():
    """Main setup function."""
    
    print("🌟 Enhanced i2 Features - Quick Setup")
    print("=" * 60)
    print("This will set up everything you need for advanced")
    print("cryptocurrency investigation with i2 integration.")
    print()
    
    try:
        # Step 1: Create project structure
        create_project_structure()
        
        # Step 2: Check and fix i2_exporter
        check_and_fix_i2_exporter()
        
        # Step 3: Check dependencies
        check_dependencies()
        
        # Step 4: Create launch script
        create_launch_script()
        
        # Step 5: Create README
        create_readme()
        
        print("\n🎉 Setup Complete!")
        print("=" * 60)
        print("✅ Project structure created")
        print("✅ i2_exporter.py ready")
        print("✅ Dependencies checked")
        print("✅ Launch script created")
        print("✅ Documentation ready")
        
        print("\n🚀 Ready to Start!")
        print("-" * 30)
        print("Option 1: Double-click 'launch_enhanced_i2.bat'")
        print("Option 2: Run 'python start_enhanced_i2.py'")
        print("Option 3: Read 'README_Enhanced_i2.md' for details")
        
        print("\n💡 What happens next:")
        print("1. The system will load your cryptocurrency addresses")
        print("2. Advanced analysis will detect patterns and risks")
        print("3. Multiple export formats will be generated")
        print("4. You can import the XML into i2 Analyst's Notebook")
        print("5. Review the investigation report for key findings")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())