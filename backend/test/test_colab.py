from knowledge.embeddings import FastAPIEmbeddings

emb = FastAPIEmbeddings()

# Test single embedding
vector = emb.embed_query("دانشگاه تهران")
print(f"Vector length: {len(vector)}")
print(f"First 5 values: {vector[:5]}")

# Test batch embedding
vectors = emb.embed_documents(["سلام", "خداحافظ"])
print(f"Number of vectors: {len(vectors)}")