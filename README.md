# Angular Pattern Detector

A proof-of-concept tool for detecting and analyzing UI patterns in Angular components.

## What it Shows

The generated catalog displays key metrics for each detected UI pattern:
- **Usage Count**: How often the pattern appears across components
- **Complexity Score**: Combined measure of template, style, and logic complexity
- **Maintainability Index**: Code maintainability rating (0-1)
- **Complexity Breakdown**:
  - Template: HTML structure and directive usage
  - Styles: CSS rule complexity
  - Logic: Data binding and event handling density

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
    python main.py --project-path .\sample-project\src\ --output-format all --generate-catalog
    ```

> Note: This is an MVP proof-of-concept for pattern detection and analysis in Angular applications.