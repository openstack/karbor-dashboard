#    Copyright (c) 2016 Huawei, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import absolute_import
import logging

from django.conf import settings
from horizon import exceptions
from horizon.utils import functions as utils
from horizon.utils.memoized import memoized
from openstack_dashboard.api import base
from smaugclient.v1 import client as smaug_client

LOG = logging.getLogger(__name__)


def get_smaug_endpoint(request):
    endpoint = ""
    try:
        endpoint = base.url_for(request, "data-protect")
    except exceptions.ServiceCatalogException:
        endpoint = 'http://localhost:8799'
        LOG.warning('Smaug API location could not be found in Service '
                    'Catalog, using default: {0}'.format(endpoint))
    return endpoint


@memoized
def smaugclient(request):
    endpoint = get_smaug_endpoint(request)
    LOG.debug('smaugclient connection created using the token "%s" and url'
              '"%s"' % (request.user.token.id, endpoint))
    c = smaug_client.Client(endpoint=endpoint,
                            auth_url=getattr(settings,
                                             'OPENSTACK_KEYSTONE_URL'),
                            token=request.user.token.id,
                            username=request.user.username,
                            project_id=request.user.tenant_id,
                            auth_plugin='token',
                            )
    return c


def update_pagination(entities, page_size, marker, sort_dir, sort_key,
                      reversed_order):
    has_more_data = has_prev_data = False
    if len(entities) > page_size:
        has_more_data = True
        entities.pop()
        if marker is not None:
            has_prev_data = True
    # first page condition when reached via prev back
    elif reversed_order and marker is not None:
        has_more_data = True
    # last page condition
    elif marker is not None:
        has_prev_data = True

    # restore the original ordering here
    if reversed_order:
        entities = sorted(entities, key=lambda entity:
                          (getattr(entity, sort_key) or '').lower(),
                          reverse=(sort_dir == 'asc'))

    return entities, has_more_data, has_prev_data


def plan_create(request, name, provider_id, resources):
    return smaugclient(request).plans.create(name, provider_id, resources)


def plan_delete(request, plan_id):
    return smaugclient(request).plans.delete(plan_id)


def plan_update(request, plan_id, data):
    return smaugclient(request).plans.update(plan_id, data)


def plan_list(request, detailed=False, search_opts=None, marker=None,
              limit=None, sort_key=None, sort_dir=None, sort=None):
    return smaugclient(request).plans.list(detailed=detailed,
                                           search_opts=search_opts,
                                           marker=marker,
                                           limit=limit,
                                           sort_key=sort_key,
                                           sort_dir=sort_dir,
                                           sort=sort)


def plan_list_paged(request, detailed=False, search_opts=None, marker=None,
                    limit=None, sort_key=None, sort_dir=None, sort=None,
                    paginate=False, reversed_order=False):
    has_more_data = False
    has_prev_data = False

    if paginate:
        if reversed_order:
            sort_dir = 'desc' if sort_dir == 'asc' else 'asc'
        page_size = utils.get_page_size(request)
        plans = smaugclient(request).plans.list(detailed=detailed,
                                                search_opts=search_opts,
                                                marker=marker,
                                                limit=page_size + 1,
                                                sort_key=sort_key,
                                                sort_dir=sort_dir,
                                                sort=sort)
        plans, has_more_data, has_prev_data = update_pagination(
            plans, page_size, marker, sort_dir, sort_key, reversed_order)
    else:
        plans = smaugclient(request).plans.list(detailed=detailed,
                                                search_opts=search_opts,
                                                marker=marker,
                                                limit=limit,
                                                sort_key=sort_key,
                                                sort_dir=sort_dir,
                                                sort=sort)
    return (plans, has_more_data, has_prev_data)


def plan_get(request, plan_id):
    return smaugclient(request).plans.get(plan_id)


def scheduled_operation_create(request, name, operation_type, trigger_id,
                               operation_definition):
    return smaugclient(request).scheduled_operations.create(
        name,
        operation_type,
        trigger_id,
        operation_definition)


def scheduled_operation_delete(request, scheduled_operation_id):
    return smaugclient(request).scheduled_operations.delete(
        scheduled_operation_id)


def scheduled_operation_list(request, detailed=False, search_opts=None,
                             marker=None, limit=None, sort_key=None,
                             sort_dir=None, sort=None):
    return smaugclient(request).scheduled_operations.list(
        detailed=detailed,
        search_opts=search_opts,
        marker=marker,
        limit=limit,
        sort_key=sort_key,
        sort_dir=sort_dir,
        sort=sort)


def scheduled_operation_list_paged(request, detailed=False, search_opts=None,
                                   marker=None, limit=None, sort_key=None,
                                   sort_dir=None, sort=None, paginate=False,
                                   reversed_order=False):
    has_more_data = False
    has_prev_data = False

    if paginate:
        if reversed_order:
            sort_dir = 'desc' if sort_dir == 'asc' else 'asc'
        page_size = utils.get_page_size(request)
        scheduled_operations = smaugclient(request).scheduled_operations.list(
            detailed=detailed,
            search_opts=search_opts,
            marker=marker,
            limit=page_size + 1,
            sort_key=sort_key,
            sort_dir=sort_dir,
            sort=sort)
        scheduled_operations, has_more_data, has_prev_data = update_pagination(
            scheduled_operations,
            page_size,
            marker,
            sort_dir,
            sort_key,
            reversed_order)
    else:
        scheduled_operations = smaugclient(request).scheduled_operations.list(
            detailed=detailed,
            search_opts=search_opts,
            marker=marker,
            limit=limit,
            sort_key=sort_key,
            sort_dir=sort_dir,
            sort=sort)

    return (scheduled_operations, has_more_data, has_prev_data)


def scheduled_operation_get(request, scheduled_operation_id):
    return smaugclient(request).scheduled_operations.get(
        scheduled_operation_id)


def restore_create(request, provider_id, checkpoint_id,
                   restore_target, parameters):
    return smaugclient(request).restores.create(provider_id,
                                                checkpoint_id,
                                                restore_target,
                                                parameters)


def restore_delete(request, restore_id):
    return smaugclient(request).restores.delete(restore_id)


def restore_list(request, detailed=False, search_opts=None, marker=None,
                 limit=None, sort_key=None, sort_dir=None, sort=None):
    return smaugclient(request).restores.list(detailed=detailed,
                                              search_opts=search_opts,
                                              marker=marker,
                                              limit=limit,
                                              sort_key=sort_key,
                                              sort_dir=sort_dir,
                                              sort=sort)


def restore_list_paged(request, detailed=False, search_opts=None, marker=None,
                       limit=None, sort_key=None, sort_dir=None, sort=None,
                       paginate=False, reversed_order=False):
    has_more_data = False
    has_prev_data = False

    if paginate:
        if reversed_order:
            sort_dir = 'desc' if sort_dir == 'asc' else 'asc'
        page_size = utils.get_page_size(request)
        restores = smaugclient(request).restores.list(detailed=detailed,
                                                      search_opts=search_opts,
                                                      marker=marker,
                                                      limit=page_size + 1,
                                                      sort_key=sort_key,
                                                      sort_dir=sort_dir,
                                                      sort=sort)
        restores, has_more_data, has_prev_data = update_pagination(
            restores, page_size, marker, sort_dir, sort_key, reversed_order)
    else:
        restores = smaugclient(request).restores.list(detailed=detailed,
                                                      search_opts=search_opts,
                                                      marker=marker,
                                                      limit=limit,
                                                      sort_key=sort_key,
                                                      sort_dir=sort_dir,
                                                      sort=sort)

    return (restores, has_more_data, has_prev_data)


def restore_get(request, restore_id):
    return smaugclient(request).restores.get(restore_id)


def protectable_list(request):
    return smaugclient(request).protectables.list()


def protectable_get(request, protectable_type):
    return smaugclient(request).protectables.get(protectable_type)


def protectable_list_instances(request, protectable_type, search_opts=None,
                               marker=None, limit=None, sort_key=None,
                               sort_dir=None, sort=None):
    return smaugclient(request).protectables.list_instances(
        protectable_type=protectable_type,
        search_opts=search_opts,
        marker=marker,
        limit=limit,
        sort_key=sort_key,
        sort_dir=sort_dir,
        sort=sort)


def protectable_list_instances_paged(request, protectable_type,
                                     search_opts=None, marker=None, limit=None,
                                     sort_key=None, sort_dir=None, sort=None,
                                     paginate=False, reversed_order=False):
    has_more_data = False
    has_prev_data = False

    if paginate:
        if reversed_order:
            sort_dir = 'desc' if sort_dir == 'asc' else 'asc'
        page_size = utils.get_page_size(request)
        instances = smaugclient(request).protectables.list_instances(
            protectable_type,
            search_opts=search_opts,
            marker=marker,
            limit=page_size + 1,
            sort_key=sort_key,
            sort_dir=sort_dir,
            sort=sort)
        instances, has_more_data, has_prev_data = update_pagination(
            instances, page_size, marker, sort_dir, sort_key, reversed_order)
    else:
        instances = smaugclient(request).protectables.list_instances(
            protectable_type,
            search_opts=search_opts,
            marker=marker,
            limit=limit,
            sort_key=sort_key,
            sort_dir=sort_dir,
            sort=sort)

    return (instances, has_more_data, has_prev_data)


def protectable_get_instance(request, type, id):
    return smaugclient(request).protectables.get_instance(type, id)


def provider_list(request, detailed=False, search_opts=None, marker=None,
                  limit=None, sort_key=None, sort_dir=None, sort=None):
    return smaugclient(request).providers.list(detailed=detailed,
                                               search_opts=search_opts,
                                               marker=marker,
                                               limit=limit,
                                               sort_key=sort_key,
                                               sort_dir=sort_dir,
                                               sort=sort)


def provider_list_paged(request, detailed=False, search_opts=None, marker=None,
                        limit=None, sort_key=None, sort_dir=None, sort=None,
                        paginate=False, reversed_order=False):
    has_more_data = False
    has_prev_data = False

    if paginate:
        if reversed_order:
            sort_dir = 'desc' if sort_dir == 'asc' else 'asc'
        page_size = utils.get_page_size(request)
        providers = smaugclient(request).providers.list(
            detailed=detailed,
            search_opts=search_opts,
            marker=marker,
            limit=page_size + 1,
            sort_key=sort_key,
            sort_dir=sort_dir,
            sort=sort)
        providers, has_more_data, has_prev_data = update_pagination(
            providers, page_size, marker, sort_dir, sort_key, reversed_order)
    else:
        providers = smaugclient(request).providers.list(
            detailed=detailed,
            search_opts=search_opts,
            marker=marker,
            limit=limit,
            sort_key=sort_key,
            sort_dir=sort_dir,
            sort=sort)

    return (providers, has_more_data, has_prev_data)


def provider_get(request, provider_id):
    return smaugclient(request).providers.get(provider_id)


def checkpoint_create(request, provider_id, plan_id):
    return smaugclient(request).checkpoints.create(provider_id, plan_id)


def checkpoint_delete(request, provider_id, checkpoint_id):
    return smaugclient(request).checkpoints.delete(provider_id, checkpoint_id)


def checkpoint_list(request, provider_id=None, search_opts=None, marker=None,
                    limit=None, sort_key=None, sort_dir=None, sort=None):
    return smaugclient(request).checkpoints.list(provider_id=provider_id,
                                                 search_opts=search_opts,
                                                 marker=marker,
                                                 limit=limit,
                                                 sort_key=sort_key,
                                                 sort_dir=sort_dir,
                                                 sort=sort)


def checkpoint_list_paged(request, provider_id=None, search_opts=None,
                          marker=None, limit=None, sort_key=None,
                          sort_dir=None, sort=None, paginate=False,
                          reversed_order=False):
    has_more_data = False
    has_prev_data = False

    if paginate:
        if reversed_order:
            sort_dir = 'desc' if sort_dir == 'asc' else 'asc'
        page_size = utils.get_page_size(request)
        checkpoints = smaugclient(request).checkpoints.list(
            provider_id=provider_id,
            search_opts=search_opts,
            marker=marker,
            limit=page_size + 1,
            sort_key=sort_key,
            sort_dir=sort_dir,
            sort=sort)
        checkpoints, has_more_data, has_prev_data = update_pagination(
            checkpoints, page_size, marker, sort_dir, sort_key, reversed_order)
    else:
        checkpoints = smaugclient(request).checkpoints.list(
            provider_id=provider_id,
            search_opts=search_opts,
            marker=marker,
            limit=limit,
            sort_key=sort_key,
            sort_dir=sort_dir,
            sort=sort)

    return (checkpoints, has_more_data, has_prev_data)


def checkpoint_get(request, provider_id, checkpoint_id):
    return smaugclient(request).checkpoints.get(provider_id, checkpoint_id)


def trigger_create(request, name, type, properties):
    return smaugclient(request).triggers.create(name, type, properties)


def trigger_delete(request, trigger_id):
    return smaugclient(request).triggers.delete(trigger_id)


def trigger_list(request, detailed=False, search_opts=None, marker=None,
                 limit=None, sort_key=None, sort_dir=None, sort=None):
    return smaugclient(request).triggers.list(detailed=detailed,
                                              search_opts=search_opts,
                                              marker=marker,
                                              limit=limit,
                                              sort_key=sort_key,
                                              sort_dir=sort_dir,
                                              sort=sort)


def trigger_list_paged(request, detailed=False, search_opts=None, marker=None,
                       limit=None, sort_key=None, sort_dir=None, sort=None,
                       paginate=False, reversed_order=False):
    has_more_data = False
    has_prev_data = False

    if paginate:
        if reversed_order:
            sort_dir = 'desc' if sort_dir == 'asc' else 'asc'
        page_size = utils.get_page_size(request)
        triggers = smaugclient(request).triggers.list(detailed=detailed,
                                                      search_opts=search_opts,
                                                      marker=marker,
                                                      limit=page_size + 1,
                                                      sort_key=sort_key,
                                                      sort_dir=sort_dir,
                                                      sort=sort)
        triggers, has_more_data, has_prev_data = update_pagination(
            triggers, page_size, marker, sort_dir, sort_key, reversed_order)
    else:
        triggers = smaugclient(request).triggers.list(detailed=detailed,
                                                      search_opts=search_opts,
                                                      marker=marker,
                                                      limit=limit,
                                                      sort_key=sort_key,
                                                      sort_dir=sort_dir,
                                                      sort=sort)

    return (triggers, has_more_data, has_prev_data)


def trigger_get(request, trigger_id):
    return smaugclient(request).triggers.get(trigger_id)
