from django.shortcuts import render
from hybrid_recommender import hybrid_recommender
from decimal import *
from django.shortcuts import redirect
from django.db.models import Func, F
from django.views import View
from .forms import UserForm
from .forms import FeedbackForm
from .models import User
from .models import Hotel
from .models import LogInstance
from .models import LogComment
from .models import LogAction
from .models import Rating
import pickle


#We fit the recommender system
top_results=10

pickle_off_1=open("pickle/Rec1.pickle","rb")
my_recommender1 = pickle.load(pickle_off_1)

pickle_off_2=open("pickle/Rec2.pickle","rb")
my_recommender2 = pickle.load(pickle_off_2)

pickle_off_3=open("pickle/Rec3.pickle","rb")
my_recommender3 = pickle.load(pickle_off_3)



class IndexView(View):

    def get(self,request):
        context = {}
        return render(request, 'hotelrecommendation/index.html', context)

    def post(self,request):

        #We create a new instance
        newLogInstance = LogInstance()
        newLogInstance.save()

        #We create a logAction that the user has logged In
        newLogAction = LogAction(log_instance_id= newLogInstance.id, log_action_description="User has logged in, redirecting to default page.")
        newLogAction.save()

        return redirect('hotelrecommendation:result_view', newLogInstance.id, 18, 200, False,False,False,"M",1, "L", 0)

class ResultView(View):

    def get(self, request,log, age, target_price,physically_disabled,is_married,have_kids,gender, algo,type, data):

        #We create a logAction that the page was shown to the user
        newLogAction = LogAction(log_instance_id= log, log_action_description="User is shown the page (age,price,wheelchair,married,kids,gender,algo,type,data) = ("+str(age)+","+str(target_price)+","+str(physically_disabled)+","+str(is_married)+","+str(have_kids)+","+gender+","+str(algo)+","+str(type)+","+str(data)+").")
        newLogAction.save()

        #We get the comments from the user
        set_comments = {}
        for c in LogComment.objects.filter(log_instance_id = log):
            set_comments[c.log_about] = { 'log_radio1' : c.log_radio1,
                                          'log_comment' : c.log_comment,}

        #We have to find old instances of this user
        OldActionsUpdate = [s for s in list(LogAction.objects.filter(log_instance_id=log)) if "User requested the page (age,price,wheelchair,married,kids,gender,algo,type,data)" in s.log_action_description]
        OldPresetsString = [s.log_action_description[85:-2] for s in OldActionsUpdate]
        OldPresets = []
        for s in OldPresetsString:
            splitted = s.split(',')
            OldPresets.append({
                'age' : int(splitted[0]),
                'price': Decimal(splitted[1]),
                'wheelchair': splitted[2] == "True",
                'married': splitted[3] == "True",
                'kids': splitted[4] == "True",
                'gender': splitted[5],
                'algo': int(splitted[6]),
                'type': splitted[7],
                'data': int(splitted[8]),
            })

        #We get the users with the same status
        set_relevant_users = []
        for o in OldPresets:
            amplitude = 0
            while True:
                relevant_users = User.objects.filter(type = o['type'],user_disable = o['wheelchair'], user_is_married = o['married'], user_have_kids = o['kids'], gender= o['gender'], user_target_price__gte = o['price']-amplitude, user_target_price__lte = o['price']+amplitude)
                if not relevant_users:
                    amplitude=amplitude+5
                else:
                    set_relevant_users.append(relevant_users)
                    break

        set_ordered_age = []
        #We have to rank them and take the closest user and the similar users
        for s in set_relevant_users:
            set_ordered_age.append(s.annotate(age_diff=Func(F('user_age') - age, function='ABS')).order_by('age_diff'))

        similarUsers = []
        if set_ordered_age:
            similarUsers = (list(set_ordered_age[-1][:5]))

        set_closest = []
        for s in set_ordered_age:
            set_closest.append(s.last())


        #We take the predictions for the closest user
        set_predictions = []
        for o,s in zip(OldPresets,set_closest):
            if o['algo'] == 1:
                set_predictions.append(my_recommender1[o['data']].predict([s.id]).values.tolist())
            elif o['algo'] == 2:
                set_predictions.append(my_recommender2[o['data']].predict([s.id]).values.tolist())
            else:
                set_predictions.append(my_recommender3[o['data']].predict([s.id]).values.tolist())

        #We take the hotels that correspond
        set_list_hotels = []
        for s in set_predictions:
            listHotelT = []
            for l in s:
                listHotelT.append(Hotel.objects.filter(id = l[0]).first())
            set_list_hotels.append(listHotelT)


        #We take statistics on those hotels
        set_averagePrice = []
        set_averageReview = []
        set_percentageSingle = []
        set_percentageTwin = []
        set_percentageFamily = []
        set_percentageDouble = []
        set_percentageSwim = []
        set_percentageBreak = []
        set_percentageAccessible = []

        for Q in set_list_hotels:
            averagePrice = 0
            averageReview = 0
            percentageSingle = 0
            percentageTwin = 0
            percentageFamily = 0
            percentageDouble = 0
            percentageSwim = 0
            percentageBreak = 0
            percentageAccessible = 0
            for l in Q:
                averagePrice += l.hotel_night_price
                averageReview +=l.hotel_user_reviews
                if l.hotel_room_type == "S":
                    percentageSingle = percentageSingle+1
                elif l.hotel_room_type == "T":
                    percentageTwin = percentageTwin+1
                elif l.hotel_room_type == "F":
                    percentageFamily = percentageFamily+1
                else:
                    percentageDouble = percentageDouble+1

                if l.hotel_disability_access:
                    percentageAccessible = percentageAccessible +1

                if l.hotel_swimming_pool:
                    percentageSwim = percentageSwim +1

                if l.hotel_breakfast_available:
                    percentageBreak = percentageBreak +1

            percentageAccessible /= (top_results/100)
            set_percentageAccessible.append(percentageAccessible)

            percentageSingle /= (top_results/100)
            set_percentageSingle.append(percentageSingle)

            percentageTwin /= (top_results/100)
            set_percentageTwin.append(percentageTwin)

            percentageFamily /= (top_results/100)
            set_percentageFamily.append(percentageFamily)

            percentageDouble /= (top_results/100)
            set_percentageDouble.append(percentageDouble)

            percentageSwim /= (top_results/100)
            set_percentageSwim.append(percentageSwim)

            percentageBreak /= (top_results/100)
            set_percentageBreak.append(percentageBreak)

            averagePrice /= top_results
            set_averagePrice.append(averagePrice)

            averageReview /= top_results
            set_averageReview.append(averageReview)


        context ={
            'target_price': target_price,
            'physically_disabled': physically_disabled,
            'is_married': is_married,
            'have_kids': have_kids,
            'age' : age,
            'log' : log,
            'gender': gender,
            "L" : zip(set_list_hotels,OldPresets,set_averagePrice, set_averageReview ,set_percentageSingle ,set_percentageTwin ,set_percentageFamily ,set_percentageDouble ,set_percentageSwim ,set_percentageBreak ,set_percentageAccessible),
            'S' : similarUsers,
            'algo' : algo,
            'set_comments' : set_comments,
            'type' : type,
            'data' : data,
                  }

        return render(request, 'hotelrecommendation/results.html', context)


    def post(self, request, log, age, target_price, physically_disabled, is_married, have_kids, gender, algo,type, data):

        if request.POST.__contains__('comment'): #This means that we are saving a comment
            form = FeedbackForm(data = request.POST)
            feed = '0'
            comment = ''
            instance = request.POST.__getitem__('data-instance')
            if form.is_valid():
                feed = form.cleaned_data.get('feed')
                comment = form.cleaned_data.get('comment')
            print(form.errors)

            feed = 'No answers' if feed == "" else 'Totally disagree' if feed == "1" else 'Disagree' if feed == "2" else 'Neutral' if feed == "3" else 'I do not know' if feed == "4" else 'Agree' if feed == "5" else 'Totally Agree'

            if not LogComment.objects.filter(log_instance_id = log, log_about= instance).exists(): #We never saw such object
                newLogComment = LogComment(log_instance_id = log, log_comment = comment, log_radio1 = feed, log_about= instance)
                newLogComment.save()

                #We save the action of giving a feedback
                newLogAction = LogAction(log_instance_id= log, log_action_description="User gave his feedback for "+instance+".")
                newLogAction.save()
            else: #We have such objects, in this case, we update the database
                LogComment.objects.filter(log_instance_id = log, log_about= instance).update(log_comment = comment, log_radio1 = feed)

                #We save the action of updating a feedback
                newLogAction = LogAction(log_instance_id= log, log_action_description="User updated his feedback for "+instance+".")
                newLogAction.save()

        elif request.POST.__contains__('algo'): #This means that we are changin a profile
            form = UserForm(data = request.POST)
            if form.is_valid():
                age = form.cleaned_data.get('age')
                target_price = form.cleaned_data.get('target_price')
                physically_disabled = form.cleaned_data.get('physically_disabled')
                is_married = form.cleaned_data.get('is_married')
                have_kids = form.cleaned_data.get('have_kids')
                gender = form.cleaned_data.get('gender')
                algo =  form.cleaned_data.get('algo')
                type = form.cleaned_data.get('type')
                data = form.cleaned_data.get('data')
            print(form.errors)

            #We create a logAction that the page was shown to the user
            newLogAction = LogAction(log_instance_id= log, log_action_description="User requested the page (age,price,wheelchair,married,kids,gender,algo,type,data) = ("+str(age)+","+str(target_price)+","+str(physically_disabled)+","+str(is_married)+","+str(have_kids)+","+gender+","+str(algo)+","+str(type)+","+str(data)+").")
            newLogAction.save()

        return redirect('hotelrecommendation:result_view', log, age, target_price, physically_disabled,is_married,have_kids,gender,algo, type, data)



class ResultRatingUser(View):
    def get(self, request, log, age, target_price,physically_disabled,is_married,have_kids,gender,algo, id_user, type, data):



        #We need to display the ratings from a specific user
        rater = User.objects.filter(id = id_user).first()

        #We need to get the hotels that he rated
        rater_rating = Rating.objects.filter(rating_user = id_user)
        rater_rating = list(rater_rating)

        #We create a logAction that the page was shown to the user
        newLogAction = LogAction(log_instance_id= log, log_action_description="We show the page of user "+str(rater.id)+".")
        newLogAction.save()

        context ={
            'log' : log,
            'target_price': target_price,
            'physically_disabled': physically_disabled,
            'is_married': is_married,
            'have_kids': have_kids,
            'age' : age,
            'algo': algo,
            'gender': gender,
            'rater' : rater,
            'rater_rating': rater_rating,
            'type' : type,
            'data' : data,
                  }

        return render(request, 'hotelrecommendation/rating_detail.html', context)

