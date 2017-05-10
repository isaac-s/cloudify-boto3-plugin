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

import unittest
from cloudify_boto3.common.tests.test_base import TestBase
from mock import MagicMock

from cloudify.mocks import MockCloudifyContext
from cloudify.state import current_ctx
from cloudify.exceptions import NonRecoverableError

from cloudify_boto3.common import utils


class TestUtils(TestBase):

    def test_get_resource_id(self):
        _test_name = 'test_get_resource_id'
        _test_node_properties = {
            'use_external_resource': False
        }
        _test_runtime_properties = {
            'resource_config': {}
        }
        _ctx = self.get_mock_ctx(
            _test_name,
            test_properties=_test_node_properties,
            test_runtime_properties=_test_runtime_properties,
            type_hierarchy=['cloudify.nodes.Root']
        )
        current_ctx.set(_ctx)
        self.assertEqual(utils.get_resource_id(), None)

        with self.assertRaises(NonRecoverableError):
            utils.get_resource_id(raise_on_missing=True)

    def test_get_resource_arn(self):
        _test_name = 'test_get_resource_arn'
        _test_node_properties = {
            'use_external_resource': False
        }
        _test_runtime_properties = {
            'resource_config': {}
        }
        _ctx = self.get_mock_ctx(
            _test_name,
            test_properties=_test_node_properties,
            test_runtime_properties=_test_runtime_properties,
            type_hierarchy=['cloudify.nodes.Root']
        )
        current_ctx.set(_ctx)
        self.assertEqual(utils.get_resource_arn(), None)

        with self.assertRaises(NonRecoverableError):
            utils.get_resource_arn(raise_on_missing=True)

    def test_update_resource_id(self):
        mock_instance = MagicMock()

        mock_instance.runtime_properties = {}

        utils.update_resource_id(mock_instance, 'val')

        self.assertEqual(mock_instance.runtime_properties,
                         {'aws_resource_id': 'val'})

    def test_update_resource_arn(self):
        mock_instance = MagicMock()

        mock_instance.runtime_properties = {}

        utils.update_resource_arn(mock_instance, 'val')

        self.assertEqual(mock_instance.runtime_properties,
                         {'aws_resource_arn': 'val'})

    def test_get_parent_resource_id_empty(self):
        mock_instance = MagicMock()
        mock_instance.relationships = []

        self.assertEqual(
            utils.get_parent_resource_id(mock_instance,
                                         raise_on_missing=False),
            None
        )

    def test_get_parent_resource_id(self):
        mock_child = MagicMock()
        mock_child.type_hierarchy = 'some_type'
        mock_child.target.instance.runtime_properties = {
            'aws_resource_id': 'a'
        }

        mock_instance = MockCloudifyContext(
            'parent_id',
            deployment_id='deployment_id',
            properties={'a': 'b'},
            runtime_properties={'c': 'd'},
            relationships=[mock_child]
        )

        current_ctx.set(mock_instance)

        with self.assertRaises(NonRecoverableError):
            utils.get_parent_resource_id(mock_instance.instance)

        self.assertEqual(
            utils.get_parent_resource_id(mock_instance.instance, 'some_type'),
            'a'
        )

    def test_is_node_type(self):

        node = MagicMock()
        node.type_hierarchy = ['cloudify.nodes.Root', 'cloudify.nodes.Network']

        self.assertTrue(utils.is_node_type(node, 'cloudify.nodes.Root'))
        self.assertFalse(utils.is_node_type(node, 'cloudify.nodes.Compute'))

    def test_get_ancestor_resource_id_empty(self):
        mock_instance = MagicMock()
        mock_instance.relationships = []

        self.assertEqual(
            utils.get_ancestor_resource_id(
                mock_instance, 'cloudify.nodes.Root', raise_on_missing=False
            ), None
        )


if __name__ == '__main__':
    unittest.main()
