from moto import mock_s3
from powatools.s3 import key_exists, get_json, put_json, delete_object

import base64
import boto3
import json
import unittest

TestBucket = {"name": "test-bucket"}

@mock_s3
class S3Test(unittest.TestCase):

    def setUp(self, buckets = [TestBucket]):
        def create_bucket(s3, bucket):
            config = {'LocationConstraint': 'EU'}
            s3.create_bucket(Bucket = bucket["name"],
                             CreateBucketConfiguration = config)
        self.s3 = boto3.client("s3")
        for bucket in buckets:
            create_bucket(self.s3, bucket)
            
    def test_json_lifecycle(self,
                            bucket = TestBucket,
                            key = "hello.json"):
        self.assertTrue(not key_exists(s3 = self.s3,
                                       bucket_name = bucket["name"],
                                       key = key))
        # put
        put_json(s3 = self.s3,
                 bucket_name = bucket["name"],
                 key = key,
                 struct = {"hello": "world"})
        self.assertTrue(key_exists(s3 = self.s3,
                                   bucket_name = bucket["name"],
                                   key = key))
        # get
        struct = get_json(s3 = self.s3,
                          bucket_name = bucket["name"],
                          key = key)
        self.assertTrue(isinstance(struct, dict))
        self.assertTrue("hello" in struct)
        # delete
        delete_object(s3 = self.s3,
                      bucket_name = bucket["name"],
                      key = key)
        self.assertTrue(not key_exists(s3 = self.s3,
                                       bucket_name = bucket["name"],
                                       key = key))
        
    def tearDown(self, buckets = [TestBucket]):
        def empty_bucket(s3, bucket):            
            struct = s3.list_objects(Bucket = bucket["name"])
            if "Contents" in struct:
                for obj in struct["Contents"]:
                    s3.delete_object(Bucket = bucket["name"],
                                     Key = obj["Key"])
        def delete_bucket(s3, bucket):
            s3.delete_bucket(Bucket = bucket["name"])
        for bucket in buckets:
            empty_bucket(self.s3, bucket)
            delete_bucket(self.s3, bucket)
        
if __name__ == "__main__":
    unittest.main()

        
