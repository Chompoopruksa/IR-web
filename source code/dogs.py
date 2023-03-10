from flask import Flask, request
from markupsafe import escape
from flask import render_template
from elasticsearch import Elasticsearch
import math
from dotenv import load_dotenv
load_dotenv()

ELASTIC_PASSWORD = "thepassword1234"

es = Elasticsearch("https://localhost:9200", http_auth=("elastic", ELASTIC_PASSWORD), verify_certs=False)
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    page_size = 10
    keyword = request.args.get('keyword')
    if request.args.get('page'):
        page_no = int(request.args.get('page'))
    else:
        page_no = 1

    body = {
        'size': page_size,
        'from': page_size * (page_no-1),
        'query': {
            'multi_match': {
                'query': keyword,
                'fields': ['breedName', 'description','dogInfo'],
                "fuzziness": "auto",
                "fuzzy_transpositions": True
            }
        }
    }

    res = es.search(index='dogs', body=body)
    hits = [{'breedName': doc['_source']['breedName'], 'image': doc['_source']['image'], 'description': doc['_source']['description'],'breedGroup': doc['_source']["dogInfo"]["breedGroup"], 'height': doc['_source']["dogInfo"]["height"], 'weight': doc['_source']["dogInfo"]["weight"], 'life': doc['_source']["dogInfo"]["life"]} for doc in res['hits']['hits']]
    page_total = math.ceil(res['hits']['total']['value']/page_size) 
    return render_template('search.html',keyword=keyword, hits=hits, page_no=page_no, page_total=page_total)