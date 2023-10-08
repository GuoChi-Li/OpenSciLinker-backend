import requests
from pathlib import Path
import json
from tqdm import tqdm
import time

def register_user(data):
    api_url = "http://localhost:8080/api/register"

    # 设置请求头
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    # 发起POST请求
    response = requests.post(api_url, json=data, headers=headers)

    # 检查响应状态码
    if response.status_code == 200:
        # 解析JSON响应
        result = response.json()
        return result
    else:
        print("Error with status code:", response.status_code)
        return None

def create_post(data):
    api_url = "http://localhost:8080/api/posts"

    # 设置请求头
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    # 发起POST请求
    response = requests.post(api_url, json=data, headers=headers)

    time.sleep(0.3)
    # 检查响应状态码
    if response.status_code == 200:
        # 解析JSON响应
        result = response.json()
        return result
    else:
        print("Error with status code:", response.status_code)
        return None

fail_idx =  [17, 28, 77, 110, 134, 155, 174, 179, 201, 217, 233, 235, 290, 308, 370, 371, 420, 474]



if __name__ == '__main__':
    data = {'username':'', 'email':'', 'password':''}
    register_user(data)

    json_file_path = Path('/Users/berrywei/Downloads/knowledge_graph_full_merged 2.json')
    if json_file_path.exists():
        with json_file_path.open() as json_file:
            data = json.load(json_file)
    else:
        print("File does not exist:", json_file_path)

    data = data['nodes']

    failed_posts = []
    pbar = tqdm(total=len(data), dynamic_ncols=True)

    idx = 0
    for post_data in data:
        if idx in fail_idx:
            tags_split_list = post_data['tag'].split(',')
            merge_data = {
                'title': post_data['title'],
                'content': post_data['abstract'],
                'url':post_data['url'],
                'author_email':'',
                'tags': list(set([item.strip() for item in tags_split_list])),
                'timestamp': '2023-10-08T08:39:16.120Z'
            }
            print(merge_data)
            
            post_result = create_post(merge_data)
            if post_result:
                # Update the progress bar with custom description
                pbar.set_description(f"Processing post id {post_result['post_id']}")
                pbar.update(1)
            else:
                failed_posts.append(idx)

        idx+=1
    pbar.close()

    if failed_posts:
        print("\nFailed to post the following titles:")
        for title in failed_posts:
            print(title)
            
