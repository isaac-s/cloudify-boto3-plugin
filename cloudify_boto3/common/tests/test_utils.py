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


if __name__ == '__main__':
    unittest.main()
