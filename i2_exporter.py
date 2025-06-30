"""
IBM i2 Analyst's Notebook Export Module
======================================

This module exports cryptocurrency investigation data in formats
compatible with i2 Analyst's Notebook for advanced graph analysis.
"""

import logging
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List, Dict, Any, Callable
from datetime import datetime
import csv
from dataclasses import dataclass

@dataclass
class i2Entity:
    """i2 Entity representation."""
    entity_id: str
    entity_type: str  # 'Person', 'CryptoAddress', 'Exchange', 'Transaction'
    label: str
    attributes: Dict[str, Any]
    icon_style: str = ""

@dataclass  
class i2Link:
    """i2 Link representation."""
    link_id: str
    from_entity: str
    to_entity: str
    link_type: str  # 'SendsTo', 'Controls', 'UsesService', 'ConnectedTo'
    label: str
    attributes: Dict[str, Any]
    strength: float = 1.0

class i2Exporter:
    """Export cryptocurrency investigation data to i2 Analyst's Notebook."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # i2 entity types for cryptocurrency investigations
        self.ENTITY_TYPES = {
            'crypto_address': 'CryptoAddress',
            'exchange': 'Exchange', 
            'mixer': 'Mixer',
            'wallet_service': 'WalletService',
            'entity': 'Entity',
            'transaction': 'Transaction',
            'cluster': 'Cluster'
        }
        
        # i2 link types for crypto tracing
        self.LINK_TYPES = {
            'sends_to': 'SendsTo',
            'receives_from': 'ReceivesFrom',
            'controls': 'Controls',
            'uses_service': 'UsesService',
            'belongs_to_cluster': 'BelongsTo',
            'connected_to': 'ConnectedTo',
            'suspicious_activity': 'SuspiciousActivity'
        }
    
    def export_investigation_data(self, addresses: List['ExtractedAddress'], 
                                 relationships: Dict = None,
                                 case_info: Dict = None,
                                 progress_callback: Callable = None) -> str:
        """
        Export complete investigation data to i2 format with progress tracking.
        
        Args:
            addresses: List of extracted cryptocurrency addresses
            relationships: Address relationships from API analysis
            case_info: Case metadata
            progress_callback: Function to call with progress updates (stage, detail)
            
        Returns:
            Path to exported i2 file
        """
        
        def update_progress(stage: str, detail: str = ""):
            """Update progress if callback provided."""
            if progress_callback:
                progress_callback(stage, detail)
            self.logger.debug(f"i2 Export Progress: {stage} - {detail}")
        
        self.logger.info(f"Exporting {len(addresses)} addresses to i2 format")
        
        entities = []
        links = []
        
        # Convert addresses to i2 entities
        update_progress('entities', f'Creating {len(addresses)} address entities')
        entities.extend(self._create_address_entities(addresses))
        
        # Create cluster entities for grouped addresses
        update_progress('clusters', 'Creating entity clusters from API data')
        cluster_entities, cluster_links = self._create_cluster_entities(addresses)
        entities.extend(cluster_entities)
        links.extend(cluster_links)
        self.logger.info(f"Created {len(cluster_entities)} cluster entities with {len(cluster_links)} cluster links")
        
        # Create exchange/service entities
        update_progress('services', 'Creating exchange and service entities')
        service_entities, service_links = self._create_service_entities(addresses)
        entities.extend(service_entities)
        links.extend(service_links)
        self.logger.info(f"Created {len(service_entities)} service entities with {len(service_links)} service links")
        
        # Add relationship links if available
        if relationships:
            update_progress('relationships', f'Processing {len(relationships)} relationship sets')
            relationship_links = self._create_relationship_links(relationships)
            links.extend(relationship_links)
            self.logger.info(f"Created {len(relationship_links)} relationship links")
        
        # Generate i2 files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        case_id = case_info.get('case_id', 'CRYPTO_CASE') if case_info else 'CRYPTO_CASE'
        filename_base = f"{case_id}_{timestamp}"
        
        # Export XML format
        update_progress('export_xml', f'Writing XML file with {len(entities)} entities and {len(links)} links')
        xml_path = self._export_i2_xml(entities, links, filename_base)
        
        # Export CSV format  
        update_progress('export_csv', 'Writing CSV files for alternative import')
        csv_path = self._export_i2_csv(entities, links, filename_base)
        
        self.logger.info(f"i2 export complete: {xml_path}, {csv_path}")
        self.logger.info(f"Export summary: {len(entities)} entities, {len(links)} links")
        
        return xml_path
    
    
    def _is_service_an_exchange(self, name, category):
        """
        Helper method to determine if a service is an exchange.
        
        Args:
            name (str): Service name
            category (str): Service category
            
        Returns:
            bool: True if the service is an exchange
        """
        if not name or not isinstance(name, str):
            return False
        
        name_lower = name.lower()
        category_lower = category.lower() if category else ''
        
        # Exchange categories
        exchange_categories = [
            'exchange', 'centralized exchange', 'cex', 'dex', 'decentralized exchange',
            'cryptocurrency exchange', 'crypto exchange', 'trading platform'
        ]
        
        for exc_cat in exchange_categories:
            if exc_cat in category_lower:
                return True
        
        # Known exchange names
        exchanges = [
            'binance', 'coinbase', 'kraken', 'bitfinex', 'huobi', 'okx', 'okex',
            'kucoin', 'gate.io', 'gate', 'bybit', 'bitstamp', 'gemini', 'bittrex',
            'poloniex', 'crypto.com', 'mexc', 'uniswap', 'pancakeswap', 'sushiswap'
        ]
        
        for exchange in exchanges:
            if exchange in name_lower:
                return True
        
        return False


    
    def _is_service_an_exchange(self, name, category):
        """
        Helper method to determine if a service is an exchange.
        
        Args:
            name (str): Service name
            category (str): Service category
            
        Returns:
            bool: True if the service is an exchange
        """
        if not name or not isinstance(name, str):
            return False
        
        name_lower = name.lower()
        category_lower = category.lower() if category else ''
        
        # Exchange categories
        exchange_categories = [
            'exchange', 'centralized exchange', 'cex', 'dex', 'decentralized exchange',
            'cryptocurrency exchange', 'crypto exchange', 'trading platform'
        ]
        
        for exc_cat in exchange_categories:
            if exc_cat in category_lower:
                return True
        
        # Known exchange names
        exchanges = [
            'binance', 'coinbase', 'kraken', 'bitfinex', 'huobi', 'okx', 'okex',
            'kucoin', 'gate.io', 'gate', 'bybit', 'bitstamp', 'gemini', 'bittrex',
            'poloniex', 'crypto.com', 'mexc', 'uniswap', 'pancakeswap', 'sushiswap'
        ]
        
        for exchange in exchanges:
            if exchange in name_lower:
                return True
        
        return False


    def _create_address_entities(self, addresses: List['ExtractedAddress']) -> List[i2Entity]:
        """
        Create i2 entities for cryptocurrency addresses with proper None handling.
        
        Args:
            addresses (List[ExtractedAddress]): List of cryptocurrency addresses
            
        Returns:
            List[i2Entity]: List of i2 entities
        """
        entities = []
        
        for addr in addresses:
            try:
                # Determine entity properties with None handling
                risk_level = getattr(addr, 'risk_level', None) or 'Unknown'
                cluster_name = getattr(addr, 'api_cluster_name', None) or 'Unknown'
                balance = getattr(addr, 'api_balance', None) or 0
                
                # Choose icon based on risk and type
                icon_style = self._get_address_icon_style(addr, risk_level)
                
                # Create comprehensive attributes for i2
                attributes = {
                    'Address': addr.address,
                    'CryptoType': addr.crypto_type,
                    'CryptoCurrency': addr.crypto_name,
                    'Confidence': f"{addr.confidence:.1f}%",
                    'RiskLevel': risk_level,
                    'Balance': f"{balance:,.8f}" if balance else "Unknown",
                    'ClusterName': cluster_name,
                    'SourceFile': addr.filename,
                    'SourceSheet': addr.sheet_name or "N/A",
                    'SourceLocation': f"Row {addr.row}, Col {addr.column}",
                    'ExtractedDate': datetime.now().strftime('%Y-%m-%d'),
                    'IsDuplicate': 'Yes' if addr.is_duplicate else 'No'
                }
                
                # Add API-derived attributes if available (with None checks)
                if hasattr(addr, 'api_total_received') and addr.api_total_received is not None:
                    attributes['TotalReceived'] = f"{addr.api_total_received:,.8f}"
                if hasattr(addr, 'api_total_sent') and addr.api_total_sent is not None:
                    attributes['TotalSent'] = f"{addr.api_total_sent:,.8f}"
                if hasattr(addr, 'api_transfer_count') and addr.api_transfer_count is not None:
                    attributes['TransactionCount'] = str(addr.api_transfer_count)
                if hasattr(addr, 'api_cluster_category') and addr.api_cluster_category:
                    attributes['ClusterCategory'] = addr.api_cluster_category
                
                # Enhanced exchange exposure detection
                has_exchange_exposure = False
                exposure_list = []
                
                # Check all possible exposure sources
                exposure_sources = [
                    ('api_exchange_exposure', 'legacy'),
                    ('api_direct_exposure', 'direct'),
                    ('api_indirect_exposure', 'indirect'),
                    ('api_sending_direct_exposure', 'sending_direct'),
                    ('api_sending_indirect_exposure', 'sending_indirect'),
                    ('api_receiving_direct_exposure', 'receiving_direct'),
                    ('api_receiving_indirect_exposure', 'receiving_indirect')
                ]
                
                for attr_name, source_type in exposure_sources:
                    if hasattr(addr, attr_name):
                        exposures = getattr(addr, attr_name)
                        if exposures:
                            for exp in exposures[:3]:  # Top 3 exposures per source
                                if exp and isinstance(exp, dict):
                                    name = exp.get('name', 'Unknown')
                                    value = exp.get('value', 0)
                                    percentage = exp.get('percentage', 0)
                                    category = exp.get('category', 'Unknown')
                                    
                                    # Enhanced exchange detection
                                    is_exchange = self._is_service_an_exchange(name, category)
                                    
                                    if is_exchange and (value > 0 or percentage > 0):
                                        has_exchange_exposure = True
                                        
                                        # Format the exposure entry
                                        if percentage > 0:
                                            exposure_entry = f"{name}: {percentage:.1f}%"
                                        elif value > 0:
                                            exposure_entry = f"{name}: ${value:,.2f}"
                                        else:
                                            exposure_entry = name
                                        
                                        # Add source type for debugging
                                        if source_type != 'legacy':
                                            exposure_entry += f" ({source_type})"
                                        
                                        exposure_list.append(exposure_entry)
                
                # Set the HasExchangeExposure attribute
                if has_exchange_exposure and exposure_list:
                    attributes['ExchangeExposure'] = "; ".join(exposure_list[:5])  # Top 5 total
                    attributes['HasExchangeExposure'] = 'Yes'
                else:
                    attributes['HasExchangeExposure'] = 'No'
                else:
                    attributes['HasExchangeExposure'] = 'No'
                
                # Create display label
                display_addr = addr.address[:20] + "..." if len(addr.address) > 25 else addr.address
                label = f"{addr.crypto_type}:{display_addr}"
                if cluster_name != 'Unknown':
                    label += f" ({cluster_name})"
                
                entity = i2Entity(
                    entity_id=f"addr_{addr.address}_{addr.crypto_type}",
                    entity_type=self.ENTITY_TYPES['crypto_address'],
                    label=label,
                    attributes=attributes,
                    icon_style=icon_style
                )
                
                entities.append(entity)
                
            except Exception as e:
                self.logger.error(f"Failed to create entity for address {addr.address}: {str(e)}")
                continue
        
        self.logger.info(f"Created {len(entities)} address entities")
        return entities




    def _create_cluster_entities(self, addresses: List['ExtractedAddress']) -> tuple[List[i2Entity], List[i2Link]]:
        """
        Create cluster entities and links to addresses.
        
        This method groups addresses by cluster and creates i2 entities for each cluster
        with proper error handling for None cluster names.
        
        Args:
            addresses (List[ExtractedAddress]): List of addresses with potential API data
            
        Returns:
            tuple[List[i2Entity], List[i2Link]]: Cluster entities and their links
            
        Raises:
            Exception: If entity creation fails
        """
        entities = []
        links = []
        
        try:
            # Group addresses by cluster with None handling
            clusters = {}
            for addr in addresses:
                # Handle None cluster names properly
                cluster_name = getattr(addr, 'api_cluster_name', None)
                
                # Convert None or empty string to 'Unknown'
                if not cluster_name:
                    cluster_name = 'Unknown'
                
                # Skip 'Unknown' clusters unless specifically requested
                if cluster_name != 'Unknown':
                    if cluster_name not in clusters:
                        clusters[cluster_name] = []
                    clusters[cluster_name].append(addr)
            
            self.logger.info(f"Found {len(clusters)} named clusters to process")
            
            # Create cluster entities
            for cluster_name, cluster_addresses in clusters.items():
                # Only create clusters with multiple addresses
                if len(cluster_addresses) > 1:
                    try:
                        # Calculate cluster statistics with None handling
                        total_balance = sum(getattr(addr, 'api_balance', 0) or 0 for addr in cluster_addresses)
                        crypto_types = list(set(addr.crypto_type for addr in cluster_addresses))
                        
                        # Get cluster category with None handling
                        cluster_category = None
                        for addr in cluster_addresses:
                            cat = getattr(addr, 'api_cluster_category', None)
                            if cat:
                                cluster_category = cat
                                break
                        
                        if not cluster_category:
                            cluster_category = 'Unknown'
                        
                        # Determine cluster risk
                        high_risk_count = sum(1 for addr in cluster_addresses 
                                            if getattr(addr, 'risk_level', 'LOW') in ['HIGH', 'CRITICAL'])
                        cluster_risk = 'HIGH' if high_risk_count > 0 else 'MEDIUM'
                        
                        # Build attributes dictionary
                        attributes = {
                            'ClusterName': cluster_name,
                            'Category': cluster_category,
                            'AddressCount': len(cluster_addresses),
                            'CryptoTypes': ", ".join(crypto_types),
                            'TotalBalance': f"{total_balance:,.8f}",
                            'RiskLevel': cluster_risk,
                            'HighRiskAddresses': high_risk_count
                        }
                        
                        # Create safe entity ID (handle special characters)
                        safe_cluster_id = cluster_name
                        for char in [' ', '/', '\\', ':', '*', '?', '"', '<', '>', '|', '.', ',']:
                            safe_cluster_id = safe_cluster_id.replace(char, '_')
                        
                        # Ensure entity ID is not too long
                        if len(safe_cluster_id) > 50:
                            safe_cluster_id = safe_cluster_id[:50]
                        
                        cluster_entity = i2Entity(
                            entity_id=f"cluster_{safe_cluster_id}",
                            entity_type=self.ENTITY_TYPES['cluster'],
                            label=f"Cluster: {cluster_name}",
                            attributes=attributes,
                            icon_style=self._get_cluster_icon_style(cluster_category, cluster_risk)
                        )
                        
                        entities.append(cluster_entity)
                        self.logger.debug(f"Created cluster entity: {cluster_name} with {len(cluster_addresses)} addresses")
                        
                        # Create links from cluster to addresses
                        for addr in cluster_addresses:
                            try:
                                # Create safe address ID
                                addr_id = f"{addr.address[:20]}_{addr.crypto_type}" if len(addr.address) > 20 else f"{addr.address}_{addr.crypto_type}"
                                
                                link = i2Link(
                                    link_id=f"cluster_link_{cluster_entity.entity_id}_{addr_id}",
                                    from_entity=cluster_entity.entity_id,
                                    to_entity=f"addr_{addr.address}_{addr.crypto_type}",
                                    link_type=self.LINK_TYPES['controls'],
                                    label=f"Controls {addr.crypto_type} Address",
                                    attributes={'RelationshipType': 'ClusterMembership'},
                                    strength=0.9
                                )
                                links.append(link)
                                
                            except Exception as e:
                                self.logger.warning(f"Failed to create cluster link for address {addr.address}: {str(e)}")
                                continue
                                
                    except Exception as e:
                        self.logger.error(f"Failed to create cluster entity for '{cluster_name}': {str(e)}")
                        continue
            
            self.logger.info(f"Created {len(entities)} cluster entities with {len(links)} links")
            return entities, links
            
        except Exception as e:
            self.logger.error(f"Error in _create_cluster_entities: {str(e)}", exc_info=True)
            # Return empty lists on error to allow export to continue
            return [], []
    
    def _create_service_entities(self, addresses: List['ExtractedAddress']) -> tuple[List[i2Entity], List[i2Link]]:
        """
        Create entities for exchanges and services.
        Updated to handle direct and indirect exposure separately.
        """
        entities = []
        links = []
        
        # Track services/exchanges mentioned
        services = {}
        
        for addr in addresses:
            # Handle both the old api_exchange_exposure and new separate attributes
            all_exposures = []
            
            # Check for new direct/indirect exposure attributes
            if hasattr(addr, 'api_direct_exposure') and addr.api_direct_exposure:
                for exposure in addr.api_direct_exposure:
                    if isinstance(exposure, dict):  # Ensure it's a dict
                        exposure_copy = exposure.copy()
                        exposure_copy['exposure_type'] = 'direct'
                        all_exposures.append(exposure_copy)
            
            if hasattr(addr, 'api_indirect_exposure') and addr.api_indirect_exposure:
                for exposure in addr.api_indirect_exposure:
                    if isinstance(exposure, dict):  # Ensure it's a dict
                        exposure_copy = exposure.copy()
                        exposure_copy['exposure_type'] = 'indirect'
                        all_exposures.append(exposure_copy)
            
            # Fall back to old api_exchange_exposure if new attributes don't exist
            if not all_exposures and hasattr(addr, 'api_exchange_exposure') and addr.api_exchange_exposure:
                for exposure in addr.api_exchange_exposure:
                    if isinstance(exposure, dict):  # Ensure it's a dict
                        all_exposures.append(exposure)
            
            # Process all exposures
            for exposure in all_exposures:
                try:
                    service_name = exposure.get('name', 'Unknown')
                    service_category = exposure.get('category', 'Unknown')
                    
                    if service_name not in services:
                        services[service_name] = {
                            'name': service_name,
                            'category': service_category,
                            'connected_addresses': [],
                            'total_exposure': 0.0,
                            'connection_count': 0,
                            'direct_count': 0,
                            'indirect_count': 0
                        }
                    
                    services[service_name]['connected_addresses'].append(addr)
                    services[service_name]['total_exposure'] += exposure.get('value', 0)
                    services[service_name]['connection_count'] += 1
                    
                    # Track direct vs indirect
                    if exposure.get('exposure_type') == 'direct':
                        services[service_name]['direct_count'] += 1
                    elif exposure.get('exposure_type') == 'indirect':
                        services[service_name]['indirect_count'] += 1
                        
                except Exception as e:
                    self.logger.warning(f"Error processing exposure for address {addr.address}: {str(e)}")
                    continue
        
        # Create service entities
        for service_name, service_data in services.items():
            try:
                # Determine service type
                category = service_data['category'].lower() if service_data['category'] else ''
                
                if 'exchange' in category:
                    entity_type = self.ENTITY_TYPES.get('exchange', 'Exchange')
                    icon_style = 'Exchange'
                elif 'mixer' in category or 'tumbler' in category:
                    entity_type = self.ENTITY_TYPES.get('mixer', 'Mixer')
                    icon_style = 'Mixer_HighRisk'
                else:
                    entity_type = self.ENTITY_TYPES.get('wallet_service', 'WalletService')
                    icon_style = 'WalletService'
                
                # Build description with direct/indirect counts
                description_parts = []
                if service_data['direct_count'] > 0:
                    description_parts.append(f"{service_data['direct_count']} direct")
                if service_data['indirect_count'] > 0:
                    description_parts.append(f"{service_data['indirect_count']} indirect")
                
                connection_desc = " & ".join(description_parts) if description_parts else "connections"
                
                attributes = {
                    'ServiceName': service_name,
                    'Category': service_data['category'],
                    'ConnectedAddresses': service_data['connection_count'],
                    'DirectConnections': service_data['direct_count'],
                    'IndirectConnections': service_data['indirect_count'],
                    'TotalExposure': f"{service_data['total_exposure']:.2f}",
                    'RiskLevel': 'HIGH' if 'mixer' in category else 'MEDIUM',
                    'ConnectionType': connection_desc
                }
                
                service_entity = i2Entity(
                    entity_id=f"service_{service_name.replace(' ', '_').replace('/', '_')}",
                    entity_type=entity_type,
                    label=f"{service_name} ({service_data['category']})",
                    attributes=attributes,
                    icon_style=icon_style
                )
                
                entities.append(service_entity)
                
                # Create links to connected addresses
                for addr in service_data['connected_addresses']:
                    # Find the exposure value for this specific address
                    exposure_value = 0.0
                    exposure_type = 'unknown'
                    
                    # Check direct exposures
                    if hasattr(addr, 'api_direct_exposure') and addr.api_direct_exposure:
                        for exp in addr.api_direct_exposure:
                            if isinstance(exp, dict) and exp.get('name') == service_name:
                                exposure_value = exp.get('value', 0)
                                exposure_type = 'direct'
                                break
                    
                    # Check indirect exposures if not found in direct
                    if exposure_type == 'unknown' and hasattr(addr, 'api_indirect_exposure') and addr.api_indirect_exposure:
                        for exp in addr.api_indirect_exposure:
                            if isinstance(exp, dict) and exp.get('name') == service_name:
                                exposure_value = exp.get('value', 0)
                                exposure_type = 'indirect'
                                break
                    
                    # Fall back to old api_exchange_exposure
                    if exposure_type == 'unknown' and hasattr(addr, 'api_exchange_exposure') and addr.api_exchange_exposure:
                        for exp in addr.api_exchange_exposure:
                            if isinstance(exp, dict) and exp.get('name') == service_name:
                                exposure_value = exp.get('value', 0)
                                exposure_type = 'legacy'
                                break
                    
                    link_label = f"Uses Service ({exposure_type}) - ${exposure_value:.2f}"
                    
                    link = i2Link(
                        link_id=f"service_link_{service_entity.entity_id}_{addr.address[:20]}",
                        from_entity=f"addr_{addr.address}_{addr.crypto_type}",
                        to_entity=service_entity.entity_id,
                        link_type=self.LINK_TYPES.get('uses_service', 'UsesService'),
                        label=link_label,
                        attributes={
                            'ExposureValue': exposure_value,
                            'ServiceType': service_data['category'],
                            'ExposureType': exposure_type
                        },
                        strength=min(1.0, exposure_value / 1000)  # Normalize strength
                    )
                    links.append(link)
                    
            except Exception as e:
                self.logger.error(f"Error creating service entity for '{service_name}': {str(e)}")
                continue
        
        self.logger.info(f"Created {len(entities)} service entities with {len(links)} links")
        return entities, links
    
    def _create_relationship_links(self, relationships: Dict) -> List[i2Link]:
        """Create relationship links from provided relationship data."""
        links = []
        
        for source_addr, connections in relationships.items():
            for connection in connections:
                target = connection.get('target', '')
                relationship_type = connection.get('type', 'connected_to')
                weight = connection.get('weight', 1.0)
                evidence = connection.get('evidence', '')
                
                link = i2Link(
                    link_id=f"rel_{source_addr[:10]}_{target[:10]}_{relationship_type}",
                    from_entity=f"addr_{source_addr}",
                    to_entity=f"addr_{target}" if not target.startswith('service_') else target,
                    link_type=self.LINK_TYPES.get(relationship_type, 'ConnectedTo'),
                    label=f"{relationship_type.replace('_', ' ').title()}",
                    attributes={
                        'RelationshipType': relationship_type,
                        'Evidence': evidence,
                        'Weight': weight
                    },
                    strength=weight
                )
                links.append(link)
        
        return links
    
    def _get_address_icon_style(self, addr: 'ExtractedAddress', risk_level: str) -> str:
        """Determine appropriate i2 icon style for address."""
        
        # Base icon on crypto type and risk
        crypto_icons = {
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum', 
            'XMR': 'Monero_Privacy',
            'ZEC': 'Zcash_Privacy',
            'DASH': 'Dash_Privacy',
            'USDT': 'Tether_Stablecoin',
            'USDC': 'USDC_Stablecoin'
        }
        
        base_icon = crypto_icons.get(addr.crypto_type, 'CryptoAddress')
        
        # Modify based on risk level
        if risk_level == 'CRITICAL':
            return f"{base_icon}_Critical"
        elif risk_level == 'HIGH':
            return f"{base_icon}_HighRisk"
        elif getattr(addr, 'api_has_exchange_exposure', False):
            return f"{base_icon}_ExchangeConnected"
        else:
            return base_icon
    
    def _get_cluster_icon_style(self, category: str, risk_level: str) -> str:
        """Determine icon style for cluster entities."""
        
        category_lower = category.lower()
        
        if 'exchange' in category_lower:
            return 'Exchange_Cluster'
        elif 'mixer' in category_lower or 'tumbler' in category_lower:
            return 'Mixer_Cluster_Critical'
        elif risk_level == 'HIGH':
            return 'Entity_HighRisk'
        else:
            return 'Entity_Cluster'
    
    def _export_i2_xml(self, entities: List[i2Entity], links: List[i2Link], filename: str) -> str:
        """Export data in i2 XML format."""
        
        # Create XML structure for i2
        root = ET.Element("i2:Investigation")
        root.set("xmlns:i2", "http://www.i2group.com/Investigation")
        root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        
        # Add case information
        case_info = ET.SubElement(root, "CaseInfo")
        ET.SubElement(case_info, "CaseTitle").text = f"Cryptocurrency Investigation - {filename}"
        ET.SubElement(case_info, "DateCreated").text = datetime.now().isoformat()
        ET.SubElement(case_info, "CreatedBy").text = "Crypto Address Extractor"
        
        # Add entities
        entities_elem = ET.SubElement(root, "Entities")
        for entity in entities:
            entity_elem = ET.SubElement(entities_elem, "Entity")
            entity_elem.set("EntityId", entity.entity_id)
            entity_elem.set("EntityType", entity.entity_type)
            
            ET.SubElement(entity_elem, "Label").text = entity.label
            if entity.icon_style:
                ET.SubElement(entity_elem, "IconStyle").text = entity.icon_style
            
            # Add attributes
            attrs_elem = ET.SubElement(entity_elem, "Attributes")
            for key, value in entity.attributes.items():
                attr_elem = ET.SubElement(attrs_elem, "Attribute")
                attr_elem.set("Name", key)
                attr_elem.text = str(value)
        
        # Add links
        links_elem = ET.SubElement(root, "Links")
        for link in links:
            link_elem = ET.SubElement(links_elem, "Link")
            link_elem.set("LinkId", link.link_id)
            link_elem.set("FromEntity", link.from_entity)
            link_elem.set("ToEntity", link.to_entity)
            link_elem.set("LinkType", link.link_type)
            
            ET.SubElement(link_elem, "Label").text = link.label
            ET.SubElement(link_elem, "Strength").text = str(link.strength)
            
            # Add attributes
            attrs_elem = ET.SubElement(link_elem, "Attributes")
            for key, value in link.attributes.items():
                attr_elem = ET.SubElement(attrs_elem, "Attribute")
                attr_elem.set("Name", key)
                attr_elem.text = str(value)
        
        # Write XML file
        output_path = f"{filename}_i2_investigation.xml"
        
        # Pretty print XML
        rough_string = ET.tostring(root, 'unicode')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        return output_path
    
    def _export_i2_csv(self, entities: List[i2Entity], links: List[i2Link], filename: str) -> str:
        """Export data in CSV format for i2 import."""
        
        # Export entities to CSV
        entities_csv = f"{filename}_entities.csv"
        
        if entities:
            # Get all unique attribute keys
            all_attrs = set()
            for entity in entities:
                all_attrs.update(entity.attributes.keys())
            
            fieldnames = ['EntityId', 'EntityType', 'Label', 'IconStyle'] + sorted(all_attrs)
            
            with open(entities_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for entity in entities:
                    row = {
                        'EntityId': entity.entity_id,
                        'EntityType': entity.entity_type,
                        'Label': entity.label,
                        'IconStyle': entity.icon_style
                    }
                    row.update(entity.attributes)
                    writer.writerow(row)
        
        # Export links to CSV
        links_csv = f"{filename}_links.csv"
        
        if links:
            all_link_attrs = set()
            for link in links:
                all_link_attrs.update(link.attributes.keys())
            
            link_fieldnames = ['LinkId', 'FromEntity', 'ToEntity', 'LinkType', 'Label', 'Strength'] + sorted(all_link_attrs)
            
            with open(links_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=link_fieldnames)
                writer.writeheader()
                
                for link in links:
                    row = {
                        'LinkId': link.link_id,
                        'FromEntity': link.from_entity,
                        'ToEntity': link.to_entity,
                        'LinkType': link.link_type,
                        'Label': link.label,
                        'Strength': link.strength
                    }
                    row.update(link.attributes)
                    writer.writerow(row)
        
        self.logger.info(f"CSV export complete: {entities_csv}, {links_csv}")
        return entities_csv