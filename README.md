# Event Management

Using Flask for event bookibg

## Prerequisites

Ensure you have the following installed on your system:

- Python (version 3.x)
- pip (Python package manager)

## Setup Instructions

Follow these steps to set up and run the project:

1. **Install Python**  
   Ensure Python is installed on your system. You can download it from [python.org](https://www.python.org/).

2. **Create a Virtual Environment**  
   Open a terminal and run:
   ```sh
   python3 -m venv .venv
   ```

3. **Activate the Virtual Environment**  
   - On macOS/Linux:
     ```sh
     source .venv/bin/activate
     ```
   - On Windows:
     ```sh
     .venv\Scripts\activate
     ```

4. **Install Dependencies**  
   ```sh
   pip install flask
   ```

5. **Create Required Directories**  
   ```sh
   mkdir -p static/uploads
   ```

6. **Remove Existing Database (If Exists)**  
   ```sh
   rm -f user.db
   ```

7. **Run the Application**  
   ```sh
   python app.py
   ```

