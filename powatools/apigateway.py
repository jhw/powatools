import base64
import decimal
import json
import jsonschema
import re

def assert_GET_parameters(patterns):
    def decorator(fn):
        def wrapped(event, context = None, **kwargs):
            if "queryStringParameters" not in event:
                raise RuntimeError("event is missing querystring")
            parameters, errors = event["queryStringParameters"], []
            for key in patterns:
                if key not in parameters:
                    errors.append(key)
            if errors != []:
                raise RuntimeError("missing parameters - %s" % ", ".join(errors))
            errors = []
            for key, pattern in patterns.items():
                if not re.search(pattern, parameters[key]):
                    errors.append(key)
            if errors != []:
                raise RuntimeError("invalid parameters - %s" % ", ".join(errors))
            return fn(event, context, **kwargs)
        return wrapped
    return decorator

def handle_POST_body(schema = None):
    def decode_body(event):
        if "body" not in event:
            raise RuntimeError("POST body not found in event")
        body = event["body"]
        if ("isBase64Encoded" in event and
            event["isBase64Encoded"]):
            try:
                body = base64.b64decode(body).decode("utf-8")
            except:
                raise RuntimeError("error base64- decoding POST body")
        return body
    def parse_json(body):
        try:
            return json.loads(body)
        except:
            raise RuntimeError("error json- loading POST body")
    def validate_schema(struct, schema):
        try:
            jsonschema.validate(instance = struct,
                                schema = schema)
        except jsonschema.exceptions.ValidationError as error:
            raise RuntimeError(f"error validating schema against POST body: {error}")
    def decorator(fn):
        def wrapped(event, *args, **kwargs):
            body = parse_json(decode_body(event))
            if schema:
                validate_schema(struct = body,
                                schema = schema)
            event["json-body"] = body
            return fn(event, *args, **kwargs)
        return wrapped
    return decorator

def wrap_apigateway(cors_method = None):
    class DecimalEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, decimal.Decimal):
                float_val = float(obj)
                if float_val.is_integer():
                    return int(float_val)
                else:
                    return float_val
            return super().default(obj)
    def decorator(fn):
        headers = {}
        if cors_method:
            headers.update({
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent",
                "Access-Control-Allow-Methods": f"OPTIONS,{cors_method}"
            })
        def wrapped(event, *args, **kwargs):
            try:
                resp = fn(event, *args, **kwargs)
                headers["Content-Type"] = "application/json"
                return {"statusCode": 200,
                        "headers": headers,
                        "body": json.dumps(resp,
                                           cls = DecimalEncoder,
                                           indent = 2)}
            except RuntimeError as error:
                headers["Content-Type"] = "text/plain"
                return {"statusCode": 400,
                        "headers": headers,
                        "body": str(error)}
        return wrapped
    return decorator

if __name__ == "__main__":
    pass
