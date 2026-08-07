# Drawings Tracker

A clean starter scaffold for the Drawings Tracker project.

## Project goal

Provide a foundation for defining and implementing the drawing tracking workflow, including storage, status tracking, and reporting.

## Suggested structure

- `src/` — application code and package entrypoints
- `docs/` — project notes and specifications
- `tests/` — automated tests

## Getting started

1. Create and activate a virtual environment.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Run the tracker against two Excel exports:
   `python -m drawings_tracker.cli --previous previous.xlsx --current latest.xlsx --output-dir downloads --data-dir data`

## Next steps

- Define the data model and user flows.
- Decide on the persistence layer and authentication approach.
- Implement the core feature set from the project specifications.
