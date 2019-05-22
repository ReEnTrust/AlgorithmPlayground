from hybrid_recommender import hybrid_recommender
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse.linalg import svds
import pandas as pd
import numpy as np

item_id = [1,7,9,10,12,2,4,6,8,10,12,3,6,9,12,14,10,13,12,14,11,2,5,7,8,9,10,12]
user_id = [1,1,1,1,1,2,2,2,2,2,2,3,3,3,3,3,4,4,4,4,4,5,5,5,5,5,5,5]
rating = [4,5,2,3,5,2,3,2,3,4,4,5,1,2,3,1,2,4,5,3,5,3,1,3,5,3,5,3]
ratings = pd.DataFrame({'user_id':user_id,'item_id':item_id,'rating':rating})

items = [1,2,3,4,5,6,7,8,9,10,11,12,13,14]
cols = ['col1','col2','col3','col4','col5','col6']
feats =[[1,0,0,1,1,0],
       [1,1,0,0,1,1],
       [0,1,1,0,0,0],
       [0,1,1,1,0,0],
       [1,0,1,1,1,1],
       [1,1,1,0,0,1],
       [0,1,0,1,0,1],
       [0,0,0,1,0,0],
       [0,1,1,0,0,0],
       [1,1,1,0,1,0],
       [0,0,0,1,1,1],
       [0,1,0,1,0,0],
       [0,1,1,0,1,0],
       [0,0,1,1,1,1],]
item_df = pd.DataFrame(feats,index=items,columns=cols)

ratings.head()

item_df.head()

my_recommender = hybrid_recommender(item_clusters=4,top_results=5)

my_recommender.fit(ratings,item_df)

print(item_df)
print(ratings)
print(my_recommender.predict([1,2]))

