"""
Watermark Remover Configuration

This file contains all configurable parameters for the watermark remover.
Copy this file to config_local.py and modify the values as needed.
"""

# =============================================================================
# PDF Processing Settings
# =============================================================================

# DPI (Dots Per Inch) for PDF to image conversion
# - High quality (300 DPI): Better image quality, more memory usage
# - Efficient (150 DPI): Lower memory usage, acceptable quality for most cases
PDF_DPI = 300

# Memory mode: "high_quality" or "efficient"
# - high_quality: Load all pages into memory, then process (faster but uses more RAM)
# - efficient: Process one page at a time (slower but uses less RAM)
# Note: Google Drive mode always uses "efficient" regardless of this setting
MEMORY_MODE = "high_quality"

# =============================================================================
# Watermark Detection Settings
# =============================================================================

# Search region ratio: How much of the bottom-right corner to search for watermark
# Value: 0.0 to 1.0 (e.g., 0.15 means search bottom-right 15% of the image)
SEARCH_REGION_RATIO = 0.15

# Bounding box expansion ratio
# The detected text bounding box will be expanded by this factor to cover the logo
EXPAND_RATIO = 2.5

# =============================================================================
# Inpainting Settings
# =============================================================================

# Inpainting method: "telea" or "navierstokes"
# - telea: Telea algorithm, generally produces better results
# - navierstokes: Navier-Stokes algorithm
INPAINT_METHOD = "telea"

# =============================================================================
# Output Settings
# =============================================================================

# Default suffix for output files
DEFAULT_OUTPUT_SUFFIX = "_no_watermark"

# =============================================================================
# Google Drive Settings
# =============================================================================

# Default memory mode for Google Drive operations
# Always "efficient" for GD operations to minimize memory usage
GD_MEMORY_MODE = "efficient"

# =============================================================================
# Server vs Local Configuration
# =============================================================================
# For servers with limited RAM (e.g., 2GB), use these settings:
#
# MEMORY_MODE = "efficient"
# PDF_DPI = 150
#
# For local desktop with ample RAM, use:
#
# MEMORY_MODE = "high_quality"
# PDF_DPI = 300
