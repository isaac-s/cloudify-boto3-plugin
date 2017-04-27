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
from cloudify_boto3.iam import IAMBase


class TestIAMBase(TestBase):

    def setUp(self):
        self.base = IAMBase("ctx_node", resource_id=True,
                            client=True, logger=None)

    def test_properties(self):
        with self.assertRaises(NotImplementedError):
            self.base.properties()

    def test_status(self):
        with self.assertRaises(NotImplementedError):
            self.base.status()

    def test_create(self):
        with self.assertRaises(NotImplementedError):
            self.base.create(None)

    def test_delete(self):
        with self.assertRaises(NotImplementedError):
            self.base.delete(None)


if __name__ == '__main__':
    unittest.main()
