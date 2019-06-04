from django.shortcuts import render
from hybrid_recommender import hybrid_recommender
import pandas as pd
from django.shortcuts import redirect
from django.db.models import Func, F
from django.views import View
from django.views.generic.edit import FormView
from .forms import UserForm
from .models import User
from .models import Hotel
from .models import Rating
# Create your views here.


#Initialising the tabular for the computation
user_id = []
rating = []
item_id = []
items = []
cols = ['isSingle', 'isTwin', 'isDouble', 'isFamily', 'isBudget', 'isConfortable', 'isDeluxe', 'isAccessible', 'isGoodReviews', 'hasSwimmingPool', 'hasBreakfast', 'isMichelinRestaurant']
feats = []

#Other parameters
item_clusters=4
top_results=10


#We fill the tabular for the reviews and build the dataframe
for r in Rating.objects.all():
    item_id.append(r.rating_hotel.id)
    user_id.append(r.rating_user.id)
    rating.append(r.rating_note)
ratings = pd.DataFrame({'user_id':user_id,'item_id':item_id,'rating':rating})


#We take the list of items ID
for i in Hotel.objects.all():
    items.append(i.id)
    #We need to take out features
    T = []
    T.append(1 if i.hotel_room_type == "S" else 0) #Single
    T.append(1 if i.hotel_room_type == "T" else 0) #Twin
    T.append(1 if i.hotel_room_type == "D" else 0) #Double
    T.append(1 if i.hotel_room_type == "F" else 0) #Family
    T.append(1 if i.hotel_night_price <=120 else 0) #Budget
    T.append(1 if i.hotel_night_price >= 100 and i.hotel_night_price <= 220 else 0) #Confortable
    T.append(1 if i.hotel_night_price >= 220 else 0) #Deluxe
    T.append(1 if i.hotel_disability_access else 0) #Accessible for disable persons
    T.append(1 if i.hotel_user_reviews >= 3 else 0) #Good reviews
    T.append(1 if i.hotel_swimming_pool else 0) #Swimming pool
    T.append(1 if i.hotel_breakfast_available else 0) #Breakfast
    T.append(1 if i.hotel_michelin_restaurant else 0) #Michelin restaurant
    feats.append(T)

#We create the dataframe for the features
item_df = pd.DataFrame(feats,index=items,columns=cols)

#We fit the recommender system
my_recommender1 = hybrid_recommender(item_clusters,top_results,ratings_weightage=1,content_weightage=1, null_rating_replace='mean') #can be replaced by 'zero', 'one' or 'min'
my_recommender2 = hybrid_recommender(item_clusters,top_results,ratings_weightage=1,content_weightage=0.2, null_rating_replace='mean') #can be replaced by 'zero', 'one' or 'min'
my_recommender3 = hybrid_recommender(item_clusters,top_results,ratings_weightage=0.2,content_weightage=1, null_rating_replace='mean') #can be replaced by 'zero', 'one' or 'min'
my_recommender1.fit(ratings,item_df)
my_recommender2.fit(ratings,item_df)
my_recommender3.fit(ratings,item_df)


def results(request, age):
    return render(request, 'hotelrecommendation/results.html', {})


class IndexView(FormView):
    template_name = 'hotelrecommendation/index.html'
    form_class = UserForm

    def form_valid(self, form):
        age = form.cleaned_data.get('age')
        target_price = form.cleaned_data.get('target_price')
        physically_disabled = form.cleaned_data.get('physically_disabled')
        is_married = form.cleaned_data.get('is_married')
        have_kids = form.cleaned_data.get('have_kids')
        gender = form.cleaned_data.get('gender')
        return redirect('hotelrecommendation:result_view', age, target_price, physically_disabled,is_married,have_kids,gender)


class ResultView(View):
    def get(self, request, age, target_price,physically_disabled,is_married,have_kids,gender, algo):

        #We get the users with the same status
        amplitude = 0
        while True:
            relevant_users = User.objects.filter(user_disable = physically_disabled, user_is_married = is_married, user_have_kids = have_kids, gender= gender, user_target_price__gte = target_price-amplitude, user_target_price__lte = target_price+amplitude)
            if not relevant_users:
                amplitude=amplitude+5
            else:
                break

        #We have to rank them and take the closest user and the similar users
        ordered_age = relevant_users.annotate(age_diff=Func(F('user_age') - age, function='ABS')).order_by('age_diff')
        similarUsers = (list(ordered_age[:5]))
        closest_user = ordered_age.first()


        #We take the predictions for the closest user
        if algo == 1:
            hotel_id_recommendation = my_recommender1.predict([closest_user.id]).values.tolist()
        elif algo == 2:
            hotel_id_recommendation = my_recommender2.predict([closest_user.id]).values.tolist()
        else:
            hotel_id_recommendation = my_recommender3.predict([closest_user.id]).values.tolist()

        #We take the hotels that correspond
        listHotelT = []
        for l in hotel_id_recommendation:
            listHotelT.append(Hotel.objects.filter(id = l[0]).first())

        #We take statistics on those hotels
        averagePrice = 0
        averageReview = 0
        percentageSingle = 0
        percentageTwin = 0
        percentageFamily = 0
        percentageDouble = 0
        percentageSwim = 0
        percentageBreak = 0
        percentageAccessible = 0
        for l in listHotelT:
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
        percentageNotAccessible = 100- percentageAccessible
        percentageSingle /= (top_results/100)
        percentageTwin /= (top_results/100)
        percentageFamily /= (top_results/100)
        percentageDouble /= (top_results/100)
        percentageSwim /= (top_results/100)
        percentageBreak /= (top_results/100)
        percentageNotSwim = 100 - percentageSwim
        percentageNotBreak = 100 - percentageBreak
        averagePrice /= top_results
        averageReview /= top_results

        testForm = UserForm()

        context ={
                  'target_price': target_price,
                  'physically_disabled': physically_disabled,
                  'is_married': is_married,
                  'have_kids': have_kids,
                  'age' : age,
                  'gender': gender,
                  "L" : listHotelT,
                  'S' : similarUsers,
                  'algo' : algo,
            'testForm' : testForm,
            'averagePrice' : averagePrice,
            'averageReview' : averageReview,
            'percentageDouble' : percentageDouble,
            'percentageTwin' : percentageTwin,
            'percentageSingle' : percentageSingle,
            'percentageFamily' : percentageFamily,
            'percentageAccessible' : percentageAccessible,
            'percentageNotAccessible' : percentageNotAccessible,
            'percentageSwim' : percentageSwim,
            'percentageNotSwim' : percentageNotSwim,
            'percentageBreak' : percentageBreak,
            'percentageNotBreak' : percentageNotBreak,
                  }

        return render(request, 'hotelrecommendation/results.html', context)


    def post(self, request, age, target_price, physically_disabled, is_married, have_kids, gender, algo):
        form = UserForm(data = request.POST)
        if form.is_valid():
            age = form.cleaned_data.get('age')
            target_price = form.cleaned_data.get('target_price')
            physically_disabled = form.cleaned_data.get('physically_disabled')
            is_married = form.cleaned_data.get('is_married')
            have_kids = form.cleaned_data.get('have_kids')
            gender = form.cleaned_data.get('gender')
            algo =  form.cleaned_data.get('algo')
        print(form.errors)

        return redirect('hotelrecommendation:result_view', age, target_price, physically_disabled,is_married,have_kids,gender,algo)



class ResultRatingUser(View):
    def get(self, request, age, target_price,physically_disabled,is_married,have_kids,gender,algo, id_user):

        #We need to display the ratings from a specific user
        rater = User.objects.filter(id = id_user).first()

        #We need to get the hotels that he rated
        rater_rating = Rating.objects.filter(rating_user = id_user)
        rater_rating = list(rater_rating)



        context ={
                  'target_price': target_price,
                  'physically_disabled': physically_disabled,
                  'is_married': is_married,
                  'have_kids': have_kids,
                  'age' : age,
                  'algo': algo,
                  'gender': gender,
                  'rater' : rater,
                  'rater_rating': rater_rating,
                  }

        return render(request, 'hotelrecommendation/rating_detail.html', context)

