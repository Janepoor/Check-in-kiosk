# Create your views here.

from django.shortcuts import redirect,render
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test, login_required, permission_required
from django.contrib.auth import logout
from django.utils import timezone
import datetime, requests, urllib, pytz
import dateutil.parser


