import random
import re
from requests_html import HTMLSession
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost, EditPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media


XML_RPC_API = 'http://wp.py4you.com/xmlrpc.php'
USER = 'admin'
PASS = 'Admin123456'


wp_client = Client(XML_RPC_API, USER, PASS)

all_posts = wp_client.call(GetPosts())
post = WordPressPost()


def get_text_from_google(keyword):
    session = HTMLSession()
    response = session.get(f'https://www.google.com/search?q={keyword}&num=10&hl=en')
    links = response.html.xpath('//div[@class="yuRUbf"]/a/@href')
    print(links)

    for link in random.sample(links, 3):
        response_link = session.get(link)
        text_list = response_link.html.xpath('//p[1]/text()')
        post.content = ' '.join(text_list)

    post.terms_names = {
        'post_tag': ['test', 'firstpost'],
        'category': ['Introductions', 'Tests']
    }

    post.post_status = 'publish'


def get_images_from_google(keyword):
    url = f'https://www.google.com/search?q={keyword}&tbm=isch'
    with HTMLSession() as session:
        response = session.get(url)
    with open('absd.html', 'w', encoding='utf-8') as f:
        f.write(response.text)

    matches = re.findall(r'\[\"(.*?)\",', response.text)
    img_types = {'.jpg', }
    images = []
    for match in matches:
        if not any(tp in match for tp in img_types):
            continue
        img = match.split('?')[0]
        images.append(img)

    img_url = session.get(images[2])
    image_name = images[0].split('/')[-1]
    img_path = f'images/{image_name}'
    print(img_path)
    with open(img_path, 'wb') as f:
        f.write(img_url.content)

    data = {
        'name': img_path,
       'type': 'image/jpeg',
    }

    with open(img_path, 'rb') as img:
        data['bits'] = xmlrpc_client.Binary(img.read())

    response = wp_client.call(media.UploadFile(data))
    print(response)

    attachment_id = response['id']
    post.thumbnail = attachment_id


def main():
    keyword = input(' Send Keyword:  ')
    post.title = f'Romanchenko Olga Post :Keywors - {keyword}'
    get_text_from_google(keyword)
    get_images_from_google(keyword)
    post.id = wp_client.call(NewPost(post))


if __name__ == '__main__':
    main()






