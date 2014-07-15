
import json
from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.conf import settings


DEBUG = settings.DEBUG

class ThiefREST(object):
    __singleton__ = None
    template = None
    
    def __new__(self, request, *args, **kwargs):
        if not self.__singleton__:
            self.__singleton__ = object.__new__(self)
            self.__init__(self.__singleton__)
        
        return self.__singleton__(request, *args, **kwargs)
    
    def __call__(self, request, *args, **kw):
        if request.method == 'GET':
            response = self.get(request, **kw)
        elif request.method == 'POST':
            alt_method = request.POST.get('__method__')
            if alt_method == 'put':
                response = self.put(request, **kw)
            elif alt_method == 'delete':
                response = self.delete(request, **kw)
            else:
                response = self.post(request, **kw)
        
        elif request.method == 'PUT':
            response = self.put(request, **kw)
        elif request.method == 'DELETE':
            response = self.delete(request, **kw)
        else:
            raise Http404("Does not implement %s" % request.method)
            
        assert response != None, "where is the response?"
        
        if isinstance(response, HttpResponse):
            return response
        else:
            assert self.template, 'No template specific for REST'
            response['user'] = request.user
            return render_to_response(self.template, response, context_instance=RequestContext(request))
    
    def render(self, request, data):
        data['user'] = request.user
        return render_to_response(self.template, data, context_instance=RequestContext(request))
    
    def get(self, request, **kw):
        raise Http404("Does not implement GET")
            
    def post(self, request, **kw):
        raise Http404("Does not implement POST")
        
    def put(self, request, **kw):
        raise Http404("Does not implement PUT")
        
    def delete(self, request, **kw):
        raise Http404("Does not implement DELETE")

class ThiefRestAPI(ThiefREST):
    def __call__(self, request, format, *args, **kw):
        try:
            if request.method == 'GET':
                response = self.get(request, **kw)
            elif request.method == 'POST':
                a = request.POST.get('__action__')
                if a == 'PUT':
                    response = self.put(request, **kw)
                elif a == 'DELETE':
                    response = self.delete(request, **kw)
                else:
                    response = self.post(request, **kw)
            elif request.method == 'PUT':
                response = self.put(request, **kw)
            elif request.method == 'DELETE':
                response = self.delete(request, **kw)
        
            if format == 'json':
                return HttpResponse(json.dumps(response), content_type="application/json")
            else:
                return HttpResponse("404 unknow format", content_type="text/plain", status=404)
        except RestException as e:
            if format == 'json':
                return HttpResponse(json.dumps(e.response), content_type="application/json", status=e.status_code)
            else:
                return HttpResponse("404 unknow format", content_type="text/plain", status=404)
            
class RestException(Exception):
    def __init__(self, status_code, response):
        self.status_code = status_code
        self.response = response
        Exception.__init__(self, status_code, response)


class Rest404Error(RestException):
    def __init__(self, status_code=404, response={"error": "not found"}):
        RestException.__init__(self, status_code, response)
