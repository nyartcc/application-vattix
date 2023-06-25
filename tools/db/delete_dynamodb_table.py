import boto3

"""
This script allows you to delete all items from a DynamoDB table.
You need to specify the name of the table in the main() function below.

WARNING: This script will delete all items from the specified table!

Usage:
    python dynamodb_delete_all_items.py
"""

# Initialize a DynamoDB client
dynamodb = boto3.resource('dynamodb')


def get_primary_key_names(table_name):
    # Use DynamoDB client to get table description
    client = boto3.client('dynamodb')
    response = client.describe_table(TableName=table_name)

    # Extract the primary key names
    key_names = {}
    for key_schema in response['Table']['KeySchema']:
        if key_schema['KeyType'] == 'HASH':
            key_names['partition_key'] = key_schema['AttributeName']
        if key_schema['KeyType'] == 'RANGE':
            key_names['sort_key'] = key_schema['AttributeName']
    return key_names


def delete_all_items(table_name):
    # Get the table
    table = dynamodb.Table(table_name)

    # Get primary key names
    primary_key_names = get_primary_key_names(table_name)

    # Scan all items
    response = table.scan()
    items = response['Items']
    delete_counter = 0

    # Get a confirmation from the user
    print(f"Are you sure you want to delete all {len(items)} items from the table '{table_name}'? (yes/no)")
    confirm = input()

    if confirm.lower() != "yes":
        print("Aborted.")
        return

    # Check if there are any items to delete
    if len(items) == 0:
        print("No items to delete. Aborted.")
        return

    # Iterate over each item
    for item in items:
        # Prepare the primary key
        key = {key_name: item[key_name] for key_name in primary_key_names.values()}

        # Delete the item
        try:
            table.delete_item(Key=key)
            delete_counter += 1
            if delete_counter % 15 == 0:
                remaining = len(items) - delete_counter
                print(f"Deleted {delete_counter} items so far ({remaining} remaining)")
        except Exception as e:
            print(f"Error deleting {key}: {e}")

    print(f"{delete_counter} items deleted successfully.")


if __name__ == '__main__':
    delete_all_items('dev_vattix_controller_sessions')
