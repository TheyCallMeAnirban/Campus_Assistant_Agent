import os
import pandas as pd

def preprocess():
    data_dir = "knowledge"
    
    files = ["college_info.csv", "fees.csv", "placements.csv", "hostel.csv", "admission.csv", "exam_rules.csv", "scholarship.csv"]
    
    for f in files:
        path = os.path.join(data_dir, f)
        if os.path.exists(path):
            df = pd.read_csv(path)
            # Simple cleaning: drop duplicates
            cleaned_df = df.drop_duplicates()
            cleaned_df.to_csv(path, index=False)
            print(f"Cleaned and saved {f}")

if __name__ == "__main__":
    preprocess()

