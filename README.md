# HashBox: File Integrity Monitoring System

## Overview
HashBox is a comprehensive file integrity monitoring system designed to provide real-time vigilance over your files and directories. Using SHA-256 hashing and metadata tracking, HashBox allows users to detect unauthorized modifications, ensuring the integrity and security of sensitive data.

## Features

### Hash Comparison
- Monitors individual files using SHA-256 hashing
- Provides real-time alerts when file content changes
- Compares current hash values with baseline values to detect modifications

### Directory Monitoring
- Observes entire directories for any file system events
- Tracks file creation, deletion, and modification within the directory
- Provides detailed logging of all directory changes

### Metadata Monitoring
- Tracks changes to file attributes including:
  - File size
  - Timestamp modifications
  - File ownership changes
  - EXIF data for media files(like images, ppt)

### Additional Features
- User-friendly GUI with intuitive navigation
- Real-time terminal display of monitoring events
- Export monitoring logs to Excel spreadsheets
- Threaded architecture for responsive performance

## Installation

### Prerequisites
- Python
- Required Python packages:
  - tkinter
  - PIL (Pillow)
  - xlsxwriter
  - exifread
  - watchdog
  - pywin32 (for Windows systems)

### Setup
1. Clone the repository:
```
git clone https://github.com/yourusername/hashbox.git
```

2. Install required dependencies:
```
pip install <dependency_name>
```

3. Ensure the "images" directory contains the required icons:
   - fileIcon.PNG
   - folderIcon.PNG

## Usage

1. Run the application:
```
python fileIntegrityCheck.py
```

2. Select a file or directory to monitor:
   - Click "Browse File" to monitor a specific file
   - Click "Browse Directory" to monitor an entire directory

3. Choose a monitoring method:
   - **Hash Comparison**: For monitoring content changes to a specific file
   - **Directory Monitoring**: For tracking changes within a directory
   - **Metadata Monitoring**: For tracking file metadata changes

4. View real-time alerts in the terminal display

5. Save monitoring logs:
   - Click "Save Logs" to export the monitoring history to an Excel file
   - Logs include timestamps, file owners, and detailed event descriptions

6. Stop monitoring:
   - Click "Stop Monitoring" to halt all current monitoring threads

## Technical Implementation

HashBox utilizes multiple monitoring approaches:

- **SHA-256 Hashing**: Creates cryptographic hash values of files to detect any content modifications
- **WatchDog Library**: Employs filesystem event observers for directory monitoring
- **EXIF Data Analysis**: Extracts and compares metadata from media files
- **Windows Security API**: Tracks file ownership changes using win32security
- **Threaded Architecture**: Implements concurrent monitoring threads for responsive UI

**Note: HashBox provides detection capabilities but does not prevent file modifications**
