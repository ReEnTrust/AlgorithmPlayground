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
from django.http import HttpResponse





#Initialising the tabular for the computation
user_id = []
rating = []
item_id = []
items = []
items_picture = []
cols = []
feats = []

#Other parameters
item_clusters=4
top_results=5
ratings_weightage=1
content_weightage=1
null_rating_replace='mean' #can be replaced by 'zero', 'one' or 'min'

#We fill the tabular for the reviews and build the dataframe
for r in Review.objects.all():
    item_id.append(r.item.id)
    user_id.append(r.customer.id)
    rating.append(r.note)
ratings = pd.DataFrame({'user_id':user_id,'item_id':item_id,'rating':rating})

#We take the list of items ID
for i in Item.objects.all():
    items.append(i.id)
    items_picture.append(i.item_picture)

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

def index(request):
    #We create the recommender
    my_recommender = set_recommender()

    #We make the prediction
    df_all_recommendation = my_recommender.predict()

    #We export it to html
    result = []
    user_id_unique = list(dict.fromkeys(user_id))
    for i in user_id_unique:
        result.append(df_all_recommendation[df_all_recommendation['User_id'] == str(i)].filter(items=["item_id","mean"]).to_html())

    context = {'ratings': ratings.to_html(),
               'item_df' : item_df.to_html(),
               'result': zip(result, user_id_unique),
               'item_clusters': item_clusters,
               'top_results': top_results,
               'ratings_weightage': ratings_weightage*100,
               'content_weightage':content_weightage*100,
               'null_rating_replace': null_rating_replace,
               'items_picture': zip(items,items_picture)}

    return render(request, 'recommender/index.html', context)




def set_recommender():
    #We fit the recommender system
    my_recommender = hybrid_recommender(item_clusters,top_results,ratings_weightage,content_weightage, null_rating_replace)
    my_recommender.fit(ratings,item_df)
    return my_recommender