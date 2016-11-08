import random
import boto3
from datetime import datetime

class FashionDatabase:
    def __init__(self):
        dynamodb = boto3.resource('dynamodb')
        self.db = dynamodb.Table('fashion-products')
        print(self.db.creation_date_time)

    def add_item(self,content):
        content['item-id'] = datetime.now().strftime('%Y%m%d%H%M%S')+ '-' +\
                             format(random.randint(0, 9999), "04")
        self.db.put_item(Item=content)