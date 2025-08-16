from openai import OpenAI
import numpy as np

# Initialize the OpenAI client
client = OpenAI(api_key="YOUR_API_KEY_HERE")  # set via env var OPENAI_API_KEY if preferred

def get_embedding(text, model="text-embedding-3-small"):
    """Get embedding vector for a given text."""
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding

def cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two vectors."""
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

if __name__ == "__main__":
    # Example strings
    s1 = "How to learn Python quickly"
    s2 = "Best ways to pick up Python fast"

    # Get embeddings
    e1 = get_embedding(s1)
    e2 = get_embedding(s2)

    # Calculate similarity
    score = cosine_similarity(e1, e2)

    print(f"Semantic similarity between:\n'{s1}'\n and \n'{s2}'\n= {score:.4f}")
