# Copyright (c) 2017 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.
from mock import patch, MagicMock
from cloudify_boto3.lambda_serverless.resources import function
import unittest
from io import StringIO
from cloudify.manager import DirtyTrackingDict
from cloudify_boto3.common.tests.test_base import TestBase
from functools import wraps

# Constants
SUBNET_GROUP_I = ['cloudify.nodes.Root', 'cloudify.nodes.aws.lambda.Invoke']
SUBNET_GROUP_F = ['cloudify.nodes.Root', 'cloudify.nodes.aws.lambda.Function']


def mock_decorator(*args, **kwargs):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)
        return decorated_function
    return decorator


class TestLambdaFunction(TestBase):

    def setUp(self):
        super(TestLambdaFunction, self).setUp()

    def _get_relationship_context(self, subnet_group):
        _test_name = 'test_lambda'
        _test_node_properties = {
            'use_external_resource': False,
            'resource_id': 'target'
        }
        _test_runtime_properties = {'resource_config': 'resource',
                                    '_set_changed': True}
        source = self.get_mock_ctx("source_node", _test_node_properties,
                                   DirtyTrackingDict(_test_runtime_properties),
                                   SUBNET_GROUP_I)
        target = self.get_mock_ctx("target_node", _test_node_properties,
                                   DirtyTrackingDict(_test_runtime_properties),
                                   subnet_group)
        return self.get_mock_relationship_ctx(_test_name,
                                              _test_node_properties,
                                              _test_runtime_properties,
                                              source,
                                              target,
                                              SUBNET_GROUP_F)

    def _get_ctx(self):
        _test_name = 'test_properties'
        _test_node_properties = {
            'use_external_resource': False
        }
        _test_runtime_properties = {'resource_config': False}
        return self.get_mock_ctx(_test_name, _test_node_properties,
                                 _test_runtime_properties,
                                 None)

    def test_class_properties(self):
        ctx = self._get_ctx()
        with patch(
            'cloudify_boto3.lambda_serverless.resources.function.LambdaBase',
                MagicMock()):
            fun = function.LambdaFunction(ctx)
            fun.resource_id = 'test_function'
            fake_client = self.make_client_function(
                'get_function',
                return_value={'Configuration':
                              {'FunctionName': 'test_function'}})
            fun.client = fake_client

            result = fun.properties
            self.assertEqual(result, {'FunctionName': 'test_function'})

            fake_client = self.make_client_function(
                'get_function',
                return_value={'Configuration': None})
            fun.client = fake_client
            result = fun.properties
            self.assertIsNone(result)

            fake_client = self.make_client_function(
                'get_function',
                side_effect=self.get_client_error_exception('get_function'))

            fun.client = fake_client
            result = fun.properties
            self.assertIsNone(result)

    def test_class_status(self):
        ctx = self._get_ctx()
        with patch(
            'cloudify_boto3.lambda_serverless.resources.function.LambdaBase',
                MagicMock()):
            fun = function.LambdaFunction(ctx)
            fun.resource_id = 'test_function'
            fake_client = self.make_client_function(
                'get_function',
                return_value={'Configuration':
                              {'FunctionName': 'test_function'}})
            fun.client = fake_client
            status = fun.status
            self.assertEqual(status, 'available')

            fake_client = self.make_client_function(
                'get_function',
                return_value={})
            fun.client = fake_client
            status = fun.status
            self.assertIsNone(status)

    def test_class_create(self):
        ctx = self._get_ctx()
        with patch(
            'cloudify_boto3.lambda_serverless.resources.function.LambdaBase',
                MagicMock()):
            fun = function.LambdaFunction(ctx)
            fun.logger = MagicMock()
            fun.resource_id = 'test_function'
            fake_client = self.make_client_function(
                'create_function',
                return_value={'FunctionArn': 'test_function_arn',
                              'FunctionName': 'test_function'})
            fun.client = fake_client
            res_id, farn = fun.create({'param': 'params'})
            self.assertEqual(res_id, fun.resource_id)
            self.assertEqual(farn, 'test_function_arn')

    def test_class_delete(self):
        ctx = self._get_ctx()
        with patch(
            'cloudify_boto3.lambda_serverless.resources.function.LambdaBase',
                MagicMock()):
            fun = function.LambdaFunction(ctx)
            fun.logger = MagicMock()
            fun.resource_id = 'test_function'
            fake_client = self.make_client_function(
                'delete_function',
                return_value=None)
            fun.client = fake_client
            fun.delete({'param': 'params'})

    def test_class_invoke(self):
        ctx = self._get_ctx()
        with patch(
            'cloudify_boto3.lambda_serverless.resources.function.LambdaBase',
                MagicMock()):
            fun = function.LambdaFunction(ctx)
            fun.logger = MagicMock()
            fun.resource_id = 'test_function'
            fake_client = self.make_client_function(
                'invoke',
                return_value={'Payload': StringIO(u"text")})
            fun.client = fake_client
            result = fun.invoke({'param': 'params'})
            self.assertEqual(result, {'Payload': u'text'})

            fake_client = self.make_client_function(
                'invoke',
                return_value='')
            fun.client = fake_client
            result = fun.invoke({'param': 'params'})
            self.assertEqual(result, '')

    def test_create(self):
        ctx = self._get_ctx()
        with patch('cloudify_boto3.common.decorators.aws_resource',
                   mock_decorator),\
            patch(
                'cloudify_boto3.lambda_serverless.resources.function.LambdaBase',
                MagicMock()):
            fun = function.LambdaFunction(ctx)
            reload(function)
            fun.logger = MagicMock()
            fun.resource_id = 'test_function'
            fake_client = self.make_client_function(
                'create_function',
                return_value={'FunctionArn': 'test_function_arn',
                              'FunctionName': 'test_function'})
            fun.client = fake_client
            function.create(ctx, fun, {})

    def test_delete(self):
        with patch('cloudify_boto3.common.decorators.wait_for_delete',
                   mock_decorator),\
             patch('cloudify_boto3.common.decorators.aws_resource',
                   mock_decorator):
            reload(function)
            iface = MagicMock()
            function.delete(iface, None)
            self.assertTrue(iface.delete.called)

if __name__ == '__main__':
    unittest.main()
