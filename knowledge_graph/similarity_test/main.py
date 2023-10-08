from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Example tags
tag1 = "machine learning"
tag2 = "deep learning"
tag3 = "natural language processing"

# Create a TF-IDF vectorizer
vectorizer = TfidfVectorizer()

# Vectorize the tags
tag_vectors = vectorizer.fit_transform([tag1, tag2, tag3])

# Compute cosine similarity between tags
similarity_matrix = cosine_similarity(tag_vectors)

# Print similarity scores
print("Cosine Similarity Matrix:")
print(similarity_matrix)
