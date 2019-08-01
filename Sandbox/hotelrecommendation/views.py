from django.shortcuts import render
from decimal import *
from django.shortcuts import redirect
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
from sklearn.neighbors import NearestNeighbors
import math


#We fit the recommender system
top_results=10

def recommandation(algo, data, user_id):
    if algo == 1:
        pickle_off_1=open("pickle/Rec1.pickle","rb")
        my_recommender1 = pickle.load(pickle_off_1)
        return my_recommender1[data].predict([user_id]).values.tolist()
    elif algo == 2:
        pickle_off_2=open("pickle/Rec2.pickle","rb")
        my_recommender2 = pickle.load(pickle_off_2)
        return my_recommender2[data].predict([user_id]).values.tolist()
    else:
        pickle_off_3=open("pickle/Rec3.pickle","rb")
        my_recommender3 = pickle.load(pickle_off_3)
        return my_recommender3[data].predict([user_id]).values.tolist()

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
            set_relevant_users.append(compute_neighbor(o['age'],o['price'],o['wheelchair'],o['married'],o['kids'],o['gender'],o['type']))

        similarUsers = []
        if set_relevant_users:
            similarUsers.append(set_relevant_users[-1])

        set_closest = set_relevant_users


        #We take the predictions for the closest user
        set_predictions = []
        for o,s in zip(OldPresets,set_closest):
            set_predictions.append(recommandation(o['algo'],o['data'],s.id))


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

        elif request.POST.__contains__('algo'): #This means that we are changing a profile
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
        rater_rating = Rating.objects.filter(rating_user = id_user, rating_type = data)
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







##### MISC FUNCTIONS


def int_bool(val):
    if val:
        return 1
    return 0

def int_gen(val):
    if val=='M':
        return 0
    return 1

def int_type(val):
    if val=='B':
        return 0
    return 1

def user_to_user_sample(u):
    return (u.user_age,float(u.user_target_price),int_bool(u.user_disable),int_bool(u.user_is_married),int_bool(u.user_have_kids),int_gen(u.gender),int_type(u.type))

def dist(a,b):
    # a and b are two users with the following (numerical) parameters: age, target_price, physically_disabled, is_married, have_kids, gender, type

    # weights on the parameters:
    # age -> 1.5/7
    # target_price -> 0.5/7
    # physically disables -> 2/7
    # is_married -> 0.25/7
    # have_kids -> 0.5/7
    # gender -> 2/7
    # type -> 0.25/7

    # weights array:
    weights = [200,20,1000,20,30,200,20]

    #euclidean distance:
    d = math.sqrt(weights[0]*(a[0]-b[0])**2+weights[1]*(a[1]-b[1])**2+weights[2]*(a[2]-b[2])**2+weights[3]*(a[3]-b[3])**2+weights[4]*(a[4]-b[4])**2+weights[5]*(a[5]-b[5])**2+weights[6]*(a[6]-b[6])**2)

    return d




def compute_neighbor(age,target_price,physically_disabled,is_married,have_kids,gender,type):
    target_user=[age,float(target_price),int_bool(physically_disabled),int_bool(is_married),int_bool(have_kids),int_gen(gender),int_type(type)]
    samples=[]
    tmp=()
    dic_users={}
    for u in User.objects.all():
        tmp=user_to_user_sample(u)
        samples.append(tmp)
        dic_users[u.id]=tmp

    rev_dic_users={value: key for key,value in dic_users.items()}

    neigh = NearestNeighbors(n_neighbors=2, algorithm='ball_tree',metric=dist)
    neigh.fit(samples)

    kNeighb = neigh.kneighbors([target_user], 5, return_distance=False)

    nn_id = rev_dic_users[samples[kNeighb[0][0]]]
    nn = User.objects.filter(id = nn_id).first()

    return nn





