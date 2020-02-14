from django.shortcuts import render

import logging
import json
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

import duckduckgo.duckduckgo as duckduckgo


# Create your views here.
@csrf_exempt
@require_POST
def wikianswer(request):
    """

    :param request:
    :return:
    """
    try:
        byte_str = request.body if request.body else {}
        print(byte_str)
        str_json = byte_str.decode('utf8').replace("'", '"')
        print(str_json)
        data = json.loads(str_json)
        query_string = data['query']
        response = duckduckgo.wikisearch(query_string)
        print("", response)
        # print(response)

        return JsonResponse(response)
    except Exception as exception:
        print("error -- " , exception)
        response = {
            "status": "Failure",
            "Message": "Failed to process the query",
            "Error": exception,
            "data": {}
        }
        return JsonResponse(response)
