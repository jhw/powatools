import base64
import decimal
import json

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            float_val = float(obj)
            if float_val.is_integer():
                return int(float_val)
            else:
                return float_val
        return super().default(obj)

def assert_GET_parameters(parameters):
    def decorator(fn):
        def wrapped(event, context = None, **kwargs):
            if "queryStringParameters" not in event:
                raise RuntimeError("event is missing querystring")
            missing = []
            for parameter in parameters:
                if parameter not in event["queryStringParameters"]:
                    missing.append(parameter)
            if missing != []:
                raise RuntimeError("event is missing %s parameters" % ", ".join(missing))
            return fn(event, context, **kwargs)
        return wrapped
    return decorator

def parse_POST_body(event):
    payload = event["body"]
    if ("isBase64Encoded" in event and
        event["isBase64Encoded"]):
        payload = base64.b64decode(payload).decode("utf-8")
    return json.loads(payload)

def CORS_headers(method):
    def decorator(fn):
        def wrapped(event, *args, **kwargs):
            resp = fn(event, *args, **kwargs)
            resp["headers"].update({
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent",
                "Access-Control-Allow-Methods": f"OPTIONS,{method}"
            })
            return resp
        return wrapped
    return decorator

def wrap_apigateway(fn):
    def wrapped(event, *args, **kwargs):
        try:
            resp = fn(event, *args, **kwargs)
            return {"statusCode": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps(resp,
                                       cls = DecimalEncoder,
                                       indent = 2)}
        except RuntimeError as error:
            return {"statusCode": 400,
                    "headers": {"Content-Type": "text/plain"},
                    "body": str(error)}
    return wrapped

if __name__ == "__main__":
    pass
