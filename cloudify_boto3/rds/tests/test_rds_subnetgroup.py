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
import boto3

from mock import patch, MagicMock
import unittest

from cloudify.mocks import MockCloudifyContext
from cloudify.state import current_ctx
from cloudify import exceptions as cfy_exc
from cloudify.exceptions import NonRecoverableError
from botocore.exceptions import UnknownServiceError
from botocore.exceptions import ClientError

# Constants
SUBNET_GROUP_TH = ['cloudify.nodes.Root', 'cloudify.nodes.aws.rds.SubnetGroup']

class TestRDSSubnetGroup(unittest.TestCase):

    def tearDown(self):
        current_ctx.clear()
        super(TestRDSSubnetGroup, self).tearDown()

    def get_mock_ctx(self,
                     test_name,
                     test_properties):

        test_node_id = test_name
        test_properties = test_properties

        ctx = MockCloudifyContext(
            node_id=test_node_id,
            deployment_id=test_name,
            properties=test_properties
        )

        ctx.node.type_hierarchy = SUBNET_GROUP_TH

        return ctx

    def fake_boto_client(self, client_type):
        fake_client = MagicMock()
        if client_type == "rds":
            fake_client.create_db_subnet_group = MagicMock(side_effect=UnknownServiceError(service_name=client_type, known_service_names=['rds']))
            fake_client.describe_db_subnet_groups = MagicMock(side_effect=ClientError(error_response={"Error": {}}, operation_name="describe_db_subnet_groups"))
        return MagicMock(return_value=fake_client), fake_client

    def test_create_raises_UnknownServiceError(self):
        _test_name = 'test_create'
        _test_node_properties = {
            'use_external_resource': False
        }
        _test_instance_runtime_properties = {}
        _ctx = self.get_mock_ctx(_test_name, _test_node_properties)
        current_ctx.set(_ctx)
        fake_boto, fake_client = self.fake_boto_client('rds')
        with patch('boto3.client', fake_boto):
            with self.assertRaises(NonRecoverableError) as error:
                subnet_group.create(ctx=_ctx)

            # RDS Subnet Group ID# "None" no longer exists...
            self.assertFalse(str(error.exception).find(
                'no longer exists'
            ) == -1)

            fake_boto.assert_called_with('rds', region_name=None)


if __name__ == '__main__':
    unittest.main()
