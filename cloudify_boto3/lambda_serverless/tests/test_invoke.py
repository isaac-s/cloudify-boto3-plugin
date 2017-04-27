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

from cloudify_boto3.lambda_serverless.resources import invoke
from mock import patch, MagicMock

import unittest

from cloudify.manager import DirtyTrackingDict

from cloudify_boto3.common.tests.test_base import TestBase

# Constants
SUBNET_GROUP_I = ['cloudify.nodes.Root', 'cloudify.nodes.aws.lambda.Invoke']
SUBNET_GROUP_F = ['cloudify.nodes.Root', 'cloudify.nodes.aws.lambda.Function']


class TestLambdaInvoke(TestBase):

    def setUp(self):
        super(TestLambdaInvoke, self).setUp()

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

    def test_configure(self):
        _test_name = 'test_configure'
        _test_node_properties = {
            'use_external_resource': False
        }
        _test_runtime_properties = {'resource_config': False}
        ctx = self.get_mock_ctx(_test_name, _test_node_properties,
                                _test_runtime_properties,
                                SUBNET_GROUP_I)
        invoke.configure(ctx=ctx, resource_config=True)
        self.assertTrue(
            ctx.instance.runtime_properties['resource_config'])

    def test_attach_to(self):
        relation_ctx = self._get_relationship_context(SUBNET_GROUP_F)
        with patch(
            'cloudify_boto3.lambda_serverless.resources.invoke.LambdaFunction',
                MagicMock()) as mock:
            invoke.attach_to(ctx=relation_ctx, resource_config=True)
        self.assertTrue(mock.called)
        output = relation_ctx.source.instance.runtime_properties['output']
        self.assertIsInstance(output, MagicMock)

        relation_ctx = self._get_relationship_context(SUBNET_GROUP_I)
        with patch(
            'cloudify_boto3.lambda_serverless.resources.invoke.LambdaFunction',
                MagicMock()) as mock:
            invoke.attach_to(ctx=relation_ctx, resource_config=True)
        self.assertFalse(mock.called)

    def test_detach_from(self):
        relation_ctx = self._get_relationship_context(SUBNET_GROUP_I)
        invoke.detach_from(ctx=relation_ctx, resource_config=None)


if __name__ == '__main__':
    unittest.main()
