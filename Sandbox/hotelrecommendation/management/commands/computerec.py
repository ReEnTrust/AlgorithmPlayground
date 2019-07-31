import pickle
from django.core.management.base import BaseCommand, CommandError
from hotelrecommendation.models import Hotel, Rating
from hybrid_recommender import hybrid_recommender
import pandas as pd
from decimal import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        #Initialising the tabular for the computation
        items = []
        cols = ['isSingle', 'isTwin', 'isDouble', 'isFamily', 'isAccessible', 'isGoodReviews', 'hasSwimmingPool', 'hasBreakfast', 'isMichelinRestaurant', 'price', 'location_score']
        feats = []
        ratings = []
        max_price_hotel = Hotel.objects.latest('hotel_night_price').hotel_night_price #This is the highest price

        #Other parameters
        item_clusters=4
        top_results=10

        #We fill the tabular for the reviews and build the dataframe
        for i in range(0,4):
            user_id = []
            rating = []
            item_id = []
            for r in list(Rating.objects.filter(rating_type=i)):
                item_id.append(r.rating_hotel.id)
                user_id.append(r.rating_user.id)
                rating.append(r.rating_note)
            ratings.append(pd.DataFrame({'user_id':user_id,'item_id':item_id,'rating':rating}))

        print("We created the ratings dataframe")

        #We take the list of items ID
        for i in Hotel.objects.all():
            items.append(i.id)
            #We need to take out features
            T = []
            T.append(1 if i.hotel_room_type == "S" else 0) #Single
            T.append(1 if i.hotel_room_type == "T" else 0) #Twin
            T.append(1 if i.hotel_room_type == "D" else 0) #Double
            T.append(1 if i.hotel_room_type == "F" else 0) #Family
            T.append(1 if i.hotel_disability_access else 0) #Accessible for disable persons
            #T.append(1 if i.hotel_user_reviews >= 3 else 0) #Good reviews
            T.append(i.hotel_user_reviews/5)
            T.append(1 if i.hotel_swimming_pool else 0) #Swimming pool
            T.append(1 if i.hotel_breakfast_available else 0) #Breakfast
            T.append(1 if i.hotel_michelin_restaurant else 0) #Michelin restaurant
            T.append(i.hotel_night_price / max_price_hotel) #This correspond to the price
            T.append(i.hotel_location_score/5) #This is the location score
            feats.append(T)

        #We create the dataframe for the features
        item_df = pd.DataFrame(feats,index=items,columns=cols)

        print("We created the hotel dataframe")

        #We fit the recommender system
        my_recommender1 = []
        my_recommender2 = []
        my_recommender3 = []

        for i in range(0,4):
            my_recommender1.append(hybrid_recommender(item_clusters,top_results,ratings_weightage=1,content_weightage=1, null_rating_replace='mean')) #can be replaced by 'zero', 'one' or 'min'
            my_recommender1[i].fit(ratings[i],item_df)

        print("We computed the recommender for algorithm 1")

        for i in range(0,4):
            my_recommender2.append(hybrid_recommender(item_clusters,top_results,ratings_weightage=1,content_weightage=0.2, null_rating_replace='mean')) #can be replaced by 'zero', 'one' or 'min'
            my_recommender2[i].fit(ratings[i],item_df)

        print("We computed the recommender for algorithm 2")

        for i in range(0,4):
            my_recommender3.append(hybrid_recommender(item_clusters,top_results,ratings_weightage=0.2,content_weightage=1, null_rating_replace='mean')) #can be replaced by 'zero', 'one' or 'min'
            my_recommender3[i].fit(ratings[i],item_df)

        print("We computed the recommender for algorithm 3")


        print("We are writing the first file")
        pickle_on_1=open("Rec1.pickle","wb")
        pickle.dump(my_recommender1,pickle_on_1)
        pickle_on_1.close()
        print("Done.")

        print("We are writing the second file")
        pickle_on_2=open("Rec2.pickle","wb")
        pickle.dump(my_recommender2,pickle_on_2)
        pickle_on_2.close()
        print("Done.")

        print("We are writing the third file")
        pickle_on_3=open("Rec3.pickle","wb")
        pickle.dump(my_recommender3,pickle_on_3)
        pickle_on_3.close()
        print("Done.")

