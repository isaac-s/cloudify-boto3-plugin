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
    EC2.InternetGateway
    ~~~~~~~~~~~~~~
    AWS EC2 Internet interface
'''
# Cloudify
from cloudify_boto3.common import decorators, utils
from cloudify_boto3.ec2 import EC2Base
from cloudify_boto3.common.constants import EXTERNAL_RESOURCE_ID
# Boto
from botocore.exceptions import ClientError

RESOURCE_TYPE = 'EC2 Internet Gateway Bucket'
INTERNETGATEWAYS = 'InternetGateways'
INTERNETGATEWAY_ID = 'InternetGatewayId'
INTERNETGATEWAY_IDS = 'InternetGatewayIds'
VPC_ID = 'VpcId'
VPC_TYPE = 'cloudify.nodes.aws.ec2.Vpc'
VPC_TYPE_DEPRECATED = 'cloudify.aws.nodes.Vpc'


class EC2InternetGateway(EC2Base):
    '''
        EC2 Internet Gateway interface
    '''
    def __init__(self, ctx_node, resource_id=None, client=None, logger=None):
        EC2Base.__init__(self, ctx_node, resource_id, client, logger)
        self.type_name = RESOURCE_TYPE

    @property
    def properties(self):
        '''Gets the properties of an external resource'''
        params = {INTERNETGATEWAY_IDS: [self.resource_id]}
        try:
            resources = \
                self.client.describe_internet_gateways(**params)
        except ClientError:
            pass
        else:
            return resources.get(INTERNETGATEWAYS)[0] if resources else None

    @property
    def status(self):
        '''Gets the status of an external resource'''
        props = self.properties
        if not props:
            return None
        return props['State']

    def create(self, params):
        '''
            Create a new AWS EC2 Internet Gateway.
        '''
        self.logger.debug('Creating %s with parameters: %s'
                          % (self.type_name, params))
        res = self.client.create_internet_gateway(**params)
        self.logger.debug('Response: %s' % res)
        return res

    def delete(self, params=None):
        '''
            Deletes an existing AWS EC2 Internet Gateway.
        '''
        self.logger.debug('Deleting %s with parameters: %s'
                          % (self.type_name, params))
        res = self.client.delete_internet_gateway(**params)
        self.logger.debug('Response: %s' % res)
        return res

    def attach(self, params):
        '''
            Attach an AWS EC2 Internet Gateway to a VPC.
        '''
        self.logger.debug('Attaching %s with: %s'
                          % (self.type_name, params.get(VPC_ID, None)))
        res = self.client.attach_internet_gateway(**params)
        self.logger.debug('Response: %s' % res)
        return res


@decorators.aws_resource(resource_type=RESOURCE_TYPE)
def prepare(ctx, resource_config, **_):
    '''Prepares an AWS EC2 Internet Gateway'''
    # Save the parameters
    ctx.instance.runtime_properties['resource_config'] = resource_config


@decorators.aws_resource(EC2InternetGateway, RESOURCE_TYPE)
def create(ctx, iface, resource_config, **_):
    '''Creates an AWS EC2 Internet Gateway'''
    params = dict() if not resource_config else resource_config.copy()

    # Actually create the resource
    internet_gateway = iface.create(params)
    utils.update_resource_id(
            ctx.instance, internet_gateway.get(INTERNETGATEWAY_ID))


@decorators.aws_resource(EC2InternetGateway, RESOURCE_TYPE,
                         ignore_properties=True)
def delete(iface, resource_config, **_):
    '''Deletes an AWS EC2 Internet Gateway'''
    params = dict() if not resource_config else resource_config.copy()

    internet_gateway_id = params.get(INTERNETGATEWAY_ID)
    if not internet_gateway_id:
        internet_gateway_id = iface.resource_id

    params.update({INTERNETGATEWAY_ID: internet_gateway_id})
    iface.delete(resource_config)


@decorators.aws_resource(EC2InternetGateway, RESOURCE_TYPE)
def attach(ctx, iface, resource_config, **_):
    '''Creates an AWS EC2 Internet Gateway'''
    params = dict() if not resource_config else resource_config.copy()

    internet_gateway_id = params.get(INTERNETGATEWAY_ID)
    if not internet_gateway_id:
        internet_gateway_id = iface.resource_id

    params.update({INTERNETGATEWAY_ID: internet_gateway_id})

    vpc_id = params.get(VPC_ID)
    if not vpc_id:
        targ = \
            utils.find_rel_by_node_type(
                    ctx.instance,
                    VPC_TYPE) or utils.find_rel_by_node_type(
                    ctx.instance,
                    VPC_TYPE_DEPRECATED)

        # Attempt to use the VPC ID from parameters.
        # Fallback to connected VPC.
        params[VPC_ID] = \
            vpc_id or \
            targ.target.instance.runtime_properties.get(
                    EXTERNAL_RESOURCE_ID)

    # Actually create the resource
    iface.attach(params)
