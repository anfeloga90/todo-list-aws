# from pprint import pprint
import warnings
import unittest
import boto3
from moto import mock_dynamodb2
import sys
import os
import json
from botocore.exceptions import ClientError

@mock_dynamodb2
def mock_table(self):
    print ('---------------------')
    print ('Mocking table')
    from src.todoList import get_table
    from unittest.mock import Mock
    
    self.table = get_table(self.dynamodb)
    self.table = Mock()
    print ('Table Mocked')
    
    from botocore.exceptions import ClientError
    self.dbException = ClientError({'Error': {'Code': 'MockedException', 'Message': 'This is a Mock'}},
        os.environ['DYNAMODB_TABLE'])
    print ('DB mock Exception ready')
    
@mock_dynamodb2
class TestDatabaseFunctions(unittest.TestCase):
    def setUp(self):
        print ('---------------------')
        print ('Start: setUp')
        warnings.filterwarnings( "ignore", category=ResourceWarning, message="unclosed.*<socket.socket.*>")
        warnings.filterwarnings( "ignore", category=DeprecationWarning, message="callable is None.*")
        warnings.filterwarnings( "ignore", category=DeprecationWarning, message="Using or importing.*")
        """Create the mock database and table"""
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.is_local = 'true'
        self.uuid = "123e4567-e89b-12d3-a456-426614174000"
        self.text = "Aprender DevOps y Cloud en la UNIR"
        from src.todoList import create_todo_table
        self.table = create_todo_table(self.dynamodb)
        self.dbException = None
        #self.table_local = create_todo_table()
        print ('End: setUp')

    def tearDown(self):
        print ('---------------------')
        print ('Start: tearDown')
        """Delete mock database and table after test is run"""
        self.table.delete()
        print ('Table deleted succesfully')
        #self.table_local.delete()
        self.dynamodb = None
        print ('End: tearDown')

    def test_table_exists(self):
        print ('---------------------')
        print ('Start: test_table_exists')
        self.assertTrue(self.table)  # check if we got a result
        #self.assertTrue(self.table_local)  # check if we got a result

        print('Table name:' + self.table.name)
        tableName = os.environ['DYNAMODB_TABLE'];
        # check if the table name is 'ToDo'
        self.assertIn(tableName, self.table.name)
        #self.assertIn('todoTable', self.table_local.name)
        print ('End: test_table_exists')
        

    def test_put_todo(self):
        print ('---------------------')
        print ('Start: test_put_todo')
        # Testing file functions
        from src.todoList import put_item
        # Table local
        response = put_item(self.text, self.dynamodb)
        print ('Response put_item:' + str(response))
        self.assertEqual(200, response['statusCode'])
        # Table mock
        self.assertRaises(Exception, put_item("", self.dynamodb))
        #self.assertEqual(200, put_item(self.text, self.dynamodb)[
                         #'ResponseMetadata']['HTTPStatusCode'])
        print ('End: test_put_todo')

    def test_put_todo_error(self):
        print ('---------------------')
        print ('Start: test_put_todo_error')
        # Testing file functions
        from src.todoList import put_item
        # Table mock
        self.assertRaises(Exception, put_item("", self.dynamodb))
        self.assertRaises(Exception, put_item("", self.dynamodb))
        print ('End: test_put_todo_error')

    def test_get_todo(self):
        print ('---------------------')
        print ('Start: test_get_todo')
        from src.todoList import get_item
        from src.todoList import put_item

        # Testing file functions
        # Table mock
        responsePut = put_item(self.text, self.dynamodb)
        print ('Response put_item:' + str(responsePut))
        idItem = json.loads(responsePut['body'])['id']
        print ('Id item:' + idItem)
        self.assertEqual(200, responsePut['statusCode'])
        responseGet = get_item(idItem,self.dynamodb)
        print ('Response Get:' + str(responseGet))
        self.assertEqual(self.text,responseGet['text'])
        mock_table(self)
        self.table.get_item.side_effect = self.dbException
        self.assertRaises(Exception, get_item(self.text, self.dynamodb))
        print ('End: test_get_todo')
    
    def test_list_todo(self):
        print ('---------------------')
        print ('Start: test_list_todo')
        from src.todoList import put_item
        from src.todoList import get_items

        # Testing file functions
        # Table mock
        put_item(self.text, self.dynamodb)
        result = get_items(self.dynamodb)
        print ('Response GetItems' + str(result))
        self.assertTrue(len(result) == 1)
        self.assertTrue(result[0]['text'] == self.text)
        print ('End: test_list_todo')


    def test_update_todo(self):
        print ('---------------------')
        print ('Start: test_update_todo')
        from src.todoList import put_item
        from src.todoList import update_item
        from src.todoList import get_item
        updated_text = "Aprender más cosas que DevOps y Cloud en la UNIR"
        # Testing file functions
        # Table mock
        responsePut = put_item(self.text, self.dynamodb)
        print ('Response PutItem' + str(responsePut))
        idItem = json.loads(responsePut['body'])['id']
        print ('Id item:' + idItem)
        result = update_item(idItem, updated_text,
                            "false",
                            self.dynamodb)
        print ('Result Update Item:' + str(result))
        self.assertEqual(result['text'], updated_text)
        print ('End: test_update_todo')


    def test_update_todo_error(self):
        print ('---------------------')
        print ('Start: test_update_todo_error')
        from src.todoList import put_item
        from src.todoList import update_item
        updated_text = "Aprender más cosas que DevOps y Cloud en la UNIR"
        # Testing file functions
        # Table mock
        responsePut = put_item(self.text, self.dynamodb)
        print ('Response PutItem' + str(responsePut))
        self.assertRaises(Exception,update_item(updated_text,"","false",self.dynamodb))
        self.assertRaises(TypeError,update_item("", self.uuid,"false",self.dynamodb))
        self.assertRaises(Exception,update_item(updated_text,self.uuid,"",self.dynamodb))
        mock_table(self)
        self.table.put_item.side_effect = self.dbException
        self.assertRaises(Exception, put_item('id', self.dynamodb))
        mock_table(self)
        self.table.update_item.side_effect = self.dbException
        self.assertRaises(Exception, update_item(updated_text,"","false",self.dynamodb))
        print ('End: test_update_todo_error')

    def test_delete_todo(self):
        print ('---------------------')
        print ('Start: test_delete_todo')
        from src.todoList import delete_item
        from src.todoList import put_item
        from src.todoList import get_items
        # Testing file functions
        # Table mock
        responsePut = put_item(self.text, self.dynamodb)
        print ('Response PutItem' + str(responsePut))
        idItem = json.loads(responsePut['body'])['id']
        print ('Id item:' + idItem)
        delete_item(idItem, self.dynamodb)
        print ('Item deleted succesfully')
        self.assertTrue(len(get_items(self.dynamodb)) == 0)
        print ('End: test_delete_todo')

    def test_delete_todo_error(self):
        print ('---------------------')
        print ('Start: test_delete_todo_error')
        from src.todoList import delete_item
        # Testing file functions
        self.assertRaises(TypeError, delete_item("", self.dynamodb))
        mock_table(self)
        self.table.delete_item.side_effect = self.dbException
        print ('Table mocked for delete_item()')
        self.assertRaises(Exception, delete_item('id', self.dynamodb))
        print ('End: test_delete_todo_error')
        
    def test_get_translation(self):
        print ('---------------------')
        print ('Start: test_get_translation')
        from src.todoList import get_translation
        translation = get_translation(self.text, "en")
        self.assertEqual(self.text, "Aprender DevOps y Cloud en la UNIR")

        print ('End: test_get_translation')


# create
# create_todo_table
# delete

# get

# get_table

# list

if __name__ == '__main__':
    unittest.main()