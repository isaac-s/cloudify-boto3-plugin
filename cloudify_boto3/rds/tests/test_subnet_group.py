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

from cloudify_boto3.rds.resources import subnet_group
from botocore.exceptions import UnknownServiceError

from mock import patch, MagicMock
import unittest

from cloudify.state import current_ctx

from cloudify_boto3.common.tests.test_base import TestBase

# Constants
SUBNET_GROUP_TH = ['cloudify.nodes.Root',
                   'cloudify.nodes.aws.rds.SubnetGroup']


class TestRDSSubnetGroup(TestBase):

    def test_create_raises_UnknownServiceError(self):
        _test_name = 'test_create_UnknownServiceError'
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
            type_hierarchy=SUBNET_GROUP_TH
        )
        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('rds')
        with patch('boto3.client', fake_boto):
            with self.assertRaises(UnknownServiceError) as error:
                subnet_group.create(ctx=_ctx, resource_config=None, iface=None)

            self.assertEqual(
                str(error.exception),
                "Unknown service: 'rds'. Valid service names are: ['rds']"
            )

            fake_boto.assert_called_with('rds', region_name=None)

    def test_create(self):
        _test_name = 'test_create'
        _test_node_properties = {
            'use_external_resource': False,
            'resource_id': 'zzzzzz-subnet-group',
            'client_config': {
                'aws_access_key_id': 'xxx',
                'aws_secret_access_key': 'yyy',
                'region_name': 'zzz'
            }
        }
        _test_runtime_properties = {
            'resource_config': {
                'SubnetIds': ['subnet-xxxxxxxx', 'subnet-yyyyyyyy'],
                'DBSubnetGroupDescription': 'MySQL5.7 Subnet Group for Dev',
                'DBSubnetGroupName': 'zzzzzz-subnet-group'
            }
        }
        _ctx = self.get_mock_ctx(
            _test_name,
            test_properties=_test_node_properties,
            test_runtime_properties=_test_runtime_properties,
            type_hierarchy=SUBNET_GROUP_TH
        )

        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('rds')

        with patch('boto3.client', fake_boto):
            fake_client.describe_db_subnet_groups = MagicMock(
                return_value={'DBSubnetGroups': [{
                    'SubnetGroupStatus': 'Complete',
                    'DBSubnetGroup': {
                        'DBSubnetGroupName': 'DBSubnetGroupName',
                        'DBSubnetGroupArn': 'DBSubnetGroupArn'
                    }
                }]}
            )

            fake_client.create_db_subnet_group = MagicMock(
                return_value={'DBSubnetGroup': {
                    'DBSubnetGroupName': 'DBSubnetGroupName',
                    'DBSubnetGroupArn': 'DBSubnetGroupArn'}
                }
            )

            subnet_group.create(ctx=_ctx, resource_config=None, iface=None)

            fake_boto.assert_called_with(
                'rds', aws_access_key_id='xxx', aws_secret_access_key='yyy',
                region_name='zzz'
            )
            fake_client.create_db_subnet_group.assert_called_with(
                DBSubnetGroupDescription='MySQL5.7 Subnet Group for Dev',
                DBSubnetGroupName='zzzzzz-subnet-group',
                SubnetIds=['subnet-xxxxxxxx', 'subnet-yyyyyyyy']
            )
            fake_client.describe_db_subnet_groups.assert_called_with(
                DBSubnetGroupName='DBSubnetGroupName'
            )

            self.assertEqual(
                _ctx.instance.runtime_properties, {
                    'aws_resource_arn': 'DBSubnetGroupArn',
                    'aws_resource_id': 'DBSubnetGroupName',
                    'resource_config': {
                        'DBSubnetGroupDescription':
                                        'MySQL5.7 Subnet Group for Dev',
                        'DBSubnetGroupName': 'zzzzzz-subnet-group',
                        'SubnetIds': ['subnet-xxxxxxxx', 'subnet-yyyyyyyy']
                    }
                }
            )


if __name__ == '__main__':
    unittest.main()
