import random
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key,Attr

class FashionDatabase:
    def __init__(self,name='fashion-items'):
        self.name = name
        self.schema = [{'AttributeName':'item-id','KeyType':'HASH'}]
        self.gs_indexes = [{'IndexName':'CategoriesIndex',
                           'KeySchema':
                               [{'AttributeName':'item-id','KeyType':'HASH'}],
                           'Projection':{'ProjectionType':'INCLUDE',
                                'NonKeyAttributes':['category','subcategory']},
                           'ProvisionedThroughput': {'ReadCapacityUnits':1,
                                                     'WriteCapacityUnits':1}}]
        self.attr_def = [{'AttributeName':'item-id','AttributeType':'S'}]
        self.provisions = {'ReadCapacityUnits': 2,'WriteCapacityUnits': 2}

    def connect(self):
        dynamodb = boto3.resource('dynamodb')
        self.db = dynamodb.Table(self.name)
        print(self.db.creation_date_time)

    def add_item(self,content):
        content['item-id'] = datetime.now().strftime('%Y%m%d%H%M%S')+ '-' +\
                             format(random.randint(0, 9999), "04")
        self.db.put_item(Item=content)

class BrandsDatabase:
    def __init__(self,name='brands-scraping'):
        self.name = name
        self.dynamodb = boto3.resource('dynamodb')
        self.client = boto3.client('dynamodb')
        self.db = self.dynamodb.Table(self.name)
        print(self.db.creation_date_time)

    def get_brands_letter(self,letter):
        fe = Attr('letter').eq(letter)
        response = self.db.scan(FilterExpression=fe)
        return response['Items']

    def set_brand_scraped(self,id):
        self.db.update_item(Key={'brand-id':id},
                                UpdateExpression="SET scraped = :val",
                                ExpressionAttributeValues={":val":True})