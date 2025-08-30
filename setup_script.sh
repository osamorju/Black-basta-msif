#!/bin/bash
# MSIF Framework Installation Script
# Installs dependencies and sets up the research environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARN: $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    warn "Running as root. Consider running as a regular user."
fi

log "Starting MSIF Framework installation..."

# Check system requirements
check_system_requirements() {
    log "Checking system requirements..."
    
    # Check OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log "Linux detected"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log "macOS detected"
    else
        error "Unsupported operating system: $OSTYPE"
    fi
    
    # Check memory (minimum 8GB, recommended 32GB)
    MEMORY_GB=$(free -g 2>/dev/null | awk 'NR==2{print $2}' || echo "0")
    if [ "$MEMORY_GB" -lt 8 ]; then
        warn "System has less than 8GB RAM. Minimum 8GB recommended, 32GB for full deployment."
    else
        log "Memory check passed: ${MEMORY_GB}GB RAM available"
    fi
    
    # Check disk space (minimum 100GB)
    DISK_GB=$(df -BG . | awk 'NR==2 {gsub(/G/,""); print $4}')
    if [ "$DISK_GB" -lt 100 ]; then
        warn "Less than 100GB free disk space available. This may be insufficient for full deployment."
    else
        log "Disk space check passed: ${DISK_GB}GB available"
    fi
}

# Install system dependencies
install_system_dependencies() {
    log "Installing system dependencies..."
    
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y \
            python3.8 python3.8-dev python3-pip \
            git curl wget unzip \
            build-essential libffi-dev libssl-dev \
            docker.io docker-compose \
            htop tree jq
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        sudo yum update -y
        sudo yum install -y \
            python38 python38-devel python3-pip \
            git curl wget unzip \
            gcc gcc-c++ make libffi-devel openssl-devel \
            docker docker-compose \
            htop tree jq
    elif command -v brew &> /dev/null; then
        # macOS
        brew install python@3.8 git curl wget
        brew install --cask docker
    else
        error "Package manager not found. Please install dependencies manually."
    fi
    
    log "System dependencies installed successfully"
}

# Setup Python environment
setup_python_environment() {
    log "Setting up Python environment..."
    
    # Check Python version
    if ! command -v python3.8 &> /dev/null; then
        if command -v python3 &> /dev/null; then
            PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
            if [ "$PYTHON_VERSION" != "3.8" ]; then
                warn "Python 3.8 not found. Using Python $PYTHON_VERSION"
            fi
            PYTHON_CMD="python3"
        else
            error "Python 3.8+ not found. Please install Python 3.8 or higher."
        fi
    else
        PYTHON_CMD="python3.8"
    fi
    
    # Create virtual environment
    log "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    python -m pip install --upgrade pip setuptools wheel
    
    # Install requirements
    log "Installing Python dependencies..."
    pip install -r requirements.txt
    
    log "Python environment setup completed"
}

# Setup Docker
setup_docker() {
    log "Setting up Docker environment..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker not found. Please install Docker first."
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        error "Docker is not running. Please start Docker service."
    fi
    
    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null; then
        error "docker-compose not found. Please install docker-compose."
    fi
    
    # Add user to docker group (Linux only)
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if ! groups $USER | grep -q docker; then
            log "Adding user to docker group..."
            sudo usermod -aG docker $USER
            warn "Please log out and back in for Docker group changes to take effect"
        fi
    fi
    
    log "Docker environment setup completed"
}

# Create directory structure
create_directory_structure() {
    log "Creating directory structure..."
    
    # Main directories
    mkdir -p data/{raw,processed,anonymized,synthetic,honeypots,malware_samples}
    mkdir -p logs/{honeypots,analysis,system}
    mkdir -p results/{statistical_analysis,validation,visualizations,reports}
    mkdir -p models/{pretrained,checkpoints}
    mkdir -p config/{development,production}
    
    # Infrastructure directories
    mkdir -p infrastructure/{honeypots/{cowrie,dionaea},elk_stack/{elasticsearch,logstash,kibana},analysis_lab/{cuckoo,yara_rules,vm_configs}}
    
    # Create .gitkeep files for empty directories
    find . -type d -empty -exec touch {}/.gitkeep \;
    
    log "Directory structure created successfully"
}

# Setup configuration files
setup_configuration() {
    log "Setting up configuration files..."
    
    # Create default configuration
    cat > config/default.yml << 'EOF'
# MSIF Framework Default Configuration

# Application settings
app:
  name: "MSIF Framework"
  version: "1.0.0"
  debug: false
  log_level: "INFO"

# Data processing settings
data_processing:
  batch_size: 1000
  max_workers: 4
  chunk_size: 10000

# Model settings
models:
  ensemble_weights: [0.4, 0.3, 0.3]
  cross_validation_folds: 5
  random_state: 42

# Infrastructure settings
infrastructure:
  honeypot_ports: [22, 23, 80, 443, 3389]
  log_retention_days: 90
  max_malware_samples: 10000

# Security settings
security:
  encryption_key_size: 256
  hash_algorithm: "SHA256"
  session_timeout: 3600
EOF

    # Create development configuration
    cat > config/development.yml << 'EOF'
# Development Configuration
debug: true
log_level: "DEBUG"

# Database settings (development)
database:
  host: "localhost"
  port: 5432
  name: "msif_dev"
  user: "msif_user"
  password: "msif_password"

# External services
elasticsearch:
  host: "localhost"
  port: 9200
  
redis:
  host: "localhost"
  port: 6379
EOF

    log "Configuration files created successfully"
}

# Setup logging
setup_logging() {
    log "Setting up logging configuration..."
    
    cat > config/logging.yml << 'EOF'
version: 1
disable_existing_loggers: false

formatters:
  standard:
    format: "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
  detailed:
    format: "[%(asctime)s] %(levelname)s in %(name)s [%(filename)s:%(lineno)d]: %(message)s"

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: standard
    stream: ext://sys.stdout
    
  file:
    class: logging.handlers.RotatingFileHandler
    level: DEBUG
    formatter: detailed
    filename: logs/system/msif.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

root:
  level: DEBUG
  handlers: [console, file]

loggers:
  src:
    level: DEBUG
    handlers: [console, file]
    propagate: false
EOF

    log "Logging configuration created successfully"
}

# Validate installation
validate_installation() {
    log "Validating installation..."
    
    # Check Python imports
    python -c "
import sys
import numpy, pandas, scikit_learn, tensorflow
import matplotlib, seaborn, plotly
print('Python dependencies validated successfully')
print(f'Python version: {sys.version}')
print(f'NumPy version: {numpy.__version__}')
print(f'Pandas version: {pandas.__version__}')
print(f'Scikit-learn version: {scikit_learn.__version__}')
print(f'TensorFlow version: {tensorflow.__version__}')
"
    
    # Check Docker
    docker --version
    docker-compose --version
    
    # Test Docker containers
    log "Testing Docker containers..."
    docker-compose config > /dev/null
    
    log "Installation validation completed successfully"
}

# Main installation process
main() {
    log "=== MSIF Framework Installation ==="
    log "This will install all dependencies and set up the research environment"
    
    # Get user confirmation
    read -p "Continue with installation? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Installation cancelled by user"
        exit 0
    fi
    
    # Installation steps
    check_system_requirements
    install_system_dependencies
    setup_python_environment
    setup_docker
    create_directory_structure
    setup_configuration
    setup_logging
    validate_installation
    
    log "=== Installation Completed Successfully ==="
    log ""
    log "Next steps:"
    log "1. Activate the Python environment: source venv/bin/activate"
    log "2. Start the Docker services: docker-compose up -d"
    log "3. Run the example analysis: python -m src.models.ensemble_classifier"
    log "4. Access Jupyter notebooks: http://localhost:8888"
    log "5. Access Kibana dashboard: http://localhost:5601"
    log ""
    log "For more information, see docs/README.md"
    log "For support, visit: https://github.com/jude-osamor/black-basta-msif/issues"
}

# Run main function
main "$@"