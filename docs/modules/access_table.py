from __future__ import print_function
from botocore.config import Config
from boto3.dynamodb.conditions import Key
import boto3
import json
import decimal
def lambda_handler(event, context):
    """Fetches rows from a Smalltable.

    Retrieves rows pertaining to the given keys from the Table instance
    represented by table_handle.  String keys will be UTF-8 encoded.

    Args:
      table_handle:
        An open smalltable.Table instance.
      keys:
        A sequence of strings representing the key of each table row to
        fetch.  String keys will be UTF-8 encoded.
      require_all_keys:
        Optional; If require_all_keys is True only rows with values set
        for all keys will be returned.

    Returns:
      A dict mapping keys to the corresponding table row data
      fetched. Each row is represented as a tuple of strings. For
      example:

      {b'Serak': ('Rigel VII', 'Preparer'),
       b'Zim': ('Irk', 'Invader'),
       b'Lrrr': ('Omicron Persei 8', 'Emperor')}

      Returned keys are always bytes.  If a key from the keys argument is
      missing from the dictionary, then that row was not found in the
      table (and require_all_keys must have been False).

    Raises:
      IOError: An error occurred accessing the smalltable.
    """
    
    """
    Retrieves operation and payload from the event and 
    performs dynamo db batch operation processing.

    Args:
        event: An json-lized dict with keys named operation and payload.

            |

            operation: read or write.

            |
                
            payload: If the operation is write, for writing batch of items 
            to the dynamodb,the pyload format has to be:

                .. code-block:: python

                    ## list of items
                    [   
                        {
                            'UserID': string, 
                            'OrderTimestamp': string,
                            "lie_percentage": string,
                            "sit_percentage": string,
                            "stand_percentage": string,
                            "walk_percentage": string,
                            "entry_dict": dict
                        },
                        {
                            'UserID': string, 
                            'OrderTimestamp': string,
                            "lie_percentage": string,
                            "sit_percentage": string,
                            "stand_percentage": string,
                            "walk_percentage": string,
                            "entry_dict": dict
                        },
                    ]

                If the operation is read, you need to provide the partition key
                and the sort key's range to retrive the items from dynamodb.
                the pyload format has to be:

                .. code-block:: python

                    {
                        'key1': string,
                        'key2range':[string, string]
                    }
    
        context: A magical object auto pass by AWS API Gateway

    Returns:

        A dict includes the 'statusCode' and 'headers' and 'body'.

        A response object will than pass by AWS API Gateway and it 
        contains query items or creation result as its content. Use

            .. code-block:: python

                response['content']

        to access the content.

    Raises:
        HTTPError: http errors.

    """
    
    event = json.loads(event['body'])
    operation = event['operation']
    
    #declare table instance
    dynamodb = boto3.resource('dynamodb',  region_name='ap-northeast-1')
    table = dynamodb.Table('User')
    
    if operation == 'create':
        
        with table.batch_writer() as batch:
            for item in event['payload']:
                batch.put_item(Item = item)
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': 'create success'
        }
    elif operation == 'read':

        primary_key1 = 'UserID'
        primary_key2 = 'OrderTimestamp'

        key1 = event['payload']['key1']
        key2range = event['payload']['key2range']
        
        response = table.query(
            KeyConditionExpression= Key(primary_key1).eq(key1)\
            & Key(primary_key2).between(key2range[0], key2range[1])
        )
        

        class DecimalEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, decimal.Decimal):
                    # wanted a simple yield str(o) in the next line,
                    # but that would mean a yield on the line with super(...),
                    # which wouldn't work (see my comment below), so...
                    #return (str(o) for o in [o])
                    return int(o)
                return super(DecimalEncoder, self).default(o)
        

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response['Items'], cls=DecimalEncoder)
        }
        