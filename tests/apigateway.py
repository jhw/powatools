from decimal import Decimal
from powatools.apigateway import wrap_apigateway, handle_POST_body,  assert_GET_parameters

import base64
import json
import unittest

HelloWorldSchema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "hello": {
            "type": "string",
            "enum": ["world"]
        }
    },
    "required": ["hello"],
    "additionalProperties": False
}

class ApiGatewayTest(unittest.TestCase):

    def test_wrap_apigateway_200(self, cors_method = "GET"):
        @wrap_apigateway(cors_method)
        def handler(event, context = None):
            return {"hello": "world"}
        resp = handler(event = {})
        self.assertTrue("statusCode" in resp)
        self.assertEqual(resp["statusCode"], 200)
        self.assertTrue("headers" in resp)
        headers = resp["headers"]
        for header in ["Content-Type",
                       "Access-Control-Allow-Methods"]:
            self.assertTrue(header in headers)
        self.assertTrue(cors_method in headers["Access-Control-Allow-Methods"])
        self.assertTrue("body" in resp)
        body = json.loads(resp["body"])
        self.assertTrue("hello" in body)
        self.assertEqual(body["hello"], "world")

    def test_wrap_apigateway_400(self):
        @wrap_apigateway()
        def handler(event, context = None):
            raise RuntimeError("oops")
        resp = handler(event = {})
        self.assertTrue("statusCode" in resp)
        self.assertEqual(resp["statusCode"], 400)
        self.assertTrue("headers" in resp)
        self.assertTrue("Content-Type" in resp["headers"])
        self.assertEqual(resp["headers"]["Content-Type"], "text/plain")
        self.assertTrue("body" in resp)
        self.assertEqual(resp["body"], "oops")

    def test_decimal_encoder(self):
        @wrap_apigateway()
        def handler(event, context = None):
            return {"int": Decimal("1"),
                    "float": Decimal("1.1")}
        resp = handler(event = {})
        self.assertTrue("statusCode" in resp)
        self.assertEqual(resp["statusCode"], 200)
        self.assertTrue("body" in resp)
        body = json.loads(resp["body"])
        for key in ["int", "float"]:
            self.assertTrue(isinstance(body[key], eval(key)))

    def test_handle_POST_body_200(self, schema = HelloWorldSchema):
        @wrap_apigateway()
        @handle_POST_body(schema)
        def handler(event, context = None):
            return event["json-body"]
        event = {"body": base64.b64encode(json.dumps({"hello": "world"}).encode("utf-8")),
                 "isBase64Encoded": True}
        resp = handler(event = event)
        self.assertTrue("statusCode" in resp)
        self.assertEqual(resp["statusCode"], 200)
        self.assertTrue("body" in resp)
        body = json.loads(resp["body"])
        self.assertTrue("hello" in body)
        self.assertEqual(body["hello"], "world")

    def test_handle_POST_body_400_bad_json(self):
        @wrap_apigateway()
        @handle_POST_body()
        def handler(event, context = None):
            return event["json-body"]
        event = {"body": base64.b64encode("garbage".encode("utf-8")),
                 "isBase64Encoded": True}
        resp = handler(event = event)
        self.assertTrue("statusCode" in resp)
        self.assertEqual(resp["statusCode"], 400)
        self.assertTrue("body" in resp)
        self.assertTrue("error json- loading POST body" in resp["body"])

    def test_handle_POST_body_400_bad_data(self, schema = HelloWorldSchema):
        @wrap_apigateway()
        @handle_POST_body(schema)
        def handler(event, context = None):
            return event["json-body"]
        event = {"body": base64.b64encode(json.dumps({"hello": "universe"}).encode("utf-8")),
                 "isBase64Encoded": True}
        resp = handler(event = event)
        self.assertTrue("statusCode" in resp)
        self.assertEqual(resp["statusCode"], 400)
        self.assertTrue("body" in resp)
        self.assertTrue("error validating schema" in resp["body"])

    def test_assert_GET_parameters_200(self):
        @wrap_apigateway()
        @assert_GET_parameters({"hello": "world"})
        def handler(event, context = None):
            return event["queryStringParameters"]
        event = {"queryStringParameters": {"hello": "world"}}
        resp = handler(event = event)
        self.assertTrue("statusCode" in resp)
        self.assertEqual(resp["statusCode"], 200)

    def test_assert_GET_parameters_400_missing(self):
        @wrap_apigateway()
        @assert_GET_parameters({"hello": "world"})
        def handler(event, context = None):
            return event["queryStringParameters"]
        event = {"queryStringParameters": {"foo": "bar"}}
        resp = handler(event = event)
        self.assertTrue("statusCode" in resp)
        self.assertEqual(resp["statusCode"], 400)
        self.assertTrue("body" in resp)
        self.assertTrue("missing" in resp["body"])

    def test_assert_GET_parameters_400_invalid(self):
        @wrap_apigateway()
        @assert_GET_parameters({"hello": "world"})
        def handler(event, context = None):
            return event["queryStringParameters"]
        event = {"queryStringParameters": {"hello": "earth"}}
        resp = handler(event = event)
        self.assertTrue("statusCode" in resp)
        self.assertEqual(resp["statusCode"], 400)
        self.assertTrue("body" in resp)
        self.assertTrue("invalid" in resp["body"])
        
if __name__ == "__main__":
    unittest.main()
        
