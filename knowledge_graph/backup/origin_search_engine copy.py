from whoosh.index import create_in
from whoosh.fields import Schema, TEXT
from whoosh.qparser import QueryParser
import os
import json


class SearchEngine:
    def __init__(self, tag_json_path="knowledge_graph/tags.json"):
        schema = Schema(tag=TEXT(stored=True), content=TEXT)

        index_path = "knowledge_graph/indexdir"
        if not os.path.exists(index_path):
            os.mkdir(index_path)
        self.ix = create_in(index_path, schema)

        self.writer = self.ix.writer()
        self.load_tag_documents(tag_json_path)

    def load_tag_documents(self, tag_json_path):
        print("***** Loading tag data to the search engine!")
        with open(tag_json_path, 'r') as json_file:
            tag_data = json.load(json_file)
        
        for data in tag_data:
            tag = data['tag']
            data['content'].insert(0, tag)
            content = ", ".join(data['content']).strip().lower()
            # print(f"title: {title}, content: {content}")
            self.writer.add_document(tag=tag, content=content)
        
        self.writer.commit()
        print("***** Tag data successfully loaded into the search engine!")
    
    def get_tag(self, input_query):
        with self.ix.searcher() as searcher:
            parser = QueryParser("content", self.ix.schema)
            query = parser.parse(input_query.lower())
            results = searcher.search(query, limit=100)
            selected_tags = []
            for hit in results:
                print(f"Tag: {hit['tag']}, score: {hit.score}")
    


if __name__ == "__main__":
    search_engine = SearchEngine()

    input_query = input("Type something to search: ")
    while len(input_query) >= 1:
        search_engine.get_tag(input_query)
        print("-"*50)
        input_query = input("Type something to search: ")