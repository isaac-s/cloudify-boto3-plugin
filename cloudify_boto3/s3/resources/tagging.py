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
    S3.Bucket.Tagging
    ~~~~~~~~~~~~~~
    AWS S3 Bucket Tagging interface
'''
# Cloudify
from cloudify_boto3.common import decorators, utils
from cloudify_boto3.s3 import S3Base
from cloudify_boto3.common.constants import EXTERNAL_RESOURCE_ID
# Boto
from botocore.exceptions import ClientError

RESOURCE_TYPE = 'S3 Bucket Tagging'
BUCKET = 'Bucket'
TAGGING = 'Tagging'
BUCKET_TYPE = 'cloudify.nodes.aws.s3.Bucket'
TAGSET = 'TagSet'


class S3BucketTagging(S3Base):
    '''
        AWS S3 Bucket Tagging interface
    '''
    def __init__(self, ctx_node, resource_id=None, client=None, logger=None):
        S3Base.__init__(self, ctx_node, resource_id, client, logger)
        self.type_name = RESOURCE_TYPE

    @property
    def properties(self):
        '''Gets the properties of an external resource'''
        try:
            resource = \
                self.client.get_bucket_tagging(
                    {BUCKET: self.resource_id})
        except ClientError:
            pass
        else:
            return [] if not resource else resource.get(TAGSET, [])

    @property
    def status(self):
        '''Gets the status of an external resource'''
        pass

    def create(self, params):
        '''
            Create a new AWS Bucket Tagging.
        '''
        self.logger.debug('Creating %s with parameters: %s'
                          % (self.type_name, params))
        res = self.client.put_bucket_tagging(**params)
        self.logger.debug('Response: %s' % res)
        return res

    def delete(self, params=None):
        '''
            Deletes an existing AWS Bucket Tagging.
        '''
        if BUCKET not in params.keys():
            params.update({BUCKET: self.resource_id})
        self.logger.debug('Deleting %s with parameters: %s'
                          % (self.type_name, params))
        self.client.delete_bucket_tagging(**params)


@decorators.aws_resource(resource_type=RESOURCE_TYPE)
def prepare(ctx, resource_config, **_):
    '''Prepares an AWS Bucket Bucket Tagging'''
    # Save the parameters
    ctx.instance.runtime_properties['resource_config'] = resource_config


@decorators.aws_resource(S3BucketTagging, RESOURCE_TYPE)
def create(ctx, iface, resource_config, **_):
    '''Creates an AWS S3 Bucket Bucket Tagging'''

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


@decorators.aws_resource(S3BucketTagging, RESOURCE_TYPE,
                         ignore_properties=True)
def delete(iface, resource_config, **_):
    '''Deletes an AWS S3 Bucket Bucket Tagging'''
    iface.delete(resource_config)
