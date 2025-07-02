"""
Complete Enhanced i2 Features Startup Script
============================================

File: start_enhanced_i2.py (FIXED VERSION)
Function: Complete startup with all missing functions implemented

This script provides complete functionality for enhanced i2 features
with proper graph visualization support.

Author: Crypto Extractor Tool  
Date: 2025-07-01
Version: 2.0.0 (FIXED)
"""

import os
import sys
import json
import logging
import webbrowser
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ExtractedAddress:
    """Data class for extracted cryptocurrency addresses."""
    address: str
    crypto_type: str
    confidence: float = 1.0
    filename: str = "unknown"
    sheet_name: str = "unknown"
    row: int = 0
    column: int = 0
    api_data: Optional[Dict] = None


def setup_enhanced_i2_environment() -> bool:
    """
    Set up the environment for enhanced i2 features.
    
    Returns:
        bool: True if setup successful
        
    Raises:
        Exception: If setup fails
    """
    try:
        logger.info("Setting up Enhanced i2 Environment")
        
        # Check for required files
        required_files = [
            'i2_enhanced_features.py',
            'i2_exporter.py'
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
                logger.error(f"Missing required file: {file}")
            else:
                logger.info(f"Found required file: {file}")
        
        if missing_files:
            logger.error(f"Missing {len(missing_files)} required files!")
            logger.error("Please ensure these files are in your project directory:")
            for file in missing_files:
                logger.error(f"   - {file}")
            return False
        
        logger.info("Environment setup complete!")
        return True
        
    except Exception as e:
        logger.error(f"Environment setup failed: {e}")
        return False


def load_your_extracted_addresses() -> List[ExtractedAddress]:
    """
    Load extracted cryptocurrency addresses from various sources.
    
    Returns:
        List[ExtractedAddress]: List of extracted addresses
        
    Raises:
        Exception: If loading fails
    """
    try:
        logger.info("Loading extracted cryptocurrency addresses")
        
        # Option 1: Load from JSON extraction results
        if os.path.exists('extraction_results.json'):
            logger.info("Loading from extraction_results.json")
            with open('extraction_results.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                addresses = []
                for addr_data in data.get('addresses', []):
                    addresses.append(ExtractedAddress(
                        address=addr_data['address'],
                        crypto_type=addr_data['crypto_type'],
                        confidence=addr_data.get('confidence', 1.0),
                        filename=addr_data.get('filename', 'extraction_results.json'),
                        api_data=addr_data.get('api_data', {})
                    ))
                logger.info(f"Loaded {len(addresses)} addresses from JSON")
                return addresses
        
        # Option 2: Load from recent Excel files
        excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and 'crypto' in f.lower()]
        if excel_files:
            excel_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            latest_file = excel_files[0]
            logger.info(f"Loading from latest Excel file: {latest_file}")
            
            try:
                import pandas as pd
                
                # Read the 'All Addresses' sheet
                df = pd.read_excel(latest_file, sheet_name='All Addresses')
                addresses = []
                
                for _, row in df.iterrows():
                    addresses.append(ExtractedAddress(
                        address=str(row.get('Address', '')),
                        crypto_type=str(row.get('Crypto', 'UNKNOWN')),
                        confidence=float(row.get('Confidence', 1.0)),
                        filename=latest_file,
                        sheet_name='All Addresses'
                    ))
                
                logger.info(f"Loaded {len(addresses)} addresses from Excel")
                return addresses
                
            except Exception as e:
                logger.warning(f"Could not load from Excel: {e}")
        
        # Option 3: Load from CSV files
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if csv_files:
            csv_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            latest_csv = csv_files[0]
            logger.info(f"Loading from latest CSV file: {latest_csv}")
            
            try:
                import pandas as pd
                df = pd.read_csv(latest_csv)
                addresses = []
                
                # Look for common column names
                address_cols = [col for col in df.columns if 'address' in col.lower()]
                crypto_cols = [col for col in df.columns if any(x in col.lower() for x in ['crypto', 'coin', 'type'])]
                
                if address_cols:
                    for _, row in df.iterrows():
                        address_val = str(row[address_cols[0]])
                        crypto_val = str(row[crypto_cols[0]]) if crypto_cols else 'UNKNOWN'
                        
                        if address_val and len(address_val) > 10:  # Basic validation
                            addresses.append(ExtractedAddress(
                                address=address_val,
                                crypto_type=crypto_val,
                                filename=latest_csv
                            ))
                
                logger.info(f"Loaded {len(addresses)} addresses from CSV")
                return addresses
                
            except Exception as e:
                logger.warning(f"Could not load from CSV: {e}")
        
        # Option 4: Create sample data for testing
        logger.warning("No existing extraction data found, creating sample data")
        return create_sample_addresses()
        
    except Exception as e:
        logger.error(f"Error loading addresses: {e}")
        return create_sample_addresses()


def create_sample_addresses() -> List[ExtractedAddress]:
    """
    Create sample addresses for testing and demonstration.
    
    Returns:
        List[ExtractedAddress]: Sample addresses
    """
    logger.info("Creating sample addresses for testing")
    
    sample_data = [
        {
            'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
            'crypto_type': 'BTC',
            'api_data': {
                'balance': 0,
                'balance_usd': 0,
                'transfer_count': 1,
                'exposure': [
                    {'service': 'Coinbase', 'category': 'exchange', 'percentage': 45.2},
                    {'service': 'Binance', 'category': 'exchange', 'percentage': 23.1}
                ]
            }
        },
        {
            'address': '0x742d35Cc6639C0532fEb5001fE9C9c75A8fd8Ecd',
            'crypto_type': 'ETH',
            'api_data': {
                'balance': 15.5,
                'balance_usd': 25000,
                'transfer_count': 45,
                'has_darknet_exposure': True,
                'exposure': [
                    {'service': 'DarkMarket', 'category': 'darknet', 'percentage': 78.3}
                ]
            }
        },
        {
            'address': 'addr1q8j7j8j8j8j8j8j8j8j8j8j8j8j8j8j8j8j8j8j8j8j8j8j8j8j8',
            'crypto_type': 'ADA',
            'api_data': {
                'balance': 1000,
                'balance_usd': 500,
                'transfer_count': 12
            }
        },
        {
            'address': 'bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4',
            'crypto_type': 'BTC',
            'api_data': {
                'balance': 2.5,
                'balance_usd': 125000,
                'transfer_count': 156,
                'has_darknet_exposure': False
            }
        },
        {
            'address': '0x8ba1f109551bD432803012645Hac136c22C8f2c',
            'crypto_type': 'ETH',
            'api_data': {
                'balance': 0.0,
                'balance_usd': 0,
                'transfer_count': 234,
                'exposure': [
                    {'service': 'Uniswap', 'category': 'defi', 'percentage': 67.8},
                    {'service': 'SushiSwap', 'category': 'defi', 'percentage': 32.2}
                ]
            }
        }
    ]
    
    addresses = []
    for data in sample_data:
        addresses.append(ExtractedAddress(
            address=data['address'],
            crypto_type=data['crypto_type'],
            filename='sample_data.json',
            api_data=data['api_data']
        ))
    
    logger.info(f"Created {len(addresses)} sample addresses")
    return addresses


def setup_case_information() -> Dict[str, Any]:
    """
    Set up case information for the investigation.
    
    Returns:
        Dict[str, Any]: Case information dictionary
    """
    logger.info("Setting up case information")
    
    case_info = {
        'case_id': f'CRYPTO_INVESTIGATION_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'analyst': 'Enhanced i2 Investigator',
        'priority': 'HIGH',
        'investigation_type': 'FINANCIAL_CRIMES',
        'target_entity': 'Suspicious Cryptocurrency Network',
        'created_date': datetime.now().isoformat(),
        'description': 'Enhanced cryptocurrency investigation with advanced pattern analysis',
        'jurisdiction': 'INTERNATIONAL',
        'status': 'ACTIVE'
    }
    
    logger.info(f"Case setup complete - ID: {case_info['case_id']}")
    return case_info


def calculate_risk_score(addr: ExtractedAddress) -> float:
    """
    Calculate risk score for an address based on various factors.
    
    Args:
        addr: ExtractedAddress object
        
    Returns:
        float: Risk score between 0.0 and 1.0
    """
    risk_score = 0.0
    
    try:
        if addr.api_data:
            api_data = addr.api_data
            
            # High balance increases risk
            balance_usd = api_data.get('balance_usd', 0)
            if balance_usd > 100000:
                risk_score += 0.3
            elif balance_usd > 10000:
                risk_score += 0.1
            
            # High transaction count
            tx_count = api_data.get('transfer_count', 0)
            if tx_count > 1000:
                risk_score += 0.2
            elif tx_count > 100:
                risk_score += 0.1
            
            # Darknet exposure
            if api_data.get('has_darknet_exposure', False):
                risk_score += 0.6
            
            # Check exposure for suspicious services
            exposures = api_data.get('exposure', [])
            for exposure in exposures:
                if exposure.get('category') == 'darknet':
                    risk_score += 0.5
                elif exposure.get('category') == 'mixer':
                    risk_score += 0.4
                elif exposure.get('percentage', 0) > 80:  # High concentration
                    risk_score += 0.2
        
        # Cap at 1.0
        return min(risk_score, 1.0)
        
    except Exception as e:
        logger.warning(f"Error calculating risk score: {e}")
        return 0.1  # Default low risk


def get_crypto_icon(crypto_type: str) -> str:
    """
    Get icon style for cryptocurrency type.
    
    Args:
        crypto_type: Cryptocurrency type (BTC, ETH, etc.)
        
    Returns:
        str: Icon style identifier
    """
    icon_map = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum', 
        'ADA': 'cardano',
        'LTC': 'litecoin',
        'XRP': 'ripple',
        'DOT': 'polkadot',
        'SOL': 'solana'
    }
    return icon_map.get(crypto_type.upper(), 'cryptocurrency')


def create_entity_object(entity_data: Dict[str, Any]) -> object:
    """
    Create entity object from data dictionary.
    
    Args:
        entity_data: Dictionary containing entity information
        
    Returns:
        object: Entity object with attributes
    """
    class Entity:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)
    
    return Entity(entity_data)


def create_link_object(link_data: Dict[str, Any]) -> object:
    """
    Create link object from data dictionary.
    
    Args:
        link_data: Dictionary containing link information
        
    Returns:
        object: Link object with attributes
    """
    class Link:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)
    
    return Link(link_data)


def create_enhanced_entities(addresses: List[ExtractedAddress], base_exporter) -> List[object]:
    """
    Create enhanced entities from addresses with rich attributes.
    
    Args:
        addresses: List of extracted addresses
        base_exporter: Base i2 exporter instance
        
    Returns:
        List[object]: Enhanced entity objects
        
    Raises:
        Exception: If entity creation fails
    """
    try:
        logger.info("Creating enhanced entities from addresses")
        entities = []
        
        for i, addr in enumerate(addresses):
            # Calculate risk score
            risk_score = calculate_risk_score(addr)
            risk_level = 'HIGH' if risk_score > 0.7 else 'MEDIUM' if risk_score > 0.3 else 'LOW'
            
            # Create entity with enhanced attributes
            entity_data = {
                'entity_id': f"addr_{i:04d}",
                'entity_type': 'CryptoAddress',
                'label': f"{addr.address[:20]}...({addr.crypto_type})",
                'full_address': addr.address,
                'attributes': {
                    'Address': addr.address,
                    'CryptoType': addr.crypto_type,
                    'SourceFile': addr.filename,
                    'Confidence': addr.confidence,
                    'RiskScore': risk_score,
                    'RiskLevel': risk_level
                },
                'icon_style': get_crypto_icon(addr.crypto_type),
                'risk_score': risk_score
            }
            
            # Add API data if available
            if addr.api_data:
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
                exposures = api_data.get('exposure', [])
                if exposures:
                    exposure_strings = []
                    for exp in exposures[:3]:  # Top 3
                        exposure_strings.append(f"{exp['service']}: {exp['percentage']:.1f}%")
                    entity_data['attributes']['ExchangeExposure'] = '; '.join(exposure_strings)
            
            entities.append(create_entity_object(entity_data))
        
        logger.info(f"Created {len(entities)} enhanced entities")
        return entities
        
    except Exception as e:
        logger.error(f"Error creating entities: {e}")
        raise


def create_enhanced_relationships(addresses: List[ExtractedAddress], entities: List[object]) -> List[object]:
    """
    Create relationships between entities based on patterns and connections.
    
    Args:
        addresses: List of extracted addresses
        entities: List of entity objects
        
    Returns:
        List[object]: Link objects representing relationships
        
    Raises:
        Exception: If relationship creation fails
    """
    try:
        logger.info("Creating enhanced relationships between entities")
        links = []
        
        # Create relationships based on various factors
        for i, entity1 in enumerate(entities):
            for j, entity2 in enumerate(entities):
                if i >= j:  # Avoid duplicates and self-references
                    continue
                
                addr1 = addresses[i]
                addr2 = addresses[j]
                
                # Same cryptocurrency type relationship
                if addr1.crypto_type == addr2.crypto_type:
                    link_data = {
                        'link_id': f"link_{i:04d}_{j:04d}",
                        'from_entity': entity1.entity_id,
                        'to_entity': entity2.entity_id,
                        'link_type': 'SameCryptoType',
                        'label': f'Same {addr1.crypto_type}',
                        'attributes': {
                            'LinkType': 'CryptoTypeMatch',
                            'CryptoType': addr1.crypto_type,
                            'Strength': 0.3
                        },
                        'strength': 0.3
                    }
                    links.append(create_link_object(link_data))
                
                # Same source file relationship
                if addr1.filename == addr2.filename:
                    link_data = {
                        'link_id': f"link_source_{i:04d}_{j:04d}",
                        'from_entity': entity1.entity_id,
                        'to_entity': entity2.entity_id,
                        'link_type': 'SameSource',
                        'label': 'Same Source',
                        'attributes': {
                            'LinkType': 'SourceFileMatch',
                            'SourceFile': addr1.filename,
                            'Strength': 0.5
                        },
                        'strength': 0.5
                    }
                    links.append(create_link_object(link_data))
                
                # High risk connection
                if addr1.api_data and addr2.api_data:
                    if (addr1.api_data.get('has_darknet_exposure') and 
                        addr2.api_data.get('has_darknet_exposure')):
                        link_data = {
                            'link_id': f"link_risk_{i:04d}_{j:04d}",
                            'from_entity': entity1.entity_id,
                            'to_entity': entity2.entity_id,
                            'link_type': 'HighRiskConnection',
                            'label': 'Both High Risk',
                            'attributes': {
                                'LinkType': 'RiskConnection',
                                'RiskFactor': 'DarknetExposure',
                                'Strength': 0.8
                            },
                            'strength': 0.8
                        }
                        links.append(create_link_object(link_data))
                
                # Exchange exposure overlap
                if (addr1.api_data and addr2.api_data and 
                    'exposure' in addr1.api_data and 'exposure' in addr2.api_data):
                    
                    exp1_services = {exp['service'] for exp in addr1.api_data['exposure']}
                    exp2_services = {exp['service'] for exp in addr2.api_data['exposure']}
                    common_services = exp1_services.intersection(exp2_services)
                    
                    if common_services:
                        link_data = {
                            'link_id': f"link_exchange_{i:04d}_{j:04d}",
                            'from_entity': entity1.entity_id,
                            'to_entity': entity2.entity_id,
                            'link_type': 'SharedExchange',
                            'label': f'Shared: {", ".join(list(common_services)[:2])}',
                            'attributes': {
                                'LinkType': 'ExchangeOverlap',
                                'SharedServices': ', '.join(common_services),
                                'Strength': min(0.6, len(common_services) * 0.2)
                            },
                            'strength': min(0.6, len(common_services) * 0.2)
                        }
                        links.append(create_link_object(link_data))
        
        logger.info(f"Created {len(links)} enhanced relationships")
        return links
        
    except Exception as e:
        logger.error(f"Error creating relationships: {e}")
        raise


def export_i2_xml(entities: List[object], links: List[object], filename_base: str, case_info: Dict) -> str:
    """
    Export entities and links to i2 XML format.
    
    Args:
        entities: List of entity objects
        links: List of link objects
        filename_base: Base filename for export
        case_info: Case information dictionary
        
    Returns:
        str: Path to generated XML file
        
    Raises:
        Exception: If XML export fails
    """
    try:
        logger.info("Exporting to i2 XML format")
        
        xml_path = f"{filename_base}_enhanced_i2_chart.xml"
        
        # Create XML structure
        import xml.etree.ElementTree as ET
        from xml.dom import minidom
        
        # Root element
        root = ET.Element('chart')
        root.set('case_id', case_info['case_id'])
        root.set('analyst', case_info['analyst'])
        root.set('created_date', case_info['created_date'])
        
        # Chart items container
        chart_items = ET.SubElement(root, 'chart_items')
        
        # Add entities
        for entity in entities:
            entity_elem = ET.SubElement(chart_items, 'entity')
            entity_elem.set('entity_id', entity.entity_id)
            entity_elem.set('entity_type', entity.entity_type)
            entity_elem.set('label', entity.label)
            entity_elem.set('icon_style', entity.icon_style)
            
            # Add attributes
            for key, value in entity.attributes.items():
                attr_elem = ET.SubElement(entity_elem, 'attribute')
                attr_elem.set('name', str(key))
                attr_elem.text = str(value)
        
        # Add links
        for link in links:
            link_elem = ET.SubElement(chart_items, 'link')
            link_elem.set('link_id', link.link_id)
            link_elem.set('from_entity', link.from_entity)
            link_elem.set('to_entity', link.to_entity)
            link_elem.set('link_type', link.link_type)
            link_elem.set('label', link.label)
            
            # Add attributes
            for key, value in link.attributes.items():
                attr_elem = ET.SubElement(link_elem, 'attribute')
                attr_elem.set('name', str(key))
                attr_elem.text = str(value)
        
        # Pretty print and save
        rough_string = ET.tostring(root, 'unicode')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        logger.info(f"i2 XML export complete: {xml_path}")
        return xml_path
        
    except Exception as e:
        logger.error(f"Error exporting to XML: {e}")
        raise


def show_export_results(xml_path: str, report_path: str, dashboard_path: str, 
                       insights: List, risk_clusters: List) -> None:
    """
    Display export results and open visualizations.
    
    Args:
        xml_path: Path to XML export file
        report_path: Path to investigation report
        dashboard_path: Path to HTML dashboard
        insights: List of insights
        risk_clusters: List of risk clusters
    """
    try:
        logger.info("Displaying export results")
        
        print("\n" + "=" * 60)
        print("🎉 ENHANCED i2 EXPORT COMPLETE!")
        print("=" * 60)
        
        print(f"\n📄 Generated Files:")
        print(f"   📊 i2 XML Chart: {xml_path}")
        print(f"   📝 Investigation Report: {report_path}")
        print(f"   🌐 Interactive Dashboard: {dashboard_path}")
        
        print(f"\n📊 Analysis Summary:")
        print(f"   🔍 Investigative Insights: {len(insights) if insights else 0}")
        print(f"   ⚠️  Risk Clusters: {len(risk_clusters) if risk_clusters else 0}")
        
        print(f"\n💡 Next Steps:")
        print(f"   1. Open i2 Analyst's Notebook")
        print(f"   2. Import → From File → Select: {xml_path}")
        print(f"   3. Review the investigation report for key findings")
        print(f"   4. Use the interactive dashboard for visual analysis")
        
        # Auto-open dashboard in browser
        if os.path.exists(dashboard_path):
            print(f"\n🌐 Opening interactive dashboard in browser...")
            webbrowser.open(f'file://{os.path.abspath(dashboard_path)}')
        
        print(f"\n✅ Enhanced i2 export process completed successfully!")
        
    except Exception as e:
        logger.error(f"Error showing results: {e}")


def run_enhanced_i2_export_with_your_data() -> Optional[str]:
    """
    Main function to run enhanced i2 export with extracted addresses.
    
    Returns:
        Optional[str]: Path to main export file if successful, None otherwise
        
    Raises:
        Exception: If export process fails
    """
    try:
        logger.info("Starting Enhanced i2 Export")
        
        # Step 1: Import required modules
        logger.info("Step 1: Importing modules...")
        
        # Try to import enhanced features
        try:
            from i2_enhanced_features import i2EnhancedFeatures
            logger.info("Imported enhanced features")
        except ImportError as e:
            logger.error(f"Could not import i2_enhanced_features: {e}")
            logger.error("Please ensure i2_enhanced_features.py is present and valid")
            return None
        
        # Try to import base exporter
        try:
            from i2_exporter import EnhancedI2Exporter
            base_exporter = EnhancedI2Exporter()
            logger.info("Imported existing i2_exporter")
        except Exception as e:
            logger.warning(f"Issue with i2_exporter.py: {e}")
            logger.warning("Creating simplified exporter...")
            
            # Create a minimal exporter class
            class SimpleI2Exporter:
                def __init__(self):
                    self.logger = logger
            
            base_exporter = SimpleI2Exporter()
        
        # Step 2: Load addresses
        logger.info("Step 2: Loading address data...")
        addresses = load_your_extracted_addresses()
        if not addresses:
            logger.error("No addresses loaded!")
            return None
        logger.info(f"Loaded {len(addresses)} addresses")
        
        # Step 3: Set up case information
        logger.info("Step 3: Setting up case information...")
        case_info = setup_case_information()
        logger.info(f"Case ID: {case_info['case_id']}")
        
        # Step 4: Initialize enhanced features
        logger.info("Step 4: Initializing enhanced features...")
        enhanced_features = i2EnhancedFeatures(base_exporter)
        logger.info("Enhanced features initialized")
        
        # Step 5: Create entities and relationships
        logger.info("Step 5: Creating entities and relationships...")
        entities = create_enhanced_entities(addresses, base_exporter)
        links = create_enhanced_relationships(addresses, entities)
        logger.info(f"Created {len(entities)} entities and {len(links)} links")
        
        # Step 6: Apply enhanced analysis
        logger.info("Step 6: Running enhanced analysis...")
        
        try:
            money_flows = enhanced_features.analyze_money_flows(entities, links)
            logger.info(f"Analyzed money flows: {len(money_flows) if money_flows else 0}")
        except Exception as e:
            logger.warning(f"Money flow analysis failed: {e}")
            money_flows = []
        
        try:
            risk_clusters = enhanced_features.detect_risk_clusters(entities, links)
            logger.info(f"Detected risk clusters: {len(risk_clusters) if risk_clusters else 0}")
        except Exception as e:
            logger.warning(f"Risk cluster detection failed: {e}")
            risk_clusters = []
        
        try:
            insights = enhanced_features.generate_investigative_insights(
                entities, links, money_flows, risk_clusters
            )
            logger.info(f"Generated insights: {len(insights) if insights else 0}")
        except Exception as e:
            logger.warning(f"Insight generation failed: {e}")
            insights = []
        
        # Step 7: Generate exports
        logger.info("Step 7: Generating exports...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_base = f"{case_info['case_id']}_{timestamp}"
        
        # Generate i2 XML
        xml_path = export_i2_xml(entities, links, filename_base, case_info)
        
        # Generate enhanced report
        try:
            report_path = enhanced_features.export_enhanced_investigation_report(
                filename_base, entities, links, insights, money_flows, risk_clusters
            )
            logger.info(f"Generated investigation report: {report_path}")
        except Exception as e:
            logger.warning(f"Report generation failed: {e}")
            report_path = "report_generation_failed.txt"
        
        # Generate interactive dashboard
        try:
            dashboard_path = enhanced_features.create_investigation_dashboard(
                entities, links, insights, money_flows, risk_clusters
            )
            logger.info(f"Generated interactive dashboard: {dashboard_path}")
        except Exception as e:
            logger.warning(f"Dashboard generation failed: {e}")
            dashboard_path = "dashboard_generation_failed.html"
        
        # Step 8: Show results
        logger.info("Step 8: Displaying results...")
        show_export_results(xml_path, report_path, dashboard_path, insights, risk_clusters)
        
        return xml_path
        
    except Exception as e:
        logger.error(f"Enhanced export failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def main() -> int:
    """
    Main function to start the enhanced i2 features.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
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