from collections import Counter
import re
import json
import nltk
from nltk.stem import PorterStemmer
# from nltk.stem import WordNetLemmatizer
nltk.download('punkt')
nltk.download('wordnet')


class JsonSearchEngine:
    def __init__(self, tag_json="knowledge_graph/tag_standard/tags.json", threshold=0.0):
        self.threshold = threshold
        self.stemmer = PorterStemmer()
        self.tags, self.subtags = self.load_tag_documents(tag_json)
        self.subtag_frequencies_list = [self.calculate_subword_frequencies(subtag) for subtag in self.subtags]

    def load_tag_documents(self, tag_json_path):
        print("***** Loading tag data to the search engine!")
        with open(tag_json_path, 'r') as json_file:
            tag_data = json.load(json_file)
        
        tags = []
        subtags = []
        for data in tag_data:
            tag = data['tag']
            data['subtag'].insert(0, tag)
            subtag = " ".join(data['subtag']).strip().lower()
            stemmed_words = [self.stemmer.stem(word) for word in nltk.word_tokenize(subtag)]
            subtag = " ".join(stemmed_words)
            tags.append(tag)
            subtags.append(subtag)
        
        print("***** Tag data successfully loaded into the search engine!")
        return tags, subtags
    

    # 定义一个函数来计算子词频率
    def calculate_subword_frequencies(self, text):
        # 使用正则表达式将文本拆分为子词
        subwords = re.findall(r'\w+', text.lower())
        # 使用Counter来计算子词频率
        subword_counts = Counter(subwords)
        return subword_counts
    

    # 定义一个函数来计算查询和上下文之间的相似性分数
    def calculate_similarity(self, query, subtag_frequencies):
        # 计算查询和上下文的子词频率
        query_frequencies = self.calculate_subword_frequencies(query)
        
        # 计算相似性分数
        similarity_score = sum((query_frequencies & subtag_frequencies).values()) / len(query_frequencies)
        
        return similarity_score
    

    def get_tags(self, input_query):
        input_query = input_query.lower()
        # print("original query:", input_query)
        stemmed_words = [self.stemmer.stem(word) for word in nltk.word_tokenize(input_query)]
        input_query = " ".join(stemmed_words)
        # print("after query:", input_query)

        scores = []
        for subtag_frequencies in self.subtag_frequencies_list:
            score = self.calculate_similarity(input_query, subtag_frequencies)
            scores.append(score)

        combined_list = list(zip(self.tags, scores))
        ranked_pairs = sorted(combined_list, key=lambda x: x[1], reverse=True)
        ranked_tags = [item[0] for item in ranked_pairs]
        ranked_scores = [item[1] for item in ranked_pairs]
        max_score = max(ranked_scores)
        if max_score == 0:
            return ["Computer Science"], [0.2]
        ranked_scores = [score / max_score for score in ranked_scores]
        
        for i in range(5):
            print(f"Tag: {ranked_tags[i]}, score: {ranked_scores[i]}")
        
        return_tags = []
        return_scores = []
        for tag, score in zip(ranked_tags, ranked_scores):
            if score > self.threshold:
                return_tags.append(tag)
                return_scores.append(score)

        return return_tags, return_scores
    
class NodeSearchEngine:
    def __init__(self, nodes, threshold=0):
        self.nodes = nodes
        self.threshold = threshold
        self.stemmer = PorterStemmer()
        self.subtag_frequencies_list = [self.calculate_subword_frequencies(node.subtag) for node in nodes]

    def calculate_subword_frequencies(self, text):
        subwords = re.findall(r'\w+', text.lower())
        subword_counts = Counter(subwords)
        return subword_counts
    
    def calculate_similarity(self, query, subtag_frequencies):
        query_frequencies = self.calculate_subword_frequencies(query)
        similarity_score = sum((query_frequencies & subtag_frequencies).values()) / len(query_frequencies)
        return similarity_score
    
    def get_link(self, input_query):
        input_query = input_query.lower()
        stemmed_words = [self.stemmer.stem(word) for word in nltk.word_tokenize(input_query)]
        input_query = " ".join(stemmed_words)

        scores = []
        for subtag_frequencies in self.subtag_frequencies_list:
            score = self.calculate_similarity(input_query, subtag_frequencies)
            scores.append(score)

        link_idx = [self.nodes[i].idx for i, score in enumerate(scores) if score>=self.threshold]
        return link_idx

    def get_links_map(self):
        return {node.idx: self.get_link(node.tag) for node in self.nodes}

if __name__ == "__main__":
    search_engine = JsonSearchEngine(threshold=0)

    input_query = input("Type something to search: ")
    while len(input_query) >= 1:
        tag_score_pairs = search_engine.get_tags(input_query, return_full=True)
        print("***** Received pairs:", tag_score_pairs)
        print("-"*50)
        input_query = input("Type something to search: ")