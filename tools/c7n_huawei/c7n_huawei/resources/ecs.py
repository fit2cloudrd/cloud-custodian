# Copyright 2017-2018 Capital One Services, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import operator

from openstack import connection

from c7n_huawei.provider import resources
from c7n_huawei.query import QueryResourceManager, TypeInfo
from c7n_huawei.filters.filter import HuaweiAgeFilter
from c7n_huawei.actions import MethodAction

from c7n.utils import type_schema

conn = connection.Connection(
            cloud="myhuaweicloud.com",
            ak=os.getenv('HUAWEI_AK'),
            sk=os.getenv('HUAWEI_SK'),
            region=os.getenv('HUAWEI_DEFAULT_REGION'),
            project_id=os.getenv('HUAWEI_PROJECT')
        )

@resources.register('ecs')
class Ecs(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'compute.ecs'
        enum_spec = (None, None, None)
        id = 'InstanceId'
        dimension = 'InstanceId'

    def get_requst(self):
        servers = conn.compute.servers(limit=10000)
        arr = list() # 创建 []
        for server in servers:
            json = dict() # 创建 {}
            for name in dir(server):
                if not name.startswith('_'):
                    value = getattr(server, name)
                    if not callable(value):
                        json[name] = value
            arr.append(json)
        return arr

@Ecs.filter_registry.register('instance-age')
class EcsAgeFilter(HuaweiAgeFilter):
    """Filters instances based on their age (in days)

        policies:
          - name: huawei-ecs-30-days-plus
            resource: huawei.ecs
            filters:
              - type: instance-age
                op: lt
                days: 30
    """

    date_attribute = "LaunchTime"
    ebs_key_func = operator.itemgetter('AttachTime')

    schema = type_schema(
        'instance-age',
        op={'$ref': '#/definitions/filters_common/comparison_operators'},
        days={'type': 'number'},
        hours={'type': 'number'},
        minutes={'type': 'number'})

    def get_resource_date(self, i):
        return i['CreationTime']

@Ecs.action_registry.register('start')
class Start(MethodAction):

    schema = type_schema('start')
    method_spec = {'op': 'start'}
    attr_filter = ('Status', ('Stopped',))

    def get_requst(self, instance):
        server = conn.compute.start_server(instance['InstanceId'])
        json = dict()  # 创建 {}
        for name in dir(server):
            if not name.startswith('_'):
                value = getattr(server, name)
                if not callable(value):
                    json[name] = value
        return json

@Ecs.action_registry.register('stop')
class Stop(MethodAction):

    schema = type_schema('stop')
    method_spec = {'op': 'stop'}
    attr_filter = ('Status', ('Running',))

    def get_requst(self, instance):
        server = conn.compute.stop_server(instance['InstanceId'])
        json = dict()  # 创建 {}
        for name in dir(server):
            if not name.startswith('_'):
                value = getattr(server, name)
                if not callable(value):
                    json[name] = value
        return json


@Ecs.action_registry.register('delete')
class Delete(MethodAction):

    schema = type_schema('delete')
    method_spec = {'op': 'delete'}

    def get_requst(self, instance):
        server = conn.compute.delete_server(instance['InstanceId'])
        json = dict()  # 创建 {}
        for name in dir(server):
            if not name.startswith('_'):
                value = getattr(server, name)
                if not callable(value):
                    json[name] = value
        return json