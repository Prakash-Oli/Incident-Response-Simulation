# Quick Start Guide

## Getting Started

This guide will help you quickly understand and use the Incident Response Simulation Project.

## Prerequisites

- Python 3.7 or higher
- Text editor or markdown viewer
- Windows PowerShell (for running batch scripts)

## Quick Start (5 minutes)

### 1. Run the Analysis Scripts

**Option A: Using the batch script (Windows)**
```bash
run_analysis.bat
```

**Option B: Manual execution**
```bash
# Log Analysis
cd scripts/analysis
python log_analyzer.py
cd ../..

# Timeline Generation
cd scripts/forensics
python timeline_generator.py
cd ../..

# Evidence Extraction
cd scripts/forensics
python evidence_extractor.py
cd ../..
```

### 2. Review Generated Reports

After running the scripts, check the `reports/` directory:
- `log_analysis_report.txt` - Analysis of network logs
- `incident_timeline.txt` - Chronological timeline of events
- `evidence_report.txt` - Extracted evidence and IoCs
- `evidence_package.json` - Machine-readable evidence

### 3. Read the Documentation

Start with these documents in order:
1. `reports/incident_timeline.md` - What happened and when
2. `reports/incident_report.md` - Complete incident analysis
3. `reports/recommendations.md` - How to prevent similar incidents
4. `playbooks/incident_response_playbook.md` - Response procedures

## Project Structure Overview

```
logs/              → Simulated security logs
├── network/       → Firewall, DNS, HTTP proxy logs
└── endpoint/      → System, process, file access logs

evidence/          → Forensic evidence
├── pcaps/         → Network traffic summaries
└── malware/       → Malware analysis reports

scripts/           → Analysis tools
├── analysis/      → Log analysis scripts
└── forensics/     → Forensic analysis tools

reports/           → Generated reports and documentation
playbooks/         → Incident response procedures
```

## Understanding the Incident

### The Attack Flow

1. **08:15:23** - User accesses legitimate-site.com
2. **08:16:12** - Redirected to malicious site, downloads payload.exe
3. **08:16:20** - Malware executes on endpoint 192.168.1.105
4. **08:17:00** - Establishes C2 communication to 198.51.100.67:4444
5. **08:17:30** - Attempts lateral movement
6. **08:18:00** - Accesses SAM registry (credential theft)
7. **08:23:00** - Begins data exfiltration
8. **08:20:15** - Incident detected and contained

### Key Indicators

- **C2 Server**: 198.51.100.67:4444
- **Malicious Domains**: c2-server.example, malicious-download.net
- **Compromised Host**: 192.168.1.105
- **Malware**: payload.exe

## Learning Path

### Beginner Level
1. Review the incident timeline
2. Understand the attack flow
3. Read the incident report summary
4. Review basic recommendations

### Intermediate Level
1. Run analysis scripts and understand output
2. Review log files manually
3. Study evidence extraction process
4. Understand containment procedures

### Advanced Level
1. Modify analysis scripts
2. Create custom detection rules
3. Extend the timeline generator
4. Develop additional playbooks

## Common Tasks

### Analyzing a Specific Log File

```python
# Example: Analyze firewall logs
from scripts.analysis.log_analyzer import LogAnalyzer

analyzer = LogAnalyzer()
findings = analyzer.analyze_firewall_log('logs/network/firewall.log')
print(analyzer.generate_report(findings))
```

### Generating Custom Timeline

```python
# Example: Generate timeline from specific logs
from scripts.forensics.timeline_generator import TimelineGenerator

generator = TimelineGenerator()
generator.parse_firewall_log('logs/network/firewall.log')
generator.parse_system_log('logs/endpoint/system.log')
timeline = generator.generate_timeline()
print(timeline)
```

### Extracting Specific Evidence

```python
# Example: Extract network indicators
from scripts.forensics.evidence_extractor import EvidenceExtractor

extractor = EvidenceExtractor()
log_files = {
    'firewall': 'logs/network/firewall.log',
    'dns': 'logs/network/dns.log'
}
extractor.extract_network_indicators(log_files)
evidence = extractor.generate_evidence_package()
print(evidence['malicious_ips'])
```

## Troubleshooting

### Scripts Not Running

**Issue**: "ModuleNotFoundError" or import errors
**Solution**: Ensure you're running from the correct directory or use absolute paths

### Reports Not Generated

**Issue**: Reports directory not found
**Solution**: Create the reports directory manually or run from project root

### Path Errors

**Issue**: File not found errors
**Solution**: Check that you're in the correct directory structure. Scripts assume specific relative paths.

## Next Steps

1. **Experiment**: Modify the log files to create different scenarios
2. **Extend**: Add new analysis scripts or tools
3. **Practice**: Use the playbook to practice incident response
4. **Learn**: Study the recommendations and implement security improvements

## Additional Resources

- **MITRE ATT&CK**: https://attack.mitre.org/
- **NIST Cybersecurity Framework**: https://www.nist.gov/cyberframework
- **SANS Incident Response**: https://www.sans.org/reading-room/

## Support

For questions or issues:
1. Review the README.md for detailed documentation
2. Check the script comments for code explanations
3. Review the incident report for methodology details

---

**Happy Learning!**

