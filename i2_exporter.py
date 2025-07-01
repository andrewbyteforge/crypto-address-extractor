"""
Enhanced i2 Exporter with Advanced Features
==========================================

File: i2_exporter.py (Enhanced Version)

This enhanced version adds:
1. Advanced relationship detection
2. Risk-based entity prioritization  
3. Timeline analysis
4. Geographic clustering
5. Transaction flow analysis
6. Comprehensive validation
7. Multiple export formats
8. Development and testing tools

Author: Crypto Extractor Tool
Date: 2025-01-09
Version: 2.0.0 - Enhanced with advanced analytics
"""

import logging
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List, Dict, Any, Callable, Tuple, Optional
from datetime import datetime, timedelta
import csv
import json
import hashlib
from dataclasses import dataclass
from collections import defaultdict, Counter
import re

@dataclass
class i2Entity:
    """Enhanced i2 Entity representation with additional metadata."""
    entity_id: str
    entity_type: str  # 'Person', 'CryptoAddress', 'Exchange', 'Transaction', 'Cluster'
    label: str
    attributes: Dict[str, Any]
    icon_style: str = ""
    risk_score: float = 0.0
    confidence: float = 1.0
    geo_location: Optional[str] = None
    last_activity: Optional[datetime] = None

@dataclass  
class i2Link:
    """Enhanced i2 Link representation with additional metadata."""
    link_id: str
    from_entity: str
    to_entity: str
    link_type: str  # 'SendsTo', 'Controls', 'UsesService', 'ConnectedTo'
    label: str
    attributes: Dict[str, Any]
    strength: float = 1.0
    confidence: float = 1.0
    direction: str = "directed"  # 'directed', 'undirected'
    weight: float = 1.0
    created_date: Optional[datetime] = None

class EnhancedI2Exporter:
    """Enhanced export for cryptocurrency investigation data to i2 Analyst's Notebook."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Enhanced case information
        case_elem = ET.SubElement(root, "CaseInfo")
        if case_info:
            ET.SubElement(case_elem, "CaseTitle").text = case_info.get('case_id', f"Cryptocurrency Investigation - {filename}")
            ET.SubElement(case_elem, "CaseId").text = case_info.get('case_id', f"CASE_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            ET.SubElement(case_elem, "Analyst").text = case_info.get('analyst', 'Unknown')
            ET.SubElement(case_elem, "Priority").text = case_info.get('priority', 'MEDIUM')
            ET.SubElement(case_elem, "InvestigationType").text = case_info.get('investigation_type', 'FINANCIAL_CRIMES')
            ET.SubElement(case_elem, "TargetEntity").text = case_info.get('target_entity', '')
        else:
            ET.SubElement(case_elem, "CaseTitle").text = f"Cryptocurrency Investigation - {filename}"
            ET.SubElement(case_elem, "CaseId").text = f"CASE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        ET.SubElement(case_elem, "DateCreated").text = datetime.now().isoformat()
        ET.SubElement(case_elem, "CreatedBy").text = "Enhanced Crypto Address Extractor v2.0"
        ET.SubElement(case_elem, "ExportVersion").text = "2.0"
        
        # Add investigation metadata
        metadata_elem = ET.SubElement(root, "InvestigationMetadata")
        ET.SubElement(metadata_elem, "TotalEntities").text = str(len(entities))
        ET.SubElement(metadata_elem, "TotalLinks").text = str(len(links))
        
        # Entity type distribution
        entity_types = Counter(entity.entity_type for entity in entities)
        entity_dist_elem = ET.SubElement(metadata_elem, "EntityDistribution")
        for entity_type, count in entity_types.items():
            type_elem = ET.SubElement(entity_dist_elem, "EntityType")
            type_elem.set("type", entity_type)
            type_elem.text = str(count)
        
        # Risk level distribution
        risk_levels = Counter(entity.attributes.get('RiskLevel', 'UNKNOWN') for entity in entities if hasattr(entity, 'attributes'))
        risk_dist_elem = ET.SubElement(metadata_elem, "RiskDistribution")
        for risk_level, count in risk_levels.items():
            risk_elem = ET.SubElement(risk_dist_elem, "RiskLevel")
            risk_elem.set("level", risk_level)
            risk_elem.text = str(count)
        
        # Enhanced entities section
        entities_elem = ET.SubElement(root, "Entities")
        for entity in entities:
            entity_elem = ET.SubElement(entities_elem, "Entity")
            entity_elem.set("EntityId", entity.entity_id)
            entity_elem.set("EntityType", entity.entity_type)
            
            if hasattr(entity, 'risk_score'):
                entity_elem.set("RiskScore", f"{entity.risk_score:.3f}")
            if hasattr(entity, 'confidence'):
                entity_elem.set("Confidence", f"{entity.confidence:.3f}")
            
            ET.SubElement(entity_elem, "Label").text = entity.label
            
            if entity.icon_style:
                ET.SubElement(entity_elem, "IconStyle").text = entity.icon_style
            
            if hasattr(entity, 'geo_location') and entity.geo_location:
                ET.SubElement(entity_elem, "GeoLocation").text = entity.geo_location
            
            if hasattr(entity, 'last_activity') and entity.last_activity:
                ET.SubElement(entity_elem, "LastActivity").text = entity.last_activity.isoformat()
            
            # Enhanced attributes
            attrs_elem = ET.SubElement(entity_elem, "Attributes")
            for key, value in entity.attributes.items():
                attr_elem = ET.SubElement(attrs_elem, "Attribute")
                attr_elem.set("Name", key)
                attr_elem.set("Type", self._get_attribute_type(value))
                attr_elem.text = str(value)
        
        # Enhanced links section
        links_elem = ET.SubElement(root, "Links")
        for link in links:
            link_elem = ET.SubElement(links_elem, "Link")
            link_elem.set("LinkId", link.link_id)
            link_elem.set("FromEntity", link.from_entity)
            link_elem.set("ToEntity", link.to_entity)
            link_elem.set("LinkType", link.link_type)
            
            if hasattr(link, 'confidence'):
                link_elem.set("Confidence", f"{link.confidence:.3f}")
            if hasattr(link, 'direction'):
                link_elem.set("Direction", link.direction)
            
            ET.SubElement(link_elem, "Label").text = link.label
            ET.SubElement(link_elem, "Strength").text = str(link.strength)
            
            if hasattr(link, 'weight'):
                ET.SubElement(link_elem, "Weight").text = str(link.weight)
            
            if hasattr(link, 'created_date') and link.created_date:
                ET.SubElement(link_elem, "CreatedDate").text = link.created_date.isoformat()
            
            # Enhanced link attributes
            attrs_elem = ET.SubElement(link_elem, "Attributes")
            for key, value in link.attributes.items():
                attr_elem = ET.SubElement(attrs_elem, "Attribute")
                attr_elem.set("Name", key)
                attr_elem.set("Type", self._get_attribute_type(value))
                attr_elem.text = str(value)
        
        # Write enhanced XML file
        output_path = f"{filename}_enhanced_i2_investigation.xml"
        
        # Pretty print XML with validation
        try:
            rough_string = ET.tostring(root, 'unicode')
            reparsed = minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="  ")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(pretty_xml)
            
            # Validate XML structure
            self._validate_xml_export(output_path)
            
            self.logger.info(f"Enhanced XML export complete: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error writing enhanced XML: {e}")
            raise
    
    def _export_i2_json(self, entities: List[i2Entity], links: List[i2Link], 
                       filename: str, case_info: Dict = None) -> str:
        """
        Export data in JSON format for web visualization and API integration.
        
        Args:
            entities: List of entities
            links: List of links
            filename: Base filename
            case_info: Case information
            
        Returns:
            str: Path to exported JSON file
            
        Raises:
            Exception: For export errors
        """
        try:
            # Prepare JSON structure
            export_data = {
                "investigation_info": {
                    "case_id": case_info.get('case_id', f"CASE_{datetime.now().strftime('%Y%m%d_%H%M%S')}") if case_info else f"CASE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "created_date": datetime.now().isoformat(),
                    "created_by": "Enhanced Crypto Address Extractor v2.0",
                    "export_version": "2.0",
                    "total_entities": len(entities),
                    "total_links": len(links)
                },
                "entities": [],
                "links": [],
                "statistics": {
                    "entity_types": {},
                    "link_types": {},
                    "risk_distribution": {},
                    "crypto_types": {}
                }
            }
            
            # Add case info if available
            if case_info:
                export_data["investigation_info"].update({
                    "analyst": case_info.get('analyst', 'Unknown'),
                    "priority": case_info.get('priority', 'MEDIUM'),
                    "investigation_type": case_info.get('investigation_type', 'FINANCIAL_CRIMES'),
                    "target_entity": case_info.get('target_entity', '')
                })
            
            # Convert entities to JSON
            for entity in entities:
                entity_data = {
                    "id": entity.entity_id,
                    "type": entity.entity_type,
                    "label": entity.label,
                    "icon_style": entity.icon_style,
                    "attributes": entity.attributes
                }
                
                # Add enhanced properties if available
                if hasattr(entity, 'risk_score'):
                    entity_data["risk_score"] = entity.risk_score
                if hasattr(entity, 'confidence'):
                    entity_data["confidence"] = entity.confidence
                if hasattr(entity, 'geo_location') and entity.geo_location:
                    entity_data["geo_location"] = entity.geo_location
                if hasattr(entity, 'last_activity') and entity.last_activity:
                    entity_data["last_activity"] = entity.last_activity.isoformat()
                
                export_data["entities"].append(entity_data)
                
                # Update statistics
                entity_type = entity.entity_type
                export_data["statistics"]["entity_types"][entity_type] = export_data["statistics"]["entity_types"].get(entity_type, 0) + 1
                
                # Risk distribution
                risk_level = entity.attributes.get('RiskLevel', 'UNKNOWN')
                export_data["statistics"]["risk_distribution"][risk_level] = export_data["statistics"]["risk_distribution"].get(risk_level, 0) + 1
                
                # Crypto types
                crypto_type = entity.attributes.get('CryptoType', '')
                if crypto_type:
                    export_data["statistics"]["crypto_types"][crypto_type] = export_data["statistics"]["crypto_types"].get(crypto_type, 0) + 1
            
            # Convert links to JSON
            for link in links:
                link_data = {
                    "id": link.link_id,
                    "from": link.from_entity,
                    "to": link.to_entity,
                    "type": link.link_type,
                    "label": link.label,
                    "strength": link.strength,
                    "attributes": link.attributes
                }
                
                # Add enhanced properties if available
                if hasattr(link, 'confidence'):
                    link_data["confidence"] = link.confidence
                if hasattr(link, 'direction'):
                    link_data["direction"] = link.direction
                if hasattr(link, 'weight'):
                    link_data["weight"] = link.weight
                if hasattr(link, 'created_date') and link.created_date:
                    link_data["created_date"] = link.created_date.isoformat()
                
                export_data["links"].append(link_data)
                
                # Update link type statistics
                link_type = link.link_type
                export_data["statistics"]["link_types"][link_type] = export_data["statistics"]["link_types"].get(link_type, 0) + 1
            
            # Write JSON file
            output_path = f"{filename}_i2_data.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"JSON export complete: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error writing JSON export: {e}")
            raise
    
    def _generate_investigation_summary(self, entities: List[i2Entity], links: List[i2Link], 
                                      filename: str, case_info: Dict = None) -> str:
        """
        Generate a comprehensive investigation summary report.
        
        Args:
            entities: List of entities
            links: List of links
            filename: Base filename
            case_info: Case information
            
        Returns:
            str: Path to summary report
            
        Raises:
            Exception: For report generation errors
        """
        try:
            summary_path = f"{filename}_investigation_summary.txt"
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("ENHANCED CRYPTOCURRENCY INVESTIGATION SUMMARY\n")
                f.write("=" * 80 + "\n\n")
                
                # Case information
                if case_info:
                    f.write("CASE INFORMATION:\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"Case ID: {case_info.get('case_id', 'Unknown')}\n")
                    f.write(f"Analyst: {case_info.get('analyst', 'Unknown')}\n")
                    f.write(f"Priority: {case_info.get('priority', 'Unknown')}\n")
                    f.write(f"Investigation Type: {case_info.get('investigation_type', 'Unknown')}\n")
                    f.write(f"Target Entity: {case_info.get('target_entity', 'Unknown')}\n")
                    f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Overall statistics
                f.write("OVERALL STATISTICS:\n")
                f.write("-" * 40 + "\n")
                f.write(f"Total Entities: {len(entities)}\n")
                f.write(f"Total Relationships: {len(links)}\n\n")
                
                # Entity analysis
                entity_types = Counter(entity.entity_type for entity in entities)
                f.write("ENTITY TYPE DISTRIBUTION:\n")
                f.write("-" * 40 + "\n")
                for entity_type, count in entity_types.most_common():
                    percentage = (count / len(entities)) * 100
                    f.write(f"{entity_type:<20}: {count:>5} ({percentage:>5.1f}%)\n")
                f.write("\n")
                
                # Risk analysis
                risk_levels = Counter(entity.attributes.get('RiskLevel', 'UNKNOWN') for entity in entities if hasattr(entity, 'attributes'))
                f.write("RISK LEVEL DISTRIBUTION:\n")
                f.write("-" * 40 + "\n")
                for risk_level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN']:
                    count = risk_levels.get(risk_level, 0)
                    percentage = (count / len(entities)) * 100 if len(entities) > 0 else 0
                    f.write(f"{risk_level:<10}: {count:>5} ({percentage:>5.1f}%)\n")
                f.write("\n")
                
                # High-risk entities
                high_risk_entities = [e for e in entities if hasattr(e, 'risk_score') and e.risk_score >= 0.7]
                if high_risk_entities:
                    f.write("HIGH-RISK ENTITIES (Risk Score >= 0.7):\n")
                    f.write("-" * 40 + "\n")
                    high_risk_entities.sort(key=lambda x: x.risk_score, reverse=True)
                    for entity in high_risk_entities[:10]:  # Top 10
                        f.write(f"{entity.label:<30}: {entity.risk_score:.3f} ({entity.attributes.get('RiskLevel', 'UNKNOWN')})\n")
                    f.write("\n")
                
                # Cryptocurrency distribution
                crypto_types = Counter()
                for entity in entities:
                    if entity.entity_type == 'CryptoAddress':
                        crypto_type = entity.attributes.get('CryptoType', 'Unknown')
                        crypto_types[crypto_type] += 1
                
                if crypto_types:
                    f.write("CRYPTOCURRENCY DISTRIBUTION:\n")
                    f.write("-" * 40 + "\n")
                    for crypto_type, count in crypto_types.most_common():
                        percentage = (count / sum(crypto_types.values())) * 100
                        f.write(f"{crypto_type:<10}: {count:>5} ({percentage:>5.1f}%)\n")
                    f.write("\n")
                
                # Link analysis
                link_types = Counter(link.link_type for link in links)
                f.write("RELATIONSHIP TYPE DISTRIBUTION:\n")
                f.write("-" * 40 + "\n")
                for link_type, count in link_types.most_common():
                    percentage = (count / len(links)) * 100 if len(links) > 0 else 0
                    f.write(f"{link_type:<25}: {count:>5} ({percentage:>5.1f}%)\n")
                f.write("\n")
                
                # Darknet exposure analysis
                darknet_entities = [e for e in entities if e.attributes.get('DarknetExposure') == 'YES']
                if darknet_entities:
                    f.write("DARKNET MARKET EXPOSURE:\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"Addresses with darknet exposure: {len(darknet_entities)}\n")
                    f.write("High-priority addresses for investigation:\n")
                    for entity in darknet_entities[:5]:  # Top 5
                        f.write(f"  - {entity.label}\n")
                    f.write("\n")
                
                # Investigation recommendations
                f.write("INVESTIGATION RECOMMENDATIONS:\n")
                f.write("-" * 40 + "\n")
                
                critical_count = risk_levels.get('CRITICAL', 0)
                high_count = risk_levels.get('HIGH', 0)
                
                if critical_count > 0:
                    f.write(f"🚨 URGENT: {critical_count} CRITICAL risk entities require immediate investigation\n")
                if high_count > 0:
                    f.write(f"⚠️  HIGH PRIORITY: {high_count} HIGH risk entities need detailed analysis\n")
                
                if darknet_entities:
                    f.write(f"🕵️  DARKNET: {len(darknet_entities)} addresses show darknet market exposure\n")
                
                # Top clusters by size
                clusters = defaultdict(list)
                for entity in entities:
                    if entity.entity_type == 'CryptoAddress':
                        cluster_name = entity.attributes.get('ClusterName', 'Unknown')
                        clusters[cluster_name].append(entity)
                
                large_clusters = [(name, addrs) for name, addrs in clusters.items() if len(addrs) > 1]
                if large_clusters:
                    f.write(f"🔗 CLUSTERS: {len(large_clusters)} multi-address clusters identified\n")
                
                f.write("\n")
                f.write("NEXT STEPS:\n")
                f.write("1. Focus on CRITICAL and HIGH risk entities first\n")
                f.write("2. Investigate darknet market connections\n")
                f.write("3. Analyze large clusters for entity consolidation\n")
                f.write("4. Cross-reference with external intelligence sources\n")
                f.write("5. Consider transaction flow analysis for high-risk addresses\n\n")
                
                f.write("=" * 80 + "\n")
                f.write("End of Investigation Summary\n")
                f.write("=" * 80 + "\n")
            
            self.logger.info(f"Investigation summary generated: {summary_path}")
            return summary_path
            
        except Exception as e:
            self.logger.error(f"Error generating investigation summary: {e}")
            raise
    
    def _get_attribute_type(self, value: Any) -> str:
        """Determine attribute type for XML export."""
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "decimal"
        elif isinstance(value, datetime):
            return "datetime"
        else:
            return "string"
    
    def _validate_xml_export(self, xml_path: str) -> bool:
        """
        Validate the exported XML for correctness.
        
        Args:
            xml_path: Path to XML file
            
        Returns:
            bool: True if valid
            
        Raises:
            Exception: If validation fails
        """
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Basic structure validation
            assert root.tag.endswith('Investigation'), "Root element must be Investigation"
            assert root.find('.//CaseInfo') is not None, "CaseInfo element required"
            assert root.find('.//Entities') is not None, "Entities element required"
            assert root.find('.//Links') is not None, "Links element required"
            
            # Entity validation
            entities = root.findall('.//Entities/Entity')
            entity_ids = set()
            for entity in entities:
                entity_id = entity.get('EntityId')
                assert entity_id, "Entity must have EntityId"
                assert entity_id not in entity_ids, f"Duplicate EntityId: {entity_id}"
                entity_ids.add(entity_id)
            
            # Link validation
            links = root.findall('.//Links/Link')
            for link in links:
                from_entity = link.get('FromEntity')
                to_entity = link.get('ToEntity')
                assert from_entity in entity_ids, f"Link references non-existent FromEntity: {from_entity}"
                assert to_entity in entity_ids, f"Link references non-existent ToEntity: {to_entity}"
            
            self.logger.info(f"XML validation passed: {len(entities)} entities, {len(links)} links")
            return True
            
        except Exception as e:
            self.logger.error(f"XML validation failed: {e}")
            raise
    
    def _extract_geographic_info(self, addr: 'ExtractedAddress') -> Optional[str]:
        """Extract geographic information from address attributes."""
        # This would be enhanced with actual geolocation data
        # For now, return None or implement basic logic
        return None
    
    def _get_enhanced_address_icon_style(self, addr: 'ExtractedAddress', risk_level: str) -> str:
        """Get enhanced icon style based on address properties and risk."""
        crypto_icons = {
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum',
            'XMR': 'Monero_Privacy',
            'ZEC': 'Zcash_Privacy', 
            'DASH': 'Dash_Privacy',
            'USDT': 'Tether_Stablecoin',
            'USDC': 'USDC_Stablecoin',
            'SOL': 'Solana'
        }
        
        base_icon = crypto_icons.get(addr.crypto_type, 'CryptoAddress')
        
        # Modify based on risk and properties
        if risk_level == 'CRITICAL':
            return f"{base_icon}_Critical"
        elif risk_level == 'HIGH':
            return f"{base_icon}_HighRisk"
        elif hasattr(addr, 'api_has_darknet_exposure') and addr.api_has_darknet_exposure:
            return f"{base_icon}_Darknet"
        elif hasattr(addr, 'api_cluster_category') and 'exchange' in addr.api_cluster_category.lower():
            return f"{base_icon}_Exchange"
        else:
            return base_icon

    # Create aliases for backward compatibility
    i2Exporter = EnhancedI2Exporterd entity types for comprehensive cryptocurrency investigations
            self.ENTITY_TYPES = {
                'crypto_address': 'CryptoAddress',
                'exchange': 'Exchange', 
                'mixer': 'Mixer',
                'tumbler': 'Tumbler',
                'wallet_service': 'WalletService',
                'entity': 'Entity',
                'transaction': 'Transaction',
                'cluster': 'Cluster',
                'darknet_market': 'DarknetMarket',
                'defi_protocol': 'DeFiProtocol',
                'bridge': 'CrossChainBridge',
                'gambling': 'GamblingService',
                'payment_processor': 'PaymentProcessor',
                'bank': 'TraditionalBank',
                'atm': 'CryptoATM',
                'jurisdiction': 'Jurisdiction'
            }
            
            # Enhanced link types for detailed relationship mapping
            self.LINK_TYPES = {
                'sends_to': 'SendsTo',
                'receives_from': 'ReceivesFrom',
                'controls': 'Controls',
                'uses_service': 'UsesService',
                'belongs_to_cluster': 'BelongsTo',
                'connected_to': 'ConnectedTo',
                'suspicious_activity': 'SuspiciousActivity',
                'high_frequency': 'HighFrequencyTransactions',
                'large_amount': 'LargeTransaction',
                'same_owner': 'SameOwner',
                'co_spent': 'CoSpentInputs',
                'temporal_proximity': 'TemporallyProximate',
                'geographic_proximity': 'GeographicallyProximate',
                'pattern_match': 'PatternMatch',
                'risk_propagation': 'RiskPropagation'
            }
            
            # Risk scoring thresholds
            self.RISK_THRESHOLDS = {
                'LOW': 0.3,
                'MEDIUM': 0.6,
                'HIGH': 0.8,
                'CRITICAL': 0.95
            }
    
    def export_investigation_data(self, addresses: List['ExtractedAddress'], 
                                 relationships: Dict = None,
                                 case_info: Dict = None,
                                 progress_callback: Callable = None,
                                 export_options: Dict = None) -> str:
        """
        Enhanced export with advanced analytics and multiple output formats.
        
        Args:
            addresses: List of extracted cryptocurrency addresses
            relationships: Address relationships from API analysis
            case_info: Case metadata
            progress_callback: Function to call with progress updates
            export_options: Additional export configuration
            
        Returns:
            Path to primary exported i2 file
            
        Raises:
            Exception: For export errors
        """
        
        def update_progress(stage: str, detail: str = ""):
            """Update progress if callback provided."""
            if progress_callback:
                progress_callback(stage, detail)
            self.logger.debug(f"Enhanced i2 Export Progress: {stage} - {detail}")
        
        # Set default export options
        if not export_options:
            export_options = {
                'include_timeline': True,
                'include_risk_analysis': True,
                'include_geographic_clustering': True,
                'include_transaction_flows': True,
                'export_formats': ['xml', 'csv', 'json'],
                'max_entities': 10000,
                'relationship_threshold': 0.1
            }
        
        self.logger.info(f"Enhanced export: {len(addresses)} addresses with advanced analytics")
        
        entities = []
        links = []
        
        # Step 1: Create address entities with enhanced attributes
        update_progress('entities', f'Creating {len(addresses)} enhanced address entities')
        address_entities = self._create_enhanced_address_entities(addresses)
        entities.extend(address_entities)
        
        # Step 2: Advanced cluster analysis
        update_progress('clusters', 'Performing advanced cluster analysis')
        cluster_entities, cluster_links = self._create_advanced_cluster_entities(addresses)
        entities.extend(cluster_entities)
        links.extend(cluster_links)
        
        # Step 3: Enhanced service and exchange entities
        update_progress('services', 'Creating enhanced service entities with risk analysis')
        service_entities, service_links = self._create_enhanced_service_entities(addresses)
        entities.extend(service_entities)
        links.extend(service_links)
        
        # Step 4: Advanced relationship detection
        update_progress('relationships', 'Detecting advanced relationships and patterns')
        if export_options.get('include_transaction_flows', True):
            advanced_links = self._detect_advanced_relationships(addresses, export_options)
            links.extend(advanced_links)
        
        # Step 5: Risk analysis and propagation
        if export_options.get('include_risk_analysis', True):
            update_progress('risk_analysis', 'Performing risk analysis and propagation')
            entities, links = self._perform_risk_analysis(entities, links)
        
        # Step 6: Timeline analysis
        if export_options.get('include_timeline', True):
            update_progress('timeline', 'Creating timeline entities')
            timeline_entities, timeline_links = self._create_timeline_entities(addresses)
            entities.extend(timeline_entities)
            links.extend(timeline_links)
        
        # Step 7: Geographic clustering
        if export_options.get('include_geographic_clustering', True):
            update_progress('geographic', 'Analyzing geographic clustering')
            geo_entities, geo_links = self._create_geographic_entities(addresses)
            entities.extend(geo_entities)
            links.extend(geo_links)
        
        # Step 8: Data validation and cleanup
        update_progress('validation', 'Validating and optimizing export data')
        entities, links = self._validate_and_optimize_data(entities, links, export_options)
        
        # Step 9: Generate multiple export formats
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        case_id = case_info.get('case_id', 'CRYPTO_CASE') if case_info else 'CRYPTO_CASE'
        filename_base = f"{case_id}_{timestamp}"
        
        export_paths = []
        
        # XML Export (primary)
        if 'xml' in export_options.get('export_formats', ['xml']):
            update_progress('export_xml', f'Writing enhanced XML with {len(entities)} entities, {len(links)} links')
            xml_path = self._export_enhanced_i2_xml(entities, links, filename_base, case_info)
            export_paths.append(xml_path)
        
        # CSV Export
        if 'csv' in export_options.get('export_formats', []):
            update_progress('export_csv', 'Writing enhanced CSV files')
            csv_path = self._export_enhanced_i2_csv(entities, links, filename_base)
            export_paths.append(csv_path)
        
        # JSON Export (for web visualization)
        if 'json' in export_options.get('export_formats', []):
            update_progress('export_json', 'Writing JSON for web visualization')
            json_path = self._export_i2_json(entities, links, filename_base, case_info)
            export_paths.append(json_path)
        
        # Generate summary report
        update_progress('summary', 'Generating investigation summary')
        summary_path = self._generate_investigation_summary(entities, links, filename_base, case_info)
        export_paths.append(summary_path)
        
        self.logger.info(f"Enhanced i2 export complete: {len(export_paths)} files generated")
        self.logger.info(f"Export summary: {len(entities)} entities, {len(links)} links")
        
        return export_paths[0] if export_paths else None
    
    def _create_enhanced_address_entities(self, addresses: List['ExtractedAddress']) -> List[i2Entity]:
        """
        Create enhanced address entities with comprehensive attributes and risk scoring.
        
        Args:
            addresses: List of extracted addresses
            
        Returns:
            List[i2Entity]: Enhanced address entities
            
        Raises:
            Exception: For entity creation errors
        """
        entities = []
        
        for addr in addresses:
            try:
                # Calculate risk score based on multiple factors
                risk_score = self._calculate_address_risk_score(addr)
                risk_level = self._get_risk_level(risk_score)
                
                # Determine last activity
                last_activity = None
                if hasattr(addr, 'api_last_transaction_date'):
                    try:
                        last_activity = datetime.fromisoformat(addr.api_last_transaction_date)
                    except:
                        pass
                
                # Enhanced attributes
                attributes = {
                    'Address': addr.address,
                    'CryptoType': addr.crypto_type,
                    'Confidence': getattr(addr, 'confidence', 1.0),
                    'RiskScore': risk_score,
                    'RiskLevel': risk_level,
                    'SourceFile': getattr(addr, 'filename', 'Unknown'),
                    'SourceSheet': getattr(addr, 'sheet_name', 'Unknown'),
                    'ExtractionRow': getattr(addr, 'row', 0),
                    'ExtractionColumn': getattr(addr, 'column', 0)
                }
                
                # Add API data if available
                if hasattr(addr, 'api_balance'):
                    attributes.update({
                        'Balance': getattr(addr, 'api_balance', 0),
                        'BalanceUSD': getattr(addr, 'api_balance_usd', 0),
                        'TotalReceived': getattr(addr, 'api_total_received', 0),
                        'TotalSent': getattr(addr, 'api_total_sent', 0),
                        'TransactionCount': getattr(addr, 'api_transfer_count', 0),
                        'ClusterName': getattr(addr, 'api_cluster_name', 'Unknown'),
                        'ClusterCategory': getattr(addr, 'api_cluster_category', 'Unknown'),
                        'ClusterRootAddress': getattr(addr, 'api_cluster_root_address', addr.address)
                    })
                
                # Add exchange exposure summary
                exposures = []
                for direction in ['sending', 'receiving']:
                    for exposure_type in ['direct', 'indirect']:
                        attr_name = f'api_{direction}_{exposure_type}_exposure'
                        if hasattr(addr, attr_name):
                            exposure_data = getattr(addr, attr_name, [])
                            for exp in exposure_data[:3]:  # Top 3 exposures
                                if exp and isinstance(exp, dict):
                                    exposures.append(f"{exp.get('name', 'Unknown')}: {exp.get('percentage', 0):.1f}%")
                
                if exposures:
                    attributes['ExchangeExposure'] = '; '.join(exposures)
                
                # Check for darknet exposure
                if hasattr(addr, 'api_has_darknet_exposure') and addr.api_has_darknet_exposure:
                    attributes['DarknetExposure'] = 'YES'
                    risk_score = max(risk_score, 0.9)  # Boost risk for darknet exposure
                
                # Geographic information (if available)
                geo_location = self._extract_geographic_info(addr)
                if geo_location:
                    attributes['GeographicLocation'] = geo_location
                
                # Create entity
                entity = i2Entity(
                    entity_id=f"addr_{addr.address}_{addr.crypto_type}",
                    entity_type='CryptoAddress',
                    label=f"{addr.address[:20]}...({addr.crypto_type})",
                    attributes=attributes,
                    icon_style=self._get_enhanced_address_icon_style(addr, risk_level),
                    risk_score=risk_score,
                    confidence=getattr(addr, 'confidence', 1.0),
                    geo_location=geo_location,
                    last_activity=last_activity
                )
                
                entities.append(entity)
                
            except Exception as e:
                self.logger.error(f"Error creating enhanced entity for address {addr.address}: {e}")
                continue
        
        self.logger.info(f"Created {len(entities)} enhanced address entities")
        return entities
    
    def _calculate_address_risk_score(self, addr: 'ExtractedAddress') -> float:
        """
        Calculate comprehensive risk score for an address based on multiple factors.
        
        Args:
            addr: ExtractedAddress object
            
        Returns:
            float: Risk score between 0.0 and 1.0
            
        Raises:
            None
        """
        risk_factors = []
        
        # Factor 1: Darknet exposure
        if hasattr(addr, 'api_has_darknet_exposure') and addr.api_has_darknet_exposure:
            risk_factors.append(0.9)
        
        # Factor 2: Large balance relative to average
        if hasattr(addr, 'api_balance_usd'):
            balance_usd = addr.api_balance_usd
            if balance_usd > 1000000:  # > $1M
                risk_factors.append(0.7)
            elif balance_usd > 100000:  # > $100K
                risk_factors.append(0.5)
        
        # Factor 3: High transaction frequency
        if hasattr(addr, 'api_transfer_count'):
            tx_count = addr.api_transfer_count
            if tx_count > 1000:
                risk_factors.append(0.6)
            elif tx_count > 100:
                risk_factors.append(0.4)
        
        # Factor 4: Privacy coin usage
        if addr.crypto_type in ['XMR', 'ZEC', 'DASH']:
            risk_factors.append(0.6)
        
        # Factor 5: Mixer/Tumbler exposure
        mixer_exposure = False
        for direction in ['sending', 'receiving']:
            for exposure_type in ['direct', 'indirect']:
                attr_name = f'api_{direction}_{exposure_type}_exposure'
                if hasattr(addr, attr_name):
                    exposures = getattr(addr, attr_name, [])
                    for exp in exposures:
                        if isinstance(exp, dict):
                            category = exp.get('category', '').lower()
                            name = exp.get('name', '').lower()
                            if 'mixer' in category or 'tumbler' in category:
                                mixer_exposure = True
                                break
        
        if mixer_exposure:
            risk_factors.append(0.8)
        
        # Factor 6: Cluster category risk
        if hasattr(addr, 'api_cluster_category'):
            category = addr.api_cluster_category.lower()
            if 'unknown' in category:
                risk_factors.append(0.5)
            elif 'suspicious' in category:
                risk_factors.append(0.7)
        
        # Calculate final risk score
        if not risk_factors:
            return 0.1  # Baseline risk
        
        # Use weighted average with diminishing returns
        risk_score = max(risk_factors)  # Start with highest risk
        for factor in risk_factors[1:]:
            risk_score = risk_score + (factor * (1 - risk_score) * 0.5)
        
        return min(risk_score, 1.0)
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to categorical risk level."""
        if risk_score >= self.RISK_THRESHOLDS['CRITICAL']:
            return 'CRITICAL'
        elif risk_score >= self.RISK_THRESHOLDS['HIGH']:
            return 'HIGH'
        elif risk_score >= self.RISK_THRESHOLDS['MEDIUM']:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _detect_advanced_relationships(self, addresses: List['ExtractedAddress'], 
                                    options: Dict) -> List[i2Link]:
        """
        Detect advanced relationships and patterns between addresses.
        
        Args:
            addresses: List of addresses
            options: Export options
            
        Returns:
            List[i2Link]: Detected relationship links
            
        Raises:
            None
        """
        links = []
        threshold = options.get('relationship_threshold', 0.1)
        
        try:
            # Group addresses by cluster
            clusters = defaultdict(list)
            for addr in addresses:
                cluster_root = getattr(addr, 'api_cluster_root_address', addr.address)
                clusters[cluster_root].append(addr)
            
            # Detect same-cluster relationships
            for cluster_root, cluster_addresses in clusters.items():
                if len(cluster_addresses) > 1:
                    # Create links between addresses in the same cluster
                    for i, addr1 in enumerate(cluster_addresses):
                        for addr2 in cluster_addresses[i+1:]:
                            link = i2Link(
                                link_id=f"cluster_rel_{addr1.address[:10]}_{addr2.address[:10]}",
                                from_entity=f"addr_{addr1.address}_{addr1.crypto_type}",
                                to_entity=f"addr_{addr2.address}_{addr2.crypto_type}",
                                link_type='BelongsTo',
                                label=f"Same Cluster: {getattr(addr1, 'api_cluster_name', 'Unknown')}",
                                attributes={
                                    'RelationshipType': 'same_cluster',
                                    'ClusterName': getattr(addr1, 'api_cluster_name', 'Unknown'),
                                    'ClusterRoot': cluster_root
                                },
                                strength=0.8,
                                confidence=0.9
                            )
                            links.append(link)
            
            # Detect exchange co-usage patterns
            exchange_usage = defaultdict(list)
            for addr in addresses:
                for direction in ['sending', 'receiving']:
                    for exposure_type in ['direct', 'indirect']:
                        attr_name = f'api_{direction}_{exposure_type}_exposure'
                        if hasattr(addr, attr_name):
                            exposures = getattr(addr, attr_name, [])
                            for exp in exposures:
                                if isinstance(exp, dict) and exp.get('percentage', 0) > threshold * 100:
                                    exchange_name = exp.get('name', 'Unknown')
                                    exchange_usage[exchange_name].append({
                                        'address': addr,
                                        'direction': direction,
                                        'exposure_type': exposure_type,
                                        'percentage': exp.get('percentage', 0)
                                    })
            
            # Create links for addresses using the same exchanges
            for exchange, usage_list in exchange_usage.items():
                if len(usage_list) > 1:
                    for i, usage1 in enumerate(usage_list):
                        for usage2 in usage_list[i+1:]:
                            addr1, addr2 = usage1['address'], usage2['address']
                            
                            # Calculate relationship strength based on usage patterns
                            strength = min(usage1['percentage'], usage2['percentage']) / 100.0
                            
                            if strength > threshold:
                                link = i2Link(
                                    link_id=f"exchange_couser_{addr1.address[:10]}_{addr2.address[:10]}_{exchange[:10]}",
                                    from_entity=f"addr_{addr1.address}_{addr1.crypto_type}",
                                    to_entity=f"addr_{addr2.address}_{addr2.crypto_type}",
                                    link_type='PatternMatch',
                                    label=f"Co-use {exchange}",
                                    attributes={
                                        'RelationshipType': 'exchange_co_usage',
                                        'ExchangeName': exchange,
                                        'Addr1Usage': f"{usage1['direction']} {usage1['exposure_type']} {usage1['percentage']:.1f}%",
                                        'Addr2Usage': f"{usage2['direction']} {usage2['exposure_type']} {usage2['percentage']:.1f}%"
                                    },
                                    strength=strength,
                                    confidence=0.7
                                )
                                links.append(link)
            
            self.logger.info(f"Detected {len(links)} advanced relationship links")
            
        except Exception as e:
            self.logger.error(f"Error detecting advanced relationships: {e}")
        
        return links
    
    def _create_timeline_entities(self, addresses: List['ExtractedAddress']) -> Tuple[List[i2Entity], List[i2Link]]:
        """
        Create timeline entities for temporal analysis.
        
        Args:
            addresses: List of addresses
            
        Returns:
            Tuple[List[i2Entity], List[i2Link]]: Timeline entities and links
            
        Raises:
            None
        """
        entities = []
        links = []
        
        try:
            # Group addresses by time periods (monthly)
            time_periods = defaultdict(list)
            
            for addr in addresses:
                if hasattr(addr, 'api_last_transaction_date'):
                    try:
                        last_tx = datetime.fromisoformat(addr.api_last_transaction_date)
                        period_key = last_tx.strftime('%Y-%m')
                        time_periods[period_key].append(addr)
                    except:
                        continue
            
            # Create timeline entities
            for period, period_addresses in time_periods.items():
                if len(period_addresses) > 1:  # Only create if multiple addresses
                    # Calculate aggregate statistics
                    total_balance = sum(getattr(addr, 'api_balance_usd', 0) for addr in period_addresses)
                    total_transactions = sum(getattr(addr, 'api_transfer_count', 0) for addr in period_addresses)
                    
                    entity = i2Entity(
                        entity_id=f"timeline_{period}",
                        entity_type='Timeline',
                        label=f"Activity Period: {period}",
                        attributes={
                            'TimePeriod': period,
                            'AddressCount': len(period_addresses),
                            'TotalBalance': total_balance,
                            'TotalTransactions': total_transactions,
                            'CryptoTypes': list(set(addr.crypto_type for addr in period_addresses))
                        },
                        icon_style='Timeline_Period'
                    )
                    entities.append(entity)
                    
                    # Create links from addresses to timeline
                    for addr in period_addresses:
                        link = i2Link(
                            link_id=f"timeline_link_{addr.address[:10]}_{period}",
                            from_entity=f"addr_{addr.address}_{addr.crypto_type}",
                            to_entity=f"timeline_{period}",
                            link_type='TemporallyProximate',
                            label=f"Active in {period}",
                            attributes={
                                'TimePeriod': period,
                                'ActivityType': 'transaction_activity'
                            },
                            strength=0.6
                        )
                        links.append(link)
            
            self.logger.info(f"Created {len(entities)} timeline entities with {len(links)} temporal links")
            
        except Exception as e:
            self.logger.error(f"Error creating timeline entities: {e}")
        
        return entities, links
    
    def _export_enhanced_i2_xml(self, entities: List[i2Entity], links: List[i2Link], 
                              filename: str, case_info: Dict = None) -> str:
        """
        Export enhanced i2 XML with additional metadata and validation.
        
        Args:
            entities: List of entities
            links: List of links
            filename: Base filename
            case_info: Case information
            
        Returns:
            str: Path to exported XML file
            
        Raises:
            Exception: For export errors
        """
        # Create enhanced XML structure
        root = ET.Element("i2:Investigation")
        root.set("xmlns:i2", "http://www.i2group.com/Investigation")
        root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.set("version", "2.0")
        
        # Enhance