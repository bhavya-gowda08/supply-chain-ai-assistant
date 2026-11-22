
import os
import pandas as pd
from vector_store import extract_pdf_pages

DOCUMENT_FOLDER = "documents"

for root, dirs, files in os.walk(DOCUMENT_FOLDER):

    # Skip uploaded copies to avoid duplicate output
    dirs[:] = [d for d in dirs if d != "uploaded_docs"]

    for filename in files:

        file_path = os.path.join(root, filename)

        print("\n" + "=" * 70)
        print("DOCUMENT:", filename)
        print("=" * 70)

        try:
            extension = os.path.splitext(filename)[1].lower()

            if extension == ".pdf":
                pages = extract_pdf_pages(file_path)

                for page_number, page in enumerate(pages, start=1):
                    print(f"\nPage {page_number}:")
                    print(page)

            elif extension == ".txt":
                with open(file_path, "r", encoding="utf-8") as file:
                    print(file.read())

            elif extension == ".csv":
                df = pd.read_csv(file_path)
                print("Columns:", list(df.columns))
                print(df.to_string(index=False))

            elif extension in [".xlsx", ".xls"]:
                sheets = pd.read_excel(file_path, sheet_name=None)

                for sheet_name, df in sheets.items():
                    print("\nSheet:", sheet_name)
                    print("Columns:", list(df.columns))
                    print(df.to_string(index=False))

        except Exception as error:
            print("Error reading document:", error)
