from decimal import Decimal
from powatools.apigateway import wrap_apigateway, CORS_headers, parse_POST_body

import base64
import json
import unittest

class ApiGatewayTest(unittest.TestCase):

    def test_wrap_apigateway_200(self):
        @wrap_apigateway
        def handler(event, context = None):
            return {"hello": "world"}
        resp = handler(event = {})
        self.assertTrue("statusCode" in resp)
        self.assertEqual(resp["statusCode"], 200)
        self.assertTrue("headers" in resp)
        self.assertTrue("Content-Type" in resp["headers"])
        self.assertEqual(resp["headers"]["Content-Type"], "application/json")
        self.assertTrue("body" in resp)
        body = json.loads(resp["body"])
        self.assertTrue("hello" in body)
        self.assertEqual(body["hello"], "world")

    def test_wrap_apigateway_400(self):
        @wrap_apigateway
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

    def test_CORS_headers(self, method = "GET"):
        @CORS_headers(method)               
        @wrap_apigateway
        def handler(event, context = None):
            return {"hello": "world"}
        resp = handler(event = {})
        self.assertTrue("statusCode" in resp)
        self.assertTrue("headers" in resp)
        headers = resp["headers"]
        for header in ["Content-Type",
                       "Access-Control-Allow-Methods"]:
            self.assertTrue(header in headers)
        self.assertTrue(method in headers["Access-Control-Allow-Methods"])
        self.assertTrue("body" in resp)

    def test_decimal_encoder(self):
        @wrap_apigateway
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

    def test_parse_POST_body(self):
        event = {"body": base64.b64encode(json.dumps({"hello": "world"}).encode("utf-8")),
                 "isBase64Encoded": True}
        body = parse_POST_body(event)
        self.assertTrue("hello" in body)
        self.assertEqual(body["hello"], "world")
            
if __name__ == "__main__":
    unittest.main()
        
