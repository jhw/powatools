import json

def key_exists(s3, bucket_name, key):
    try:
        s3.head_object(Bucket = bucket_name,
                       Key = key)
        return True
    except:
        return False

def get_json(s3, bucket_name, key):
    return json.loads(s3.get_object(Bucket = bucket_name,
                                    Key = key)["Body"].read().decode("utf-8"))

def put_json(s3, bucket_name, key, struct):
    return s3.put_object(Bucket = bucket_name,
                         Key = key,
                         Body = json.dumps(struct),
                         ContentType = "application/json")

def delete_object(s3, bucket_name, key):
    return s3.delete_object(Bucket = bucket_name,
                            Key = key)

if __name__ == "__main__":
    pass
