# Black Basta Ransomware: Multi-Source Intelligence Framework (MSIF)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

## Overview

This repository contains the complete implementation of the Multi-Source Intelligence Framework (MSIF) for advanced cyber threat analysis and proactive defense against Black Basta ransomware, as described in:

**"Black Basta Ransomware: A Novel Multi-Source Intelligence Framework for Advanced Cyber Threat Analysis and Proactive Defense"**  
*Jude Osamor*  
*University of the West of England, Bristol*  
*2025*

## Key Research Contributions

- **87.4% accuracy** (95% CI: 84.2%-90.6%) in Black Basta attack vector prediction
- **75.3% prevention rate** vs. 24.5% control group (p<0.001) in controlled testing
- **5.2-minute mean response time** with automated threat mitigation
- **Multi-source intelligence** integration across honeypots, malware analysis, and behavioral patterns
- **Reproducible research** environment with complete containerized deployment
- **Ethical compliance** framework with IRB approval and differential privacy

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.8+
- 32GB RAM, 8 CPU cores, 1TB storage (recommended for full deployment)

### Installation
```bash
git clone https://github.com/jude-osamor/black-basta-msif.git
cd black-basta-msif
chmod +x scripts/setup/install_dependencies.sh
./scripts/setup/install_dependencies.sh
docker-compose up -d
```

### Basic Usage
```python
from src.models.ensemble_classifier import MSIFEnsemble
from src.data_processing.feature_engineering import FeatureExtractor

# Load pre-trained model
model = MSIFEnsemble.load_pretrained('models/msif_ensemble.pkl')

# Extract features from network data
extractor = FeatureExtractor()
features = extractor.transform(network_data)

# Predict attack probability
attack_probability = model.predict_proba(features)
confidence_score = model.get_confidence_score(features)

print(f"Attack probability: {attack_probability:.3f}")
print(f"Confidence: {confidence_score:.3f}")
```

## Repository Structure

```
├── src/                    # Core MSIF implementation
├── infrastructure/         # Honeypot and analysis lab configs
├── data/                   # Datasets (see Data Access section)
├── notebooks/             # Analysis and visualization notebooks
├── docs/                  # Documentation and guides
├── tests/                 # Test suites
├── scripts/               # Utility and deployment scripts
├── results/               # Statistical outputs and reports
└── config/                # Configuration files
```

## Performance Metrics

| Component | Accuracy | 95% CI | Precision | Recall | F1-Score |
|-----------|----------|---------|-----------|---------|----------|
| Network Indicators | 84.3% | 81.7-86.9% | 82.1% | 86.8% | 84.4% |
| Temporal Patterns | 81.7% | 78.9-84.5% | 79.4% | 84.3% | 81.8% |
| Target Analysis | 86.9% | 84.5-89.3% | 85.2% | 88.7% | 86.9% |
| **Combined MSIF** | **87.4%** | **84.2-90.6%** | **86.1%** | **88.9%** | **87.5%** |

## Data Access

Due to cybersecurity data sensitivity, we provide tiered access:

### Tier 1: Public Access
- Synthetic datasets (differential privacy ε=1.0)
- Complete source code and documentation
- Sample data for algorithm testing

### Tier 2: Academic Access
- Anonymized feature datasets
- Cross-validation splits
- Enhanced documentation

### Tier 3: Controlled Access
- Full anonymized datasets
- Longitudinal data with temporal relationships
- Industry validation data

**Request Access:** See [docs/data_access.md](docs/data_access.md)

## Key Features

### Multi-Source Intelligence Integration
- **47 distributed honeypots** across 3 geographic regions
- **Reverse engineering lab** with automated malware analysis
- **Network traffic analysis** with real-time pattern detection
- **Victim impact assessment** from 127 documented incidents

### Machine Learning Architecture
- **Ensemble classifier** combining Random Forest, SVM, and LSTM
- **Early detection framework** with 48-72 hour prediction capability
- **Adaptive defense system** with automated response mechanisms
- **Statistical validation** with bootstrap confidence intervals

### Ethical Research Framework
- **IRB Approval:** UWE-REC-2023-0847-CYB
- **Responsible disclosure:** 90-day coordinated vulnerability disclosure
- **Data protection:** Multi-layer anonymization with k-anonymity and differential privacy
- **Legal compliance:** GDPR, Computer Fraud and Abuse Act adherence

## Replication Guide

Complete replication instructions available at [docs/replication/replication_guide.md](docs/replication/replication_guide.md)

**Estimated completion time:** 20-30 hours on recommended hardware  
**Validation criteria:** ±2% accuracy tolerance from published results  
**Hardware requirements:** 32GB RAM, 8 CPU cores, 1TB storage

### Quick Replication
```bash
# 1. Setup environment
./scripts/setup/setup_python_environment.sh

# 2. Download datasets (requires access approval)
./scripts/data_collection/download_datasets.sh --tier=academic

# 3. Run full analysis pipeline
python scripts/analysis/run_full_analysis.py --validate-results

# 4. Generate reports
python scripts/analysis/generate_reports.py --output=results/
```

## Citation

If you use this work, please cite:

```bibtex
@article{osamor2025blackbasta,
  title={Black Basta Ransomware: A Novel Multi-Source Intelligence Framework for Advanced Cyber Threat Analysis and Proactive Defense},
  author={Osamor, Jude},
  journal={[Under Review]},
  year={2025},
  institution={University of the West of England, Bristol},
  url={https://github.com/jude-osamor/black-basta-msif}
}
```

## Ethics and Security

This research follows responsible cybersecurity research practices:

- **University IRB Approval:** Protocol UWE-REC-2023-0847-CYB
- **Informed consent** for all organizational interviews
- **Coordinated disclosure** for discovered vulnerabilities
- **Data anonymization** protecting victim organizations

**Security Warning:** Malware samples and attack signatures are provided for research purposes only. Use appropriate isolation and security measures.

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](.github/CONTRIBUTING.md) for guidelines.

### Areas for Contribution
- Additional ransomware family analysis
- Enhanced machine learning models
- Infrastructure optimization
- Documentation improvements

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support and Contact

- **Technical Documentation:** [docs/](docs/)
- **Issues:** [GitHub Issues](https://github.com/jude-osamor/black-basta-msif/issues)
- **Discussions:** [GitHub Discussions](https://github.com/jude-osamor/black-basta-msif/discussions)
- **Principal Investigator:** jude.osamor@ieee.org
- **Institution:** University of the West of England, Bristol

## Acknowledgments

- University of the West of England Research Ethics Committee
- UK National Cyber Security Centre
- Canadian Centre for Cyber Security
- Industry collaboration partners (anonymized per agreements)
- Open source cybersecurity research community

## Project Status

- **Current Version:** 1.0.0
- **Status:** Active Development
- **Last Updated:** January 2025
- **Next Release:** February 2025 (enhanced detection algorithms)