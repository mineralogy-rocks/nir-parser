# NIR Parser

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A tool for processing Near-Infrared (NIR) spectral data, extracting features, and generating visualizations.

## 📋 Table of Contents

- [Features](#-features)
- [Requirements](#-requirements)
- [Installing Git](#-installing-git)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Examples](#-examples)
- [Logging](#-logging)

## ✨ Features

- Process NIR spectral data from CSV files
- Remove continuum and extract spectral features
- Generate visualizations of original and processed spectra
- Export processed data as text files
- Comprehensive logging of all operations

## 📦 Requirements

- Python 3.10 or higher
- UV package manager
- Git

## 💻 Installing Git

Before you can clone the repository, you need to have Git installed on your system.

### Windows

1. Download the Git installer from [Git for Windows](https://git-scm.com/download/win)
2. Run the installer and follow the installation wizard
3. During installation, accept the default options unless you have specific preferences
4. After installation, open Git Bash or Command Prompt to verify installation:
   ```bash
   git --version
   ```

### macOS

1. **Using Homebrew (recommended)**:
   ```bash
   brew install git
   ```

2. **Using the installer**:
   - Download the latest Git installer from [Git for macOS](https://git-scm.com/download/mac)
   - Run the installer and follow the instructions

3. Verify installation:
   ```bash
   git --version
   ```

### Linux (Debian/Ubuntu)

1. Update your package index:
   ```bash
   sudo apt update
   ```

2. Install Git:
   ```bash
   sudo apt install git
   ```

3. Verify installation:
   ```bash
   git --version
   ```

### Linux (Fedora)

1. Install Git:
   ```bash
   sudo dnf install git
   ```

2. Verify installation:
   ```bash
   git --version
   ```

## 🚀 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/nir-parser.git
   cd nir-parser
   ```

2. **Install UV package manager**

   Follow the installation instructions at [UV Documentation](https://docs.astral.sh/uv/getting-started/installation/).

3. **Create a virtual environment**

   ```bash
   uv venv .venv
   ```

4. **Activate the virtual environment**

   On macOS/Linux:
   ```bash
   source .venv/bin/activate
   ```

   On Windows:
   ```bash
   .\.venv\Scripts\activate
   ```

5. **Install dependencies**

   ```bash
   uv sync
   ```

## ⚙️ Configuration

1. **Create environment file**

   Create a `.env` file in the project root directory using `.env.example` as a template:

   ```
   PROJECT_DIRECTORY=/path/to/your/project
   INPUT_FOLDER_NAME=input
   OUTPUT_FOLDER_NAME=output
   ```

   - `PROJECT_DIRECTORY`: The absolute path to your project directory
   - `INPUT_FOLDER_NAME`: Name of the folder containing input CSV files (default: "input")
   - `OUTPUT_FOLDER_NAME`: Name of the folder where results will be saved (default: "output")

2. **Prepare input data**

   Place your CSV files in the input folder. The input folder cannot be empty.

## 🔧 Usage

Run the NIR parser from the command line:

```bash
python -m src.base.main [options]
```

### Command-line options

- `--no-plots`: Do not show plots during processing (useful for batch processing)

## 📝 Examples

**Run with default settings:**
```bash
python -m src.base.main
```

**Run without showing plots:**
```bash
python -m src.base.main --no-plots
```

## 📊 Logging

The parser logs all operations to both the console and a log file (`nir_parser.log`) in the results directory. This helps track the processing steps and diagnose any issues that might occur.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
