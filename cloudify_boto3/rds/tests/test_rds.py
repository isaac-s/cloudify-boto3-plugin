########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
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


from os import path
import unittest
from cloudify import mocks as cfy_mocks
from cloudify.state import current_ctx

from cloudify_boto3.rds.resources import option

class TestRDS(unittest.TestCase):

    def _regen_ctx(self):
        self.fake_ctx = cfy_mocks.MockCloudifyContext()
        current_ctx.set(self.fake_ctx)

    def tearDown(self):
        current_ctx.clear()

    def test_RdsOption(self):
        self._regen_ctx()
        option.configure(ctx=self.fake_ctx)
