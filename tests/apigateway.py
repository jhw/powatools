from powatools.apigateway import wrap_apigateway

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

if __name__ == "__main__":
    unittest.main()
        
