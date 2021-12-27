import pandas as pd
import json
import sys

sys.path.append("lib")
import databaseinsert

df = pd.read_json("./datas/tweet.json", lines=True)

import nltk

# nltk.download()

import re
from bs4 import BeautifulSoup
from nltk.tokenize import TweetTokenizer


def DataCleansing(instance):
    # Remove caracteres, artificios indesejados (links, virgula, pontuação, etc...)
    instance = (
        re.sub(r"http\S+", "", instance)
        .lower()
        .replace(".", "")
        .replace(";", "")
        .replace("-", "")
        .replace(":", "")
        .replace(")", "")
    )
    stopwords = set(nltk.corpus.stopwords.words("portuguese"))
    words = [i for i in instance.split() if not i in stopwords]
    return " ".join(words)


def PreprocessTweet(tweet):
    tweet = BeautifulSoup(tweet, "html.parser").get_text()
    tweet = re.sub(r"[^a-zA-Zà-úÀ-Ú0-9]+", " ", tweet.lower())
    return tweet


tweets = [DataCleansing(i) for i in df.tweet]
df["clean_data"] = tweets

df["preprocessed_data"] = [PreprocessTweet(tweet) for tweet in df.clean_data]
df_clean = df.drop(["clean_data"], axis=1)

print("Pre-process sucess!")
print(df_clean)
print("--------------------------------")

# Importação de biblioteca para contar o número de vezes que uma palavra ocorre
from sklearn.feature_extraction.text import CountVectorizer

cv = CountVectorizer()
counts = cv.fit_transform(df.preprocessed_data)

# Captura as palavras de todos os tweets
cv.get_feature_names()

counts.toarray()

word_count = pd.DataFrame(cv.get_feature_names(), columns=["word"])
word_count["count"] = counts.sum(axis=0).tolist()[0]
word_count = word_count.sort_values("count", ascending=False).reset_index(drop=True)

# Criando dataframe de ranking de palavras associadas
words = [
    index
    for index, row in word_count.iterrows()
    if row["word"] == "violência"
    or row["word"] == "doméstica"
    or row["word"] == "pra"
    or row["word"] == "day"
    or row["word"] == "quase"
    or row["word"] == "pq"
    or row["word"] == "sobre"
    or row["word"] == "francisco"
    or row["word"] == "papa"
    or row["word"] == "mulher"
]
df_wordcount = word_count.drop(words)
df_wordcount.reset_index(inplace=True, drop=True)

# Configurando para dicionário para inserção no banco de dados
word_ranking = df_wordcount.set_index("word").T.to_dict("list")
print(word_ranking)
print("Running...")

# Conectando e inserindo no banco
databaseinsert.connect_firebase()

for index, row in df_wordcount.iterrows():
    if index + 1 > 50:
        break
    elif index + 1 <= 50:

        data = {"word": row["word"], "count": row["count"], "position": index + 1}
        position = data["position"] - 1
        databaseinsert.insert_data(data, "word_ranking", position)

print("Process sucess!")
