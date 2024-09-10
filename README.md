
# MongoDB Sanity Check Script

This Python script performs comprehensive sanity checks on a MongoDB cluster. It includes connection validation, replica set status checks, collection validation, index health, and basic data validation. The script also supports customizable verbosity levels for controlling the amount of information displayed.

## Features

- **Connection Check**: Ensures the connection to MongoDB is successful.
- **Ping Command**: Verifies that MongoDB responds to a basic ping command.
- **Replica Set Status**: Checks the health and state of the replica set members (if applicable).
- **Collection Validation**: Validates the structure and integrity of each collection.
- **Index Health Check**: Lists the indexes on each collection and ensures they are functioning.
- **Data Sampling**: Reads a sample document from one collection to verify data integrity.
- **Verbosity Levels**: Allows control over the logging level (`error`, `warning`, or `info`).

## Requirements

- Python 3.x
- pymongo library

You can install the required Python dependencies with the following command:

```bash
pip install pymongo
```

## Usage

1. **Run the script with default verbosity (`info`)**:

   ```bash
   python sanity_check.py --uri "your_mongodb_atlas_uri"
   ```

2. **Run the script with warnings and errors only**:

   ```bash
   python sanity_check.py --uri "your_mongodb_atlas_uri" --verbosity warning
   ```

3. **Run the script with errors only**:

   ```bash
   python sanity_check.py --uri "your_mongodb_atlas_uri" --verbosity error
   ```

If the MongoDB URI is not provided via the command-line, the script will check for an environment variable `MONGO_URI` and if it's not found, it will prompt you to enter it interactively.

### Command-Line Options

- `--uri` or `-u`: Provide the MongoDB connection URI. If omitted, the script will check the `MONGO_URI` environment variable.
- `--verbosity` or `-v`: Set the verbosity level. Choose from:
  - `error`: Show errors only.
  - `warning`: Show warnings and errors.
  - `info`: Show all logs (default).

## Example

Run the script with the MongoDB URI and the default verbosity level (`info`):

```bash
python sanity_check.py --uri "mongodb+srv://user:password@cluster.mongodb.net"
```

Run the script with warnings and errors only:

```bash
python sanity_check.py --uri "mongodb+srv://user:password@cluster.mongodb.net" --verbosity warning
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
