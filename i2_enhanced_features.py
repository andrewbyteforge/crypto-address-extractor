"""
i2 Enhanced Features Addon
==========================

File: i2_enhanced_features.py
Function: Advanced investigative features for i2 Analyst's Notebook

This module extends the base i2_exporter.py with advanced features that
investigators find most useful in real-world cryptocurrency investigations.

Key Features:
1. Money Flow Analysis
2. Risk Heat Maps  
3. Cluster Visualization
4. Timeline Analysis
5. Geographic Mapping
6. Darknet Market Detection
7. Exchange Pattern Analysis
8. Automated Investigation Reports

Author: Crypto Extractor Tool
Date: 2025-07-01
Version: 1.0.0 - Enhanced Investigative Features
"""

import logging
import json
import csv
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
import xml.etree.ElementTree as ET
from xml.dom import minidom


@dataclass
class InvestigativeInsight:
    """Represents an investigative insight or finding."""
    insight_type: str  # 'risk_pattern', 'money_flow', 'cluster_analysis', etc.
    title: str
    description: str
    severity: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    entities: List[str]  # Entity IDs involved
    evidence: Dict[str, Any]
    recommendations: List[str]
    confidence: float


@dataclass
class MoneyFlowPath:
    """Represents a money flow path between entities."""
    path_id: str
    source_entity: str
    destination_entity: str
    intermediate_entities: List[str]
    total_value: float
    transaction_count: int
    risk_score: float
    flow_pattern: str  # 'direct', 'layered', 'complex'


@dataclass
class RiskCluster:
    """Represents a cluster of related high-risk entities."""
    cluster_id: str
    cluster_name: str
    risk_level: str
    entities: List[str]
    common_attributes: Dict[str, Any]
    risk_factors: List[str]
    investigation_priority: int


class i2EnhancedFeatures:
    """
    Enhanced investigative features for cryptocurrency analysis.
    
    This class works with your existing i2_exporter.py to add advanced
    analytical capabilities that investigators need.
    """
    
    def __init__(self, base_exporter=None):
        """
        Initialize enhanced features.
        
        Args:
            base_exporter: Instance of your existing i2Exporter class
            
        Raises:
            Exception: If initialization fails
        """
        try:
            self.logger = logging.getLogger(__name__)
            self.base_exporter = base_exporter
            
            # Investigation settings
            self.risk_thresholds = {
                'CRITICAL': 0.9,
                'HIGH': 0.7,
                'MEDIUM': 0.4,
                'LOW': 0.0
            }
            
            # Pattern detection settings
            self.flow_analysis_settings = {
                'min_flow_value': 1000,  # USD
                'max_hops': 5,
                'cluster_threshold': 0.8
            }
            
            # Darknet indicators
            self.darknet_indicators = [
                'darknet', 'dark market', 'silk road', 'alphabay', 'dream market',
                'empire market', 'white house market', 'darkweb', 'tor market'
            ]
            
            # Exchange patterns to watch
            self.suspicious_exchange_patterns = [
                'rapid_deposit_withdrawal',
                'round_number_transactions',
                'structured_deposits',
                'cross_exchange_arbitrage',
                'wash_trading_indicators'
            ]
            
            self.logger.info("Enhanced investigative features initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize enhanced features: {e}")
            raise

    def analyze_money_flows(self, entities: List, links: List) -> List[MoneyFlowPath]:
        """
        Analyze money flows between entities to identify suspicious patterns.
        
        Args:
            entities: List of i2Entity objects
            links: List of i2Link objects
            
        Returns:
            List[MoneyFlowPath]: Identified money flow paths
            
        Raises:
            Exception: If analysis fails
        """
        try:
            self.logger.info("Analyzing money flows and transaction patterns")
            
            flows = []
            
            # Build transaction graph
            transaction_graph = defaultdict(list)
            for link in links:
                if link.link_type in ['SendsTo', 'ReceivesFrom', 'UsesService']:
                    transaction_graph[link.from_entity].append({
                        'to': link.to_entity,
                        'type': link.link_type,
                        'attributes': link.attributes,
                        'strength': getattr(link, 'strength', 1.0)
                    })
            
            # Find significant flow paths
            for entity in entities:
                if entity.entity_type == 'CryptoAddress':
                    paths = self._trace_money_flows(
                        entity.entity_id, 
                        transaction_graph, 
                        max_depth=self.flow_analysis_settings['max_hops']
                    )
                    flows.extend(paths)
            
            # Rank flows by risk and value
            flows.sort(key=lambda x: (x.risk_score, x.total_value), reverse=True)
            
            self.logger.info(f"Identified {len(flows)} money flow paths")
            return flows[:50]  # Return top 50 flows
            
        except Exception as e:
            self.logger.error(f"Money flow analysis failed: {e}")
            raise

    def detect_risk_clusters(self, entities: List, links: List) -> List[RiskCluster]:
        """
        Detect clusters of related high-risk entities.
        
        Args:
            entities: List of entities
            links: List of links
            
        Returns:
            List[RiskCluster]: Identified risk clusters
            
        Raises:
            Exception: If detection fails
        """
        try:
            self.logger.info("Detecting high-risk entity clusters")
            
            clusters = []
            
            # Group entities by risk level and common attributes
            high_risk_entities = [
                e for e in entities 
                if getattr(e, 'risk_score', 0) >= self.risk_thresholds['HIGH']
            ]
            
            if not high_risk_entities:
                return clusters
            
            # Cluster by common attributes
            attribute_clusters = defaultdict(list)
            
            for entity in high_risk_entities:
                # Create clustering keys based on common attributes
                cluster_keys = []
                
                if hasattr(entity, 'attributes'):
                    attrs = entity.attributes
                    
                    # Cluster by exchange usage
                    if 'ExchangeExposure' in attrs:
                        for exposure in attrs['ExchangeExposure'].split(';'):
                            exchange_name = exposure.split(':')[0].strip()
                            cluster_keys.append(f"exchange_{exchange_name}")
                    
                    # Cluster by darknet exposure
                    if attrs.get('DarknetExposure') == 'YES':
                        cluster_keys.append("darknet_exposed")
                    
                    # Cluster by geographic location
                    if 'GeographicLocation' in attrs:
                        cluster_keys.append(f"geo_{attrs['GeographicLocation']}")
                    
                    # Cluster by crypto type
                    cluster_keys.append(f"crypto_{attrs.get('CryptoType', 'unknown')}")
                
                # Add to clusters
                for key in cluster_keys:
                    attribute_clusters[key].append(entity)
            
            # Create risk clusters from groups
            cluster_id = 0
            for cluster_key, cluster_entities in attribute_clusters.items():
                if len(cluster_entities) >= 2:  # Minimum cluster size
                    
                    # Calculate cluster risk score
                    avg_risk = sum(getattr(e, 'risk_score', 0) for e in cluster_entities) / len(cluster_entities)
                    
                    # Determine cluster risk level
                    if avg_risk >= self.risk_thresholds['CRITICAL']:
                        risk_level = 'CRITICAL'
                        priority = 1
                    elif avg_risk >= self.risk_thresholds['HIGH']:
                        risk_level = 'HIGH'
                        priority = 2
                    else:
                        risk_level = 'MEDIUM'
                        priority = 3
                    
                    # Extract common attributes
                    common_attrs = self._extract_common_attributes(cluster_entities)
                    
                    # Identify risk factors
                    risk_factors = self._identify_cluster_risk_factors(cluster_entities, cluster_key)
                    
                    cluster = RiskCluster(
                        cluster_id=f"risk_cluster_{cluster_id:03d}",
                        cluster_name=f"High-Risk Group: {cluster_key.replace('_', ' ').title()}",
                        risk_level=risk_level,
                        entities=[e.entity_id for e in cluster_entities],
                        common_attributes=common_attrs,
                        risk_factors=risk_factors,
                        investigation_priority=priority
                    )
                    
                    clusters.append(cluster)
                    cluster_id += 1
            
            # Sort by priority and risk
            clusters.sort(key=lambda x: (x.investigation_priority, -len(x.entities)))
            
            self.logger.info(f"Detected {len(clusters)} risk clusters")
            return clusters
            
        except Exception as e:
            self.logger.error(f"Risk cluster detection failed: {e}")
            raise

    def generate_investigative_insights(self, entities: List, links: List, 
                                      flows: List[MoneyFlowPath] = None,
                                      clusters: List[RiskCluster] = None) -> List[InvestigativeInsight]:
        """
        Generate actionable investigative insights from the analysis.
        
        Args:
            entities: List of entities
            links: List of links
            flows: Money flow analysis results
            clusters: Risk cluster analysis results
            
        Returns:
            List[InvestigativeInsight]: Generated insights
            
        Raises:
            Exception: If insight generation fails
        """
        try:
            self.logger.info("Generating investigative insights")
            
            insights = []
            
            # Insight 1: Darknet Market Exposure
            darknet_entities = [
                e for e in entities 
                if hasattr(e, 'attributes') and e.attributes.get('DarknetExposure') == 'YES'
            ]
            
            if darknet_entities:
                insight = InvestigativeInsight(
                    insight_type='darknet_exposure',
                    title='Darknet Market Exposure Detected',
                    description=f"Found {len(darknet_entities)} addresses with direct or indirect darknet market exposure. These addresses require immediate investigation for potential illicit activity.",
                    severity='CRITICAL',
                    entities=[e.entity_id for e in darknet_entities],
                    evidence={
                        'darknet_addresses': len(darknet_entities),
                        'total_balance': sum(float(e.attributes.get('BalanceUSD', 0)) for e in darknet_entities),
                        'affected_crypto_types': list(set(e.attributes.get('CryptoType', 'Unknown') for e in darknet_entities))
                    },
                    recommendations=[
                        "Investigate transaction history of darknet-exposed addresses",
                        "Check for connections to known criminal entities",
                        "Monitor for ongoing suspicious activity",
                        "Consider freezing high-value accounts pending investigation"
                    ],
                    confidence=0.95
                )
                insights.append(insight)
            
            # Insight 2: High-Value Concentration
            high_value_entities = [
                e for e in entities 
                if hasattr(e, 'attributes') and float(e.attributes.get('BalanceUSD', 0)) > 100000
            ]
            
            if high_value_entities:
                total_value = sum(float(e.attributes.get('BalanceUSD', 0)) for e in high_value_entities)
                
                insight = InvestigativeInsight(
                    insight_type='high_value_concentration',
                    title='High-Value Address Concentration',
                    description=f"Identified {len(high_value_entities)} addresses holding over $100K each, totaling ${total_value:,.2f}. This concentration warrants enhanced due diligence.",
                    severity='HIGH',
                    entities=[e.entity_id for e in high_value_entities],
                    evidence={
                        'high_value_count': len(high_value_entities),
                        'total_value_usd': total_value,
                        'average_value': total_value / len(high_value_entities),
                        'max_individual_value': max(float(e.attributes.get('BalanceUSD', 0)) for e in high_value_entities)
                    },
                    recommendations=[
                        "Verify source of funds for high-value addresses",
                        "Check compliance with reporting thresholds",
                        "Investigate beneficial ownership",
                        "Monitor for large transactions"
                    ],
                    confidence=0.85
                )
                insights.append(insight)
            
            # Insight 3: Privacy Coin Usage
            privacy_entities = [
                e for e in entities 
                if hasattr(e, 'attributes') and e.attributes.get('CryptoType') in ['XMR', 'ZEC', 'DASH']
            ]
            
            if privacy_entities:
                insight = InvestigativeInsight(
                    insight_type='privacy_coin_usage',
                    title='Privacy Coin Usage Detected',
                    description=f"Found {len(privacy_entities)} addresses using privacy-focused cryptocurrencies (Monero, Zcash, Dash). These require special investigation techniques.",
                    severity='MEDIUM',
                    entities=[e.entity_id for e in privacy_entities],
                    evidence={
                        'privacy_coin_count': len(privacy_entities),
                        'coin_types': list(set(e.attributes.get('CryptoType') for e in privacy_entities)),
                        'total_balance': sum(float(e.attributes.get('BalanceUSD', 0)) for e in privacy_entities)
                    },
                    recommendations=[
                        "Use specialized blockchain analysis tools for privacy coins",
                        "Focus on exchange entry/exit points",
                        "Investigate timing patterns",
                        "Check for mixing service usage"
                    ],
                    confidence=0.90
                )
                insights.append(insight)
            
            # Insight 4: Cluster Analysis Results
            if clusters:
                for cluster in clusters[:3]:  # Top 3 clusters
                    insight = InvestigativeInsight(
                        insight_type='cluster_analysis',
                        title=f'Risk Cluster: {cluster.cluster_name}',
                        description=f"Identified cluster of {len(cluster.entities)} related entities with {cluster.risk_level} risk level. Common patterns suggest coordinated activity.",
                        severity=cluster.risk_level,
                        entities=cluster.entities,
                        evidence={
                            'cluster_size': len(cluster.entities),
                            'risk_factors': cluster.risk_factors,
                            'common_attributes': cluster.common_attributes
                        },
                        recommendations=[
                            "Investigate entities as a group rather than individually",
                            "Look for common beneficial ownership",
                            "Check for coordinated transaction patterns",
                            "Consider entity consolidation for reporting"
                        ],
                        confidence=0.80
                    )
                    insights.append(insight)
            
            # Insight 5: Suspicious Exchange Patterns
            exchange_patterns = self._detect_suspicious_exchange_patterns(entities, links)
            if exchange_patterns:
                insight = InvestigativeInsight(
                    insight_type='exchange_patterns',
                    title='Suspicious Exchange Activity Patterns',
                    description=f"Detected {len(exchange_patterns)} suspicious exchange usage patterns including rapid deposits/withdrawals and structured transactions.",
                    severity='HIGH',
                    entities=[p['entity_id'] for p in exchange_patterns],
                    evidence={
                        'pattern_count': len(exchange_patterns),
                        'pattern_types': list(set(p['pattern_type'] for p in exchange_patterns)),
                        'affected_exchanges': list(set(p['exchange'] for p in exchange_patterns))
                    },
                    recommendations=[
                        "Investigate rapid exchange transactions",
                        "Check for structuring to avoid reporting",
                        "Look for wash trading indicators",
                        "Verify legitimate business purposes"
                    ],
                    confidence=0.75
                )
                insights.append(insight)
            
            # Sort insights by severity and confidence
            severity_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
            insights.sort(key=lambda x: (severity_order[x.severity], x.confidence), reverse=True)
            
            self.logger.info(f"Generated {len(insights)} investigative insights")
            return insights
            
        except Exception as e:
            self.logger.error(f"Insight generation failed: {e}")
            raise

    def create_investigation_dashboard(self, entities: List, links: List, 
                                    insights: List[InvestigativeInsight],
                                    flows: List[MoneyFlowPath] = None,
                                    clusters: List[RiskCluster] = None) -> str:
        """
        Create an HTML dashboard with interactive visualizations.
        
        Args:
            entities: List of entities
            links: List of links
            insights: List of insights
            flows: Money flow paths
            clusters: Risk clusters
            
        Returns:
            str: Path to generated HTML dashboard
            
        Raises:
            Exception: If dashboard creation fails
        """
        try:
            self.logger.info("Creating interactive investigation dashboard")
            
            # Generate dashboard HTML
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            dashboard_path = f"investigation_dashboard_{timestamp}.html"
            
            html_content = self._generate_dashboard_html(
                entities, links, insights, flows, clusters
            )
            
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Investigation dashboard created: {dashboard_path}")
            return dashboard_path
            
        except Exception as e:
            self.logger.error(f"Dashboard creation failed: {e}")
            raise

    def export_enhanced_investigation_report(self, filename: str, entities: List, links: List,
                                          insights: List[InvestigativeInsight],
                                          flows: List[MoneyFlowPath] = None,
                                          clusters: List[RiskCluster] = None) -> str:
        """
        Export a comprehensive investigation report with all enhanced features.
        
        Args:
            filename: Base filename for report
            entities: List of entities
            links: List of links
            insights: List of insights
            flows: Money flow paths
            clusters: Risk clusters
            
        Returns:
            str: Path to generated report
            
        Raises:
            Exception: If report export fails
        """
        try:
            self.logger.info("Exporting enhanced investigation report")
            
            report_path = f"{filename}_enhanced_investigation_report.txt"
            
            with open(report_path, 'w', encoding='utf-8') as f:
                # Header
                f.write("=" * 100 + "\n")
                f.write("ENHANCED CRYPTOCURRENCY INVESTIGATION REPORT\n")
                f.write("=" * 100 + "\n\n")
                
                f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Analysis Tool: Crypto Address Extractor - Enhanced Features\n")
                f.write(f"Total Entities Analyzed: {len(entities)}\n")
                f.write(f"Total Relationships: {len(links)}\n\n")
                
                # Executive Summary
                f.write("EXECUTIVE SUMMARY\n")
                f.write("-" * 50 + "\n")
                
                critical_insights = [i for i in insights if i.severity == 'CRITICAL']
                high_insights = [i for i in insights if i.severity == 'HIGH']
                
                if critical_insights:
                    f.write(f"🚨 CRITICAL FINDINGS: {len(critical_insights)} critical issues require immediate attention\n")
                if high_insights:
                    f.write(f"⚠️  HIGH PRIORITY: {len(high_insights)} high-priority issues identified\n")
                
                total_value = sum(float(e.attributes.get('BalanceUSD', 0)) for e in entities if hasattr(e, 'attributes'))
                f.write(f"💰 TOTAL VALUE ANALYZED: ${total_value:,.2f}\n")
                
                darknet_count = len([e for e in entities if hasattr(e, 'attributes') and e.attributes.get('DarknetExposure') == 'YES'])
                if darknet_count > 0:
                    f.write(f"🕵️  DARKNET EXPOSURE: {darknet_count} addresses with darknet market connections\n")
                
                f.write("\n")
                
                # Key Insights
                f.write("KEY INVESTIGATIVE INSIGHTS\n")
                f.write("-" * 50 + "\n")
                
                for i, insight in enumerate(insights[:10], 1):  # Top 10 insights
                    f.write(f"\n{i}. {insight.title} [{insight.severity}]\n")
                    f.write(f"   {insight.description}\n")
                    f.write(f"   Entities Involved: {len(insight.entities)}\n")
                    f.write(f"   Confidence: {insight.confidence:.0%}\n")
                    
                    if insight.recommendations:
                        f.write("   Recommendations:\n")
                        for rec in insight.recommendations[:3]:  # Top 3 recommendations
                            f.write(f"   • {rec}\n")
                
                # Risk Clusters
                if clusters:
                    f.write(f"\nRISK CLUSTER ANALYSIS\n")
                    f.write("-" * 50 + "\n")
                    
                    for cluster in clusters[:5]:  # Top 5 clusters
                        f.write(f"\nCluster: {cluster.cluster_name}\n")
                        f.write(f"Risk Level: {cluster.risk_level}\n")
                        f.write(f"Entities: {len(cluster.entities)}\n")
                        f.write(f"Risk Factors: {', '.join(cluster.risk_factors)}\n")
                
                # Money Flow Analysis
                if flows:
                    f.write(f"\nMONEY FLOW ANALYSIS\n")
                    f.write("-" * 50 + "\n")
                    
                    high_risk_flows = [f for f in flows if f.risk_score >= 0.7]
                    f.write(f"High-Risk Flows Identified: {len(high_risk_flows)}\n")
                    
                    for flow in high_risk_flows[:5]:  # Top 5 flows
                        f.write(f"\nFlow: {flow.path_id}\n")
                        f.write(f"Pattern: {flow.flow_pattern}\n")
                        f.write(f"Value: ${flow.total_value:,.2f}\n")
                        f.write(f"Risk Score: {flow.risk_score:.2f}\n")
                        f.write(f"Transactions: {flow.transaction_count}\n")
                
                # Investigation Priorities
                f.write(f"\nINVESTIGATION PRIORITIES\n")
                f.write("-" * 50 + "\n")
                
                priority_entities = sorted(
                    [e for e in entities if hasattr(e, 'risk_score')],
                    key=lambda x: x.risk_score,
                    reverse=True
                )[:10]
                
                f.write("Top 10 Priority Entities for Investigation:\n\n")
                for i, entity in enumerate(priority_entities, 1):
                    balance = entity.attributes.get('BalanceUSD', 0) if hasattr(entity, 'attributes') else 0
                    f.write(f"{i:2d}. {entity.label}\n")
                    f.write(f"     Risk Score: {entity.risk_score:.3f}\n")
                    f.write(f"     Balance: ${float(balance):,.2f}\n")
                    if hasattr(entity, 'attributes') and entity.attributes.get('DarknetExposure') == 'YES':
                        f.write("     🚨 DARKNET EXPOSURE\n")
                    f.write("\n")
                
                # Technical Details
                f.write("TECHNICAL ANALYSIS DETAILS\n")
                f.write("-" * 50 + "\n")
                
                # Entity type distribution
                entity_types = Counter(e.entity_type for e in entities)
                f.write("Entity Type Distribution:\n")
                for entity_type, count in entity_types.items():
                    f.write(f"  {entity_type}: {count}\n")
                
                # Risk distribution
                risk_levels = Counter(
                    getattr(e, 'attributes', {}).get('RiskLevel', 'UNKNOWN') 
                    for e in entities 
                    if hasattr(e, 'attributes')
                )
                f.write(f"\nRisk Level Distribution:\n")
                for risk_level, count in risk_levels.items():
                    f.write(f"  {risk_level}: {count}\n")
                
                # Footer
                f.write("\n" + "=" * 100 + "\n")
                f.write("END OF ENHANCED INVESTIGATION REPORT\n")
                f.write("=" * 100 + "\n")
            
            self.logger.info(f"Enhanced investigation report exported: {report_path}")
            return report_path
            
        except Exception as e:
            self.logger.error(f"Report export failed: {e}")
            raise

    # Helper methods for enhanced features
    
    def _trace_money_flows(self, start_entity: str, transaction_graph: Dict, 
                          max_depth: int = 5, current_path: List = None) -> List[MoneyFlowPath]:
        """Helper method to trace money flow paths."""
        if current_path is None:
            current_path = [start_entity]
        
        flows = []
        
        if len(current_path) >= max_depth:
            return flows
        
        for connection in transaction_graph.get(start_entity, []):
            if connection['to'] not in current_path:  # Avoid cycles
                new_path = current_path + [connection['to']]
                
                # Create flow if path is significant
                if len(new_path) >= 2:
                    flow = MoneyFlowPath(
                        path_id=f"flow_{'_'.join(new_path[:3])}",
                        source_entity=new_path[0],
                        destination_entity=new_path[-1],
                        intermediate_entities=new_path[1:-1],
                        total_value=self._estimate_flow_value(connection),
                        transaction_count=1,
                        risk_score=self._calculate_flow_risk(new_path, connection),
                        flow_pattern='direct' if len(new_path) == 2 else 'layered'
                    )
                    flows.append(flow)
                
                # Continue tracing
                flows.extend(self._trace_money_flows(
                    connection['to'], transaction_graph, max_depth, new_path
                ))
        
        return flows
    
    def _estimate_flow_value(self, connection: Dict) -> float:
        """Estimate the value of a transaction flow."""
        # This would be enhanced with actual transaction data
        return float(connection.get('attributes', {}).get('value', 1000))
    
    def _calculate_flow_risk(self, path: List[str], connection: Dict) -> float:
        """Calculate risk score for a money flow path."""
        risk_score = 0.5  # Base risk
        
        # Increase risk for longer paths (layering)
        if len(path) > 3:
            risk_score += 0.2
        
        # Increase risk for certain connection types
        if connection.get('type') == 'UsesService':
            risk_score += 0.1
        
        return min(risk_score, 1.0)
    
    def _extract_common_attributes(self, entities: List) -> Dict[str, Any]:
        """Extract common attributes from a group of entities."""
        common_attrs = {}
        
        if not entities:
            return common_attrs
        
        # Find attributes that are common to most entities
        all_attrs = defaultdict(list)
        for entity in entities:
            if hasattr(entity, 'attributes'):
                for key, value in entity.attributes.items():
                    all_attrs[key].append(value)
        
        # Keep attributes that appear in at least 50% of entities
        threshold = len(entities) * 0.5
        for attr_name, values in all_attrs.items():
            value_counts = Counter(values)
            most_common_value, count = value_counts.most_common(1)[0]
            if count >= threshold:
                common_attrs[attr_name] = most_common_value
        
        return common_attrs
    
    def _identify_cluster_risk_factors(self, entities: List, cluster_key: str) -> List[str]:
        """Identify risk factors for a cluster."""
        risk_factors = []
        
        # Check for high-risk attributes
        for entity in entities:
            if hasattr(entity, 'attributes'):
                attrs = entity.attributes
                
                if attrs.get('DarknetExposure') == 'YES':
                    risk_factors.append('Darknet market exposure')
                
                if float(attrs.get('BalanceUSD', 0)) > 50000:
                    risk_factors.append('High value holdings')
                
                if int(attrs.get('TransactionCount', 0)) > 500:
                    risk_factors.append('High transaction frequency')
        
        # Add cluster-specific factors
        if 'darknet' in cluster_key:
            risk_factors.append('Darknet market connections')
        elif 'exchange' in cluster_key:
            risk_factors.append('Common exchange usage pattern')
        elif 'geo' in cluster_key:
            risk_factors.append('Geographic clustering')
        
        return list(set(risk_factors))  # Remove duplicates
    
    def _detect_suspicious_exchange_patterns(self, entities: List, links: List) -> List[Dict]:
        """Detect suspicious exchange usage patterns."""
        patterns = []
        
        # This would be enhanced with more sophisticated pattern detection
        # For now, return basic patterns based on exchange exposure
        
        for entity in entities:
            if hasattr(entity, 'attributes') and 'ExchangeExposure' in entity.attributes:
                exposure = entity.attributes['ExchangeExposure']
                
                # Look for rapid deposit/withdrawal patterns (high percentages)
                if any(float(exp.split(':')[1].strip().rstrip('%')) > 80 for exp in exposure.split(';')):
                    patterns.append({
                        'entity_id': entity.entity_id,
                        'pattern_type': 'high_concentration',
                        'exchange': exposure.split(':')[0].strip(),
                        'description': 'High concentration of activity on single exchange'
                    })
        
        return patterns
    
    def _generate_dashboard_html(self, entities: List, links: List, 
                               insights: List[InvestigativeInsight],
                               flows: List[MoneyFlowPath] = None,
                               clusters: List[RiskCluster] = None) -> str:
        """Generate HTML dashboard content."""
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cryptocurrency Investigation Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .dashboard {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 20px; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #3498db; }}
        .insights {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .insight {{ margin-bottom: 15px; padding: 15px; border-left: 4px solid #e74c3c; background-color: #fdf2f2; }}
        .insight.high {{ border-left-color: #f39c12; background-color: #fef9e7; }}
        .insight.medium {{ border-left-color: #f1c40f; background-color: #fcf8e3; }}
        .insight.low {{ border-left-color: #27ae60; background-color: #eafaf1; }}
        .clusters {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .cluster {{ margin-bottom: 10px; padding: 10px; background-color: #ecf0f1; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🔍 Cryptocurrency Investigation Dashboard</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{len(entities)}</div>
                <div>Total Entities</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(links)}</div>
                <div>Relationships</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len([i for i in insights if i.severity == 'CRITICAL'])}</div>
                <div>Critical Issues</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len([e for e in entities if hasattr(e, 'attributes') and e.attributes.get('DarknetExposure') == 'YES'])}</div>
                <div>Darknet Exposed</div>
            </div>
        </div>
        
        <div class="insights">
            <h2>🚨 Key Investigative Insights</h2>
            {''.join(f'<div class="insight {insight.severity.lower()}"><strong>{insight.title}</strong><br>{insight.description}</div>' for insight in insights[:10])}
        </div>
        
        {f'''
        <div class="clusters">
            <h2>🎯 Risk Clusters</h2>
            {''.join(f'<div class="cluster"><strong>{cluster.cluster_name}</strong> - {cluster.risk_level} Risk<br>Entities: {len(cluster.entities)} | Factors: {", ".join(cluster.risk_factors)}</div>' for cluster in clusters[:5])}
        </div>
        ''' if clusters else ''}
        
    </div>
</body>
</html>
"""
        return html_template


def main():
    """
    Example usage of enhanced features.
    
    This shows how to use the enhanced features with your existing i2_exporter.py
    """
    try:
        print("i2 Enhanced Features Demo")
        print("=" * 50)
        
        # Initialize enhanced features
        enhanced = i2EnhancedFeatures()
        
        print("✅ Enhanced features initialized")
        print("\nKey capabilities added:")
        print("- Money flow analysis")
        print("- Risk cluster detection") 
        print("- Investigative insights generation")
        print("- Interactive dashboards")
        print("- Enhanced investigation reports")
        
        print("\nTo use with your i2_exporter.py:")
        print("1. Import this module: from i2_enhanced_features import i2EnhancedFeatures")
        print("2. Create instance: enhanced = i2EnhancedFeatures(your_exporter)")
        print("3. Analyze data: insights = enhanced.generate_investigative_insights(entities, links)")
        print("4. Create dashboard: enhanced.create_investigation_dashboard(...)")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())