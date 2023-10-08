from rank_bm25 import BM25Plus
import os
import json


class SearchEngine:
    def __init__(self, tag_json_path="knowledge_graph/tags.json"):

        self.tags, self.tokenized_contents = self.load_tag_documents(tag_json_path)
        self.k = 5
        self.bm25 = BM25Plus(self.tokenized_contents)


    def load_tag_documents(self, tag_json_path):
        print("***** Loading tag data to the search engine!")
        with open(tag_json_path, 'r') as json_file:
            tag_data = json.load(json_file)
        
        tags = []
        tokenized_contents = []
        for data in tag_data:
            tag = data['tag']
            data['content'].insert(0, tag)
            content = " ".join(data['content']).strip().lower()
            tokenized_content = list(content)
            tags.append(tag)
            tokenized_contents.append(tokenized_content)
        
        print("***** Tag data successfully loaded into the search engine!")
        return tags, tokenized_contents
    

    def get_tag(self, input_query):
        tokenized_query = list(input_query.lower())
        context_scores = self.bm25.get_scores(tokenized_query)
        top_tags = self.bm25.get_top_n(tokenized_query, self.tags, n=self.k)
        print("top tags:", top_tags)
        # for i in range(self.k):
        #     print(f"Tag: {top_tags[i]}, score: {context_scores[i]}")
        
    


if __name__ == "__main__":
    search_engine = SearchEngine()

    input_query = input("Type something to search: ")
    while len(input_query) >= 1:
        search_engine.get_tag(input_query)
        print("-"*50)
        input_query = input("Type something to search: ")