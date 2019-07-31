from decimal import *
from hotelrecommendation.models import User
from django.core.management.base import BaseCommand, CommandError
import pickle
from sklearn.neighbors import NearestNeighbors
import math


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

class Command(BaseCommand):

    def handle(self, *args, **options):

        samples=[]
        tmp=()
        for u in User.objects.all():
            tmp=user_to_user_sample(u)
            samples.append(tmp)

        neigh = NearestNeighbors(n_neighbors=2, algorithm='ball_tree',metric=dist)
        neigh.fit(samples)

        print("We are writing the neighbors file")
        neighPick=open("Neigh.pickle","wb")
        pickle.dump(neigh,neighPick)
        neighPick.close()
        print("Done.")


