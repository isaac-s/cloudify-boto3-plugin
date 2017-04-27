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

from mock import MagicMock
import unittest

from cloudify.mocks import MockCloudifyContext
from cloudify.state import current_ctx
from botocore.exceptions import UnknownServiceError
from botocore.exceptions import ClientError


class TestBase(unittest.TestCase):

    def tearDown(self):
        current_ctx.clear()
        super(TestBase, self).tearDown()

    def get_mock_ctx(self,
                     test_name,
                     test_properties,
                     test_runtime_properties,
                     type_hierarchy):

        test_node_id = test_name

        ctx = MockCloudifyContext(
            node_id=test_node_id,
            deployment_id=test_name,
            properties=test_properties,
            runtime_properties=test_runtime_properties)

        ctx.node.type_hierarchy = type_hierarchy

        return ctx

    def get_mock_relationship_ctx(self,
                                  deployment_name,
                                  test_properties,
                                  test_runtime_properties,
                                  test_source,
                                  test_target,
                                  type_hierarchy):

        ctx = MockCloudifyContext(
            deployment_id=deployment_name,
            properties=test_properties,
            source=test_source,
            target=test_target,
            runtime_properties=test_runtime_properties)
        return ctx

    def fake_boto_client(self, client_type):
        fake_client = MagicMock()
        if client_type == "rds":
            fake_client.create_db_subnet_group = MagicMock(
                side_effect=UnknownServiceError(
                    service_name=client_type,
                    known_service_names=['rds']
                )
            )
            fake_client.describe_db_subnet_groups = MagicMock(
                side_effect=ClientError(
                    error_response={"Error": {}},
                    operation_name="describe_db_subnet_groups"
                )
            )
        return MagicMock(return_value=fake_client), fake_client
