from django.shortcuts import render
from hybrid_recommender import hybrid_recommender
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse.linalg import svds
import pandas as pd
import numpy as np

# Create your views here.


from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")