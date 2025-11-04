#!/usr/bin/env python3
"""
Network Log Analyzer
Analyzes network logs to detect suspicious activity and security incidents.
"""

import re
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple

class LogAnalyzer:
    def __init__(self):
        self.suspicious_ips = set()
        self.suspicious_domains = set()
        self.alert_summary = []
        
    def analyze_firewall_log(self, log_file: str) -> Dict:
        """Analyze firewall logs for suspicious activity."""
        findings = {
            'critical_ports': [],
            'blocked_attempts': [],
            'suspicious_ips': set(),
            'port_scan_patterns': []
        }
        
        with open(log_file, 'r') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                    
                parts = line.strip().split(' | ')
                if len(parts) >= 6:
                    timestamp = parts[0]
                    src_ip = parts[1]
                    dst_ip = parts[2]
                    port = parts[3]
                    protocol = parts[4]
                    action = parts[5]
                    severity = parts[6] if len(parts) > 6 else 'INFO'
                    
                    # Detect suspicious ports
                    if port in ['4444', '5555', '6666', '12345']:
                        findings['critical_ports'].append({
                            'timestamp': timestamp,
                            'src_ip': src_ip,
                            'dst_ip': dst_ip,
                            'port': port,
                            'severity': severity
                        })
                        self.suspicious_ips.add(dst_ip)
                    
                    # Track blocked attempts
                    if action == 'BLOCKED':
                        findings['blocked_attempts'].append({
                            'timestamp': timestamp,
                            'src_ip': src_ip,
                            'dst_ip': dst_ip,
                            'port': port
                        })
        
        return findings
    
    def analyze_dns_log(self, log_file: str) -> Dict:
        """Analyze DNS logs for suspicious domain queries."""
        findings = {
            'suspicious_domains': [],
            'c2_indicators': [],
            'domain_frequency': defaultdict(int)
        }
        
        suspicious_keywords = ['malicious', 'c2-server', 'update.microsoft-fake', 'download']
        
        with open(log_file, 'r') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                    
                parts = line.strip().split(' | ')
                if len(parts) >= 5:
                    timestamp = parts[0]
                    src_ip = parts[1]
                    domain = parts[3]
                    
                    findings['domain_frequency'][domain] += 1
                    
                    # Detect suspicious domains
                    if any(keyword in domain.lower() for keyword in suspicious_keywords):
                        findings['suspicious_domains'].append({
                            'timestamp': timestamp,
                            'src_ip': src_ip,
                            'domain': domain
                        })
                        self.suspicious_domains.add(domain)
                    
                    # C2 server indicators
                    if 'c2-server' in domain.lower():
                        findings['c2_indicators'].append({
                            'timestamp': timestamp,
                            'src_ip': src_ip,
                            'domain': domain
                        })
        
        return findings
    
    def analyze_http_proxy_log(self, log_file: str) -> Dict:
        """Analyze HTTP proxy logs for suspicious web activity."""
        findings = {
            'malicious_downloads': [],
            'suspicious_user_agents': [],
            'data_exfiltration': []
        }
        
        with open(log_file, 'r') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                    
                parts = line.strip().split(' | ')
                if len(parts) >= 6:
                    timestamp = parts[0]
                    src_ip = parts[1]
                    method = parts[2]
                    url = parts[3]
                    status = parts[4]
                    user_agent = parts[5] if len(parts) > 5 else ''
                    
                    # Detect malicious downloads
                    if '.exe' in url.lower() or '.js' in url.lower():
                        if any(keyword in url.lower() for keyword in ['malicious', 'payload', 'script']):
                            findings['malicious_downloads'].append({
                                'timestamp': timestamp,
                                'src_ip': src_ip,
                                'url': url,
                                'user_agent': user_agent
                            })
                    
                    # Detect suspicious user agents
                    if 'CustomAgent' in user_agent or 'WindowsUpdateAgent' in user_agent:
                        findings['suspicious_user_agents'].append({
                            'timestamp': timestamp,
                            'src_ip': src_ip,
                            'url': url,
                            'user_agent': user_agent
                        })
                    
                    # Detect potential data exfiltration
                    if method == 'POST' and 'c2-server' in url.lower():
                        findings['data_exfiltration'].append({
                            'timestamp': timestamp,
                            'src_ip': src_ip,
                            'url': url
                        })
        
        return findings
    
    def generate_report(self, findings: Dict) -> str:
        """Generate a summary report of findings."""
        report = []
        report.append("=" * 60)
        report.append("LOG ANALYSIS SUMMARY")
        report.append("=" * 60)
        report.append("")
        
        if 'critical_ports' in findings:
            report.append(f"Critical Port Activity: {len(findings['critical_ports'])} events")
            for event in findings['critical_ports'][:5]:
                report.append(f"  - {event['timestamp']}: Port {event['port']} connection to {event['dst_ip']}")
        
        if 'suspicious_domains' in findings:
            report.append(f"\nSuspicious Domain Queries: {len(findings['suspicious_domains'])} events")
            for event in findings['suspicious_domains'][:5]:
                report.append(f"  - {event['timestamp']}: Query for {event['domain']}")
        
        if 'malicious_downloads' in findings:
            report.append(f"\nMalicious Downloads: {len(findings['malicious_downloads'])} events")
            for event in findings['malicious_downloads']:
                report.append(f"  - {event['timestamp']}: Download from {event['url']}")
        
        if 'data_exfiltration' in findings:
            report.append(f"\nPotential Data Exfiltration: {len(findings['data_exfiltration'])} events")
            for event in findings['data_exfiltration']:
                report.append(f"  - {event['timestamp']}: POST to {event['url']}")
        
        report.append("\n" + "=" * 60)
        report.append(f"Suspicious IPs Detected: {len(self.suspicious_ips)}")
        report.append(f"Suspicious Domains Detected: {len(self.suspicious_domains)}")
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    analyzer = LogAnalyzer()
    
    print("Analyzing network logs...")
    
    # Analyze firewall logs
    firewall_findings = analyzer.analyze_firewall_log('../../logs/network/firewall.log')
    
    # Analyze DNS logs
    dns_findings = analyzer.analyze_dns_log('../../logs/network/dns.log')
    
    # Analyze HTTP proxy logs
    http_findings = analyzer.analyze_http_proxy_log('../../logs/network/http_proxy.log')
    
    # Combine findings
    all_findings = {
        **firewall_findings,
        **dns_findings,
        **http_findings
    }
    
    # Generate report
    report = analyzer.generate_report(all_findings)
    print(report)
    
    # Save report
    with open('../../reports/log_analysis_report.txt', 'w') as f:
        f.write(report)


if __name__ == '__main__':
    main()

