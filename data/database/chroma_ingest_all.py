import pandas as pd
from tqdm import tqdm
from openai import OpenAI
import chromadb

# Initialize clients
client = OpenAI()
chroma = chromadb.HttpClient(host="localhost", port=8000)


# Helper function to rebuild clean collections
def recreate_collection(name: str):
    """Deletes old collection if exists, then creates a new one"""
    try:
        chroma.delete_collection(name)
        print(f"🗑️ Deleted old collection: {name}")
    except Exception:
        pass
    return chroma.get_or_create_collection(name)


# Function to store any CSV into ChromaDB
def store_to_chroma(csv_path, collection_name, text_columns, meta_columns, batch_size=50):
    print(f"\n📂 Reading file: {csv_path}")
    df = pd.read_csv(csv_path, low_memory=False)
    print(f"✅ Loaded {len(df)} records for collection '{collection_name}'")

    # Recreate collection cleanly
    collection = recreate_collection(collection_name)

    # Iterate in batches
    texts, metas, ids = [], [], []
    for i, row in tqdm(df.iterrows(), total=len(df), desc=f"Embedding {collection_name}"):
        text_parts = [str(row.get(col, "")) for col in text_columns]
        text = ". ".join([t for t in text_parts if t.strip()])

        # Skip empty rows
        if not text.strip():
            continue

        meta = {col: str(row.get(col, "")) for col in meta_columns}

        texts.append(text)
        metas.append(meta)
        ids.append(f"{collection_name}_{i}")

        # Process in batches
        if len(texts) >= batch_size:
            try:
                emb_response = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=texts
                )
                embeddings = [d.embedding for d in emb_response.data]
                collection.add(ids=ids, embeddings=embeddings, metadatas=metas, documents=texts)
            except Exception as e:
                print(f"⚠️ Batch error: {e}")
            texts, metas, ids = [], [], []

    # Handle remaining records
    if texts:
        emb_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        embeddings = [d.embedding for d in emb_response.data]
        collection.add(ids=ids, embeddings=embeddings, metadatas=metas, documents=texts)

    print(f"🏁 Finished storing '{collection_name}' data in ChromaDB!\n")


# =============================
# Ingestion starts here
# =============================
if __name__ == "__main__":

    # 🏠 Properties
    # store_to_chroma(
    #     csv_path="data/processed/Boston/properties_CLEAN_20251025.csv",
    #     collection_name="propbot_properties",
    #     text_columns=[
    #         "full_address", "CITY", "zip_code", "LU_DESC",
    #         "STRUCTURE_CLASS", "EXT_FINISHED", "OVERALL_COND",
    #         "HEAT_TYPE", "AC_TYPE"
    #     ],
    #     meta_columns=[
    #         "zip_code", "CITY", "TOTAL_VALUE", "LAND_VALUE",
    #         "BLDG_VALUE", "BED_RMS", "FULL_BTH", "NUM_PARKING", "year_built"
    #     ]
    # )

    # 🚓 Crime
    store_to_chroma(
        csv_path="data/processed/Boston/crime_2020_2025_CLEAN_20251025.csv",
        collection_name="propbot_crime",
        text_columns=[
            "OFFENSE_DESCRIPTION", "DISTRICT", "STREET", "DAY_OF_WEEK"
        ],
        meta_columns=[
            "YEAR","MONTH","HOUR","SHOOTING","Lat","Long"
        ]
    )

    # 👨‍👩‍👧 Demographics
    store_to_chroma(
        csv_path="data/processed/Boston/demographics_CLEAN_20251025.csv",
        collection_name="propbot_demographics",
        text_columns = [
        "city","zip_code","population","median_income",
        "median_age","employment_rate","education_level"
    ],
        meta_columns = [
        "zip_code","population","median_income",
        "median_age","employment_rate","education_level"
    ]

    )

    # 🏪 Amenities
    # store_to_chroma(
    #     csv_path="data/processed/Boston/amenities_CLEAN_20251025.csv",
    #     collection_name="propbot_amenities",
    #     text_columns=[
    #         "name", "category", "address", "zip_code"
    #     ],
    #     meta_columns=[
    #         "zip_code", "category", "rating", "latitude", "longitude"
    #     ]
    # )


    # 🚉 Transit
    # store_to_chroma(
    #     csv_path="data/processed/Boston/transit_CLEAN_20251025.csv",
    #     collection_name="propbot_transit",
    #     text_columns=[
    #         "station_name",       # Descriptive station name
    #         "municipality",       # City/town
    #         "wheelchair_accessible",  # Accessibility info
    #         "vehicle_type"        # Bus/train/light rail indicator
    #     ],
    #     meta_columns=[
    #         "station_id", "latitude", "longitude", "location_type"
    #     ]
    # )

    print("✅ All datasets stored successfully in ChromaDB!")
