# AutoCrate V7

**Siemens NX automation for parametric 3D industrial shipping crate generation from external Python tool data.**

## Table of Contents
- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Running the PyQt GUI](#running-the-pyqt-gui)
  - [Using the Wizard](#using-the-wizard)
  - [Expression File Generation](#expression-file-generation)
- [Project Structure](#project-structure)
- [Supported Crate Styles](#supported-crate-styles)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

AutoCrate is a comprehensive tool for designing industrial shipping crates. It provides a user-friendly interface where users can input product dimensions and specifications, and the tool calculates all necessary parameters for a compliant shipping crate. The tool then generates a Siemens NX expression file that can be imported into Siemens NX to automatically create a 3D model of the crate.

## Key Features

* **PyQt6-based GUI**: Modern, user-friendly interface for inputting crate parameters
* **Parametric Calculations**: Intelligent computation of all crate components:
  * Skid layout based on product weight and dimensions
  * Floorboard layout with optimized positioning
  * Wall panel design with proper cleating
  * Cap design with appropriate cleating
  * Support for removable panels (Style B crates)
* **Expression File Generation**: Creates .exp files compatible with Siemens NX
* **Multiple Crate Styles**: Support for different crate construction styles, with focus on Style B crates
* **Standards Compliance**: All calculations follow industry standards for shipping crates

## Technology Stack

* **Python 3.x**: Core programming language
* **PyQt6**: GUI framework
* **Siemens NX**: Target CAD system for expression file import
* **Git**: Version control

## Getting Started

### Prerequisites

* Python 3.8 or higher
* PyQt6
* Siemens NX (for importing the generated expression files)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/AutoCrate-V7.git
   cd AutoCrate-V7
   ```

2. Create and activate a virtual environment (recommended):
   ```
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Running the PyQt GUI

1. To start the PyQt GUI application:
   ```
   python run_autocrate_pyqt.py
   ```

2. The GUI will open with default values pre-filled.

### Using the Wizard

1. **Product Dimensions**: Enter the weight, width, length, and height of your product.
2. **Crate Construction**: Specify clearances and material thicknesses.
3. **Component Sizing**: Set cleat widths, floorboard thickness, and spacing parameters.
4. **Options & Features**: Select available options like skid types and floorboard choices.
5. **Removable Panels**: For Style B crates, select which panels should be removable.
6. **Output Location**: Choose where to save the generated NX expression file.
7. **Generate**: Click the "Generate & Update .exp File" button to calculate and create the expression file.

### Expression File Generation

The application generates a Siemens NX expression file (.exp) containing all calculated parameters. This file can be imported into Siemens NX to automatically create a parametric 3D model of the crate.

## Project Structure

```
AutoCrate-V7/
├── autocrate_pyqt_gui.py    # Main PyQt GUI application
├── run_autocrate_pyqt.py    # Script to run the PyQt application
├── requirements.txt         # Python dependencies
├── wizard_app/              # Core calculation modules
│   ├── __init__.py
│   ├── config.py            # Configuration constants
│   ├── skid_logic.py        # Skid calculation module
│   ├── floorboard_logic.py  # Floorboard calculation module
│   ├── wall_logic.py        # Wall panel calculation module
│   ├── cap_logic.py         # Cap calculation module
│   ├── decal_logic.py       # Decal placement module
│   └── exp_generator.py     # Expression file generator
├── docs/                    # Documentation
├── internal docs/           # Internal specifications
└── nx_part_templates/       # Templates for Siemens NX
```

## Supported Crate Styles

### Style B Crate

Style B crates feature:
- Two-way entry load-bearing lumber shipping base
- "Drop-end style" cleated plywood cap
- At least one removable side or end panel
- Support for fastening with Klimps or lag screws based on panel area
- Consistent with ASTM D6251-00 and other industry standards

## Contributing

Contributions are welcome. Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.