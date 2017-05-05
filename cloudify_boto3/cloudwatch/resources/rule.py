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
    Cloudwatch.Events.Rule
    ~~~~~~~~~~~~~~
    AWS Cloudwatch Events Rule interface
'''
# Cloudify
from cloudify_boto3.common import decorators, utils
from cloudify_boto3.cloudwatch import AWSCloudwatchBase
from cloudify_boto3.common.connection import Boto3Connection
# Boto
from botocore.exceptions import ClientError

RESOURCE_TYPE = 'Cloudwatch Alarm'
NAME = 'Name'
ARN = 'RuleArn'


class CloudwatchEventsRule(AWSCloudwatchBase):
    '''
        AWS Cloudwatch Events Rule interface
    '''
    def __init__(self, ctx_node, resource_id=None, client=None, logger=None):
        AWSCloudwatchBase.__init__(
            self,
            ctx_node,
            resource_id,
            client or Boto3Connection(ctx_node).client('events'),
            logger)
        self.type_name = RESOURCE_TYPE

    @property
    def properties(self):
        '''Gets the properties of an external resource'''
        params = {NAME: [self.resource_id]}
        try:
            resources = \
                self.client.describe_rule(**params)
        except ClientError:
            pass
        else:
            return resources[0]

    @property
    def status(self):
        '''Gets the status of an external resource'''
        props = self.properties
        if not props:
            return None
        return None

    def create(self, params):
        '''
            Create a new AWS Cloudwatch Events Rule.
        '''
        if not self.resource_id:
            setattr(self, 'resource_id', params.get(NAME))
        self.logger.debug('Creating %s with parameters: %s'
                          % (self.type_name, params))
        res = self.client.put_rule(**params)
        self.logger.debug('Response: %s' % res)
        return res[ARN]

    def delete(self, params=None):
        '''
            Deletes an existing AWS Cloudwatch Events Rule.
        '''
        if NAME not in params.keys():
            params.update({NAME: self.resource_id})
        self.logger.debug('Deleting %s with parameters: %s'
                          % (self.type_name, params))
        res = self.client.delete_rule(**params)
        self.logger.debug('Response: %s' % res)
        return res


@decorators.aws_resource(resource_type=RESOURCE_TYPE)
def prepare(ctx, resource_config, **_):
    '''Prepares an AWS Cloudwatch Events Rule'''
    # Save the parameters
    ctx.instance.runtime_properties['resource_config'] = resource_config


@decorators.aws_resource(CloudwatchEventsRule, RESOURCE_TYPE)
def create(ctx, iface, resource_config, **_):
    '''Creates an AWS Cloudwatch Events Rule'''
    params = resource_config.copy()
    rule_name = params.get(NAME)
    utils.update_resource_id(ctx.instance, rule_name)
    # Actually create the resource
    rule_arn = iface.create(params)
    utils.update_resource_arn(ctx.instance, rule_arn)


@decorators.aws_resource(CloudwatchEventsRule, RESOURCE_TYPE,
                         ignore_properties=True)
def delete(ctx, iface, resource_config, **_):
    '''Deletes an AWS Cloudwatch Events Rule'''
    params = resource_config.copy()
    iface.delete(params)
