import os
import shutil
from datetime import datetime

# 1. Define the directory you want to clean up
TARGET_DIR = os.path.expanduser("~/Downloads")

# 2. Map file extensions to their respective category folders
FILE_CATEGORIES = {
    "Documents": [".pdf", ".docx", ".txt", ".xlsx", ".pptx"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".svg"],
    "Audio_Video": [".mp3", ".mp4", ".mkv", ".avi"],
    "Zipped": [".zip", ".rar", ".tar", ".gz"],
    "Installers": [".exe", ".msi", ".dmg"]
}

def organize_folder():
    print(f"🔄 Starting automation scan in: {TARGET_DIR}")
    
    moved_count = 0
    log_entries = []

    if not os.path.exists(TARGET_DIR):
        print("❌ Error: Target directory does not exist.")
        return

    # 3. Scan through all items in the target directory
    for item in os.listdir(TARGET_DIR):
        item_path = os.path.join(TARGET_DIR, item)

        # Skip directories, the script file, and the log file itself
        if os.path.isdir(item_path) or item in ["editor.py", "automation_log.txt"]:
            continue

        _, extension = os.path.splitext(item)
        extension = extension.lower()

        # 4. Find the matching category for the extension
        moved = False
        for category, extensions in FILE_CATEGORIES.items():
            if extension in extensions:
                category_path = os.path.join(TARGET_DIR, category)
                os.makedirs(category_path, exist_ok=True)

                destination = os.path.join(category_path, item)
                shutil.move(item_path, destination)
                
                log_msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] MOVED: '{item}' ➡️ to '{category}/'"
                log_entries.append(log_msg)
                moved_count += 1
                moved = True
                break
        
        if not moved:
            others_path = os.path.join(TARGET_DIR, "Others")
            os.makedirs(others_path, exist_ok=True)
            shutil.move(item_path, os.path.join(others_path, item))

    # 5. Write out the log file activity report
    if moved_count > 0:
        log_file_path = os.path.join(TARGET_DIR, "automation_log.txt")
        with open(log_file_path, "a", encoding="utf-8") as log_file:
            log_file.write("\n".join(log_entries) + "\n")
        print(f"✅ Success! Organized {moved_count} files. Log updated.")
    else:
        print("ℹ️ No loose files moved.")

    # 6. NEW FEATURE: Clean up empty folders
    print("🧹 Checking for empty folders to delete...")
    deleted_folders_count = 0
    
    for item in os.listdir(TARGET_DIR):
        item_path = os.path.join(TARGET_DIR, item)
        
        # Check if the item is a folder
        if os.path.isdir(item_path):
            # If the folder has nothing inside, delete it safely
            if len(os.listdir(item_path)) == 0:
                os.rmdir(item_path)
                print(f"🗑️ Removed empty folder: {item}")
                deleted_folders_count += 1
                
    if deleted_folders_count == 0:
        print("ℹ️ No empty folders found.")

if __name__ == "__main__":
    organize_folder()

