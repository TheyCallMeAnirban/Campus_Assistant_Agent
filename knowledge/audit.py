import pandas as pd
import json
import os

DATA_DIR = os.path.dirname(__file__)

files = ['college_info.csv', 'fees.csv', 'placements.csv', 'hostel.csv', 'admission.csv', 'exam_rules.csv', 'scholarship.csv']

for fname in files:
    path = os.path.join(DATA_DIR, fname)
    if not os.path.exists(path):
        print(f"MISSING: {fname}")
        continue
    df = pd.read_csv(path)
    print(f"=== {fname} ===")
    print(f"  Rows: {len(df)}, Cols: {list(df.columns)}")
    if 'state' in df.columns:
        jh = len(df[df['state'] == 'Jharkhand'])
        print(f"  Jharkhand rows: {jh} / {len(df)}")
    if 'college' in df.columns:
        print(f"  Sample colleges: {df['college'].head(3).tolist()}")
    print()

# Check aliases.json
aliases_path = os.path.join(DATA_DIR, 'aliases.json')
with open(aliases_path, encoding='utf-8') as f:
    aliases = json.load(f)
print(f"=== aliases.json: {len(aliases)} entries ===")

# Check context_map.json
ctx_path = os.path.join(DATA_DIR, 'context_map.json')
with open(ctx_path, encoding='utf-8') as f:
    ctx = json.load(f)
print(f"=== context_map.json: {ctx} ===")

# Check corpus directory
corpus_dir = os.path.join(DATA_DIR, 'corpus')
if os.path.exists(corpus_dir):
    states = [d for d in os.listdir(corpus_dir) if os.path.isdir(os.path.join(corpus_dir, d))]
    print(f"\n=== corpus/ states: {states} ===")
    for state in states:
        colleges = os.listdir(os.path.join(corpus_dir, state))
        print(f"  {state}: {len(colleges)} colleges -> {colleges[:3]}")
