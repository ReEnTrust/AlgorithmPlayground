from django.shortcuts import render
from hybrid_recommender import hybrid_recommender
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse.linalg import svds
import pandas as pd
import numpy as np

from .models import Feature
from .models import Item
from .models import Review
from .models import Customer


# Create your views here.


from django.http import HttpResponse


def index(request):

    #Initialising the tabular for the computation
    user_id = []
    rating = []
    item_id = []
    items = []
    cols = []
    feats = []

    #Other parameters
    item_clusters=4
    top_results=5

    #We fill the tabular for the reviews and build the dataframe
    for r in Review.objects.all():
        item_id.append(r.item.id)
        user_id.append(r.customer.id)
        rating.append(r.note)
    ratings = pd.DataFrame({'user_id':user_id,'item_id':item_id,'rating':rating})

    #We take the list of items ID
    for i in Item.objects.all():
        items.append(i.id)

    #We take the name of the features
    for f in Feature.objects.all():
        cols.append(f.feature_text)

    #We have to create a set of sets of features
    for i in items:
        featI = []
        completeFeatI = []
        for f in Item.objects.filter(id=i)[0].item_features.all():
            featI.append(f.feature_text)
        for c in cols:
            if c in featI:
                completeFeatI.append(1)
            else:
                completeFeatI.append(0)
        feats.append(completeFeatI)


    #We create the dataframe for the features
    item_df = pd.DataFrame(feats,index=items,columns=cols)

    my_recommender = hybrid_recommender(item_clusters,top_results)
    my_recommender.fit(ratings,item_df)

    print(my_recommender.predict([1,2]))
    return HttpResponse()