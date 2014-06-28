from django.shortcuts import render

# from django.http import HttpResponse
# def index(request):
#     return HttpResponse("Rango says hello world!")

from django.template import RequestContext
from django.shortcuts import render_to_response

#Import the Category model
from rango.models import Category

def index(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
    context = RequestContext(request)
    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    context_dict = {'boldmessage': "I am bold font from the context"}
    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict['categories'] = category_list

    return render_to_response('rango/index.html', context_dict, context)

