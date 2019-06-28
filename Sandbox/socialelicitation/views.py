from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.shortcuts import redirect
from hotelrecommendation.models import User, Rating,Hotel
from socialelicitation.models import LogInstance, LogAction
from hybrid_recommender import hybrid_recommender
import random
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
        return render(request, 'socialelicitation/index.html', context)

    def post(self,request):

        #We create a new instance
        newLogInstance = LogInstance()
        newLogInstance.save()

        #We create a logAction that the user has logged In
        newLogAction = LogAction(log_instance_id= newLogInstance.id, log_action_description="User has logged in, redirecting to default page.")
        newLogAction.save()

        return redirect('socialelicitation:iter_view', newLogInstance.id, 1)


class IterView(View):

    def get(self, request,log, numbiter):


        #We get a randomUser
        randomUser = User.objects.order_by("?").first()

        #We get a random recommender
        randomAlgo1 = random.randint(1,3)
        randomAlgo2 = random.randint(1,3)
        randomData1 = random.randint(0,3)
        randomData2 = random.randint(0,3)
        if randomAlgo1 == randomAlgo2:
            while randomData1==randomData2:
                randomData2 = random.randint(0,4)


        #We create a logAction that the user is presented a user with 2 choices
        newLogAction = LogAction(log_instance_id=log, log_action_description="We present the data of user "+str(randomUser.id)+" with Choice1=algo"+str(randomAlgo1)+"/data"+str(randomData1)+" and Choice2=algo"+str(randomAlgo2)+"/data"+str(randomData2))
        newLogAction.save()



        algosData = [ {'algo' : randomAlgo1, 'data': randomData1}, {'algo' : randomAlgo2, 'data': randomData2}]

        set_predictions = []
        for s in algosData:
            if s['algo'] == 1:
                set_predictions.append(my_recommender1[s['data']].predict([randomUser.id]).values.tolist())
            elif s['algo'] == 2:
                set_predictions.append(my_recommender2[s['data']].predict([randomUser.id]).values.tolist())
            else:
                set_predictions.append(my_recommender3[s['data']].predict([randomUser.id]).values.tolist())

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
            'randomUser' : randomUser,
            'numbiter': numbiter-1,
            "L" : zip(set_list_hotels,algosData,set_averagePrice, set_averageReview ,set_percentageSingle ,set_percentageTwin ,set_percentageFamily ,set_percentageDouble ,set_percentageSwim ,set_percentageBreak ,set_percentageAccessible),
        }

        return render(request, 'socialelicitation/choice.html', context)


    def post(self, request, log, numbiter):

        #We save the choice of the user
        newLogAction = LogAction(log_instance_id=log, log_action_description="The user has choosen "+str(request.POST.get('choice'))+" for his contribution "+str(numbiter))
        newLogAction.save()

        return redirect('socialelicitation:iter_view', log, numbiter+1)

