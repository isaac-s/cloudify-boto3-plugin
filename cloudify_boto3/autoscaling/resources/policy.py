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
    Autoscaling.Policy
    ~~~~~~~~~~~~~~
    AWS Autoscaling Policy interface
'''
# Cloudify
from cloudify_boto3.common import decorators, utils
from cloudify_boto3.autoscaling import AutoscalingBase
# Boto
from botocore.exceptions import ClientError

RESOURCE_TYPE = 'Autoscaling Policy'
GROUP_NAME = 'AutoScalingGroupName'
SCALING_POLICIES = 'ScalingPolicies'
POLICY_NAMES = 'PolicyNames'
POLICY_NAME = 'PolicyName'
POLICY_ARN = 'PolicyARN'
POLICY_TYPES = 'PolicyTypes'
GROUP_TYPE = 'cloudify.nodes.aws.autoscaling.Group'


class AutoscalingPolicy(AutoscalingBase):
    '''
        Autoscaling Autoscaling Policy interface
    '''
    def __init__(self, ctx_node, resource_id=None, client=None, logger=None):
        AutoscalingBase.__init__(self, ctx_node, resource_id, client, logger)
        self.type_name = RESOURCE_TYPE

    @property
    def properties(self):
        '''Gets the properties of an external resource'''
        params = {POLICY_NAMES: [self.resource_id]}
        try:
            resources = \
                self.client.describe_policies(**params)
        except ClientError:
            pass
        else:
            return resources.get(SCALING_POLICIES, [None])[0]

    @property
    def status(self):
        '''Gets the status of an external resource'''
        props = self.properties
        if not props:
            return None
        return None

    def create(self, params):
        '''
            Create a new AWS Autoscaling Autoscaling Policy.
        '''
        if not self.resource_id:
            setattr(self, 'resource_id', params.get(POLICY_NAME))
        self.logger.debug('Creating %s with parameters: %s'
                          % (self.type_name, params))
        res = self.client.put_scaling_policy(**params)
        self.logger.debug('Response: %s' % res)
        return res.get(POLICY_ARN)

    def delete(self, params=None):
        '''
            Deletes an existing AWS Autoscaling Policy.
        '''
        if POLICY_NAME not in params.keys():
            params.update({POLICY_NAME: self.resource_id})
        self.logger.debug('Deleting %s with parameters: %s'
                          % (self.type_name, params))
        res = self.client.delete_policy(**params)
        self.logger.debug('Response: %s' % res)
        return res


@decorators.aws_resource(resource_type=RESOURCE_TYPE)
def prepare(ctx, resource_config, **_):
    '''Prepares an AWS Autoscaling Autoscaling Policy'''
    # Save the parameters
    ctx.instance.runtime_properties['resource_config'] = resource_config


@decorators.aws_resource(AutoscalingPolicy, RESOURCE_TYPE)
def create(ctx, iface, resource_config, **_):
    '''Creates an AWS Autoscaling Autoscaling Policy'''
    params = resource_config.copy()
    utils.update_resource_id(
        ctx.instance, params.get(POLICY_NAME))

    # Ensure the $GROUP_NAME parameter is populated.
    autoscaling_group = params.get(GROUP_NAME)
    if not autoscaling_group:
        autoscaling_group = \
            utils.find_resource_id_by_type(
                ctx.instance, GROUP_TYPE)
        params[GROUP_NAME] = autoscaling_group
    ctx.instance.runtime_properties[GROUP_NAME] = \
        autoscaling_group

    # Actually create the resource
    resource_arn = iface.create(params)
    utils.update_resource_arn(
        ctx.instance, resource_arn)


@decorators.aws_resource(AutoscalingPolicy, RESOURCE_TYPE,
                         ignore_properties=True)
def delete(ctx, iface, resource_config, **_):
    '''Deletes an AWS Autoscaling Autoscaling Policy'''
    params = resource_config.copy()

    # Ensure the $GROUP_NAME parameter is populated.
    autoscaling_group = params.get(GROUP_NAME)
    if not autoscaling_group:
        autoscaling_group = \
            ctx.instance.runtime_properties[GROUP_NAME]
        params.update(
            {GROUP_NAME: autoscaling_group})
    iface.delete(params)
