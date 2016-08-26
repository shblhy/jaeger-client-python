import json
import logging

from crossdock.thrift_gen.tracetest.ttypes import JoinTraceRequest, StartTraceRequest, \
    Downstream, Transport, TraceResponse, ObservedSpan


#
# Serializers for the downstream calls
#
def set_downstream_object_values(downstream_object, json_obj):
    return set_traced_service_object_values(downstream_object, json_obj, downstream_from_struct)


def join_trace_request_from_json(json_request):
    request = JoinTraceRequest()
    set_downstream_object_values(request, json.loads(json_request))
    return request


def start_trace_request_from_json(json_request):
    request = StartTraceRequest()
    set_downstream_object_values(request, json.loads(json_request))
    return request


def downstream_from_struct(json_obj):
    downstream = Downstream()
    set_downstream_object_values(downstream, json_obj)
    return downstream


def join_trace_request_to_json(downstream, server_role):
    req = {}
    if downstream is not None:
        req['downstream'] = traced_service_object_to_json(downstream)
    if server_role is not None:
        req['serverRole'] = str(server_role)
    return json.dumps(req)

#
# Serializers for the upstream responses
#


def set_upstream_object_values(obj, json_obj):
    return set_traced_service_object_values(obj, json_obj, traceresponse_from_struct)


def observed_span_from_struct(json_obj):
    os = ObservedSpan()
    set_upstream_object_values(os, json_obj)
    return os


def traceresponse_from_struct(json_obj):
    tr = TraceResponse()
    set_upstream_object_values(tr, json_obj)
    return tr


def traceresponse_from_json(json_str):
    try:
        return traceresponse_from_struct(json.loads(json_str))
    except:
        logging.exception('Failed to parse JSON')
        raise

# Generic


def class_keys(obj):
    return [a for a in dir(obj) if not a.startswith('__') and not
            callable(getattr(obj, a)) and not
            a == 'type_spec']


def traced_service_object_to_json(obj):
    json_response = {}
    for k in class_keys(obj):
        if k == 'downstream':
            if obj.downstream is not None:
                json_response['downstream'] = traced_service_object_to_json(obj.downstream)
        elif k == 'transport':
            if obj.transport is not None:
                json_response['transport'] = Transport._VALUES_TO_NAMES[obj.transport]
        elif k == 'span':
            if obj.span is not None:
                json_response['span'] = traced_service_object_to_json(obj.span)
        else:
            json_response[k] = getattr(obj, k)
    return json_response


def set_traced_service_object_values(obj, values, downstream_func):
    for k in values.iterkeys():
        if hasattr(obj, k):
            if k == 'downstream':
                obj.downstream = downstream_func(values[k])
            elif k == 'transport':
                obj.transport = Transport._NAMES_TO_VALUES[values[k]]
            elif k == 'span':
                obj.span = observed_span_from_struct(values[k])
            else:
                setattr(obj, k, values[k])
