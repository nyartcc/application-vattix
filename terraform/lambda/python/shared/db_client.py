import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from shared.logger import setup_logger

# Set up logging
logger = setup_logger(__name__)


class DBClient:
    def __init__(self, table_name):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def get_item(self, controller_id):
        response = self.table.get_item(Key={'controller_id': controller_id})
        return response.get('Item')

    def put_item(self, item):
        self.table.put_item(Item=item)

    def update_item(self, item, duration):
        table = self.table
        try:
            table.update_item(
                Key={'controller_id': item['controller_id'], 'logon_time': item['logon_time']},
                UpdateExpression="SET #d = :d, last_updated = :lu",
                ExpressionAttributeNames={
                    "#d": "duration",
                },
                ExpressionAttributeValues={
                    ':d': duration,
                    ':lu': item['last_updated']
                },
                ReturnValues="UPDATED_NEW"
            )

        except ClientError as e:
            logger.error(e.response['Error']['Message'])
        else:
            logger.info(f"[DynamoDB] UpdateItem succeeded: {item['callsign']} ({item['controller_id']}) - "
                        f"Original Duration: {item['original_duration']}, new duration:"
                        f" {duration} - Logon time: {item['logon_time']}")

    def get_all_items(self):
        response = self.table.scan()
        return response.get('Items')
