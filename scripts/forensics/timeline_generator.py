#!/usr/bin/env python3
"""
Forensic Timeline Generator
Creates a chronological timeline of events from multiple log sources.
"""

from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Tuple

class TimelineGenerator:
    def __init__(self):
        self.events = []
        
    def parse_firewall_log(self, log_file: str):
        """Parse firewall log entries."""
        with open(log_file, 'r') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                    
                parts = line.strip().split(' | ')
                if len(parts) >= 6:
                    timestamp = datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S')
                    self.events.append({
                        'timestamp': timestamp,
                        'source': 'Firewall',
                        'type': 'Network',
                        'description': f"Connection from {parts[1]} to {parts[2]}:{parts[3]} ({parts[4]}) - {parts[5]}",
                        'severity': parts[6] if len(parts) > 6 else 'INFO',
                        'raw': line.strip()
                    })
    
    def parse_system_log(self, log_file: str):
        """Parse system event log entries."""
        with open(log_file, 'r') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                    
                parts = line.strip().split(' | ')
                if len(parts) >= 6:
                    timestamp = datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S')
                    self.events.append({
                        'timestamp': timestamp,
                        'source': 'System',
                        'type': 'Endpoint',
                        'description': f"[{parts[1]}] {parts[5]}",
                        'severity': self._determine_severity(parts[5]),
                        'raw': line.strip()
                    })
    
    def parse_process_log(self, log_file: str):
        """Parse process execution log entries."""
        with open(log_file, 'r') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                    
                parts = line.strip().split(' | ')
                if len(parts) >= 6:
                    timestamp = datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S')
                    process_name = parts[3]
                    command = parts[4] if len(parts) > 4 else ''
                    
                    self.events.append({
                        'timestamp': timestamp,
                        'source': 'Process',
                        'type': 'Endpoint',
                        'description': f"Process executed: {process_name} - {command[:100]}",
                        'severity': self._determine_process_severity(process_name, command),
                        'raw': line.strip()
                    })
    
    def parse_file_access_log(self, log_file: str):
        """Parse file access log entries."""
        with open(log_file, 'r') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                    
                parts = line.strip().split(' | ')
                if len(parts) >= 5:
                    timestamp = datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S')
                    file_path = parts[3]
                    
                    self.events.append({
                        'timestamp': timestamp,
                        'source': 'FileAccess',
                        'type': 'Endpoint',
                        'description': f"{parts[2]} operation on {file_path}",
                        'severity': self._determine_file_severity(file_path),
                        'raw': line.strip()
                    })
    
    def _determine_severity(self, description: str) -> str:
        """Determine severity based on event description."""
        critical_keywords = ['Audit log cleared', 'SAM', 'privileges assigned', 'service stopped']
        high_keywords = ['network share', 'logon', 'administrator']
        
        if any(keyword in description for keyword in critical_keywords):
            return 'CRITICAL'
        elif any(keyword in description for keyword in high_keywords):
            return 'HIGH'
        return 'MEDIUM'
    
    def _determine_process_severity(self, process: str, command: str) -> str:
        """Determine severity based on process and command."""
        if 'payload.exe' in process or 'payload.exe' in command:
            return 'CRITICAL'
        if any(cmd in command.lower() for cmd in ['net use', 'net localgroup', 'reg add', 'reg export']):
            return 'HIGH'
        if 'powershell' in process.lower() and 'bypass' in command.lower():
            return 'HIGH'
        return 'MEDIUM'
    
    def _determine_file_severity(self, file_path: str) -> str:
        """Determine severity based on file path."""
        critical_paths = ['sam', 'system', 'passwords', 'credentials']
        high_paths = ['svchost.exe', 'drivers', 'config']
        
        if any(path in file_path.lower() for path in critical_paths):
            return 'CRITICAL'
        elif any(path in file_path.lower() for path in high_paths):
            return 'HIGH'
        return 'MEDIUM'
    
    def generate_timeline(self) -> str:
        """Generate chronological timeline of events."""
        # Sort events by timestamp
        sorted_events = sorted(self.events, key=lambda x: x['timestamp'])
        
        timeline = []
        timeline.append("=" * 80)
        timeline.append("INCIDENT RESPONSE TIMELINE")
        timeline.append("=" * 80)
        timeline.append("")
        
        current_date = None
        for event in sorted_events:
            event_date = event['timestamp'].date()
            if current_date != event_date:
                current_date = event_date
                timeline.append(f"\n{'='*80}")
                timeline.append(f"DATE: {current_date}")
                timeline.append(f"{'='*80}\n")
            
            timeline.append(f"[{event['timestamp'].strftime('%H:%M:%S')}] [{event['severity']}] [{event['source']}]")
            timeline.append(f"  {event['description']}")
            timeline.append("")
        
        timeline.append("=" * 80)
        timeline.append(f"Total Events: {len(sorted_events)}")
        timeline.append("=" * 80)
        
        return "\n".join(timeline)
    
    def generate_summary_by_phase(self) -> str:
        """Generate summary organized by incident response phases."""
        sorted_events = sorted(self.events, key=lambda x: x['timestamp'])
        
        # Categorize events by phase
        phases = {
            'Detection': [],
            'Containment': [],
            'Remediation': [],
            'Recovery': []
        }
        
        # Simple heuristic: first events are detection, critical events indicate containment/remediation
        detection_end = None
        for i, event in enumerate(sorted_events):
            if i < len(sorted_events) * 0.3:  # First 30% are detection
                phases['Detection'].append(event)
            elif event['severity'] in ['CRITICAL', 'HIGH']:
                if not detection_end:
                    detection_end = event['timestamp']
                if 'BLOCKED' in event['description'] or 'containment' in event['description'].lower():
                    phases['Containment'].append(event)
                elif 'delete' in event['description'].lower() or 'remove' in event['description'].lower():
                    phases['Remediation'].append(event)
                else:
                    phases['Containment'].append(event)
            else:
                phases['Recovery'].append(event)
        
        summary = []
        summary.append("=" * 80)
        summary.append("INCIDENT RESPONSE PHASES SUMMARY")
        summary.append("=" * 80)
        summary.append("")
        
        for phase, events in phases.items():
            summary.append(f"\n{phase.upper()} PHASE ({len(events)} events)")
            summary.append("-" * 80)
            for event in events[:10]:  # Show first 10 events per phase
                summary.append(f"  [{event['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}] {event['description'][:70]}")
            if len(events) > 10:
                summary.append(f"  ... and {len(events) - 10} more events")
        
        return "\n".join(summary)


def main():
    generator = TimelineGenerator()
    
    print("Parsing log files...")
    generator.parse_firewall_log('../../logs/network/firewall.log')
    generator.parse_system_log('../../logs/endpoint/system.log')
    generator.parse_process_log('../../logs/endpoint/process.log')
    generator.parse_file_access_log('../../logs/endpoint/file_access.log')
    
    print("Generating timeline...")
    timeline = generator.generate_timeline()
    
    print("Generating phase summary...")
    phase_summary = generator.generate_summary_by_phase()
    
    # Save timeline
    with open('../../reports/incident_timeline.txt', 'w') as f:
        f.write(timeline)
        f.write("\n\n")
        f.write(phase_summary)
    
    print("Timeline generated successfully!")
    print(f"Total events processed: {len(generator.events)}")


if __name__ == '__main__':
    main()

