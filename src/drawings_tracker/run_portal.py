from __future__ import annotations

from drawings_tracker.selenium_runner import SeleniumRunner, prompt_for_credentials


def main() -> None:
    url = "https://sgc.cumbra.com.pe/AppMSSO/"
    username, password = prompt_for_credentials()
    from pathlib import Path
    downloads_dir = Path("downloads").resolve()
    downloads_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Locate the existing previous export file BEFORE we download the new one
    existing_exports = sorted(
        [f for f in downloads_dir.glob("status_export_*.xlsx") if f.is_file()],
        key=lambda p: p.stat().st_mtime
    )
    previous_path = existing_exports[-1] if existing_exports else None
    
    if previous_path:
        print(f"Pre-located previous baseline file for comparison: {previous_path.name}")
    else:
        print("No previous export file found in downloads/ to compare against.")

    runner = SeleniumRunner(download_dir=downloads_dir, headless=False)
    try:
        runner.login(url, username, password)
        print("Login verified successfully. Proceeding through the repository flow...")
        export_path = runner.export_status_excel()
        print(f"Export step completed. File saved at: {export_path.name}")
        
        if previous_path:
            print(f"\nComparing {export_path.name} against previous baseline: {previous_path.name}")
            
            from drawings_tracker.core import DrawingTracker
            tracker = DrawingTracker()
            changes = tracker.compare_status_files(previous_path, export_path)
            
            # Print the comparison results
            print(f"\n==========================================")
            print(f"           COMPARISON SUMMARY")
            print(f"==========================================")
            print(f"New Drawings Added: {len(changes['new_drawings'])}")
            print(f"Updated Drawings:   {len(changes['updated_drawings'])}")
            print(f"==========================================")
            
            if changes["new_drawings"]:
                print("\n[+] NEW DRAWINGS:")
                for item in changes["new_drawings"]:
                    print(f"  • Tag/ID: {item['drawing_id']}")
                    print(f"    Revision: {item.get('revision', 'N/A')} | Status: {item.get('status', 'N/A')}")
            
            if changes["updated_drawings"]:
                print("\n[*] REVISION / STATUS CHANGES:")
                for item in changes["updated_drawings"]:
                    print(f"  • Tag/ID: {item['drawing_id']}")
                    if item.get("previous_revision") != item.get("latest_revision"):
                        print(f"    Revision Change: {item.get('previous_revision', 'N/A')} ➔ {item.get('latest_revision', 'N/A')}")
                    if item.get("previous_status") != item.get("latest_status"):
                        print(f"    Status Change:   {item.get('previous_status', 'N/A')} ➔ {item.get('latest_status', 'N/A')}")
            
            # Map each changed drawing ID to its change type (NEW or UPDATED)
            change_types = {}
            for item in changes["new_drawings"]:
                change_types[item["drawing_id"]] = "NEW"
            for item in changes["updated_drawings"]:
                change_types[item["drawing_id"]] = "UPDATED"

            if change_types:
                import pandas as pd
                latest_df = pd.read_excel(export_path)
                
                from drawings_tracker.core import DrawingTracker
                tracker_helper = DrawingTracker()
                drawing_column = tracker_helper._find_column(latest_df, "drawing_id", "drawing", "drawing_no", "drawingnumber", "codigo")
                
                if drawing_column:
                    # Filter rows where drawing ID is in the changed IDs
                    latest_df_copy = latest_df.copy()
                    latest_df_copy[drawing_column] = latest_df_copy[drawing_column].astype(str).str.strip()
                    filtered_df = latest_df[latest_df_copy[drawing_column].isin(change_types.keys())].copy()
                    
                    # Add the Change Type column as the first column in the CSV
                    filtered_df.insert(0, "Change Type", filtered_df[drawing_column].map(change_types))
                    
                    # Extract timestamp from export_path filename to keep the same format
                    stem = export_path.stem
                    if "_" in stem:
                        parts = stem.split("_")
                        timestamp = f"{parts[-2]}_{parts[-1]}"
                    else:
                        import datetime
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    csv_filename = downloads_dir / f"changes_{timestamp}.csv"
                    filtered_df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
                    print(f"Comparison details saved to CSV: {csv_filename.name}")
                else:
                    print("Error: Could not identify Drawing ID / Código column in the Excel file to generate the filtered CSV.")
            else:
                print("No changes detected. CSV file was not created.")

            # Download the changed drawings one by one with user confirmation in terminal
            if change_types:
                print(f"\nStarting individual drawing downloads ({len(change_types)} files)...")
                for i, drawing_id in enumerate(change_types.keys(), 1):
                    user_input = input(f"\n[{i}/{len(change_types)}] Ready to download drawing: '{drawing_id}'. Press Enter to proceed (or type 'skip' to skip, 'abort' to stop): ").strip().lower()
                    if user_input in ("abort", "exit", "stop"):
                        print("Aborting drawing downloads as requested.")
                        break
                    elif user_input == "skip":
                        print(f"Skipping download for '{drawing_id}'.")
                        continue
                    try:
                        runner.download_drawing(drawing_id)
                    except Exception as download_err:
                        print(f"Error downloading '{drawing_id}': {download_err}")
                
            print(f"==========================================\n")
        else:
            print("\nSkipping comparison because no previous export file existed before this run.")
            
    except RuntimeError as e:
        print(f"Error: {e}")
        return
    finally:
        runner.close()


if __name__ == "__main__":
    main()
