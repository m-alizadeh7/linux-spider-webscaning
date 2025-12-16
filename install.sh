#!/bin/bash

# Linux Spider Web Scanner - Enhanced Installation Script
# This script installs all required dependencies with detailed logging and debugging

# Colors for better visual feedback
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Debug mode flag
DEBUG_MODE=false
LOG_FILE="install_debug.log"

# Parse command line arguments
for arg in "$@"; do
    case $arg in
        --debug|-d)
            DEBUG_MODE=true
            echo "$(date '+%Y-%m-%d %H:%M:%S') - Debug mode enabled" > "$LOG_FILE"
            ;;
    esac
done

# Logging function
log_debug() {
    if [ "$DEBUG_MODE" = true ]; then
        echo -e "${CYAN}[DEBUG]${NC} $1"
        echo "$(date '+%Y-%m-%d %H:%M:%S') - DEBUG: $1" >> "$LOG_FILE"
    fi
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - INFO: $1" >> "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - SUCCESS: $1" >> "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}⚠️${NC}  $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - WARNING: $1" >> "$LOG_FILE"
}

log_error() {
    echo -e "${RED}❌${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1" >> "$LOG_FILE"
}

# Progress bar function
show_progress() {
    local current=$1
    local total=$2
    local width=50
    local percentage=$((current * 100 / total))
    local completed=$((width * current / total))
    local remaining=$((width - completed))
    
    printf "\r${CYAN}Progress: [${NC}"
    printf "%${completed}s" | tr ' ' '█'
    printf "%${remaining}s" | tr ' ' '░'
    printf "${CYAN}] ${BOLD}%d%%${NC}" "$percentage"
}

# Banner
clear
echo -e "${PURPLE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         Linux Spider Web Scanner - Installation           ║
║                  Enhanced Edition v2.0                    ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"
echo ""

log_info "Installation started at $(date)"
log_debug "Working directory: $(pwd)"
log_debug "User: $(whoami)"
log_debug "Shell: $SHELL"

TOTAL_STEPS=10
CURRENT_STEP=0

# Step 1: Check OS
CURRENT_STEP=$((CURRENT_STEP + 1))
show_progress $CURRENT_STEP $TOTAL_STEPS
echo ""
log_info "Checking operating system..."
log_debug "OSTYPE: $OSTYPE"

if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    log_error "This tool is designed for Linux systems only"
    log_debug "Detected OS: $OSTYPE"
    exit 1
fi

log_success "Linux system detected"
echo ""

# Step 2: Check Python
CURRENT_STEP=$((CURRENT_STEP + 1))
show_progress $CURRENT_STEP $TOTAL_STEPS
echo ""
log_info "Checking Python installation..."

if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is not installed"
    log_info "Please install Python 3.8 or higher first"
    log_debug "Tried command: python3 --version"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_PATH=$(which python3)
log_success "Python $PYTHON_VERSION found at $PYTHON_PATH"
log_debug "Python executable: $PYTHON_PATH"
log_debug "Python version: $PYTHON_VERSION"
echo ""

# Step 3: Check pip
CURRENT_STEP=$((CURRENT_STEP + 1))
show_progress $CURRENT_STEP $TOTAL_STEPS
echo ""
log_info "Checking pip installation..."

if ! command -v pip3 &> /dev/null; then
    log_error "pip3 is not installed"
    log_info "Please install pip3 first"
    log_debug "Tried command: pip3 --version"
    exit 1
fi

PIP_VERSION=$(pip3 --version 2>&1)
log_success "pip3 found"
log_debug "pip info: $PIP_VERSION"
echo ""

# Step 4: Check python3-venv
CURRENT_STEP=$((CURRENT_STEP + 1))
show_progress $CURRENT_STEP $TOTAL_STEPS
echo ""
log_info "Checking python3-venv package..."

# Get Python version for venv package
PYTHON_MAJOR_MINOR=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
VENV_PACKAGE="python${PYTHON_MAJOR_MINOR}-venv"

log_debug "Python version: $PYTHON_MAJOR_MINOR"
log_debug "Required package: $VENV_PACKAGE"

# Check if venv module is available
if python3 -c "import venv" 2>/dev/null; then
    log_success "python3-venv is available"
else
    log_warning "python3-venv is not installed"
    log_info "Installing $VENV_PACKAGE package..."
    
    # Detect Linux distribution
    if [ -f /etc/debian_version ]; then
        log_debug "Detected Debian/Ubuntu system"
        log_info "Updating package list..."
        sudo apt-get update -qq
        log_info "Installing $VENV_PACKAGE..."
        sudo apt-get install -y $VENV_PACKAGE
        INSTALL_STATUS=$?
    elif [ -f /etc/fedora-release ]; then
        log_debug "Detected Fedora system"
        sudo dnf install -y python3-venv
        INSTALL_STATUS=$?
    elif [ -f /etc/redhat-release ]; then
        log_debug "Detected RHEL/CentOS system"
        sudo yum install -y python3-venv
        INSTALL_STATUS=$?
    else
        log_error "Could not detect distribution"
        log_info "Please install python3-venv manually:"
        echo "   - Ubuntu/Debian: sudo apt-get install $VENV_PACKAGE"
        echo "   - Fedora: sudo dnf install python3-venv"
        echo "   - RHEL/CentOS: sudo yum install python3-venv"
        exit 1
    fi
    
    # Verify installation
    if [ $INSTALL_STATUS -eq 0 ] && python3 -c "import venv" 2>/dev/null; then
        log_success "python3-venv installed successfully"
    else
        log_error "Failed to install python3-venv"
        log_info "Please install it manually and try again"
        exit 1
    fi
fi
echo ""

# Step 5: Check nmap
CURRENT_STEP=$((CURRENT_STEP + 1))
show_progress $CURRENT_STEP $TOTAL_STEPS
echo ""
log_info "Checking nmap installation..."

if ! command -v nmap &> /dev/null; then
    log_warning "nmap is not installed"
    log_info "Installing nmap..."
    
    # Detect Linux distribution
    if [ -f /etc/debian_version ]; then
        log_debug "Detected Debian/Ubuntu system"
        sudo apt-get update -qq
        sudo apt-get install -y nmap
    elif [ -f /etc/fedora-release ]; then
        log_debug "Detected Fedora system"
        sudo dnf install -y nmap
    elif [ -f /etc/redhat-release ]; then
        log_debug "Detected RHEL/CentOS system"
        sudo yum install -y nmap
    elif [ -f /etc/arch-release ]; then
        log_debug "Detected Arch Linux system"
        sudo pacman -S --noconfirm nmap
    else
        log_warning "Could not detect distribution"
        log_info "Please install nmap manually:"
        echo "   - Debian/Ubuntu: sudo apt-get install nmap"
        echo "   - Fedora: sudo dnf install nmap"
        echo "   - RHEL/CentOS: sudo yum install nmap"
        echo "   - Arch: sudo pacman -S nmap"
    fi
else
    NMAP_VERSION=$(nmap --version | head -n1)
    log_success "nmap found: $NMAP_VERSION"
    log_debug "nmap path: $(which nmap)"
fi
echo ""

# Step 6: Clean old virtual environment
CURRENT_STEP=$((CURRENT_STEP + 1))
show_progress $CURRENT_STEP $TOTAL_STEPS
echo ""

if [ -d "venv" ]; then
    log_warning "Old virtual environment detected"
    log_info "Removing old virtual environment..."
    rm -rf venv
    log_debug "Removed directory: venv/"
fi

# Step 7: Create virtual environment
CURRENT_STEP=$((CURRENT_STEP + 1))
show_progress $CURRENT_STEP $TOTAL_STEPS
echo ""
log_info "Creating virtual environment..."
log_debug "Command: python3 -m venv venv"

if python3 -m venv venv; then
    log_success "Virtual environment created successfully"
    log_debug "Virtual environment path: $(pwd)/venv"
else
    log_error "Failed to create virtual environment"
    log_debug "Error code: $?"
    log_info "Try running with --debug flag for more information"
    exit 1
fi
echo ""

# Step 8: Activate virtual environment
CURRENT_STEP=$((CURRENT_STEP + 1))
show_progress $CURRENT_STEP $TOTAL_STEPS
echo ""
log_info "Activating virtual environment..."
log_debug "Activation script: $(pwd)/venv/bin/activate"

if [ ! -f "venv/bin/activate" ]; then
    log_error "Virtual environment activation script not found"
    log_debug "Looking for: $(pwd)/venv/bin/activate"
    log_debug "Directory contents: $(ls -la venv/bin/ 2>&1)"
    exit 1
fi

source venv/bin/activate
log_success "Virtual environment activated"
log_debug "Virtual environment: $VIRTUAL_ENV"
log_debug "Python: $(which python)"
echo ""

# Step 9: Upgrade pip
CURRENT_STEP=$((CURRENT_STEP + 1))
show_progress $CURRENT_STEP $TOTAL_STEPS
echo ""
log_info "Upgrading pip in virtual environment..."
log_debug "Command: pip install --upgrade pip"

pip install --upgrade pip -q
if [ $? -eq 0 ]; then
    NEW_PIP_VERSION=$(pip --version)
    log_success "pip upgraded successfully"
    log_debug "New pip version: $NEW_PIP_VERSION"
else
    log_warning "pip upgrade had issues but continuing..."
fi
echo ""

# Step 10: Install requirements
CURRENT_STEP=$((CURRENT_STEP + 1))
show_progress $CURRENT_STEP $TOTAL_STEPS
echo ""
log_info "Installing Python dependencies..."
log_info "This may take a few minutes..."
echo ""

if [ ! -f "requirements.txt" ]; then
    log_error "requirements.txt not found"
    log_debug "Current directory: $(pwd)"
    log_debug "Files in directory: $(ls -la)"
    exit 1
fi

log_debug "Reading requirements.txt:"
if [ "$DEBUG_MODE" = true ]; then
    cat requirements.txt >> "$LOG_FILE"
fi

# Install with detailed output in debug mode
if [ "$DEBUG_MODE" = true ]; then
    pip install -r requirements.txt 2>&1 | tee -a "$LOG_FILE"
    INSTALL_RESULT=${PIPESTATUS[0]}
else
    pip install -r requirements.txt
    INSTALL_RESULT=$?
fi

echo ""
if [ $INSTALL_RESULT -eq 0 ]; then
    log_success "All dependencies installed successfully"
    
    # Show installed packages in debug mode
    if [ "$DEBUG_MODE" = true ]; then
        log_debug "Installed packages:"
        pip list >> "$LOG_FILE"
    fi
else
    log_error "Some dependencies failed to install"
    log_info "Please check the error messages above"
    
    if [ "$DEBUG_MODE" = false ]; then
        log_info "Run with --debug flag for detailed logging: ./install.sh --debug"
        log_info "Check $LOG_FILE for details"
    fi
    
    exit 1
fi
echo ""

# Create reports directory
log_info "Creating reports directory..."
mkdir -p reports
log_success "Reports directory created"
log_debug "Reports path: $(pwd)/reports"
echo ""

# Make scripts executable
log_info "Setting permissions..."
chmod +x main.py
chmod +x run.sh
log_success "Permissions set"
log_debug "Made executable: main.py, run.sh"
echo ""

# Installation complete
show_progress $TOTAL_STEPS $TOTAL_STEPS
echo ""
echo ""

echo -e "${GREEN}${BOLD}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         🎉 Installation Completed Successfully! 🎉        ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"
echo ""

log_success "Installation completed at $(date)"
echo ""

echo -e "${CYAN}${BOLD}Quick Start Guide:${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BOLD}1.${NC} Activate virtual environment:"
echo -e "   ${GREEN}source venv/bin/activate${NC}"
echo ""
echo -e "${BOLD}2.${NC} Run the scanner:"
echo -e "   ${GREEN}python3 main.py${NC}"
echo -e "   or simply:"
echo -e "   ${GREEN}./run.sh${NC}"
echo ""
echo -e "${BOLD}3.${NC} Deactivate when done:"
echo -e "   ${GREEN}deactivate${NC}"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ "$DEBUG_MODE" = true ]; then
    echo -e "${CYAN}Debug log saved to: ${BOLD}$LOG_FILE${NC}"
    echo ""
fi

echo -e "${BLUE}Reports will be saved in the '${BOLD}reports/${NC}${BLUE}' directory${NC}"
echo ""
