import os
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import argparse

def get_mongo_uri():
    """
    Retrieves the MongoDB URI from the environment variable 'MONGO_URI'.
    If not found, prompts the user to input the URI.

    Returns:
        str: The MongoDB URI.
    """
    # Attempt to retrieve the URI from the environment variable
    mongo_uri = os.getenv('MONGO_URI')
    
    # If the URI is not found, prompt the user to input it
    if not mongo_uri:
        mongo_uri = input("Please provide your MongoDB Atlas URI: ")
    
    return mongo_uri

def log(message, level, verbosity):
    """
    Logs a message based on the verbosity level set by the user.

    Args:
        message (str): The message to log.
        level (str): The level of the message ('error', 'warning', 'info').
        verbosity (str): The verbosity level set by the user.
    """
    levels = {"error": 0, "warning": 1, "info": 2}
    
    # Log the message if its level is equal to or greater than the set verbosity
    if levels[verbosity] >= levels[level]:
        print(message)

def sanity_checks(uri, verbosity):
    """
    Performs a series of sanity checks on the MongoDB cluster, including:
    - Connection check
    - Server ping check
    - Replica set status
    - Collection validation
    - Index health check
    - Data sampling check
    
    Args:
        uri (str): The MongoDB connection URI.
        verbosity (str): The verbosity level ('error', 'warning', 'info').
    """
    try:
        # Establish connection to MongoDB
        client = MongoClient(uri)
        log("✅ Connected to MongoDB", "info", verbosity)

        # Check if the server is responsive by sending a ping command
        try:
            client.admin.command("ping")
            log("✅ MongoDB is responsive (ping check passed)", "info", verbosity)
        except OperationFailure as e:
            log(f"❌ Ping check failed: {e}", "error", verbosity)
            return

        # Check the replica set status (if applicable)
        try:
            repl_status = client.admin.command("replSetGetStatus")
            log(f"✅ Replica Set Status: {repl_status['myState']} (Primary node: {repl_status['members'][0]['name']})", "info", verbosity)
        except OperationFailure as e:
            log(f"⚠️ Unable to fetch replica set status (may not be a replica set): {e}", "warning", verbosity)

        # List and validate databases and collections
        databases = client.list_database_names()
        log(f"✅ Databases: {databases}", "info", verbosity)

        for db_name in databases:
            db = client[db_name]
            collections = db.list_collection_names()
            log(f"🔍 Validating collections in database: {db_name}", "info", verbosity)

            for collection_name in collections:
                try:
                    # Check if the collection is a view (skip index operations if it is)
                    collection_info = db.command("listCollections", filter={"name": collection_name})
                    if collection_info["cursor"]["firstBatch"][0]["type"] == "view":
                        log(f"⚠️ Skipping index check on {collection_name}: it is a view, not a collection.", "warning", verbosity)
                        continue
                    
                    # Validate the collection structure and integrity
                    validation = db.command({"validate": collection_name})
                    if validation.get("valid", False):
                        log(f"✅ {collection_name} collection is valid.", "info", verbosity)
                    else:
                        log(f"❌ {collection_name} collection validation failed: {validation}", "error", verbosity)
                    
                    # Check the health of indexes for the collection
                    indexes = db[collection_name].index_information()
                    log(f"✅ Indexes for {collection_name}: {indexes}", "info", verbosity)

                except OperationFailure as e:
                    log(f"❌ Failed to validate {collection_name}: {e}", "error", verbosity)

        # Perform a simple data check by sampling a document from one collection
        log("🔍 Checking data from one collection for sanity", "info", verbosity)
        sample_db = client[databases[0]]  # Pick the first database
        sample_collection_name = sample_db.list_collection_names()[0]  # Pick the first collection
        sample_collection = sample_db[sample_collection_name]
        sample_doc = sample_collection.find_one()
        if sample_doc:
            log(f"✅ Sample document from {sample_collection_name}: {sample_doc}", "info", verbosity)
        else:
            log(f"⚠️ No documents found in {sample_collection_name} for sampling", "warning", verbosity)

    except ConnectionFailure as ce:
        log(f"❌ Failed to connect to MongoDB: {ce}", "error", verbosity)
    finally:
        # Ensure the connection to MongoDB is closed
        client.close()
        log("🔒 Connection closed", "info", verbosity)

def main():
    """
    Main function that parses command-line arguments and runs the MongoDB sanity checks
    with the desired verbosity level.
    """
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="MongoDB Comprehensive Sanity Check Script")
    
    # Argument for MongoDB URI
    parser.add_argument('-u', '--uri', type=str, help='MongoDB Atlas URI. If not provided, the script will check the MONGO_URI environment variable.')

    # Argument for verbosity level
    parser.add_argument('-v', '--verbosity', type=str, choices=['error', 'warning', 'info'], default='info', help="Set the verbosity level (default: 'info')")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Get the MongoDB URI from command-line argument, environment variable, or prompt
    mongo_uri = args.uri if args.uri else get_mongo_uri()

    # Run sanity checks with the specified verbosity level
    sanity_checks(mongo_uri, args.verbosity)

if __name__ == "__main__":
    main()
