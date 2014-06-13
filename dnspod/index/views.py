# -*-coding:utf-8-*-

__author__ = "mush (btyh17mxy@gmail.com)"

from django.shortcuts import render_to_response
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from libs.dnspod import *

domain = Domain('btyh17mxy@gmail.com','mushcode')
record = Record('btyh17mxy@gmail.com','mushcode')

def domian_list(request):
    data = domain.list()
    return render_to_response('domain_list.html', data)

class DomainAddForm(forms.Form):
    domain = forms.CharField()

def domain_remove(request, domain_id):
    domain.remove(domain_id = domain_id)
    return HttpResponseRedirect('/')

@csrf_exempt
def domain_add(request):
    if request.method == 'GET':
        data = {}
        data['form']=DomainAddForm()
        return render_to_response('domain_add.html', data)
    else:
        form = DomainAddForm(request.POST)
        if form.is_valid():
            domain_name = form.cleaned_data['domain']
            domain.create(domain_name)
            return HttpResponseRedirect('/')
        else:
            print 'don\'t panic'

def record_list(request, domain_id):
    data = record.list(domain_id = domain_id) 
    return render_to_response('record.html', data)

class RecordAddForm(forms.Form):
    sub_domain = forms.CharField()
    value = forms.CharField()
    ttl = forms.IntegerField()
    record_line = forms.ChoiceField(choices=((u'默认',u'默认'),
        (u'电信',u'电信'),(u'联通',u'联通'),(u'教育网',u'教育网'),
        (u'百度',u'百度'),(u'搜索引擎',u'搜索引擎')))
    mx = forms.IntegerField(required=False)
    record_type = forms.ChoiceField(choices=(('A','A'),('CNAME','CNAME'),('MX','MX')))    


@csrf_exempt
def record_add(request, domain_id):
    if request.method == 'GET':
        data = {'form':RecordAddForm()}
        return render_to_response('record_add.html', data)
    else:
        form = RecordAddForm(request.POST)
        print form
        if form.is_valid():
            form_data = form.cleaned_data
            form_data['domain_id'] = domain_id
            record.create(**form_data)
            return HttpResponseRedirect('/record/list/%s'%domain_id)
        else:
            print 'fuck'
            return HttpResponseRedirect('/record/add/%s'%domain_id)


def record_remove(request, domain_id, record_id):
    record.remove(domain_id = domain_id, record_id = record_id)
    return HttpResponseRedirect('/record/list/%s'%domain_id)

class UploadFileForm(forms.Form):
    file  = forms.FileField()

def domain_info(request, domain_id):
    data = domain.info(domain_id = domain_id)
    try:
        data.update(domain.lockstatus(domain_id = domain_id))
    except DNSPodError,e:
        data.update({'lock':{'lock_status':'no'}})

    data['form'] = UploadFileForm()
    return render_to_response('domain_info.html', data)

def record_export(request, domain_id):
    utils = Utils()
    response = HttpResponse()
    utils.export_records(record, domain_id, response)
    response['Content-Disposition'] = 'attachment; filename="%s.csv"'%domain_id
    response.__setitem__('content-type', 'text/csv')
    return response

@csrf_exempt
def record_import(request, domain_id):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            utils = Utils()
            utils.import_records(record, domain_id, request.FILES['file'])
            return HttpResponseRedirect('/record/list/%s'%domain_id)
        else :
            return HttpResponse('import fail')
