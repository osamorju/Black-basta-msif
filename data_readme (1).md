# Data Directory Structure

This directory contains datasets used in the MSIF framework research. Due to the sensitive nature of cybersecurity data, access is controlled through a three-tier system.

## Directory Structure

```
data/
├── raw/                    # Raw data from various sources
│   ├── sample_data/        # Sample datasets for testing
│   └── .gitkeep
├── processed/             # Cleaned and processed data
│   ├── features/          # Extracted features
│   └── .gitkeep
├── anonymized/            # Anonymized datasets (k-anonymity, differential privacy)
├── synthetic/             # Synthetic datasets for public use
├── honeypots/             # Honeypot logs and captured data
└── malware_samples/       # Malware samples (access restricted)
```

## Data Access Tiers

### Tier 1: Public Access (No Registration Required)

**Location:** `data/synthetic/`

**Contents:**
- Synthetic datasets generated using differential privacy (ε=1.0, δ=1e-5)
- Sample feature vectors for algorithm testing
- Anonymized statistical summaries
- Validation datasets for replication studies

**Files:**
- `synthetic_incidents.csv` - Synthetic incident data
- `validation_dataset.csv` - Cross-validation synthetic data
- `feature_examples.json` - Example feature vectors
- `statistical_summaries.json` - Aggregate statistics

### Tier 2: Academic Access (Registration Required)

**Location:** `data/anonymized/`

**Access:** Submit request through jude-osamor/black-basta-msif/issues using "Data Access Request" template

**Requirements:**
- Valid academic email address
- Description of intended research use
- Agreement to data use terms

**Contents:**
- Anonymized incident characteristics (k=5 anonymity)
- Network traffic features with PII removed
- Behavioral patterns and signatures
- Cross-validation datasets with temporal splits

**Files:**
- `incident_data_anonymized.csv` - Anonymized incident records
- `network_features_anonymized.csv` - Network-based features
- `behavioral_patterns_anonymized.json` - Malware behavior data
- `victim_interviews_anonymized.json` - Interview summaries

### Tier 3: Controlled Access (Data Sharing Agreement Required)

**Location:** Not publicly available

**Access:** Email jude.osamor@ieee.org with formal request

**Requirements:**
- Institutional affiliation verification
- IRB approval for human subjects research
- Signed data sharing agreement
- Demonstration of adequate security measures

**Contents:**
- Enhanced anonymized datasets with additional features
- Longitudinal data with temporal relationships
- Industry collaboration validation data
- Raw honeypot logs (anonymized)

## Data Formats

### CSV Files
Standard comma-separated values with headers:
- UTF-8 encoding
- RFC 4180 compliant
- Missing values as empty strings or "NaN"

### JSON Files
- UTF-8 encoding
- Nested structure for complex data
- ISO 8601 timestamps
- Standardized field names

### Sample Data Schema

#### Incident Records
```csv
incident_id,date,industry,org_size,attack_vector,prevention_success,direct_cost,indirect_cost
INC001,2023-01-15,manufacturing,large,phishing,false,2400000,3600000
```

#### Network Features
```csv
flow_id,src_ip_anon,dst_port,protocol,packets,bytes,duration,flags
FL001,192.168.XXX.XXX,443,TCP,247,15680,1.23,SYN-ACK
```

#### Behavioral Patterns
```json
{
  "sample_id": "MAL001",
  "family": "black_basta",
  "file_operations": ["encrypt", "delete_shadow_copies"],
  "network_activity": ["c2_communication", "data_exfiltration"],
  "registry_modifications": 15,
  "process_injections": 3
}
```

## Data Quality Metrics

All datasets include quality metrics:
- **Completeness:** Percentage of non-null values
- **Accuracy:** Validation against ground truth
- **Consistency:** Inter-source agreement rates
- **Timeliness:** Data freshness indicators

## Ethical Considerations

### Data Anonymization
- **Direct identifiers:** Completely removed
- **Quasi-identifiers:** Generalized or suppressed
- **K-anonymity:** Minimum group size of 5
- **Differential privacy:** Added noise with ε=1.0

### Privacy Protection
- No personally identifiable information (PII)
- Organization names replaced with anonymized IDs
- IP addresses masked or anonymized
- Geographic data generalized to country/region level

### Legal Compliance
- GDPR compliant data processing
- IRB approval for human subjects research
- Informed consent from all participants
- Right to withdrawal honored

## Data Usage Guidelines

### Academic Research
- Cite original research paper
- Acknowledge data sources appropriately
- Share derived insights with research community
- Follow responsible disclosure for security findings

### Commercial Use
- Contact authors for licensing terms
- Respect intellectual property rights
- Consider ethical implications of commercial applications
- Contribute improvements back to community

### Prohibited Uses
- Re-identification of anonymized individuals/organizations
- Malicious purposes or illegal activities
- Violation of data sharing agreement terms
- Distribution without proper authorization

## Technical Support

### File Format Issues
- Check encoding (should be UTF-8)
- Verify CSV delimiter (comma)
- Validate JSON syntax

### Access Issues
- Verify your access tier permissions
- Check data sharing agreement status
- Contact administrators for technical problems

### Data Quality Questions
- Review data quality metrics in metadata
- Check data collection methodology documentation
- Report suspected data quality issues

## Contact Information

- **Data Access Requests:** Use GitHub Issues with "Data Access Request" label
- **Technical Support:** GitHub Issues with "Technical Support" label  
- **Research Collaboration:** jude.osamor@ieee.org
- **Ethics Questions:** ethics@uwe.ac.uk

## Version History

- **v1.0.0** (2025-01-15): Initial data release
- **v1.0.1** (2025-01-22): Added synthetic datasets
- **v1.0.2** (2025-01-29): Enhanced anonymization

## Acknowledgments

- University of the West of England Research Ethics Committee
- Industry partners (anonymized per agreements)
- Cybersecurity research community contributors
- Open source threat intelligence providers
