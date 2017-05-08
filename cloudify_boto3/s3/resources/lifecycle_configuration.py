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
    S3.Bucket.LifecycleConfiguration
    ~~~~~~~~~~~~~~
    AWS S3 Bucket Lifecycle Configuration interface
'''
# Cloudify
from cloudify_boto3.common import decorators, utils
from cloudify_boto3.s3 import S3Base
from cloudify_boto3.common.constants import EXTERNAL_RESOURCE_ID
# Boto
from botocore.exceptions import ClientError

RESOURCE_TYPE = 'S3 Lifecycle Configuration'
BUCKET = 'Bucket'
BUCKET_TYPE = 'cloudify.nodes.aws.s3.Bucket'
RULES = 'Rules'
ID = 'ID'


class S3BucketLifecycleConfiguration(S3Base):
    '''
        AWS S3 Bucket Lifecycle Configuration interface
    '''
    def __init__(self, ctx_node, resource_id=None, client=None, logger=None):
        S3Base.__init__(self, ctx_node, resource_id, client, logger)
        self.type_name = RESOURCE_TYPE

    @property
    def properties(self):
        '''Gets the properties of an external resource'''
        try:
            resources = \
                self.client.get_bucket_lifecycle_configuration(
                    {BUCKET: self.resource_id})
        except ClientError:
            pass
        else:
            for resource in resources.get(RULES, []):
                return resource.get(ID, None)
        return None

    @property
    def status(self):
        '''Gets the status of an external resource'''
        props = self.properties
        if not props:
            return None
        return props['Status']

    def create(self, params):
        '''
            Create a new AWS Bucket Lifecycle Configuration Policy.
        '''
        self.logger.debug('Creating %s with parameters: %s'
                          % (self.type_name, params))
        res = self.client.put_bucket_lifecycle(**params)
        self.logger.debug('Response: %s' % res)
        return res

    def delete(self, params=None):
        '''
            Deletes an existing AWS Bucket Lifecycle Configuration Policy.
        '''
        if BUCKET not in params.keys():
            params.update({BUCKET: self.resource_id})
        self.logger.debug('Deleting %s with parameters: %s'
                          % (self.type_name, params))
        self.client.delete_bucket_lifecycle(**params)


@decorators.aws_resource(resource_type=RESOURCE_TYPE)
def prepare(ctx, resource_config, **_):
    '''Prepares an AWS Bucket Lifecycle Configuration Policy'''
    # Save the parameters
    ctx.instance.runtime_properties['resource_config'] = resource_config


@decorators.aws_resource(S3BucketLifecycleConfiguration, RESOURCE_TYPE)
def create(ctx, iface, resource_config, **_):
    '''Creates an AWS S3 Bucket Lifecycle Configuration'''

    params = resource_config.copy()
    bucket_name = params.get(BUCKET)

    if not bucket_name:
        targ = utils.find_rel_by_node_type(
            ctx.instance,
            BUCKET_TYPE
        )
        target_instance = targ.target.instance
        bucket_name = \
            target_instance.runtime_properties.get(
                EXTERNAL_RESOURCE_ID
            )
        params[BUCKET] = bucket_name

    ctx.instance.runtime_properties[BUCKET] = bucket_name
    utils.update_resource_id(ctx.instance, bucket_name)
    # Actually create the resource
    iface.create(params)


@decorators.aws_resource(S3BucketLifecycleConfiguration, RESOURCE_TYPE,
                         ignore_properties=True)
def delete(iface, resource_config, **_):
    '''Deletes an AWS S3 Bucket Lifecycle Configuration'''
    iface.delete(resource_config)
