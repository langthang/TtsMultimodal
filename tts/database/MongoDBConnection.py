from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from bson import ObjectId
from AppConfig import AppConfig

class MongoDBConnection:
    """MongoDB connection manager class."""
    _instance = None

    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(MongoDBConnection, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize MongoDB connection if not already initialized."""
        if self._initialized:
            return
            
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.collection: Optional[Collection] = None
        self.config = AppConfig()
        self._initialized = True

    def connect(self, connection_string: str = "mongodb://localhost:27017/", 
                database: str = None,
                collection: str = "conversations") -> None:
        """
        Connect to MongoDB and set up database and collection.
        
        Args:
            connection_string: MongoDB connection string
            database: Database name
            collection: Collection name
        """

         # Load database name from environment if not provided
        if database is None:
            database = self.config.database_name

        try:
            print(f"Attempting to connect to MongoDB with: {connection_string}")
            self.client = MongoClient(connection_string)
            self.db = self.client[database]
            self.collection = self.db[collection]
            # Test the connection
            self.client.server_info()
            print(f"Successfully connected to MongoDB: {database}.{collection}")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            raise

    def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            self.collection = None
            print("Disconnected from MongoDB")

    def get_conversation_by_id(self, conversation_id: str) -> dict:
        """
        Retrieve a conversation document by its ID.
        
        Args:
            conversation_id: The ID of the conversation to retrieve
            
        Returns:
            The conversation document or None if not found
        """
        if self.collection is None:
            raise RuntimeError("MongoDB connection not established")
            
        try:
            object_id = ObjectId(conversation_id)
            doc = self.collection.find_one({"_id": object_id})
            if doc:
                print(f"Document found: {doc}")
                # Convert ObjectId to string for JSON serialization
                doc['_id'] = str(doc['_id'])
            else:
                print(f"No document found with _id: {object_id}")
                # Let's check if the document exists with a different ID format
                alt_doc = self.collection.find_one({"document_id": conversation_id})
                if alt_doc:
                    print(f"Document found using document_id field instead: {alt_doc}")
                    return alt_doc
            return doc
        except Exception as e:
            print(f"Error retrieving document: {e}")
            return None

    def get_all_conversations(self) -> list:
        """
        Retrieve all conversation documents.
        
        Returns:
            List of all conversation documents
        """
        if self.collection is None:
            raise RuntimeError("MongoDB connection not established")
            
        docs = list(self.collection.find())
        # Convert ObjectId to string for JSON serialization
        for doc in docs:
            doc['_id'] = str(doc['_id'])
        return docs

    def insert_conversation(self, conversation_data: dict) -> str:
        """
        Insert a new conversation document.
        
        Args:
            conversation_data: The conversation data to insert
            
        Returns:
            The ID of the inserted document as string
        """
        if self.collection is None:
            raise RuntimeError("MongoDB connection not established")
            
        # Remove _id if exists to let MongoDB generate a new one
        conversation_data.pop('_id', None)
        result = self.collection.insert_one(conversation_data)
        return str(result.inserted_id)

    def update_conversation(self, conversation_id: str, conversation_data: dict) -> bool:
        """
        Update an existing conversation document.
        
        Args:
            conversation_id: The ID of the conversation to update
            conversation_data: The new conversation data
            
        Returns:
            True if update was successful
            
        Raises:
            RuntimeError: If MongoDB connection is not established
            ValueError: If conversation_id is not a valid ObjectId
            Exception: If any other error occurs during update
        """
        if self.collection is None:
            raise RuntimeError("MongoDB connection not established")
            
        try:
            # Convert string ID to ObjectId
            try:
                object_id = ObjectId(conversation_id)
            except Exception as e:
                raise ValueError(f"Invalid conversation_id format: {e}")
            
            # Remove _id from update data if exists
            conversation_data.pop('_id', None)
            conversation_data.pop('document_id', None)
            
            result = self.collection.update_one(
                {"_id": object_id},
                {"$set": conversation_data}
            )
            
            if result.matched_count == 0:
                raise Exception(f"No document found with ID: {conversation_id}")
                
            if result.modified_count == 0:
                raise Exception(f"Document found but no changes were made. This might indicate the data is identical to what's already stored.")
                
            return True
        except Exception as e:
            # Re-raise the exception to propagate it to the caller
            raise Exception(f"Error updating document: {e}")

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation document.
        
        Args:
            conversation_id: The ID of the conversation to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        if self.collection is None:
            raise RuntimeError("MongoDB connection not established")
            
        try:
            object_id = ObjectId(conversation_id)
            result = self.collection.delete_one({"_id": object_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False 