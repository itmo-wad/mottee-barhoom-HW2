from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import pprint

MONGO_URI = "mongodb+srv://m4bbarhoom:M.0991987847b@cluster0.o6ukn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

def test_db_connection():
    try:
        client = MongoClient(MONGO_URI)
        # Force a call to the server to check the connection
        client.server_info()
        print("Connected to MongoDB successfully!")
    except ConnectionFailure as e:
        print("Failed to connect to MongoDB:", e)
        return

    # Use a test database and collection
    db = client["test_database"]
    collection = db["test_collection"]

    # Create a test document
    test_doc = {"name": "John Doe", "email": "john@example.com"}
    
    # Insert the document and print its inserted_id
    insert_result = collection.insert_one(test_doc)
    print("Inserted document ID:", insert_result.inserted_id)
    
    # Retrieve the inserted document using its _id
    retrieved_doc = collection.find_one({"_id": insert_result.inserted_id})
    print("Retrieved document:")
    pprint.pprint(retrieved_doc)
    
    # Cleanup: delete the test document
    collection.delete_one({"_id": insert_result.inserted_id})
    print("Test document deleted.")

if __name__ == "__main__":
    test_db_connection()
