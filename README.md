# Angular Pattern Detector

A Python-based tool for detecting UI patterns in Angular components.

----

## Run
1. Create a virtual environment:
   ```sh
   python -m venv ./venv
   ```
2. Activate the virtual environment:
   - Windows:
     ```sh
     .\venv\Scripts\activate
     ```
   - Linux/macOS:
     ```sh
     source venv/bin/activate
     ```
3. Install Dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run
    ```sh
    python main.py --project-path /path/to/angular/project --output-format both --export-path ./custom-report.json
    ```