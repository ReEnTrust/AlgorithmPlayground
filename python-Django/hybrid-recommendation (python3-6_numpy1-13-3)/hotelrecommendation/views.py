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
ratings_weightage=1
content_weightage=0.2
null_rating_replace='mean' #can be replaced by 'zero', 'one' or 'min'

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
my_recommender = hybrid_recommender(item_clusters,top_results,ratings_weightage,content_weightage, null_rating_replace)
my_recommender.fit(ratings,item_df)


def results(request, age):
    return render(request, 'hotelrecommendation/results.html', {})


class IndexView(FormView):
    template_name = 'hotelrecommendation/index.html'
    form_class = UserForm

    def form_valid(self, form):
        firstname = form.cleaned_data.get('firstname')
        lastname = form.cleaned_data.get('lastname')
        age = form.cleaned_data.get('age')
        target_price = form.cleaned_data.get('target_price')
        physically_disabled = form.cleaned_data.get('physically_disabled')
        is_married = form.cleaned_data.get('is_married')
        have_kids = form.cleaned_data.get('have_kids')
        gender = form.cleaned_data.get('gender')
        return redirect('hotelrecommendation:result_view', firstname, lastname, age, target_price, physically_disabled,is_married,have_kids,gender)


class ResultView(View):
    def get(self, request, firstname, lastname, age, target_price,physically_disabled,is_married,have_kids,gender):

        #We get the users with the same status
        relevant_users = User.objects.filter(user_disable = physically_disabled, user_is_married = is_married, user_have_kids = have_kids, gender= gender, user_target_price__gte = target_price-20, user_target_price__lte = target_price+20)

        #We have to rank them and take the closest user and the similar users
        ordered_age = relevant_users.annotate(age_diff=Func(F('user_age') - age, function='ABS')).order_by('age_diff')
        similarUsers = (list(ordered_age[:5]))
        closest_user = ordered_age.first()



        hotel_id_recommendation = my_recommender.predict([closest_user.id]).values.tolist()
        listHotelT = [] = []
        for l in hotel_id_recommendation:
            listHotelT.append(Hotel.objects.filter(id = l[0]).first())


        context ={'firstname': firstname,
                  'lastname': lastname,
                  'target_price': target_price,
                  'physically_disabled': physically_disabled,
                  'is_married': is_married,
                  'have_kids': have_kids,
                  'age' : age,
                  'gender': gender,
                  "L" : listHotelT,
                  'S' : similarUsers,
                  }

        return render(request, 'hotelrecommendation/results.html', context)





