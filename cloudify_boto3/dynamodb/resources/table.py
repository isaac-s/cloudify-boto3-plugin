# #######
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
'''
    DynamoDB.Table
    ~~~~~~~~~~~~~~
    AWS DynamoDB Table interface
'''
# Cloudify
from cloudify_boto3.common import decorators, utils
from cloudify_boto3.dynamodb import DynamoDBBase
# Boto
from botocore.exceptions import ClientError

RESOURCE_TYPE = 'DynamoDB Table'


class DynamoDBTable(DynamoDBBase):
    '''
        AWS DynamoDB Table interface
    '''
    def __init__(self, ctx_node, resource_id=None, client=None, logger=None):
        DynamoDBBase.__init__(self, ctx_node, resource_id, client, logger)
        self.type_name = RESOURCE_TYPE

    @property
    def properties(self):
        '''Gets the properties of an external resource'''
        resources = None
        try:
            resources = self.client.describe_table(
                TableName=self.resource_id)
        except ClientError:
            pass
        if not resources or not resources.get('Table'):
            return None
        return resources['Table']

    @property
    def status(self):
        '''Gets the status of an external resource'''
        props = self.properties
        if props and 'TableStatus' in props:
            return props['TableStatus']
        return None

    def create(self, params):
        '''
            Create a new AWS DynamoDB Table.
        '''
        self.logger.debug('Creating %s with parameters: %s'
                          % (self.type_name, params))
        res = self.client.create_table(**params)
        self.logger.debug('Response: %s' % res)
        self.update_resource_id(res['TableDescription']['TableName'])
        return self.resource_id, res['TableDescription']['TableArn']

    def delete(self, params=None):
        '''
            Deletes an existing AWS DynamoDB Table.
        '''
        params = params or dict()
        params.update(dict(TableName=self.resource_id))
        self.logger.debug('Deleting %s with parameters: %s'
                          % (self.type_name, params))
        self.client.delete_table(**params)


@decorators.aws_resource(DynamoDBTable, RESOURCE_TYPE)
@decorators.wait_for_status(status_pending=['CREATING', 'UPDATING'],
                            status_good=['ACTIVE'])
def create(ctx, iface, resource_config, **_):
    '''Creates an AWS DynamoDB Table'''
    # Build API params
    resource_config.update(dict(TableName=iface.resource_id))
    # Actually create the resource
    res_id, res_arn = iface.create(resource_config)
    utils.update_resource_id(ctx.instance, res_id)
    utils.update_resource_arn(ctx.instance, res_arn)


@decorators.aws_resource(DynamoDBTable, RESOURCE_TYPE,
                         ignore_properties=True)
@decorators.wait_for_delete(status_pending=['DELETING'])
def delete(iface, resource_config, **_):
    '''Deletes an AWS DynamoDB Table'''
    iface.delete(resource_config)
