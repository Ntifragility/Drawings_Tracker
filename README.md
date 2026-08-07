# Drawings Tracker

Drawings Tracker is a Python tool for automating the review of drawing status data from the Cumbra portal. It logs into the portal, navigates the repository explorer, exports the relevant Excel file, and compares the latest export with a previous one to identify new or updated drawings.

## Project goal

Provide an automated workflow for collecting drawing status information, detecting changes between versions, and helping teams focus on the drawings that need attention.

## What the project does

- Automates sign-in to the portal through Selenium.
- Navigates the repository and explorer flow to export status data.
- Saves exported files into the downloads folder.
- Compares two Excel exports to identify new drawings and updates.
- Makes it easier to track drawing revisions and status changes over time.

## Project structure

- `src/` — application code and package entrypoints
- `tests/` — automated tests for the comparison and tracking logic
- `downloads/` — exported files generated during use

## Getting started

1. Create and activate a virtual environment.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Run the CLI with two Excel files:
   `python -m drawings_tracker.cli --previous previous.xlsx --current latest.xlsx --output-dir downloads --data-dir data`
4. Run the Selenium workflow to export the latest status data from the portal:
   `python -m drawings_tracker.run_portal`

## Next steps

- Improve the Selenium flow for the portal’s evolving UI.
- Add more robust handling for export and download confirmation.
- Extend reporting so the tool highlights the most relevant drawing changes.
