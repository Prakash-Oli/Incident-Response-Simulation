#!/usr/bin/env python3
"""
Evidence Extractor
Extracts and correlates evidence from multiple log sources for forensic analysis.
"""

import json
from datetime import datetime
from collections import defaultdict
from typing import Dict, List

class EvidenceExtractor:
    def __init__(self):
        self.evidence = {
            'compromised_hosts': set(),
            'malicious_ips': set(),
            'malicious_domains': set(),
            'suspicious_processes': [],
            'file_artifacts': [],
            'network_connections': [],
            'indicators_of_compromise': []
        }
    
    def extract_network_indicators(self, log_files: Dict[str, str]):
        """Extract network-based indicators of compromise."""
        # Extract from firewall logs
        if 'firewall' in log_files:
            with open(log_files['firewall'], 'r') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    parts = line.strip().split(' | ')
                    if len(parts) >= 3:
                        src_ip = parts[1]
                        dst_ip = parts[2]
                        port = parts[3]
                        
                        if port in ['4444', '5555', '6666']:
                            self.evidence['malicious_ips'].add(dst_ip)
                            self.evidence['compromised_hosts'].add(src_ip)
                            self.evidence['network_connections'].append({
                                'type': 'Suspicious Port',
                                'source': src_ip,
                                'destination': dst_ip,
                                'port': port,
                                'indicator': f'Connection to non-standard port {port}'
                            })
        
        # Extract from DNS logs
        if 'dns' in log_files:
            with open(log_files['dns'], 'r') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    parts = line.strip().split(' | ')
                    if len(parts) >= 4:
                        domain = parts[3]
                        if any(keyword in domain.lower() for keyword in ['malicious', 'c2-server', 'fake']):
                            self.evidence['malicious_domains'].add(domain)
                            self.evidence['indicators_of_compromise'].append({
                                'type': 'DNS',
                                'indicator': f'Suspicious domain query: {domain}',
                                'severity': 'HIGH'
                            })
        
        # Extract from HTTP proxy logs
        if 'http_proxy' in log_files:
            with open(log_files['http_proxy'], 'r') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    parts = line.strip().split(' | ')
                    if len(parts) >= 3:
                        url = parts[3]
                        if '.exe' in url.lower() or 'malicious' in url.lower():
                            self.evidence['indicators_of_compromise'].append({
                                'type': 'HTTP',
                                'indicator': f'Malicious file download: {url}',
                                'severity': 'CRITICAL'
                            })
    
    def extract_endpoint_indicators(self, log_files: Dict[str, str]):
        """Extract endpoint-based indicators of compromise."""
        # Extract from process logs
        if 'process' in log_files:
            with open(log_files['process'], 'r') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    parts = line.strip().split(' | ')
                    if len(parts) >= 4:
                        process = parts[3]
                        command = parts[4] if len(parts) > 4 else ''
                        
                        if 'payload.exe' in process or 'payload.exe' in command:
                            self.evidence['suspicious_processes'].append({
                                'process': process,
                                'command': command,
                                'severity': 'CRITICAL',
                                'indicator': 'Malicious payload execution'
                            })
                        
                        if any(cmd in command.lower() for cmd in ['net use', 'reg add', 'net localgroup']):
                            self.evidence['indicators_of_compromise'].append({
                                'type': 'Process',
                                'indicator': f'Suspicious command execution: {command[:100]}',
                                'severity': 'HIGH'
                            })
        
        # Extract from file access logs
        if 'file_access' in log_files:
            with open(log_files['file_access'], 'r') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    parts = line.strip().split(' | ')
                    if len(parts) >= 4:
                        file_path = parts[3]
                        action = parts[2]
                        
                        if any(path in file_path.lower() for path in ['sam', 'system', 'passwords', 'credentials']):
                            self.evidence['file_artifacts'].append({
                                'file': file_path,
                                'action': action,
                                'severity': 'CRITICAL',
                                'indicator': 'Access to sensitive system files'
                            })
        
        # Extract from system logs
        if 'system' in log_files:
            with open(log_files['system'], 'r') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    parts = line.strip().split(' | ')
                    if len(parts) >= 6:
                        description = parts[5]
                        
                        if 'Audit log cleared' in description:
                            self.evidence['indicators_of_compromise'].append({
                                'type': 'System',
                                'indicator': 'Audit log cleared - evidence tampering',
                                'severity': 'CRITICAL'
                            })
    
    def generate_evidence_package(self) -> Dict:
        """Generate comprehensive evidence package."""
        return {
            'extraction_timestamp': datetime.now().isoformat(),
            'compromised_hosts': list(self.evidence['compromised_hosts']),
            'malicious_ips': list(self.evidence['malicious_ips']),
            'malicious_domains': list(self.evidence['malicious_domains']),
            'suspicious_processes': self.evidence['suspicious_processes'],
            'file_artifacts': self.evidence['file_artifacts'],
            'network_connections': self.evidence['network_connections'],
            'indicators_of_compromise': self.evidence['indicators_of_compromise'],
            'summary': {
                'total_iocs': len(self.evidence['indicators_of_compromise']),
                'compromised_host_count': len(self.evidence['compromised_hosts']),
                'malicious_ip_count': len(self.evidence['malicious_ips']),
                'malicious_domain_count': len(self.evidence['malicious_domains'])
            }
        }
    
    def generate_evidence_report(self) -> str:
        """Generate human-readable evidence report."""
        report = []
        report.append("=" * 80)
        report.append("FORENSIC EVIDENCE PACKAGE")
        report.append("=" * 80)
        report.append(f"Extraction Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        report.append("\nCOMPROMISED HOSTS")
        report.append("-" * 80)
        for host in self.evidence['compromised_hosts']:
            report.append(f"  - {host}")
        
        report.append("\nMALICIOUS IP ADDRESSES")
        report.append("-" * 80)
        for ip in self.evidence['malicious_ips']:
            report.append(f"  - {ip}")
        
        report.append("\nMALICIOUS DOMAINS")
        report.append("-" * 80)
        for domain in self.evidence['malicious_domains']:
            report.append(f"  - {domain}")
        
        report.append("\nSUSPICIOUS PROCESSES")
        report.append("-" * 80)
        for proc in self.evidence['suspicious_processes']:
            report.append(f"  - [{proc['severity']}] {proc['process']}")
            report.append(f"    Command: {proc['command'][:80]}")
        
        report.append("\nFILE ARTIFACTS")
        report.append("-" * 80)
        for artifact in self.evidence['file_artifacts']:
            report.append(f"  - [{artifact['severity']}] {artifact['action']} on {artifact['file']}")
        
        report.append("\nINDICATORS OF COMPROMISE (IoCs)")
        report.append("-" * 80)
        for ioc in self.evidence['indicators_of_compromise']:
            report.append(f"  - [{ioc['severity']}] [{ioc['type']}] {ioc['indicator']}")
        
        report.append("\n" + "=" * 80)
        report.append("SUMMARY")
        report.append("-" * 80)
        report.append(f"Total IoCs: {len(self.evidence['indicators_of_compromise'])}")
        report.append(f"Compromised Hosts: {len(self.evidence['compromised_hosts'])}")
        report.append(f"Malicious IPs: {len(self.evidence['malicious_ips'])}")
        report.append(f"Malicious Domains: {len(self.evidence['malicious_domains'])}")
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    extractor = EvidenceExtractor()
    
    log_files = {
        'firewall': '../../logs/network/firewall.log',
        'dns': '../../logs/network/dns.log',
        'http_proxy': '../../logs/network/http_proxy.log',
        'process': '../../logs/endpoint/process.log',
        'file_access': '../../logs/endpoint/file_access.log',
        'system': '../../logs/endpoint/system.log'
    }
    
    print("Extracting network indicators...")
    extractor.extract_network_indicators(log_files)
    
    print("Extracting endpoint indicators...")
    extractor.extract_endpoint_indicators(log_files)
    
    print("Generating evidence package...")
    evidence_package = extractor.generate_evidence_package()
    
    # Save JSON evidence package
    with open('../../evidence/evidence_package.json', 'w') as f:
        json.dump(evidence_package, f, indent=2)
    
    # Generate and save report
    report = extractor.generate_evidence_report()
    with open('../../reports/evidence_report.txt', 'w') as f:
        f.write(report)
    
    print("Evidence extraction completed!")
    print(f"Total IoCs extracted: {len(extractor.evidence['indicators_of_compromise'])}")


if __name__ == '__main__':
    main()

