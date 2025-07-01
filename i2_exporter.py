"""
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
