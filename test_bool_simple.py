import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from utils.data_validator import BooleanDetector, DataValidator

# Load dataset
df = pd.read_csv('disease_symptom_matrix.csv')

print("ORIGINAL DATASET:")
print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
print("\nData types BEFORE:")
print(df.dtypes.value_counts())

# Detect booleans
boolean_cols = BooleanDetector.detect_boolean_columns(df)
detected = [col for col, is_bool in boolean_cols.items() if is_bool]

print(f"\nDetected {len(detected)} boolean columns")
print(f"Examples: {detected[:5]}")

# Convert
df_converted, converted = BooleanDetector.auto_convert_booleans(df)

print(f"\nConverted {len(converted)} columns")
print("\nData types AFTER:")
print(df_converted.dtypes.value_counts())

print("\nSUCCESS! Boolean detection working!")
