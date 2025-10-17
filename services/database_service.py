from flask_pymongo import PyMongo
from flask import Flask, current_app # We only need current_app

mongo = PyMongo()

def init_db(app: Flask):
    """Initializes the PyMongo extension with the Flask app."""
    if not app.config.get("MONGO_URI"):
        raise ValueError("MONGO_URI is not set in Flask app config. Check your .env and config.py.")
    
    # It's important to set the MONGO_URI in the app's config before initializing mongo
    app.config["MONGO_URI"] = app.config.get("MONGO_URI") 
    mongo.init_app(app)
    print("MongoDB Initialized successfully.")

def get_db():
    """
    Returns the MongoDB database client associated with the current application context.
    `mongo.db` automatically uses `current_app` internally.
    If `mongo.db` returns None, it indicates a deeper issue, usually with the connection.
    """
    db_client = mongo.db
    if db_client is None:
        # This error message is crucial for debugging the real issue: connection failure.
        raise RuntimeError("MongoDB database client is None. "
                           "This usually indicates a connection failure. "
                           "Check MONGO_URI in .env, MongoDB Atlas IP whitelist, and network connectivity.")
    return db_client

def get_collection(collection_name: str):
    """Returns a specific MongoDB collection."""
    return get_db()[collection_name]