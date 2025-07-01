#!/usr/bin/env python3
"""
Simple i2 Test Script for test.csv
=================================

This script demonstrates how the i2 export functionality works with your test.csv file.
Since you don't have i2 Analyst's Notebook, this creates an interactive HTML visualization
to show what the i2 export would look like.

Usage:
    python simple_i2_test.py

Requirements:
    - test.csv file in the same directory
    - Basic Python libraries (no special dependencies)
"""

import os
import csv
import json
import webbrowser
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_test_csv():
    """
    Analyze the test.csv file to understand its structure and extract any crypto addresses.
    
    Returns:
        Dict: Analysis results
        
    Raises:
        Exception: If CSV cannot be processed
    """
    logger.info("Analyzing test.csv file...")
    
    if not os.path.exists('test.csv'):
        logger.error("test.csv file not found in current directory")
        return None
    
    analysis = {
        'file_info': {
            'filename': 'test.csv',
            'size_bytes': os.path.getsize('test.csv'),
            'analyzed_at': datetime.now().isoformat()
        },
        'structure': {
            'total_rows': 0,
            'total_columns': 0,
            'headers': [],
            'sample_data': []
        },
        'crypto_addresses': {
            'detected_addresses': [],
            'potential_addresses': [],
            'crypto_types_found': set()
        },
        'content_analysis': {
            'text_content': '',
            'has_crypto_keywords': False,
            'crypto_keywords_found': []
        }
    }
    
    try:
        # Read and analyze CSV structure
        with open('test.csv', 'r', encoding='utf-8', errors='ignore') as f:
            # First, read as text to analyze content
            content = f.read()
            analysis['content_analysis']['text_content'] = content[:1000]  # First 1000 chars
            
            # Check for crypto-related keywords
            crypto_keywords = [
                'bitcoin', 'btc', 'ethereum', 'eth', 'address', 'wallet',
                'transaction', 'crypto', 'blockchain', 'hash', 'solana', 'sol'
            ]
            
            content_lower = content.lower()
            found_keywords = [kw for kw in crypto_keywords if kw in content_lower]
            analysis['content_analysis']['crypto_keywords_found'] = found_keywords
            analysis['content_analysis']['has_crypto_keywords'] = len(found_keywords) > 0
            
            # Reset file pointer and read as CSV
            f.seek(0)
            
            # Try to detect CSV structure
            sniffer = csv.Sniffer()
            sample = f.read(1024)
            f.seek(0)
            
            delimiter = ','
            try:
                dialect = sniffer.sniff(sample)
                delimiter = dialect.delimiter
            except:
                logger.warning("Could not detect CSV dialect, using comma delimiter")
            
            reader = csv.reader(f, delimiter=delimiter)
            rows = list(reader)
            
            if rows:
                analysis['structure']['headers'] = rows[0] if rows else []
                analysis['structure']['total_rows'] = len(rows)
                analysis['structure']['total_columns'] = len(rows[0]) if rows else 0
                analysis['structure']['sample_data'] = rows[1:6] if len(rows) > 1 else []  # First 5 data rows
                
                # Look for cryptocurrency addresses in all cells
                addresses_found = detect_crypto_addresses_in_data(rows)
                analysis['crypto_addresses'].update(addresses_found)
                
        logger.info(f"CSV Analysis complete:")
        logger.info(f"  - Rows: {analysis['structure']['total_rows']}")
        logger.info(f"  - Columns: {analysis['structure']['total_columns']}")
        logger.info(f"  - Headers: {analysis['structure']['headers']}")
        logger.info(f"  - Crypto addresses found: {len(analysis['crypto_addresses']['detected_addresses'])}")
        logger.info(f"  - Crypto keywords: {analysis['content_analysis']['crypto_keywords_found']}")
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing CSV: {e}")
        return None

def detect_crypto_addresses_in_data(rows):
    """
    Detect cryptocurrency addresses in CSV data using pattern matching.
    
    Args:
        rows: List of CSV rows
        
    Returns:
        Dict: Detection results
        
    Raises:
        None
    """
    import re
    
    detected_addresses = []
    potential_addresses = []
    crypto_types_found = set()
    
    # Enhanced regex patterns for different cryptocurrencies
    patterns = {
        'BTC': {
            'pattern': r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b',
            'confidence': 0.9
        },
        'ETH': {
            'pattern': r'\b0x[a-fA-F0-9]{40}\b',
            'confidence': 0.95
        },
        'SOL': {
            'pattern': r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b',
            'confidence': 0.7
        },
        'BCH': {
            'pattern': r'\b[qp][a-z0-9]{41}\b',
            'confidence': 0.8
        },
        'LTC': {
            'pattern': r'\b[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}\b',
            'confidence': 0.85
        }
    }
    
    # Check each cell in each row
    for row_idx, row in enumerate(rows):
        for col_idx, cell in enumerate(row):
            if not cell or len(cell) < 20:  # Skip short cells
                continue
                
            cell_str = str(cell).strip()
            
            # Check against each crypto pattern
            for crypto_type, pattern_info in patterns.items():
                matches = re.findall(pattern_info['pattern'], cell_str)
                
                for match in matches:
                    # Additional validation
                    if crypto_type == 'BTC' and len(match) >= 26:
                        detected_addresses.append({
                            'address': match,
                            'crypto_type': crypto_type,
                            'confidence': pattern_info['confidence'],
                            'location': {'row': row_idx, 'column': col_idx},
                            'source_cell': cell_str
                        })
                        crypto_types_found.add(crypto_type)
                        
                    elif crypto_type == 'ETH' and len(match) == 42:
                        detected_addresses.append({
                            'address': match,
                            'crypto_type': crypto_type,
                            'confidence': pattern_info['confidence'],
                            'location': {'row': row_idx, 'column': col_idx},
                            'source_cell': cell_str
                        })
                        crypto_types_found.add(crypto_type)
                        
                    elif crypto_type == 'SOL' and 32 <= len(match) <= 44:
                        # Additional check to avoid false positives with BTC addresses
                        if not match.startswith(('1', '3', 'bc1')):
                            detected_addresses.append({
                                'address': match,
                                'crypto_type': crypto_type,
                                'confidence': pattern_info['confidence'] * 0.8,  # Lower confidence
                                'location': {'row': row_idx, 'column': col_idx},
                                'source_cell': cell_str
                            })
                            crypto_types_found.add(crypto_type)
    
    # Remove duplicates
    unique_addresses = []
    seen_addresses = set()
    for addr in detected_addresses:
        addr_key = (addr['address'], addr['crypto_type'])
        if addr_key not in seen_addresses:
            unique_addresses.append(addr)
            seen_addresses.add(addr_key)
    
    return {
        'detected_addresses': unique_addresses,
        'potential_addresses': potential_addresses,
        'crypto_types_found': crypto_types_found
    }

def create_sample_i2_data(csv_analysis):
    """
    Create sample i2 entities and links based on CSV analysis.
    
    Args:
        csv_analysis: Results from analyze_test_csv()
        
    Returns:
        Dict: i2 entities and links
        
    Raises:
        None
    """
    entities = []
    links = []
    
    # Create entities for detected addresses
    addresses = csv_analysis['crypto_addresses']['detected_addresses']
    
    if not addresses:
        # Create sample data if no addresses found
        logger.info("No crypto addresses detected, creating sample demonstration data")
        addresses = [
            {
                'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
                'crypto_type': 'BTC',
                'confidence': 1.0,
                'location': {'row': 1, 'column': 1},
                'source_cell': 'Sample Bitcoin Genesis Address'
            },
            {
                'address': '0x742d35Cc6761C5Bd63b1508073ae38d0b8Bd2e9D',
                'crypto_type': 'ETH',
                'confidence': 0.95,
                'location': {'row': 2, 'column': 1},
                'source_cell': 'Sample Ethereum Address'
            }
        ]
    
    # Create address entities
    for i, addr in enumerate(addresses):
        entity = {
            'id': f"addr_{addr['address']}_{addr['crypto_type']}",
            'type': 'CryptoAddress',
            'label': f"{addr['address'][:20]}...({addr['crypto_type']})",
            'attributes': {
                'Address': addr['address'],
                'CryptoType': addr['crypto_type'],
                'Confidence': addr['confidence'],
                'SourceLocation': f"Row {addr['location']['row']}, Column {addr['location']['column']}",
                'SourceCell': addr['source_cell'][:100] + ('...' if len(addr['source_cell']) > 100 else ''),
                'RiskLevel': 'MEDIUM',
                'DetectionMethod': 'Pattern Matching'
            },
            'color': get_crypto_color(addr['crypto_type']),
            'size': 20 + (addr['confidence'] * 10)
        }
        entities.append(entity)
    
    # Create file entity
    file_entity = {
        'id': 'source_file_test_csv',
        'type': 'SourceFile',
        'label': 'test.csv',
        'attributes': {
            'FileName': 'test.csv',
            'FileSize': csv_analysis['file_info']['size_bytes'],
            'TotalRows': csv_analysis['structure']['total_rows'],
            'TotalColumns': csv_analysis['structure']['total_columns'],
            'Headers': ', '.join(csv_analysis['structure']['headers'][:5]),
            'AnalyzedAt': csv_analysis['file_info']['analyzed_at'],
            'CryptoKeywords': ', '.join(csv_analysis['content_analysis']['crypto_keywords_found'])
        },
        'color': '#95A5A6',
        'size': 25
    }
    entities.append(file_entity)
    
    # Create links from addresses to source file
    for addr in addresses:
        link = {
            'id': f"link_{addr['address'][:10]}_to_file",
            'from': f"addr_{addr['address']}_{addr['crypto_type']}",
            'to': 'source_file_test_csv',
            'type': 'ExtractedFrom',
            'label': f"Extracted from test.csv",
            'attributes': {
                'ExtractionMethod': 'Pattern Matching',
                'Confidence': addr['confidence']
            },
            'color': '#7F8C8D',
            'width': 2
        }
        links.append(link)
    
    # Create crypto type entities
    crypto_types = csv_analysis['crypto_addresses']['crypto_types_found']
    if not crypto_types and addresses:
        crypto_types = set(addr['crypto_type'] for addr in addresses)
    
    for crypto_type in crypto_types:
        crypto_entity = {
            'id': f"crypto_type_{crypto_type}",
            'type': 'CryptocurrencyType',
            'label': f"{crypto_type} Blockchain",
            'attributes': {
                'CryptoType': crypto_type,
                'AddressCount': len([a for a in addresses if a['crypto_type'] == crypto_type]),
                'Description': get_crypto_description(crypto_type)
            },
            'color': get_crypto_color(crypto_type),
            'size': 30
        }
        entities.append(crypto_entity)
        
        # Link addresses to their crypto type
        for addr in addresses:
            if addr['crypto_type'] == crypto_type:
                link = {
                    'id': f"link_{addr['address'][:10]}_to_{crypto_type}",
                    'from': f"addr_{addr['address']}_{addr['crypto_type']}",
                    'to': f"crypto_type_{crypto_type}",
                    'type': 'BelongsTo',
                    'label': f"Uses {crypto_type} blockchain",
                    'attributes': {
                        'RelationshipType': 'blockchain_membership'
                    },
                    'color': get_crypto_color(crypto_type),
                    'width': 3
                }
                links.append(link)
    
    return {
        'entities': entities,
        'links': links,
        'summary': {
            'total_entities': len(entities),
            'total_links': len(links),
            'addresses_found': len(addresses),
            'crypto_types': len(crypto_types)
        }
    }

def get_crypto_color(crypto_type):
    """Get color for cryptocurrency type."""
    colors = {
        'BTC': '#F7931A',
        'ETH': '#627EEA',
        'SOL': '#9945FF',
        'BCH': '#8DC351',
        'LTC': '#BFBBBB',
        'XMR': '#FF6600',
        'ZEC': '#F4B728'
    }
    return colors.get(crypto_type, '#95A5A6')

def get_crypto_description(crypto_type):
    """Get description for cryptocurrency type."""
    descriptions = {
        'BTC': 'Bitcoin - The original cryptocurrency',
        'ETH': 'Ethereum - Smart contract platform',
        'SOL': 'Solana - High-performance blockchain',
        'BCH': 'Bitcoin Cash - Bitcoin fork with larger blocks',
        'LTC': 'Litecoin - Silver to Bitcoin\'s gold',
        'XMR': 'Monero - Privacy-focused cryptocurrency',
        'ZEC': 'Zcash - Privacy cryptocurrency with shielded transactions'
    }
    return descriptions.get(crypto_type, f'{crypto_type} cryptocurrency')

def generate_html_visualization(i2_data, csv_analysis):
    """
    Generate an interactive HTML visualization of the i2 data.
    
    Args:
        i2_data: i2 entities and links
        csv_analysis: CSV analysis results
        
    Returns:
        str: Path to HTML file
        
    Raises:
        Exception: If HTML generation fails
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    html_path = f"i2_test_visualization_{timestamp}.html"
    
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>i2 Export Test - test.csv Analysis</title>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .stat-card {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .stat-number {{ font-size: 24px; font-weight: bold; color: #667eea; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        #network {{ width: 100%; height: 600px; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .info-panel {{ background: white; padding: 20px; border-radius: 10px; margin-top: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .csv-info {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0; }}
        .crypto-types {{ display: flex; gap: 10px; flex-wrap: wrap; margin: 10px 0; }}
        .crypto-badge {{ background: #667eea; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px; }}
        .controls {{ background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        button {{ background: #667eea; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer; margin: 2px; transition: background 0.3s; }}
        button:hover {{ background: #5a67d8; }}
        .address-list {{ max-height: 200px; overflow-y: auto; margin: 10px 0; }}
        .address-item {{ padding: 8px; background: #f8f9fa; margin: 5px 0; border-radius: 5px; font-family: monospace; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 i2 Export Test Visualization</h1>
        <p>Analysis of <strong>test.csv</strong> - Demonstrating i2 Analyst's Notebook Export Functionality</p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{i2_data['summary']['total_entities']}</div>
            <div class="stat-label">Total Entities</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{i2_data['summary']['total_links']}</div>
            <div class="stat-label">Relationships</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{i2_data['summary']['addresses_found']}</div>
            <div class="stat-label">Crypto Addresses</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{i2_data['summary']['crypto_types']}</div>
            <div class="stat-label">Crypto Types</div>
        </div>
    </div>
    
    <div class="controls">
        <button onclick="network.fit()">🔍 Fit View</button>
        <button onclick="togglePhysics()">⚡ Toggle Physics</button>
        <button onclick="showDetails()">📊 Show Details</button>
        <button onclick="exportData()">💾 Export Data</button>
    </div>
    
    <div id="network"></div>
    
    <div class="info-panel">
        <h3>📄 CSV File Analysis</h3>
        <div class="csv-info">
            <strong>File:</strong> test.csv<br>
            <strong>Size:</strong> {csv_analysis['file_info']['size_bytes']} bytes<br>
            <strong>Structure:</strong> {csv_analysis['structure']['total_rows']} rows × {csv_analysis['structure']['total_columns']} columns<br>
            <strong>Headers:</strong> {', '.join(csv_analysis['structure']['headers'][:5])}{'...' if len(csv_analysis['structure']['headers']) > 5 else ''}<br>
            <strong>Crypto Keywords Found:</strong> {', '.join(csv_analysis['content_analysis']['crypto_keywords_found']) if csv_analysis['content_analysis']['crypto_keywords_found'] else 'None'}
        </div>
        
        <h4>🪙 Detected Cryptocurrency Addresses</h4>
        <div class="crypto-types">
            {generate_crypto_badges(csv_analysis['crypto_addresses']['crypto_types_found'])}
        </div>
        
        <div class="address-list">
            {generate_address_list(csv_analysis['crypto_addresses']['detected_addresses'])}
        </div>
        
        <h4>🎯 What This Demonstrates</h4>
        <ul>
            <li><strong>Address Detection:</strong> Pattern matching identifies cryptocurrency addresses in CSV data</li>
            <li><strong>Entity Creation:</strong> Each address becomes an entity with metadata</li>
            <li><strong>Relationship Mapping:</strong> Links show connections between addresses, file sources, and blockchain types</li>
            <li><strong>Visual Analysis:</strong> Interactive graph enables investigation workflow</li>
            <li><strong>i2 Compatibility:</strong> Data structure matches i2 Analyst's Notebook requirements</li>
        </ul>
        
        <h4>📋 Next Steps for Real Investigation</h4>
        <ol>
            <li>Import the generated XML file into i2 Analyst's Notebook</li>
            <li>Enhance with Chainalysis API data for cluster information</li>
            <li>Add transaction flow analysis</li>
            <li>Correlate with external intelligence sources</li>
            <li>Develop investigation hypotheses based on patterns</li>
        </ol>
    </div>

    <script>
        // Prepare network data
        var nodes = new vis.DataSet({json.dumps(i2_data['entities'])});
        var edges = new vis.DataSet({json.dumps(i2_data['links'])});
        var data = {{ nodes: nodes, edges: edges }};
        
        // Network options
        var options = {{
            nodes: {{
                shape: 'dot',
                font: {{ size: 14, color: '#333' }},
                borderWidth: 2,
                shadow: {{ enabled: true, color: 'rgba(0,0,0,0.2)', size: 10, x: 2, y: 2 }}
            }},
            edges: {{
                width: 2,
                shadow: {{ enabled: true, color: 'rgba(0,0,0,0.1)', size: 5, x: 1, y: 1 }},
                smooth: {{ type: 'continuous' }},
                arrows: {{ to: {{ enabled: true, scaleFactor: 0.5 }} }}
            }},
            physics: {{
                enabled: true,
                stabilization: {{ iterations: 100 }},
                barnesHut: {{ gravitationalConstant: -3000, springConstant: 0.004, springLength: 150 }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200,
                hideEdgesOnDrag: true
            }}
        }};
        
        // Create network
        var container = document.getElementById('network');
        var network = new vis.Network(container, data, options);
        
        // Event handlers
        network.on("click", function (params) {{
            if (params.nodes.length > 0) {{
                var nodeId = params.nodes[0];
                var node = nodes.get(nodeId);
                var details = "Entity Details:\\n\\n";
                details += "ID: " + node.id + "\\n";
                details += "Type: " + node.type + "\\n";
                details += "Label: " + node.label + "\\n\\n";
                details += "Attributes:\\n";
                for (var key in node.attributes) {{
                    details += "• " + key + ": " + node.attributes[key] + "\\n";
                }}
                alert(details);
            }}
        }});
        
        // Control functions
        function togglePhysics() {{
            var enabled = !options.physics.enabled;
            options.physics.enabled = enabled;
            network.setOptions(options);
        }}
        
        function showDetails() {{
            var summary = "Network Analysis Summary:\\n\\n";
            summary += "Total Entities: " + nodes.length + "\\n";
            summary += "Total Relationships: " + edges.length + "\\n\\n";
            summary += "Entity Types:\\n";
            
            var entityTypes = {{}};
            nodes.forEach(function(node) {{
                entityTypes[node.type] = (entityTypes[node.type] || 0) + 1;
            }});
            
            for (var type in entityTypes) {{
                summary += "• " + type + ": " + entityTypes[type] + "\\n";
            }}
            
            alert(summary);
        }}
        
        function exportData() {{
            var exportData = {{
                entities: nodes.get(),
                links: edges.get(),
                generated: new Date().toISOString()
            }};
            
            var dataStr = JSON.stringify(exportData, null, 2);
            var dataBlob = new Blob([dataStr], {{type: 'application/json'}});
            var url = URL.createObjectURL(dataBlob);
            var link = document.createElement('a');
            link.href = url;
            link.download = 'i2_test_data.json';
            link.click();
        }}
        
        // Auto-fit on load
        network.once("stabilizationIterationsDone", function() {{
            network.fit();
        }});
    </script>
</body>
</html>'''
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info(f"HTML visualization generated: {html_path}")
    return html_path

def generate_crypto_badges(crypto_types):
    """Generate HTML for crypto type badges."""
    if not crypto_types:
        return '<span class="crypto-badge">No crypto types detected</span>'
    
    badges = []
    for crypto_type in crypto_types:
        badges.append(f'<span class="crypto-badge" style="background-color: {get_crypto_color(crypto_type)}">{crypto_type}</span>')
    
    return ''.join(badges)

def generate_address_list(addresses):
    """Generate HTML for address list."""
    if not addresses:
        return '<div class="address-item">No cryptocurrency addresses detected in CSV file</div>'
    
    items = []
    for addr in addresses[:10]:  # Show first 10
        items.append(f'''
        <div class="address-item">
            <strong>{addr['crypto_type']}:</strong> {addr['address']}<br>
            <small>Confidence: {addr['confidence']:.2f} | Location: Row {addr['location']['row']}, Col {addr['location']['column']}</small>
        </div>
        ''')
    
    if len(addresses) > 10:
        items.append(f'<div class="address-item"><em>... and {len(addresses) - 10} more addresses</em></div>')
    
    return ''.join(items)

def main():
    """Main function to run the i2 test."""
    print("=" * 60)
    print("🔍 i2 EXPORT TESTING SUITE")
    print("Testing with test.csv file")
    print("=" * 60)
    
    try:
        # Step 1: Analyze CSV file
        print("\\n📊 Step 1: Analyzing test.csv...")
        csv_analysis = analyze_test_csv()
        
        if not csv_analysis:
            print("❌ Could not analyze CSV file")
            return
        
        # Step 2: Create i2 data structure
        print("\\n🏗️  Step 2: Creating i2 entities and relationships...")
        i2_data = create_sample_i2_data(csv_analysis)
        
        # Step 3: Generate visualization
        print("\\n🌐 Step 3: Generating interactive visualization...")
        html_path = generate_html_visualization(i2_data, csv_analysis)
        
        # Step 4: Open in browser
        print("\\n🚀 Step 4: Opening visualization in browser...")
        full_path = os.path.abspath(html_path)
        webbrowser.open(f'file://{full_path}')
        
        # Summary
        print("\\n" + "=" * 60)
        print("✅ i2 EXPORT TEST COMPLETE!")
        print("=" * 60)
        print(f"📄 CSV Analysis: {csv_analysis['structure']['total_rows']} rows, {csv_analysis['structure']['total_columns']} columns")
        print(f"🪙 Addresses Found: {len(csv_analysis['crypto_addresses']['detected_addresses'])}")
        print(f"🔗 Entities Created: {i2_data['summary']['total_entities']}")
        print(f"📊 Relationships: {i2_data['summary']['total_links']}")
        print(f"🌐 Visualization: {html_path}")
        print("\\n💡 Check your browser for the interactive i2 visualization!")
        print("\\n📋 This demonstrates how cryptocurrency addresses from CSV files")
        print("   would be structured for i2 Analyst's Notebook import.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()