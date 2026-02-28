from extract_transform import extract_and_transform
from load import load_to_postgres


def main() -> None:
    train_df, test_df = extract_and_transform()
    load_to_postgres(train_df, test_df)
    print("BigMart ETL completed successfully.")


if __name__ == "__main__":
    main()
