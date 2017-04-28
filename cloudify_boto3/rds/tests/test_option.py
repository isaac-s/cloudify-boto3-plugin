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

from cloudify_boto3.rds.resources import option

from mock import patch
import unittest

from cloudify.state import current_ctx

from cloudify_boto3.common.tests.test_base import TestBase

# Constants
PARAMETER_OPTION_TH = ['cloudify.nodes.Root',
                       'cloudify.nodes.aws.rds.Option']


class TestRDSOption(TestBase):

    def test_configure(self):
        _test_name = 'test_create_UnknownServiceError'
        _test_node_properties = {
            'use_external_resource': False,
            "resource_id": "dev-db-option-group",
            "resource_config": {
                "kwargs": {
                    "Port": 21212
                }
            }
        }

        _ctx = self.get_mock_ctx(
            _test_name,
            test_properties=_test_node_properties,
            test_runtime_properties={},
            type_hierarchy=PARAMETER_OPTION_TH
        )
        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('rds')
        with patch('boto3.client', fake_boto):
            option.configure(ctx=_ctx, resource_config=None, iface=None)

            fake_boto.assert_not_called()

            self.assertEqual(
                _ctx.instance.runtime_properties, {
                    'resource_config': {
                        "Port": 21212
                    }
                }
            )

    def test_configure_without_resource_id(self):
        _test_name = 'test_create_UnknownServiceError'
        _test_node_properties = {
            'use_external_resource': False,
            "resource_config": {
                'OptionName': 'OptionName',
                "kwargs": {
                    "Port": 21212
                }
            }
        }

        _ctx = self.get_mock_ctx(
            _test_name,
            test_properties=_test_node_properties,
            test_runtime_properties={},
            type_hierarchy=PARAMETER_OPTION_TH
        )
        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('rds')
        with patch('boto3.client', fake_boto):
            option.configure(ctx=_ctx, resource_config=None, iface=None)

            self.assertEqual(
                _ctx.instance.runtime_properties, {
                    'aws_resource_id': 'OptionName',
                    'resource_config': {
                        'OptionName': 'OptionName',
                        "Port": 21212
                    }
                }
            )


if __name__ == '__main__':
    unittest.main()
