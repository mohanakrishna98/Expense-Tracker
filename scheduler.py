from datetime import datetime
import os


def create_scheduled_file():
  # 1. Define and create the output directory if it doesn't exist
  output_folder = "output"
  os.makedirs(output_folder, exist_ok=True)

  # 2. Get current date and time
  now = datetime.now()
  date_str = now.strftime("%Y-%m-%d")
  time_str = now.strftime("%H-%M-%S")  # Using hyphens to be filesystem-safe

  # 3. Construct the filename following your pattern
  filename = f"test schedule {date_str} {time_str}.txt"
  file_path = os.path.join(output_folder, filename)

  # 4. Write content to the file
  content = (
      f"Job successfully executed!\nTimestamp: {date_str}"
      f" {now.strftime('%H:%M:%S')}"
  )
  with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

  print(f"Successfully created: {file_path}")


if __name__ == "__main__":
  create_scheduled_file()
