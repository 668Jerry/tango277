from django.shortcuts import render

# from django.http import HttpResponse
# def index(request):
#     return HttpResponse("Rango says hello world!")

from django.template import RequestContext
from django.shortcuts import render_to_response

#Import the Category model
from rango.models import Category
from rango.models import Page
from datetime import datetime

def encode_url(str):
    return str.replace(' ', '_')

def decode_url(str):
    return str.replace('_', ' ')

def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__startswith=starts_with)
    else:
        cat_list = Category.objects.all()

    if max_results > 0:
        if (len(cat_list) > max_results):
            cat_list = cat_list[:max_results]

    for cat in cat_list:
        cat.url = encode_url(cat.name)

    return cat_list

def index(request):
    #request.session.set_test_cookie()
    #print ">>>> TEST Good Morning!!"
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

    cat_list = get_category_list()
    context_dict['cat_list'] = cat_list
#    response = render_to_response('rango/index.html', context_dict, context)
#
#    # The following two lines are new.
#    # We loop through each category returned, and create a URL attribute.
#    # This attribute stores an encoded URL (e.g. spaces replaced with underscores).
#    for category in category_list:
#        category.url = category.name.replace(' ', '_')
#
#    return render_to_response('rango/index.html', context_dict, context)
    #### NEW CODE ####
    # Obtain our Response object early so we can add cookie information.
    response = render_to_response('index.html', context_dict, context)

    # Get the number of visits to the site.
    # We use the COOKIES.get() function to obtain the visits cookie.
    # If the cookie exists, the value returned is casted to an integer.
    # If the cookie doesn't exist, we default to zero and cast that.
    visits = int(request.COOKIES.get('visits', '1000'))
    print "visits: " + str(visits)

    # Does the cookie last_visit exist?
    if 'last_visit' in request.COOKIES:
        # Yes it does! Get the cookie's value.
        last_visit = request.COOKIES['last_visit']
        print "last_visit: " + str(last_visit)
        # Cast the value to a Python date/time object.
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
        print "last_visit_time: " + str(last_visit_time)

        # If it's been more than a day since the last visit...
        if (datetime.now() - last_visit_time).seconds > 5:
            # ...reassign the value of the cookie to +1 of what it was before...
            response.set_cookie('visits', visits+1)
            # ...and update the last visit cookie, too.
            response.set_cookie('last_visit', datetime.now())
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time.
        response.set_cookie('last_visit', datetime.now())
    response.set_cookie('hello', 'Just a hello with else.')

    #### NEW CODE ####
    if request.session.get('session_last_visit'):
        # The session has a value for the last visit
        session_last_visit_time = request.session.get('session_last_visit')
        session_visits = request.session.get('session_visits', 0)

        if (datetime.now() - datetime.strptime(session_last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).seconds > 5:
            request.session['session_visits'] = session_visits + 1
            request.session['session_last_visit'] = str(datetime.now())
        print "session_visits: " + str(session_visits)
    else:
        # The get returns None, and the session does not have a value for the last visit.
        request.session['session_last_visit'] = str(datetime.now())
        request.session['session_visits'] = 1
        # print "session_visits: " + str(session_last_visit)
    #### END NEW CODE ####

    # Return response back to the user, updating any cookies that need changed.
    return response
    #### END NEW CODE ####

def evil(request):
    context = RequestContext(request)
    context_dict = {}
    return render_to_response('evil.html', context_dict, context)

def category(request, category_name_url):
    # Request our context
    context = RequestContext(request)

    # Change underscores in the category name to spaces.
    # URL's don't handle spaces well, so we encode them as underscores.
    category_name = decode_url(category_name_url)

    # Build up the dictionary we will use as out template context dictionary.
    context_dict = {'category_name': category_name, 'category_name_url': category_name_url}

    cat_list = get_category_list()
    context_dict['cat_list'] = cat_list
    try:
        # Find the category with the given name.
        # Raises an exception if the category doesn't exist.
        # We also do a case insensitive match.
        category = Category.objects.get(name__iexact=category_name)
        context_dict['category'] = category
        # Retrieve all the associated pages.
        # Note that filter returns >= 1 model instance.
        pages = Page.objects.filter(category=category).order_by('-views')

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
    except Category.DoesNotExist:
        # We get here if the category does not exist.
        # Will trigger the template to display the 'no category' message.
        pass

    if request.method == 'POST':
        query = request.POST.get('query')
        if query:
            query = query.encode('utf-8').strip()
            result_list = run_query(query)
            context_dict['result_list'] = result_list

    # Go render the response and return it to the client.
    return render_to_response('category.html', context_dict, context)

# def about(request):
#     # Request the context.
#     context = RequestContext(request)
#     context_dict = {}
#     cat_list = get_category_list()
#     context_dict['cat_list'] = cat_list
#     # If the visits session varible exists, take it and use it.
#     # If it doesn't, we haven't visited the site so set the count to zero.
#
#     count = request.session.get('visits',0)
#
#     context_dict['visit_count'] = count
#
#     # Return and render the response, ensuring the count is passed to the template engine.
#     return render_to_response('rango/about.html', context_dict , context)

from rango.forms import CategoryForm

def add_category(request):
    # Get the context from the request.
    context = RequestContext(request)

    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    cat_list = get_category_list()
    context_dict = {'form': form}
    context_dict['cat_list'] = cat_list

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('add_category.html', context_dict, context)

from rango.forms import PageForm

def decode_url(str):
    return str.replace('_', ' ')

def add_page(request, category_name_url):
    context = RequestContext(request)

    category_name = decode_url(category_name_url)
    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            # This time we cannot commit straight away.
            # Not all fields are automatically populated!
            page = form.save(commit=False)

            # Retrieve the associated Category object so we can add it.
            # Wrap the code in a try block - check if the category actually exists!
            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                # If we get here, the category does not exist.
                # Go back and render the add category form as a way of saying the category does not exist.
                return render_to_response('add_category.html', {}, context)

            # Also, create a default value for the number of views.
            page.views = 0

            # With this, we can then save our new model instance.
            page.save()

            # Now that the page is saved, display the category instead.
            return category(request, category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()

    cat_list = get_category_list()
    context_dict = {'category_name_url': category_name_url,
             'category_name': category_name, 'form': form}
    context_dict['cat_list'] = cat_list


    return render_to_response('add_page.html', context_dict, context)

from rango.forms import UserForm, UserProfileForm

def register(request):
    if request.session.test_cookie_worked():
        print ">>>> TEST COOKIE WORKED!"
        #request.session.delete_test_cookie()
    
    # Like before, get the request's context.
    context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render_to_response(
        'register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
            context)

from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse

def user_login(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('login.html', {}, context)

from django.contrib.auth.decorators import login_required
@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")

from django.contrib.auth import logout

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/')


def about(request):
    # Request the context.
    context = RequestContext(request)
    context_dict = {}
    # cat_list = get_category_list()
    # category_list = Category.objects.order_by('-likes')[:5]
    cat_list = Category.objects.order_by('-likes')[:5]
    context_dict['cat_list'] = cat_list
    # If the visits session varible exists, take it and use it.
    # If it doesn't, we haven't visited the site so set the count to zero.

    count = request.session.get('session_visits',0)

    context_dict['visit_count'] = count

    cat_list = get_category_list()
    context_dict['cat_list'] = cat_list

    if request.session.get('session_last_visit'):
        # The session has a value for the last visit
        session_last_visit_time = request.session.get('session_last_visit')
        session_visits = request.session.get('session_visits', 0)
        if (datetime.now() - datetime.strptime(session_last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).seconds > 5:
            request.session['session_visits'] = session_visits + 1
            request.session['session_last_visit'] = str(datetime.now())
        context_dict['last_visit_print'] = str(session_last_visit_time[:-7])


    # Return and render the response, ensuring the count is passed to the template engine.
    return render_to_response('about.html', context_dict , context)

from rango.bing_search import run_query

def search(request):
    context = RequestContext(request)
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].encode('utf-8').strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)
    cat_list = get_category_list()
    context_dict = {'result_list': result_list}
    context_dict['cat_list'] = cat_list
    return render_to_response('search.html', context_dict, context)


def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__startswith=starts_with)
    else:
        cat_list = Category.objects.all()

    if max_results > 0:
        if (len(cat_list) > max_results):
            cat_list = cat_list[:max_results]

    for cat in cat_list:
        cat.url = encode_url(cat.name)

    return cat_list

from django.contrib.auth.models import User
from rango.models import UserProfile


# @login_required
# def profile(request):
#     # Request the context.
#     context = RequestContext(request)
#     context_dict = {}
#     # cat_list = get_category_list()
#     # category_list = Category.objects.order_by('-likes')[:5]
#     cat_list = Category.objects.order_by('-likes')[:5]
#     context_dict['cat_list'] = cat_list
#     # If the visits session varible exists, take it and use it.
#     # If it doesn't, we haven't visited the site so set the count to zero.
#
#     count = request.session.get('session_visits',0)
#
#     context_dict['visit_count'] = count
#
#     cat_list = get_category_list()
#     context_dict['cat_list'] = cat_list
#
#     if request.session.get('session_last_visit'):
#         # The session has a value for the last visit
#         session_last_visit_time = request.session.get('session_last_visit')
#         session_visits = request.session.get('session_visits', 0)
#         if (datetime.now() - datetime.strptime(session_last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).seconds > 5:
#             request.session['session_visits'] = session_visits + 1
#             request.session['session_last_visit'] = str(datetime.now())
#         context_dict['last_visit_print'] = str(session_last_visit_time[:-7])
#
#
#     # Return and render the response, ensuring the count is passed to the template engine.
#     # return render_to_response('rango/about.html', context_dict , context)
#
#     # context = RequestContext(request)
#     # # cat_list = get_category_list()
#     # # context_dict = {'cat_list': cat_list}
#     # # u = User.objects.get(username=request.user)
#     # #
#     # # try:
#     # #     up = UserProfile.objects.get(user=u)
#     # # except:
#     # #     up = None
#     # #
#     # # context_dict['user'] = u
#     # # context_dict['userprofile'] = up
#     # return render_to_response('rango/profile.html', context_dict, context)
#         return render_to_response('profile.html', context_dict , context)

@login_required
def profile(request):
    context = RequestContext(request)
    cat_list = get_category_list()
    context_dict = {'cat_list': cat_list}
    u = User.objects.get(username=request.user)

    try:
        up = UserProfile.objects.get(user=u)
    except:
        up = None

    context_dict['user'] = u
    context_dict['userprofile'] = up
    return render_to_response('profile.html', context_dict, context)

from django.shortcuts import redirect

def track_url(request):
    context = RequestContext(request)
    page_id = None
    url = '/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass
    return redirect(url)

@login_required
def like_category(request):
    context = RequestContext(request)
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']

    likes = 0
    if cat_id:
        category = Category.objects.get(id=int(cat_id))
        if category:
            likes = category.likes + 1
            category.likes = likes
            category.save()

    return HttpResponse(likes)

def suggest_category(request):
    context = RequestContext(request)
    cat_list = []
    starts_with = ''
    if request.method == 'GET':
        starts_with = request.GET['suggestion']
    else:
        starts_with = request.POST['suggestion']

    cat_list = get_category_list(8, starts_with)

    return render_to_response('category_list.html', {'cat_list': cat_list }, context)