import numpy as np
from sklearn.neighbors import NearestNeighbors

dic_genders={0:'M',1:'F',2:'A'}
dic_cities={0:'London',1:'Birmingham',2:'Leeds',3:'Glasgow',4:'Sheffield',5:'Bradford',6:'Manchester',7:'Edinburgh',8:'Liverpool',9:'Bristol',10:'Cardiff',11:'Belfast',12:'Leicester',13:'Wakefield',14:'Coventry',15:'Nottingham',}
dic_ab={0:'yes',1:'no'}

def get_key(d,value):
    for k,v in d.items():
        if v==value:
            return k

def euclidean0_1(vector1, vector2):
    '''calculate the euclidean distance, no numpy
    input: numpy.arrays or lists
    return: euclidean distance
    '''
    dist = [(a - b)**2 for a, b in zip(vector1, vector2)]
    dist = math.sqrt(sum(dist))
    return dist

class user_profile:

    def __init__(self):
        self.age=np.random.randint(1,101)
        self.gender = dic_genders[np.random.randint(0,3)]
        self.city = dic_cities[np.random.randint(0,16)]
        self.budget = np.random.randint(1,15)*52.8
        self.ability = dic_ab[np.random.randint(0,2)]
        self.duration = np.random.randint(1,8)

    def user_attributes(self):
        return (self.age,self.gender,self.city,self.budget,self.ability,self.duration)

    def vect_attributes(self):
        return [self.age*1.0,get_key(dic_genders,self.gender)*0.33,get_key(dic_cities,self.city)/16,self.budget,get_key(dic_ab,self.ability)*1.0,self.duration*1.0]

    def vect_raw_attributes(self):
        return [self.age,get_key(dic_genders,self.gender),get_key(dic_cities,self.city),self.budget,get_key(dic_ab,self.ability),self.duration]

datas=[]
for i in range(1000):
    u = user_profile()
    datas.append(u)
#    print(u.user_attributes())
#    print(u.vect_attributes())

u_vect = [z.vect_raw_attributes() for z in datas]
u_vect2 = [z.vect_raw_attributes() for z in datas]

X = np.array(u_vect)
nbrs = NearestNeighbors(n_neighbors=2, algorithm='ball_tree',metric='chebyshev').fit(X)
distances, indices = nbrs.kneighbors(X)
#print(distances)
#print(indices)

X2 = np.array(u_vect2)
nbrs2 = NearestNeighbors(n_neighbors=2,algorithm='ball_tree',metric='euclidean').fit(X2)
distances2, indices2 = nbrs.kneighbors(X2)
#print(distances)
#print(indices)

for i in range(len(distances)):
    if indices[i].all()!=indices2[i].all():
        print(False)
