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
"""
    S3.Bucket
    ~~~~~~~~~~~~~~
    AWS S3 Bucket interface
"""
# Generic
import json
# Cloudify
from cloudify_boto3.common import decorators, utils
from cloudify_boto3.s3 import S3Base
from cloudify_boto3.common.constants import EXTERNAL_RESOURCE_ID
# Boto
from botocore.exceptions import ClientError

RESOURCE_TYPE = 'S3 Bucket Policy'
BUCKET = 'Bucket'
POLICY = 'Policy'
BUCKET_TYPE = 'cloudify.nodes.aws.s3.Bucket'


class S3BucketPolicy(S3Base):
    """
        AWS S3 Bucket interface
    """
    def __init__(self, ctx_node, resource_id=None, client=None, logger=None):
        S3Base.__init__(self, ctx_node, resource_id, client, logger)
        self.type_name = RESOURCE_TYPE

    @property
    def properties(self):
        """Gets the properties of an external resource"""
        try:
            resource = \
                self.client.get_bucket_policy(
                    {BUCKET: self.resource_id})
        except ClientError:
            pass
        else:
            return resource[POLICY] if resource else None

    @property
    def status(self):
        """Gets the status of an external resource"""
        props = self.properties
        if not props:
            return None
        return props['Status']

    def create(self, params):
        """
            Create a new AWS S3 Bucket Policy.
        """
        self.logger.debug('Creating %s with parameters: %s'
                          % (self.type_name, params))
        res = self.client.put_bucket_policy(**params)
        self.logger.debug('Response: %s' % res)
        return res

    def delete(self, params):
        """
            Deletes an existing AWS S3 Bucket Policy.
        """
        self.logger.debug('Deleting %s with parameters: %s'
                          % (self.type_name, params))
        self.client.delete_bucket_policy(**params)


@decorators.aws_resource(resource_type=RESOURCE_TYPE)
def prepare(ctx, resource_config, **_):
    """Prepares an AWS S3 Bucket Policy"""
    # Save the parameters
    ctx.instance.runtime_properties['resource_config'] = resource_config


@decorators.aws_resource(S3BucketPolicy, RESOURCE_TYPE)
def create(ctx, iface, resource_config, **_):
    """Creates an AWS S3 Bucket Policy"""

    # Create a copy of the resource config for clean manipulation.
    params = \
        dict() if not resource_config else resource_config.copy()

    # Get the bucket name from either params or a relationship.
    bucket_name = params.get(BUCKET)
    if not bucket_name:
        targ = utils.find_rel_by_node_type(
            ctx.instance,
            BUCKET_TYPE
        )
        bucket_name = \
            targ.target.instance.runtime_properties.get(
                EXTERNAL_RESOURCE_ID
            )
        params[BUCKET] = bucket_name
    ctx.instance.runtime_properties[BUCKET] = bucket_name
    utils.update_resource_id(ctx.instance, bucket_name)

    # Get the policy name from either params or a relationship.
    bucket_policy = params.get(POLICY)
    if not isinstance(bucket_policy, basestring):
        bucket_policy = json.dumps(bucket_policy)
        params[POLICY] = bucket_policy
    ctx.instance.runtime_properties[POLICY] = bucket_policy

    # Actually create the resource
    iface.create(params)


@decorators.aws_resource(S3BucketPolicy, RESOURCE_TYPE,
                         ignore_properties=True)
def delete(iface, resource_config, **_):
    """Deletes an AWS S3 Bucket Policy"""

    # Create a copy of the resource config for clean manipulation.
    params = \
        dict() if not resource_config else resource_config.copy()

    # Add the required BUCKET parameter.
    if BUCKET not in params.keys():
        params.update({BUCKET: iface.resource_id})

    # Actually delete the resource
    iface.delete(params)
