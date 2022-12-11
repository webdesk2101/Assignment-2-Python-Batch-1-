import os
import openai
import base64
from requests import post
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv('OPENAI.API')

wp_user = os.getenv('USER')
wp_password = os.getenv('PASSWORD')
wp_credential = f'{wp_user}:{wp_password}'
wp_token = base64.b64encode(wp_credential.encode())
wp_headers = {'Authorization':f'Basic {wp_token.decode("utf-8")}'}

def openai_content(myprompt):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=myprompt,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    data = response.get("choices")[0].get("text").strip('\n')
    return data

def wp_heading_h2(text):
    return f'<!-- wp:heading --><h2>{text}</h2><!-- /wp:heading -->'

def wp_heading_h4(text):
    return f'<!-- wp:heading --><h4>{text}</h4><!-- /wp:heading -->'

def wp_para(text):
    return f'<!-- wp:paragraph --><p>{text}</p><!-- /wp:paragraph -->'

def slugify(name):
    code = name.strip().replace(' ', '-')
    return code

def create_wp_post(title, content, categories, slug, status = 'publish'):
    api_url = 'https://localhost/gsumo/wp-json/wp/v2/posts'
    data = {
        'title': title,
        'content': content,
        'categories': categories,
        'slug': slug,
        'status': status
    }
    response = post(api_url, headers=wp_headers, data=data, verify=False)
    print(f'{title} is posted')

file = open('keyword.txt')
keywords = file.readlines()
for keyword in keywords:
    keyword = keyword.strip('\n').strip('best').strip(' ')
    title = f"{keyword} buying guide".title()


    ques_bank = []
    intro_prompt = f'Write 150 words about {keyword}'
    first_ques = f'Why {keyword} is Important?'
    second_ques = f'Disadvantages of not having {keyword}'
    third_ques = f'Top 7 features to consider while buying {keyword}'
    ques_bank += first_ques, second_ques, third_ques
    conclusion = f'Write concluding words about {keyword}'
    conclusion_final = f'<!-- wp:heading --><h4>Conclusion</h4><!-- /wp:heading -->' \
                 f'<!-- wp:paragraph --><p>{openai_content(conclusion)}</p><!-- /wp:paragraph -->'

    qa_dict = {}
    for ques in ques_bank:
        answer = openai_content(ques)
        qa_dict[ques] = answer

        content = wp_para(openai_content(intro_prompt))
        for key, value in qa_dict.items():
            h2 = wp_heading_h2(key)
            p = wp_para(value)
            content = content + h2 + p
        content = content + conclusion_final
        categories = '655'
        slug = slugify(title)

    create_wp_post(title, content, categories, slug, status = 'publish')


