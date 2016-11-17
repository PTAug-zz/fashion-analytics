import random
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Attr

class FashionDatabase:

    """DynamoDB fashion articles database interface class.

    This class is an interface to the NoSQL database on AWS storing
    the fashion articles. It allows communication through simpler
    functions.

    To put an article in the database, use the `add_item` function.

    """

    def __init__(self,name='fashion-items'):
        """Create interface with Fashion items database.

        :param name: name of the database on AWS
        :type name: str
        """
        self.name = name
        dynamodb = boto3.resource('dynamodb')
        self.db = dynamodb.Table(self.name)
        print(self.db.creation_date_time)


    def add_item(self,content):
        """Add the content to the database.

        The content will be put in the database linked to the
        object. An id will be created with the timestamp and a
        number.

        :param content: dictionary to put in the database.
        :type content: dict
        """
        content['item-id'] = datetime.now().strftime('%Y%m%d%H%M%S')+ '-' +\
                             format(random.randint(0, 9999), "04")
        self.db.put_item(Item=content)

class BrandsDatabase:

    """DynamoDB brands database interface class.

    This class is an interface to the NoSQL database on AWS storing
    the brands to scrape.

    To get the brands beginning by a specific letter, use the
    `get_brands_letter` function. To set a brand as scraped, use
    the `set_brand_as_scraped` function.

    """

    def __init__(self,name='brands-scraping'):
        """Create interface with brands database.

        :param name: name of the DynamoDB brands database
        :type name: str
        """
        self.name = name
        self.dynamodb = boto3.resource('dynamodb')
        self.db = self.dynamodb.Table(self.name)
        print(self.db.creation_date_time)

    def get_brands_letter(self,letter):
        """Return brands starting with specified letter.

        Each brand returned has the `brand-id`, `url`, `brand`,
        `letter` and `scraped` attributes.

        :param letter: first letter of the brands wanted
        :type letter: str
        :return: list of brands as dictionaries
        :rtype: list of dict
        """
        fe = Attr('letter').eq(letter)
        response = self.db.scan(FilterExpression=fe)
        return response['Items']

    def set_brand_scraped(self,id):
        """Set the brand of given id as scraped.

        :param id: id of the brand to update
        """
        self.db.update_item(Key={'brand-id':id},
                                UpdateExpression="SET scraped = :val",
                                ExpressionAttributeValues={":val":True})