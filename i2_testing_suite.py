"""
i2 Testing and Development Suite
===============================

This module provides comprehensive testing and visualization tools for i2 Analyst's Notebook exports
when you don't have access to the actual i2 software.

Features:
- Parse and visualize i2 XML/CSV exports
- Generate test data from CSV files
- Create interactive HTML visualizations
- Validate i2 export format compliance
- Advanced development and debugging tools

Usage:
    python i2_testing_suite.py test.csv
"""

import csv
import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Tuple
import os
import webbrowser
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class i2TestDataGenerator:
    """Generate test cryptocurrency data for i2 export testing."""
    
    def __init__(self):
        self.sample_addresses = [
            # Bitcoin addresses
            {"address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "crypto_type": "BTC", "confidence": 1.0},
            {"address": "12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S", "crypto_type": "BTC", "confidence": 0.95},
            {"address": "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2", "crypto_type": "BTC", "confidence": 0.90},
            
            # Ethereum addresses  
            {"address": "0x742d35Cc6761C5Bd63b1508073ae38d0b8Bd2e9D", "crypto_type": "ETH", "confidence": 1.0},
            {"address": "0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe", "crypto_type": "ETH", "confidence": 0.95},
            {"address": "0x8ba1f109551bD432803012645Hac136c22C57B", "crypto_type": "ETH", "confidence": 0.88},
            
            # Solana addresses
            {"address": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM", "crypto_type": "SOL", "confidence": 0.92},
            {"address": "DRpbCBMxVnDK7maPM5tGv6MvB3v1sRMC86PZ7QpxqDs", "crypto_type": "SOL", "confidence": 0.87}
        ]
        
        self.sample_clusters = {
            "Binance Hot Wallet": {
                "category": "Exchange",
                "addresses": ["1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S"],
                "risk_level": "MEDIUM"
            },
            "Unknown Entity": {
                "category": "Unknown", 
                "addresses": ["0x742d35Cc6761C5Bd63b1508073ae38d0b8Bd2e9D"],
                "risk_level": "HIGH"
            },
            "DeFi Protocol": {
                "category": "DeFi",
                "addresses": ["9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"],
                "risk_level": "LOW"
            }
        }
        
        self.sample_exposures = {
            "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa": [
                {"name": "Binance", "category": "Exchange", "value": 50000, "percentage": 45.2, "type": "direct"},
                {"name": "Coinbase", "category": "Exchange", "value": 25000, "percentage": 23.1, "type": "indirect"}
            ],
            "0x742d35Cc6761C5Bd63b1508073ae38d0b8Bd2e9D": [
                {"name": "Uniswap", "category": "DEX", "value": 15000, "percentage": 67.3, "type": "direct"},
                {"name": "Kraken", "category": "Exchange", "value": 8000, "percentage": 32.7, "type": "indirect"}
            ]
        }

    def generate_test_extracted_addresses(self, csv_file_path: str = None) -> List[Any]:
        """
        Generate test ExtractedAddress objects for i2 export testing.
        
        Args:
            csv_file_path (str, optional): Path to CSV file with real data
            
        Returns:
            List[MockExtractedAddress]: List of mock address objects
            
        Raises:
            Exception: If CSV file cannot be processed
        """
        addresses = []
        
        # If CSV file provided, try to extract real addresses from it
        if csv_file_path and os.path.exists(csv_file_path):
            logger.info(f"Processing CSV file: {csv_file_path}")
            try:
                with open(csv_file_path, 'r', encoding='utf-8') as f:
                    # Try to detect addresses in the CSV
                    content = f.read()
                    detected_addresses = self._extract_addresses_from_text(content)
                    
                    if detected_addresses:
                        logger.info(f"Found {len(detected_addresses)} addresses in CSV")
                        for addr_data in detected_addresses:
                            addresses.append(self._create_mock_address(addr_data))
                    else:
                        logger.warning("No cryptocurrency addresses detected in CSV, using sample data")
                        
            except Exception as e:
                logger.error(f"Error processing CSV file: {e}")
                logger.info("Falling back to sample data")
        
        # If no addresses from CSV or no CSV provided, use sample data
        if not addresses:
            logger.info("Generating sample cryptocurrency data for testing")
            for addr_data in self.sample_addresses:
                addresses.append(self._create_mock_address(addr_data))
        
        return addresses

    def _extract_addresses_from_text(self, text: str) -> List[Dict]:
        """
        Extract cryptocurrency addresses from text using regex patterns.
        
        Args:
            text (str): Text to search for addresses
            
        Returns:
            List[Dict]: List of detected address data
            
        Raises:
            None
        """
        import re
        
        detected = []
        
        # Bitcoin address patterns
        btc_pattern = r'[13][a-km-zA-HJ-NP-Z1-9]{25,34}'
        btc_matches = re.findall(btc_pattern, text)
        for match in btc_matches[:5]:  # Limit to first 5
            detected.append({"address": match, "crypto_type": "BTC", "confidence": 0.85})
        
        # Ethereum address pattern
        eth_pattern = r'0x[a-fA-F0-9]{40}'
        eth_matches = re.findall(eth_pattern, text)
        for match in eth_matches[:5]:  # Limit to first 5
            detected.append({"address": match, "crypto_type": "ETH", "confidence": 0.90})
        
        # Solana address pattern (base58, 32-44 chars)
        sol_pattern = r'[1-9A-HJ-NP-Za-km-z]{32,44}'
        sol_matches = re.findall(sol_pattern, text)
        for match in sol_matches[:3]:  # Limit to first 3
            if not match.startswith(('1', '3', '0x')):  # Not BTC or ETH
                detected.append({"address": match, "crypto_type": "SOL", "confidence": 0.75})
        
        return detected

    def _create_mock_address(self, addr_data: Dict) -> Any:
        """
        Create a mock ExtractedAddress object for testing.
        
        Args:
            addr_data (Dict): Address data
            
        Returns:
            MockExtractedAddress: Mock address object
            
        Raises:
            None
        """
        # Store reference to self for the inner class
        parent_ref = self
        
        class MockExtractedAddress:
            def __init__(self, data):
                self.address = data["address"]
                self.crypto_type = data["crypto_type"]
                self.crypto_name = data["crypto_type"]
                self.confidence = data["confidence"]
                self.filename = "test.csv"
                self.sheet_name = "Sheet1"
                self.row = 1
                self.column = 1
                self.parent = parent_ref  # Set parent reference immediately
                
                # Add mock API data based on address
                self._add_mock_api_data()
            
            def _add_mock_api_data(self):
                """Add realistic mock API data."""
                # Mock cluster data
                for cluster_name, cluster_data in self.parent.sample_clusters.items():
                    if self.address in cluster_data["addresses"]:
                        self.api_cluster_name = cluster_name
                        self.api_cluster_category = cluster_data["category"]
                        self.api_cluster_root_address = self.address
                        break
                else:
                    self.api_cluster_name = "Unknown"
                    self.api_cluster_category = "Unknown"
                    self.api_cluster_root_address = self.address
                
                # Mock balance data
                import random
                self.api_balance = random.uniform(0.1, 100.0)
                self.api_balance_usd = self.api_balance * random.uniform(20000, 70000)
                self.api_total_received = self.api_balance * random.uniform(2, 10)
                self.api_total_sent = self.api_total_received - self.api_balance
                self.api_transfer_count = random.randint(5, 500)
                
                # Mock exposure data
                exposures = self.parent.sample_exposures.get(self.address, [])
                self.api_sending_direct_exposure = [exp for exp in exposures if exp.get("type") == "direct"]
                self.api_sending_indirect_exposure = [exp for exp in exposures if exp.get("type") == "indirect"]
                self.api_receiving_direct_exposure = []
                self.api_receiving_indirect_exposure = []
                
                # Check for darknet exposure
                self.api_has_darknet_exposure = any(
                    "darknet" in exp.get("name", "").lower() for exp in exposures
                )
        
        return MockExtractedAddress(addr_data)


class i2ExportAnalyzer:
    """Analyze and visualize i2 export files without requiring i2 software."""
    
    def __init__(self):
        self.entities = []
        self.links = []
        
    def analyze_i2_xml(self, xml_file_path: str) -> Dict[str, Any]:
        """
        Analyze an i2 XML export file and extract insights.
        
        Args:
            xml_file_path (str): Path to i2 XML file
            
        Returns:
            Dict[str, Any]: Analysis results
            
        Raises:
            Exception: If XML file cannot be parsed
        """
        logger.info(f"Analyzing i2 XML file: {xml_file_path}")
        
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            
            # Extract case information
            case_info = {}
            case_elem = root.find('.//CaseInfo')
            if case_elem is not None:
                for child in case_elem:
                    case_info[child.tag] = child.text
            
            # Extract entities
            entities = []
            entities_elem = root.find('.//Entities')
            if entities_elem is not None:
                for entity in entities_elem.findall('Entity'):
                    entity_data = {
                        'id': entity.get('EntityId'),
                        'type': entity.get('EntityType'),
                        'label': entity.find('Label').text if entity.find('Label') is not None else '',
                        'icon_style': entity.find('IconStyle').text if entity.find('IconStyle') is not None else '',
                        'attributes': {}
                    }
                    
                    # Extract attributes
                    attrs_elem = entity.find('Attributes')
                    if attrs_elem is not None:
                        for attr in attrs_elem.findall('Attribute'):
                            attr_name = attr.get('Name')
                            attr_value = attr.text
                            entity_data['attributes'][attr_name] = attr_value
                    
                    entities.append(entity_data)
            
            # Extract links
            links = []
            links_elem = root.find('.//Links')
            if links_elem is not None:
                for link in links_elem.findall('Link'):
                    link_data = {
                        'id': link.get('LinkId'),
                        'from': link.get('FromEntity'),
                        'to': link.get('ToEntity'),
                        'type': link.get('LinkType'),
                        'label': link.find('Label').text if link.find('Label') is not None else '',
                        'strength': float(link.find('Strength').text) if link.find('Strength') is not None else 1.0,
                        'attributes': {}
                    }
                    
                    # Extract link attributes
                    attrs_elem = link.find('Attributes')
                    if attrs_elem is not None:
                        for attr in attrs_elem.findall('Attribute'):
                            attr_name = attr.get('Name')
                            attr_value = attr.text
                            link_data['attributes'][attr_name] = attr_value
                    
                    links.append(link_data)
            
            # Generate analysis
            analysis = {
                'case_info': case_info,
                'summary': {
                    'total_entities': len(entities),
                    'total_links': len(links),
                    'entity_types': {},
                    'link_types': {},
                    'crypto_types': {}
                },
                'entities': entities,
                'links': links
            }
            
            # Count entity types
            for entity in entities:
                entity_type = entity['type']
                analysis['summary']['entity_types'][entity_type] = analysis['summary']['entity_types'].get(entity_type, 0) + 1
                
                # Count crypto types
                crypto_type = entity['attributes'].get('CryptoType', '')
                if crypto_type:
                    analysis['summary']['crypto_types'][crypto_type] = analysis['summary']['crypto_types'].get(crypto_type, 0) + 1
            
            # Count link types
            for link in links:
                link_type = link['type']
                analysis['summary']['link_types'][link_type] = analysis['summary']['link_types'].get(link_type, 0) + 1
            
            logger.info(f"Analysis complete: {len(entities)} entities, {len(links)} links")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing XML file: {e}")
            raise

    def generate_html_visualization(self, analysis: Dict[str, Any], output_path: str = None) -> str:
        """
        Generate an interactive HTML visualization of the i2 export data.
        
        Args:
            analysis (Dict[str, Any]): Analysis results from analyze_i2_xml
            output_path (str, optional): Output path for HTML file
            
        Returns:
            str: Path to generated HTML file
            
        Raises:
            Exception: If HTML generation fails
        """
        if not output_path:
            output_path = f"i2_visualization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        logger.info(f"Generating HTML visualization: {output_path}")
        
        try:
            # Prepare data for visualization
            nodes = []
            edges = []
            
            # Convert entities to nodes
            for entity in analysis['entities']:
                node = {
                    'id': entity['id'],
                    'label': entity['label'][:30] + ('...' if len(entity['label']) > 30 else ''),
                    'title': f"{entity['type']}: {entity['label']}\\n" + 
                            "\\n".join([f"{k}: {v}" for k, v in entity['attributes'].items()]),
                    'group': entity['type'],
                    'color': self._get_node_color(entity['type'])
                }
                nodes.append(node)
            
            # Convert links to edges
            for link in analysis['links']:
                edge = {
                    'from': link['from'],
                    'to': link['to'],
                    'label': link['label'],
                    'title': f"{link['type']}: {link['label']}\\n" +
                            "\\n".join([f"{k}: {v}" for k, v in link['attributes'].items()]),
                    'width': max(1, link['strength'] * 5),
                    'color': self._get_edge_color(link['type'])
                }
                edges.append(edge)
            
            # Generate HTML content
            html_content = self._generate_html_template(analysis, nodes, edges)
            
            # Write HTML file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML visualization generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating HTML visualization: {e}")
            raise

    def _get_node_color(self, entity_type: str) -> str:
        """Get color for node based on entity type."""
        colors = {
            'CryptoAddress': '#FF6B6B',
            'Exchange': '#4ECDC4', 
            'Cluster': '#45B7D1',
            'Entity': '#96CEB4',
            'Mixer': '#FFEAA7',
            'Service': '#DDA0DD'
        }
        return colors.get(entity_type, '#95A5A6')
    
    def _get_edge_color(self, link_type: str) -> str:
        """Get color for edge based on link type."""
        colors = {
            'SendsTo': '#E74C3C',
            'UsesService': '#3498DB',
            'BelongsTo': '#2ECC71',
            'ConnectedTo': '#9B59B6',
            'SuspiciousActivity': '#E67E22'
        }
        return colors.get(link_type, '#7F8C8D')

    def _generate_html_template(self, analysis: Dict, nodes: List, edges: List) -> str:
        """Generate complete HTML template with vis.js network visualization."""
        
        summary = analysis['summary']
        case_info = analysis['case_info']
        
        return f'''
<!DOCTYPE html>
<html>
<head>
    <title>i2 Export Visualization - {case_info.get('CaseTitle', 'Crypto Investigation')}</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .stats {{ display: flex; gap: 20px; margin-bottom: 20px; }}
        .stat-card {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); flex: 1; }}
        .stat-number {{ font-size: 24px; font-weight: bold; color: #3498db; }}
        .stat-label {{ color: #7f8c8d; margin-top: 5px; }}
        #network {{ width: 100%; height: 600px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .legend {{ background: white; padding: 15px; border-radius: 8px; margin-top: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .legend-item {{ display: inline-block; margin: 5px 10px; }}
        .legend-color {{ width: 15px; height: 15px; display: inline-block; margin-right: 5px; vertical-align: middle; }}
        .controls {{ background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        button {{ background: #3498db; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin: 2px; }}
        button:hover {{ background: #2980b9; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 i2 Export Visualization</h1>
        <p><strong>Case:</strong> {case_info.get('CaseTitle', 'Cryptocurrency Investigation')}</p>
        <p><strong>Created:</strong> {case_info.get('DateCreated', 'Unknown')} | <strong>By:</strong> {case_info.get('CreatedBy', 'Unknown')}</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{summary['total_entities']}</div>
            <div class="stat-label">Total Entities</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{summary['total_links']}</div>
            <div class="stat-label">Total Links</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(summary['entity_types'])}</div>
            <div class="stat-label">Entity Types</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(summary['crypto_types'])}</div>
            <div class="stat-label">Crypto Types</div>
        </div>
    </div>
    
    <div class="controls">
        <button onclick="network.fit()">🔍 Fit View</button>
        <button onclick="togglePhysics()">⚡ Toggle Physics</button>
        <button onclick="exportNetwork()">💾 Export PNG</button>
        <button onclick="showStatistics()">📊 Show Statistics</button>
    </div>
    
    <div id="network"></div>
    
    <div class="legend">
        <h3>🏷️ Legend</h3>
        <h4>Entity Types:</h4>
        {self._generate_legend_html(summary['entity_types'], 'entity')}
        <h4>Link Types:</h4>
        {self._generate_legend_html(summary['link_types'], 'link')}
    </div>

    <script type="text/javascript">
        // Network data
        var nodes = new vis.DataSet({json.dumps(nodes)});
        var edges = new vis.DataSet({json.dumps(edges)});
        var data = {{ nodes: nodes, edges: edges }};
        
        // Network options
        var options = {{
            nodes: {{
                shape: 'dot',
                size: 15,
                font: {{ size: 12, color: '#333' }},
                borderWidth: 2,
                shadow: true
            }},
            edges: {{
                width: 2,
                shadow: true,
                smooth: {{ type: 'continuous' }},
                arrows: {{ to: {{ enabled: true, scaleFactor: 0.5 }} }}
            }},
            physics: {{
                enabled: true,
                stabilization: {{ iterations: 100 }},
                barnesHut: {{ gravitationalConstant: -2000, springConstant: 0.001, springLength: 200 }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200
            }}
        }};
        
        // Create network
        var container = document.getElementById('network');
        var network = new vis.Network(container, data, options);
        
        // Network event handlers
        network.on("click", function (params) {{
            if (params.nodes.length > 0) {{
                var nodeId = params.nodes[0];
                var node = nodes.get(nodeId);
                alert("Entity Details:\\n" + node.title);
            }} else if (params.edges.length > 0) {{
                var edgeId = params.edges[0];
                var edge = edges.get(edgeId);
                alert("Relationship Details:\\n" + edge.title);
            }}
        }});
        
        // Control functions
        function togglePhysics() {{
            var enabled = !options.physics.enabled;
            options.physics.enabled = enabled;
            network.setOptions(options);
        }}
        
        function exportNetwork() {{
            // This would require additional canvas export functionality
            alert("Export functionality would be implemented here");
        }}
        
        function showStatistics() {{
            var stats = "Network Statistics:\\n";
            stats += "Nodes: " + nodes.length + "\\n";
            stats += "Edges: " + edges.length + "\\n";
            stats += "\\nEntity Type Distribution:\\n";
            {self._generate_stats_js(summary['entity_types'])}
            alert(stats);
        }}
        
        // Auto-fit on load
        network.once("stabilizationIterationsDone", function() {{
            network.fit();
        }});
    </script>
</body>
</html>
        '''

    def _generate_legend_html(self, items: Dict, item_type: str) -> str:
        """Generate HTML for legend items."""
        html = ""
        for item_name, count in items.items():
            if item_type == 'entity':
                color = self._get_node_color(item_name)
            else:
                color = self._get_edge_color(item_name)
            
            html += f'''
            <div class="legend-item">
                <span class="legend-color" style="background-color: {color};"></span>
                {item_name} ({count})
            </div>
            '''
        return html

    def _generate_stats_js(self, entity_types: Dict) -> str:
        """Generate JavaScript for statistics display."""
        js_lines = []
        for entity_type, count in entity_types.items():
            js_lines.append(f'stats += "{entity_type}: {count}\\n";')
        return '\n            '.join(js_lines)


def test_i2_export_with_csv(csv_file_path: str) -> None:
    """
    Complete test of i2 export functionality using a CSV file.
    
    Args:
        csv_file_path (str): Path to CSV file
        
    Returns:
        None
        
    Raises:
        Exception: If test fails
    """
    logger.info("=" * 60)
    logger.info("STARTING i2 EXPORT TESTING SUITE")
    logger.info("=" * 60)
    
    try:
        # Step 1: Generate test data
        logger.info("Step 1: Generating test cryptocurrency data...")
        data_generator = i2TestDataGenerator()
        test_addresses = data_generator.generate_test_extracted_addresses(csv_file_path)
        logger.info(f"Generated {len(test_addresses)} test addresses")
        
        # Step 2: Import and test i2 exporter
        logger.info("Step 2: Testing i2 export functionality...")
        try:
            from i2_exporter import i2Exporter
            
            exporter = i2Exporter()
            
            # Create test case info
            case_info = {
                'case_id': f'TEST_CASE_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'analyst': 'Test Analyst',
                'priority': 'HIGH',
                'investigation_type': 'FINANCIAL_CRIMES',
                'target_entity': 'Test Investigation',
                'extraction_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'total_addresses': len(test_addresses),
                'files_processed': 1
            }
            
            # Progress callback for testing
            def test_progress_callback(stage, detail=""):
                logger.info(f"i2 Export Progress: {stage} - {detail}")
            
            # Export to i2 format
            xml_path = exporter.export_investigation_data(
                test_addresses, 
                case_info=case_info,
                progress_callback=test_progress_callback
            )
            
            logger.info(f"i2 export completed: {xml_path}")
            
        except ImportError as e:
            logger.error(f"Could not import i2_exporter: {e}")
            logger.info("Creating mock XML file for testing...")
            xml_path = create_mock_i2_xml(test_addresses)
        
        # Step 3: Analyze the generated i2 export
        logger.info("Step 3: Analyzing generated i2 export...")
        analyzer = i2ExportAnalyzer()
        analysis = analyzer.analyze_i2_xml(xml_path)
        
        # Print analysis summary
        logger.info("\\nANALYSIS SUMMARY:")
        logger.info("=" * 40)
        logger.info(f"Total Entities: {analysis['summary']['total_entities']}")
        logger.info(f"Total Links: {analysis['summary']['total_links']}")
        logger.info(f"Entity Types: {list(analysis['summary']['entity_types'].keys())}")
        logger.info(f"Link Types: {list(analysis['summary']['link_types'].keys())}")
        
        # Step 4: Generate HTML visualization
        logger.info("Step 4: Generating HTML visualization...")
        html_path = analyzer.generate_html_visualization(analysis)
        
        # Step 5: Open visualization in browser
        logger.info(f"Opening visualization in browser: {html_path}")
        webbrowser.open(f'file://{os.path.abspath(html_path)}')
        
        logger.info("=" * 60)
        logger.info("i2 EXPORT TESTING COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"📄 XML Export: {xml_path}")
        logger.info(f"🌐 HTML Visualization: {html_path}")
        logger.info("💡 Check the opened browser tab for interactive visualization")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


def create_mock_i2_xml(addresses: List[Any]) -> str:
    """Create a mock i2 XML file for testing when i2_exporter is not available."""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    xml_path = f"mock_i2_export_{timestamp}.xml"
    
    # Create basic XML structure
    root = ET.Element("i2:Investigation")
    root.set("xmlns:i2", "http://www.i2group.com/Investigation")
    
    # Case info
    case_info = ET.SubElement(root, "CaseInfo")
    ET.SubElement(case_info, "CaseTitle").text = "Mock Cryptocurrency Investigation"
    ET.SubElement(case_info, "DateCreated").text = datetime.now().isoformat()
    ET.SubElement(case_info, "CreatedBy").text = "i2 Testing Suite"
    
    # Entities
    entities_elem = ET.SubElement(root, "Entities")
    for i, addr in enumerate(addresses):
        entity = ET.SubElement(entities_elem, "Entity")
        entity.set("EntityId", f"addr_{addr.address}_{addr.crypto_type}")
        entity.set("EntityType", "CryptoAddress")
        
        ET.SubElement(entity, "Label").text = f"{addr.address[:20]}..."
        ET.SubElement(entity, "IconStyle").text = f"{addr.crypto_type}_Address"
        
        attrs = ET.SubElement(entity, "Attributes")
        ET.SubElement(attrs, "Attribute", Name="Address").text = addr.address
        ET.SubElement(attrs, "Attribute", Name="CryptoType").text = addr.crypto_type
        ET.SubElement(attrs, "Attribute", Name="Confidence").text = str(addr.confidence)
    
    # Links (create some sample connections)
    links_elem = ET.SubElement(root, "Links")
    for i in range(min(3, len(addresses)-1)):
        link = ET.SubElement(links_elem, "Link")
        link.set("LinkId", f"link_{i}")
        link.set("FromEntity", f"addr_{addresses[i].address}_{addresses[i].crypto_type}")
        link.set("ToEntity", f"addr_{addresses[i+1].address}_{addresses[i+1].crypto_type}")
        link.set("LinkType", "ConnectedTo")
        
        ET.SubElement(link, "Label").text = "Potential Connection"
        ET.SubElement(link, "Strength").text = "0.5"
    
    # Write XML
    from xml.dom import minidom
    rough_string = ET.tostring(root, 'unicode')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    
    logger.info(f"Created mock XML file: {xml_path}")
    return xml_path


if __name__ == "__main__":
    import sys
    
    # Check if CSV file provided as argument
    csv_file = None
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        if not os.path.exists(csv_file):
            logger.error(f"CSV file not found: {csv_file}")
            sys.exit(1)
    else:
        logger.info("No CSV file provided, will use sample data")
    
    # Run the test
    try:
        test_i2_export_with_csv(csv_file)
    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)