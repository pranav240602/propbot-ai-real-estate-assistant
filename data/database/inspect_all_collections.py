import chromadb

# Connect to ChromaDB
chroma = chromadb.HttpClient(host="localhost", port=8000)

# All collections
collections = [
    "propbot_properties",
    "propbot_crime",
    "propbot_demographics",
    "propbot_amenities",
    "propbot_transit"
]

# Loop through each collection
for name in collections:
    c = chroma.get_or_create_collection(name)
    count = c.count()
    print(f"\n📦 {name} — Total Records: {count}")

    if count == 0:
        print("⚠️ Collection is empty.")
        continue

    results = c.get(limit=3)

    for i, (doc, meta) in enumerate(zip(results["documents"], results["metadatas"]), start=1):
        print(f"\n🧾 Record {i}:")
        print("TEXT:", doc[:200].replace("\n", " "), "...")
        print("META:", meta)
    print("\n" + "=" * 80)
