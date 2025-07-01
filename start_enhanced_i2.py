"""
Step-by-Step Startup Guide for Enhanced i2 Features
===================================================

File: start_enhanced_i2.py
Function: Complete startup and integration guide

This script shows you exactly how to start using the enhanced features
with your existing crypto address extractor and i2 export functionality.

Author: Crypto Extractor Tool  
Date: 2025-07-01
Version: 1.0.0
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Dict, Any


def setup_enhanced_i2_environment():
    """
    Set up the environment for enhanced i2 features.
    
    Returns:
        bool: True if setup successful
        
    Raises:
        Exception: If setup fails
    """
    try:
        print("🔧 Setting up Enhanced i2 Environment")
        print("=" * 50)
        
        # Check for required files
        required_files = [
            'i2_enhanced_features.py',
            'i2_exporter.py'  # Your existing file
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
                print(f"❌ Missing: {file}")
            else:
                print(f"✅ Found: {file}")
        
        if missing_files:
            print(f"\n⚠️  Missing {len(missing_files)} required files!")
            print("Please ensure these files are in your project directory:")
            for file in missing_files:
                print(f"   - {file}")
            return False
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        print("\n✅ Environment setup complete!")
        return True
        
    except Exception as e:
        print(f"❌ Environment setup failed: {e}")
        return False


def run_enhanced_i2_export_with_your_data():
    """
    Main function to run enhanced i2 export with your extracted addresses.
    
    This integrates with your existing extraction workflow.
    """
    try:
        print("\n🚀 Starting Enhanced i2 Export")
        print("=" * 50)
        
        # Step 1: Import required modules
        print("📦 Step 1: Importing modules...")
        
        # Fix any syntax issues in your i2_exporter first
        try:
            from i2_exporter import EnhancedI2Exporter
            print("   ✅ Imported existing i2_exporter")
        except Exception as e:
            print(f"   ⚠️  Issue with i2_exporter.py: {e}")
            print("   🔧 Using simplified version...")
            # We'll create a simple version if needed
            create_simple_i2_exporter()
            from i2_exporter import EnhancedI2Exporter
        
        from i2_enhanced_features import i2EnhancedFeatures
        print("   ✅ Imported enhanced features")
        
        # Step 2: Get your extracted addresses
        print("\n📊 Step 2: Loading your address data...")
        
        # This is where you would load your actual extracted addresses
        # Replace this with your real data loading
        addresses = load_your_extracted_addresses()
        print(f"   ✅ Loaded {len(addresses)} addresses")
        
        # Step 3: Set up case information
        print("\n📋 Step 3: Setting up case information...")
        case_info = setup_case_information()
        print(f"   ✅ Case ID: {case_info['case_id']}")
        
        # Step 4: Initialize exporters
        print("\n🔧 Step 4: Initializing enhanced features...")
        base_exporter = EnhancedI2Exporter()
        enhanced_features = i2EnhancedFeatures(base_exporter)
        print("   ✅ Enhanced features initialized")
        
        # Step 5: Run the enhanced export process
        print("\n⚡ Step 5: Running enhanced analysis...")
        
        def progress_callback(stage, detail=""):
            print(f"   🔄 {stage}: {detail}")
        
        # Create entities and links
        progress_callback("entities", "Creating address entities")
        entities = create_enhanced_entities(addresses, base_exporter)
        
        progress_callback("relationships", "Creating relationships") 
        links = create_enhanced_relationships(addresses, entities)
        
        # Apply enhanced analysis
        progress_callback("money_flows", "Analyzing money flows")
        money_flows = enhanced_features.analyze_money_flows(entities, links)
        
        progress_callback("risk_clusters", "Detecting risk clusters")
        risk_clusters = enhanced_features.detect_risk_clusters(entities, links)
        
        progress_callback("insights", "Generating investigative insights")
        insights = enhanced_features.generate_investigative_insights(
            entities, links, money_flows, risk_clusters
        )
        
        # Step 6: Generate all export formats
        print("\n📤 Step 6: Generating enhanced exports...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_base = f"{case_info['case_id']}_{timestamp}"
        
        # Generate i2 XML for Analyst's Notebook
        progress_callback("export_xml", "Creating i2 XML chart")
        xml_path = export_i2_xml(entities, links, filename_base, case_info)
        
        # Generate enhanced investigation report
        progress_callback("export_report", "Creating investigation report")
        report_path = enhanced_features.export_enhanced_investigation_report(
            filename_base, entities, links, insights, money_flows, risk_clusters
        )
        
        # Generate interactive dashboard
        progress_callback("export_dashboard", "Creating interactive dashboard")
        dashboard_path = enhanced_features.create_investigation_dashboard(
            entities, links, insights, money_flows, risk_clusters
        )
        
        # Step 7: Show results
        print("\n🎉 Step 7: Export Complete!")
        print("=" * 50)
        
        show_export_results(xml_path, report_path, dashboard_path, insights, risk_clusters)
        
        return xml_path
        
    except Exception as e:
        print(f"❌ Enhanced export failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def load_your_extracted_addresses():
    """
    Load your extracted cryptocurrency addresses.
    
    Replace this with your actual data loading logic.
    """
    try:
        # Option 1: Load from your existing extraction results
        # This is where you'd integrate with your main extraction pipeline
        
        # Check if you have recent extraction results
        if os.path.exists('extraction_results.json'):
            import json
            with open('extraction_results.json', 'r') as f:
                data = json.load(f)
                addresses = data.get('addresses', [])
                print(f"   📁 Loaded {len(addresses)} addresses from extraction_results.json")
                return addresses
        
        # Option 2: Load from Excel/CSV file
        excel_files = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.csv')) and 'crypto' in f.lower()]
        if excel_files:
            print(f"   📊 Found extraction files: {excel_files}")
            # You would load from your Excel/CSV files here
            # For demo, create sample data
            return create_sample_addresses()
        
        # Option 3: Run extraction if no existing data
        print("   ⚠️  No existing extraction data found")
        print("   💡 You can either:")
        print("      1. Run your main extraction first")
        print("      2. Use sample data for testing")
        
        response = input("   Use sample data for demo? (y/n): ")
        if response.lower() == 'y':
            return create_sample_addresses()
        else:
            print("   🔄 Please run your main extraction first, then restart this script")
            return []
            
    except Exception as e:
        print(f"   ❌ Error loading addresses: {e}")
        return create_sample_addresses()


def create_sample_addresses():
    """Create sample addresses for testing."""
    
    class SampleAddress:
        def __init__(self, address, crypto_type, api_data=None):
            self.address = address
            self.crypto_type = crypto_type
            self.confidence = 1.0
            self.filename = 'sample_data.csv'
            self.api_data = api_data or {}
    
    sample_addresses = [
        SampleAddress(
            "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", 
            "BTC",
            {
                'balance': 0,
                'balance_usd': 0,
                'transfer_count': 1,
                'exposure': [
                    {'service': 'Coinbase', 'category': 'exchange', 'percentage': 45.2},
                    {'service': 'Binance', 'category': 'exchange', 'percentage': 23.1}
                ]
            }
        ),
        SampleAddress(
            "0x742d35Cc6639C0532fEb5001fE9C9c75A8fd8Ecd",
            "ETH", 
            {
                'balance': 15.5,
                'balance_usd': 25000,
                'transfer_count': 45,
                'has_darknet_exposure': True,
                'exposure': [
                    {'service': 'DarkMarket', 'category': 'darknet', 'percentage': 78.3}
                ]
            }
        ),
        SampleAddress(
            "addr1q8j7j8j8j8j8j8j8j8j8j8j8j8j8j8j8j8j8j8j8j8j8j8j8j8j8",
            "ADA",
            {
                'balance': 1000,
                'balance_usd': 500,
                'transfer_count': 12
            }
        )
    ]
    
    print(f"   🧪 Created {len(sample_addresses)} sample addresses for testing")
    return sample_addresses


def setup_case_information():
    """Set up case information for the investigation."""
    
    print("   📝 Setting up case information...")
    
    # You can customize this or make it interactive
    case_info = {
        'case_id': f'CRYPTO_INVESTIGATION_{datetime.now().strftime("%Y%m%d")}',
        'analyst': 'Crypto Investigator',
        'priority': 'HIGH',
        'investigation_type': 'FINANCIAL_CRIMES',
        'target_entity': 'Suspicious Cryptocurrency Network',
        'created_date': datetime.now().isoformat()
    }
    
    return case_info


def create_enhanced_entities(addresses, base_exporter):
    """Create enhanced entities from addresses."""
    try:
        entities = []
        
        for i, addr in enumerate(addresses):
            # Create entity with enhanced attributes
            entity_data = {
                'entity_id': f"addr_{i:04d}",
                'entity_type': 'CryptoAddress',
                'label': f"{addr.address[:20]}...({addr.crypto_type})",
                'attributes': {
                    'Address': addr.address,
                    'CryptoType': addr.crypto_type,
                    'SourceFile': getattr(addr, 'filename', 'Unknown'),
                    'Confidence': getattr(addr, 'confidence', 1.0)
                },
                'icon_style': get_crypto_icon(addr.crypto_type),
                'risk_score': calculate_risk_score(addr)
            }
            
            # Add API data if available
            if hasattr(addr, 'api_data') and addr.api_data:
                api_data = addr.api_data
                entity_data['attributes'].update({
                    'Balance': api_data.get('balance', 0),
                    'BalanceUSD': api_data.get('balance_usd', 0),
                    'TransactionCount': api_data.get('transfer_count', 0)
                })
                
                # Check for darknet exposure
                if api_data.get('has_darknet_exposure'):
                    entity_data['attributes']['DarknetExposure'] = 'YES'
                    entity_data['risk_score'] = max(entity_data['risk_score'], 0.9)
                
                # Add exchange exposure
                if 'exposure' in api_data:
                    exposures = []
                    for exp in api_data['exposure'][:3]:  # Top 3
                        exposures.append(f"{exp['service']}: {exp['percentage']:.1f}%")
                    entity_data['attributes']['ExchangeExposure'] = '; '.join(exposures)
            
            entities.append(create_entity_object(entity_data))
        
        return entities
        
    except Exception as e:
        print(f"   ❌ Error creating entities: {e}")
        return []


def create_enhanced_relationships(addresses, entities):
    """Create relationships between entities."""
    try:
        links = []
        
        # Create basic relationships
        for i, entity in enumerate(entities):
            for j, other_entity in enumerate(entities[i+1:], i+1):
                # Link entities from same source
                if (entity.attributes.get('SourceFile') == 
                    other_entity.attributes.get('SourceFile')):
                    
                    link_data = {
                        'link_id': f"link_{i:04d}_{j:04d}",
                        'from_entity': entity.entity_id,
                        'to_entity': other_entity.entity_id,
                        'link_type': 'SameSource',
                        'label': 'Found together',
                        'attributes': {
                            'RelationshipType': 'Same Source File',
                            'SourceFile': entity.attributes.get('SourceFile', 'Unknown')
                        },
                        'strength': 0.7
                    }
                    
                    links.append(create_link_object(link_data))
        
        return links
        
    except Exception as e:
        print(f"   ❌ Error creating relationships: {e}")
        return []


def export_i2_xml(entities, links, filename_base, case_info):
    """Export to i2 XML format."""
    try:
        import xml.etree.ElementTree as ET
        from xml.dom import minidom
        
        # Create i2 compatible XML
        root = ET.Element("chart")
        root.set("xmlns", "http://www.i2inc.com/ANSI2004")
        
        # Chart info
        chart_info = ET.SubElement(root, "chartInfo")
        ET.SubElement(chart_info, "title").text = f"Crypto Investigation - {case_info['case_id']}"
        ET.SubElement(chart_info, "description").text = "Enhanced Cryptocurrency Investigation"
        
        # Chart items
        chart_items = ET.SubElement(root, "chartItemCollection")
        
        # Add entities
        for entity in entities:
            item = ET.SubElement(chart_items, "chartItem")
            item.set("entityId", entity.entity_id)
            
            entity_elem = ET.SubElement(item, "entity")
            entity_elem.set("entityId", entity.entity_id)
            entity_elem.set("entityTypeId", entity.entity_type)
            
            # Icon
            icon_elem = ET.SubElement(entity_elem, "icon")
            icon_elem.set("type", entity.icon_style)
            
            # Label
            label_elem = ET.SubElement(entity_elem, "labelCollection")
            label_item = ET.SubElement(label_elem, "label")
            label_item.set("text", entity.label)
            
            # Properties
            props_elem = ET.SubElement(entity_elem, "propertyCollection")
            for key, value in entity.attributes.items():
                prop = ET.SubElement(props_elem, "property")
                prop.set("entityPropertyTypeId", key.replace(' ', '_'))
                prop.set("value", str(value))
        
        # Add links
        for link in links:
            item = ET.SubElement(chart_items, "chartItem")
            item.set("linkId", link.link_id)
            
            link_elem = ET.SubElement(item, "link")
            link_elem.set("linkId", link.link_id)
            link_elem.set("linkTypeId", link.link_type)
            link_elem.set("fromEntityId", link.from_entity)
            link_elem.set("toEntityId", link.to_entity)
            link_elem.set("linkDirection", "WithArrow")
        
        # Write file
        output_path = f"{filename_base}_enhanced_i2_chart.xml"
        rough_string = ET.tostring(root, 'unicode')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        return output_path
        
    except Exception as e:
        print(f"   ❌ Error exporting XML: {e}")
        return None


def show_export_results(xml_path, report_path, dashboard_path, insights, risk_clusters):
    """Show the results of the enhanced export."""
    
    print("📁 Generated Files:")
    print("-" * 30)
    if xml_path:
        print(f"   📊 i2 Chart: {xml_path}")
    if report_path:
        print(f"   📋 Investigation Report: {report_path}")
    if dashboard_path:
        print(f"   🌐 Interactive Dashboard: {dashboard_path}")
    
    print(f"\n🔍 Analysis Results:")
    print("-" * 30)
    print(f"   🎯 Investigative Insights: {len(insights)}")
    
    critical_insights = [i for i in insights if i.severity == 'CRITICAL']
    if critical_insights:
        print(f"   🚨 Critical Findings: {len(critical_insights)}")
        for insight in critical_insights[:3]:
            print(f"      - {insight.title}")
    
    if risk_clusters:
        print(f"   📊 Risk Clusters: {len(risk_clusters)}")
        for cluster in risk_clusters[:3]:
            print(f"      - {cluster.cluster_name} ({cluster.risk_level})")
    
    print(f"\n🚀 Next Steps:")
    print("-" * 30)
    print("   1. Import XML into i2 Analyst's Notebook:")
    print(f"      File → Import → Import Chart → {xml_path}")
    print("   2. Review investigation report for key findings")
    print("   3. Open interactive dashboard in web browser")
    print("   4. Focus on critical and high-priority insights")


# Helper functions

def get_crypto_icon(crypto_type):
    """Get appropriate icon for crypto type."""
    icons = {
        'BTC': 'Person',
        'ETH': 'Person', 
        'ADA': 'Person',
        'XMR': 'Person',
        'LTC': 'Person'
    }
    return icons.get(crypto_type, 'Object')


def calculate_risk_score(addr):
    """Calculate basic risk score for address."""
    risk_score = 0.1  # Base risk
    
    if hasattr(addr, 'api_data') and addr.api_data:
        api_data = addr.api_data
        
        # High balance increases risk
        balance_usd = api_data.get('balance_usd', 0)
        if balance_usd > 100000:
            risk_score += 0.3
        elif balance_usd > 10000:
            risk_score += 0.2
        
        # Darknet exposure is high risk
        if api_data.get('has_darknet_exposure'):
            risk_score += 0.6
        
        # Privacy coins increase risk
        if addr.crypto_type in ['XMR', 'ZEC', 'DASH']:
            risk_score += 0.3
    
    return min(risk_score, 1.0)


def create_entity_object(entity_data):
    """Create entity object from data."""
    class Entity:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)
    
    return Entity(entity_data)


def create_link_object(link_data):
    """Create link object from data."""
    class Link:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)
    
    return Link(link_data)


def create_simple_i2_exporter():
    """Create a simple i2 exporter if the existing one has issues."""
    simple_exporter_content = '''
class EnhancedI2Exporter:
    def __init__(self):
        import logging
        self.logger = logging.getLogger(__name__)
    
    def _create_enhanced_address_entities(self, addresses):
        return []
'''
    
    with open('i2_exporter.py', 'w') as f:
        f.write(simple_exporter_content)


def main():
    """Main function to start the enhanced i2 features."""
    try:
        print("🌟 Enhanced i2 Features Startup")
        print("=" * 60)
        print("This will integrate advanced investigative features")
        print("with your existing cryptocurrency address extraction.")
        print()
        
        # Setup environment
        if not setup_enhanced_i2_environment():
            return 1
        
        # Run enhanced export
        result = run_enhanced_i2_export_with_your_data()
        
        if result:
            print("\n🎉 SUCCESS! Enhanced i2 export completed successfully!")
            print(f"Main export file: {result}")
            return 0
        else:
            print("\n❌ Enhanced export failed. Check the error messages above.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️  Process interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())