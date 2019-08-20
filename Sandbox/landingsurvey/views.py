from django.shortcuts import render
from django.shortcuts import redirect
from django.views import View
from .models import EntrySurvey

#We expect 50 for each of them
url1='https://oxford.onlinesurveys.ac.uk/explanations-transparency-and-trust-be_v1'
url2='https://oxford.onlinesurveys.ac.uk/explanations-transparency-and-trust-be_v2'
url3='https://oxford.onlinesurveys.ac.uk/explanations-transparency-and-trust-be_v3'

#We expect 25 for each of them
url4='https://oxford.onlinesurveys.ac.uk/algorithm-playground-v1'
url5='https://oxford.onlinesurveys.ac.uk/explanations-transparency-and-trust-v2'


class IndexView(View):

    def get(self,request):
        context = {}
        return render(request, 'landingsurvey/index.html', context)

    def post(self,request):

        numberSuvey1 = EntrySurvey.objects.filter(entry_url = url1).count()
        numberSuvey2 = EntrySurvey.objects.filter(entry_url = url2).count()
        numberSuvey3 = EntrySurvey.objects.filter(entry_url = url3).count()
        numberSuvey4 = EntrySurvey.objects.filter(entry_url = url4).count()
        numberSuvey5 = EntrySurvey.objects.filter(entry_url = url5).count()
        numberRest = numberSuvey4 + numberSuvey5

        if numberSuvey1 <= numberSuvey2 and numberSuvey1 <= numberSuvey3 and numberSuvey1 <= numberRest:
            entry = EntrySurvey(entry_url = url1)
            entry.save()
            context = { 'returnedURL' : url1}
        elif numberSuvey2 <= numberSuvey1 and numberSuvey2 <= numberSuvey3 and numberSuvey2 <= numberRest:
            entry = EntrySurvey(entry_url = url2)
            entry.save()
            context = { 'returnedURL' : url2}
        elif numberSuvey3 <= numberSuvey1 and numberSuvey3 <= numberSuvey2 and numberSuvey3 <= numberRest:
            entry = EntrySurvey(entry_url = url3)
            entry.save()
            context = { 'returnedURL' : url3}
        elif numberSuvey4 <= numberSuvey5:
            entry = EntrySurvey(entry_url = url4)
            entry.save()
            context = { 'returnedURL' : url4}
        else:
            entry = EntrySurvey(entry_url = url5)
            entry.save()
            context = { 'returnedURL' : url5}

        return render(request, 'landingsurvey/index.html', context)