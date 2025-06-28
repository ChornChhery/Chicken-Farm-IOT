from database import DatabaseConnection
import pandas as pd

def view_database_content():
    db = DatabaseConnection()
    data = db.get_recent_weights()
    df = pd.DataFrame(data)
    print("Database Contents:")
    print(f"Total records: {len(df)}")
    print("\nFirst few records:")
    print(df[['day', 'weight', 'timestamp']].head())
    print("\nValue ranges:")
    print(f"Days: {df['day'].min()} to {df['day'].max()}")
    print(f"Weights: {df['weight'].min():.2f} to {df['weight'].max():.2f}")
    return df

if __name__ == "__main__":
    df = view_database_content()
