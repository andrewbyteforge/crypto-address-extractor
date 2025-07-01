"""
i2 Enhanced Features Integration Example
=======================================

File: integrate_i2_enhanced.py
Function: Shows how to integrate enhanced features with existing i2_exporter.py

This example demonstrates how to use the enhanced investigative features
alongside your current i2 export functionality.

Author: Crypto Extractor Tool
Date: 2025-07-01
Version: 1.0.0
"""

import logging
from datetime import datetime
from typing import List, Dict, Any


def integrate_enhanced_features_with_export(addresses: List[Any], case_info: Dict = None) -> str:
    """
    Complete integration example showing how to use enhanced features.
    
    Args:
        addresses: List of extracted cryptocurrency addresses
        case_info: Case information dictionary
        
    Returns:
        str: Path to main export file
        
    Raises:
        Exception: If integration fails
    """
    try:
        # Step 1: Import required modules
        from i2_exporter import EnhancedI2Exporter  # Your existing exporter
        from i2_enhanced_features import i2EnhancedFeatures  # New enhanced features
        
        logger = logging.getLogger(__name__)
        logger.info("Starting enhanced i2 export with advanced features")
        
        # Step 2: Initialize both modules
        base_exporter = EnhancedI2Exporter()
        enhanced_features = i2EnhancedFeatures(base_exporter)
        
        # Step 3: Create basic entities and links using existing exporter
        logger.info("Creating basic entities and links")
        entities = base_exporter._create_enhanced_address_entities(addresses)
        
        # Create service entities if API data available
        service_entities = []
        service_links = []
        
        for addr in addresses:
            if hasattr(addr, 'api_data') and addr.api_data:
                # Create service entities from API exposure data
                for exposure in addr.api_data.get('exposure', []):
                    service_name = exposure.get('service', 'Unknown')
                    # Add service entity logic here
        
        # Create basic address relationships
        address_links = []
        # Add your relationship logic here
        
        all_entities = entities + service_entities
        all_links = address_links + service_links
        
        # Step 4: Apply enhanced analysis features
        logger.info("Applying enhanced investigative analysis")
        
        # Money flow analysis
        logger.info("Analyzing money flows")
        money_flows = enhanced_features.analyze_money_flows(all_entities, all_links)
        
        # Risk cluster detection
        logger.info("Detecting risk clusters")
        risk_clusters = enhanced_features.detect_risk_clusters(all_entities, all_links)
        
        # Generate investigative insights
        logger.info("Generating investigative insights")
        insights = enhanced_features.generate_investigative_insights(
            all_entities, all_links, money_flows, risk_clusters
        )
        
        # Step 5: Create enhanced exports
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        case_id = case_info.get('case_id', 'CRYPTO_CASE') if case_info else 'CRYPTO_CASE'
        filename_base = f"{case_id}_{timestamp}"
        
        # Export standard i2 XML (compatible with your existing code)
        logger.info("Exporting standard i2 XML")
        xml_path = base_exporter._export_enhanced_i2_xml(all_entities, all_links, filename_base, case_info)
        
        # Export enhanced investigation report
        logger.info("Creating enhanced investigation report")
        report_path = enhanced_features.export_enhanced_investigation_report(
            filename_base, all_entities, all_links, insights, money_flows, risk_clusters
        )
        
        # Create interactive dashboard
        logger.info("Creating interactive dashboard")
        dashboard_path = enhanced_features.create_investigation_dashboard(
            all_entities, all_links, insights, money_flows, risk_clusters
        )
        
        # Step 6: Export additional formats
        
        # Export insights as JSON for external tools
        insights_json_path = f"{filename_base}_insights.json"
        import json
        with open(insights_json_path, 'w', encoding='utf-8') as f:
            insights_data = [
                {
                    'type': insight.insight_type,
                    'title': insight.title,
                    'description': insight.description,
                    'severity': insight.severity,
                    'entities': insight.entities,
                    'evidence': insight.evidence,
                    'recommendations': insight.recommendations,
                    'confidence': insight.confidence
                }
                for insight in insights
            ]
            json.dump(insights_data, f, indent=2)
        
        # Export risk clusters as CSV
        clusters_csv_path = f"{filename_base}_risk_clusters.csv"
        import csv
        with open(clusters_csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Cluster ID', 'Name', 'Risk Level', 'Entity Count', 'Risk Factors'])
            for cluster in risk_clusters:
                writer.writerow([
                    cluster.cluster_id,
                    cluster.cluster_name,
                    cluster.risk_level,
                    len(cluster.entities),
                    '; '.join(cluster.risk_factors)
                ])
        
        # Step 7: Generate summary
        summary_path = f"{filename_base}_integration_summary.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("i2 ENHANCED EXPORT SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Export completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Case ID: {case_id}\n\n")
            
            f.write("FILES GENERATED:\n")
            f.write("-" * 30 + "\n")
            f.write(f"📊 i2 XML Chart: {xml_path}\n")
            f.write(f"📋 Investigation Report: {report_path}\n")
            f.write(f"🌐 Interactive Dashboard: {dashboard_path}\n")
            f.write(f"📊 Insights JSON: {insights_json_path}\n")
            f.write(f"📈 Risk Clusters CSV: {clusters_csv_path}\n\n")
            
            f.write("ANALYSIS RESULTS:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total Entities: {len(all_entities)}\n")
            f.write(f"Total Links: {len(all_links)}\n")
            f.write(f"Money Flows Identified: {len(money_flows)}\n")
            f.write(f"Risk Clusters: {len(risk_clusters)}\n")
            f.write(f"Investigative Insights: {len(insights)}\n\n")
            
            # Top insights summary
            critical_insights = [i for i in insights if i.severity == 'CRITICAL']
            if critical_insights:
                f.write("🚨 CRITICAL FINDINGS:\n")
                for insight in critical_insights:
                    f.write(f"  - {insight.title}\n")
                f.write("\n")
            
            f.write("NEXT STEPS:\n")
            f.write("-" * 30 + "\n")
            f.write("1. Import the i2 XML file into Analyst's Notebook\n")
            f.write("2. Review the investigation report for key findings\n")
            f.write("3. Open the interactive dashboard for visual analysis\n")
            f.write("4. Prioritize investigation based on critical insights\n")
            f.write("5. Use risk clusters to guide entity consolidation\n")
        
        logger.info(f"Enhanced i2 export integration complete!")
        logger.info(f"Main export file: {xml_path}")
        logger.info(f"Summary: {summary_path}")
        
        return xml_path
        
    except Exception as e:
        logger.error(f"Enhanced integration failed: {e}", exc_info=True)
        raise


def demonstrate_advanced_features():
    """
    Demonstrate the advanced features with sample data.
    """
    print("🚀 i2 Enhanced Features Integration Demo")
    print("=" * 60)
    
    # Sample case info
    sample_case_info = {
        'case_id': 'DEMO_CASE_001',
        'analyst': 'Demo Analyst',
        'priority': 'HIGH',
        'investigation_type': 'MONEY_LAUNDERING',
        'target_entity': 'Suspicious Cryptocurrency Network'
    }
    
    print("📋 Sample Case Information:")
    for key, value in sample_case_info.items():
        print(f"   {key}: {value}")
    
    print("\n🔧 Enhanced Features Available:")
    
    features = [
        ("💰 Money Flow Analysis", "Trace suspicious transaction patterns and layering schemes"),
        ("🎯 Risk Cluster Detection", "Identify groups of related high-risk entities"),
        ("🔍 Investigative Insights", "Generate actionable intelligence from patterns"),
        ("🌐 Interactive Dashboard", "Web-based visualization with charts and graphs"),
        ("📊 Enhanced Reporting", "Comprehensive investigation reports with priorities"),
        ("🕵️ Darknet Detection", "Identify addresses with darknet market exposure"),
        ("⚠️ Privacy Coin Analysis", "Specialized handling of Monero, Zcash, etc."),
        ("🏦 Exchange Pattern Analysis", "Detect suspicious exchange usage patterns"),
        ("📈 Risk Scoring", "Multi-factor risk assessment for all entities"),
        ("🔗 Advanced Relationships", "Cluster analysis and entity consolidation")
    ]
    
    for feature, description in features:
        print(f"   {feature}: {description}")
    
    print("\n💡 Integration Benefits:")
    benefits = [
        "Works with your existing i2_exporter.py",
        "Maintains backward compatibility",
        "Adds advanced investigative capabilities",
        "Provides multiple export formats",
        "Generates actionable intelligence",
        "Creates interactive visualizations",
        "Prioritizes investigation targets",
        "Automates pattern detection"
    ]
    
    for benefit in benefits:
        print(f"   ✅ {benefit}")
    
    print("\n🎯 Usage Example:")
    print("```python")
    print("# Import your existing addresses")
    print("addresses = your_extraction_results")
    print("")
    print("# Run enhanced export")
    print("xml_path = integrate_enhanced_features_with_export(addresses, case_info)")
    print("")
    print("# Result: Multiple files generated with advanced analysis")
    print("```")
    
    print("\n📁 Generated Files:")
    files = [
        ("XML Chart", "Direct import into i2 Analyst's Notebook"),
        ("Investigation Report", "Comprehensive analysis with priorities"),
        ("Interactive Dashboard", "Web-based visualization tool"),
        ("Insights JSON", "Machine-readable intelligence data"),
        ("Risk Clusters CSV", "Spreadsheet of high-risk entity groups"),
        ("Summary Report", "Executive overview and next steps")
    ]
    
    for file_type, description in files:
        print(f"   📄 {file_type}: {description}")
    
    print("\n🚀 Ready to enhance your cryptocurrency investigations!")
    print("   Save both files and follow the integration example above.")


if __name__ == "__main__":
    demonstrate_advanced_features()