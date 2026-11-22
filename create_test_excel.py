import pandas as pd

data = {
    "product_id": ["P101", "P102", "P103", "P104"],
    "product_name": ["Soap", "Shampoo", "Detergent", "Toothpaste"],
    "warehouse": ["Bangalore", "Mysore", "Chennai", "Bangalore"],
    "available_stock": [500, 300, 50, 400],
    "reorder_level": [100, 80, 100, 100]
}

df = pd.DataFrame(data)

df.to_excel("documents/test_inventory.xlsx", index=False)

print("Excel file created successfully!")