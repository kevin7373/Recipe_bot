# -*- coding: utf-8 -*-
import re
import urllib.request
import urllib.parse
import requests
import time
import json


from bs4 import BeautifulSoup
from flask import Flask, request
from slack import WebClient
from slack.web.classes import extract_json
from slack.web.classes.blocks import *
from slack.web.classes.elements import *
from slack.web.classes.interactions import MessageInteractiveEvent
from slackeventsapi import SlackEventAdapter
from string import punctuation






SLACK_TOKEN = ""
SLACK_SIGNING_SECRET = ""

text_temp =""
text2_temp =""
app = Flask(__name__)
# /listening 으로 슬랙 이벤트를 받습니다.
slack_events_adaptor = SlackEventAdapter(SLACK_SIGNING_SECRET, "/listening", app)
slack_web_client = WebClient(token=SLACK_TOKEN)


# 크롤링 함수 구현하기
def _crawl(text):
    # 여기에 함수를 구현해봅시다.
    '''
    사용자가 검색을 원하는 레시피를 챗봇에게 요청하면 레시피 사이트에서 검색을 실행
    '''

    url = re.search(r'(https?://\S+)', text.split('|')[0]).group(0)
    req = urllib.request.Request(url)

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")
    
    # '''
    # 사용자가 검색한 레시피 중 가장 상단에 위치한 레시피로 이동
    # '''

    attachments_list = []
    for recipe in soup.find('div', class_='rcp_m_list2').find_all('div', class_='col-xs-4')[:3]:
    	recipe_name = recipe.find('h4', class_='ellipsis_title2').get_text().strip()
    	recipe_img_link = recipe.find('span', class_='thumbnail_over').find_next('img').find_next('img')['src']
    	recipe_href = recipe.find('a', class_='thumbnail')['href']

    	attachments = [{
    					"type": "section", 
    					"text": {
    								"type": "mrkdwn", 
    								"text": recipe_name
    								}, 
    					"accessory": {
    									"type": "image", 
    									"image_url": recipe_img_link, 
    									"alt_text": recipe_name
    									}
    					}]
    	attachments_list.append({
    								"text": recipe_name, 
    								"image_url": recipe_img_link, 
    								"href":'http://www.10000recipe.com' + recipe_href
    								})

    first_ingredient = []
    second_ingredient = []
    third_ingredient = []
    first_recipe = []
    second_recipe = []
    third_recipe = []
    each_text = []
    for i in range(0, 3):
    	each_text.append(attachments_list[i]['href'])
    	url = re.search(r'(https?://\S+)', each_text[i].split('|')[0]).group(0)
    	req = urllib.request.Request(url)
    	
    	sourcecode = urllib.request.urlopen(url).read()
    	soup = BeautifulSoup(sourcecode, "html.parser")

    	for ingredient in soup.find_all('div', class_='ready_ingre3'):
    		for material in ingredient.find_all('li'):
    			if i == 0:
    				first_ingredient.append([material.get_text().replace(' ', '').replace('\n', ' ').strip()])
    			elif i == 1:
    				second_ingredient.append([material.get_text().replace(' ', '').replace('\n', ' ').strip()])
    			elif i == 2:
    				third_ingredient.append([material.get_text().replace(' ', '').replace('\n', ' ').strip()])

    	for j, recipe in enumerate(soup.find_all('div', class_='media-body')):
    		if 'id' in recipe.attrs:
	    		if i == 0:
	    			first_recipe.append((str(j + 1) + '. ' + recipe.get_text().replace('.', '').replace('\n', ' ').replace('니다 ', '니다. ') + '.').replace('!.', '!').replace('~.', '~'))
	    		if i == 1:
	    			second_recipe.append((str(j + 1) + '. ' + recipe.get_text().replace('.', '').replace('\n', ' ').replace('니다 ', '니다. ') + '.').replace('!.', '!').replace('~.', '~'))
	    		if i == 2:
	    			third_recipe.append((str(j + 1) + '. ' + recipe.get_text().replace('.', '').replace('\n', ' ').replace('니다 ', '니다. ') + '.').replace('!.', '!').replace('~.', '~'))
	


    first_item_image = ImageElement(
		image_url=attachments_list[0]['image_url'],
		alt_text=text
		)
    first_head_section = SectionBlock(
		text='*<' + attachments_list[0]['href'] + "|" + attachments_list[0]['text'] + '>*'
				+ '\n\n' + '*[재료]*' + '\n' + str(first_ingredient).replace("'], ['", '\n').replace("['", '').replace("']", '').replace('[', '').replace(']', '')
				+ '\n\n' + '*[조리법]*' + '\n' + str(first_recipe).replace("['", '').replace("', '", '\n').replace("']", ''),
		accessory=first_item_image
		)
    divider = {"type":"divider"}

    second_item_image = ImageElement(
		image_url=attachments_list[1]['image_url'],
		alt_text=text
		)
    second_head_section = SectionBlock(
		text='*<' + attachments_list[1]['href'] + "|" + attachments_list[1]['text'] + '>*'
				+ '\n\n' + '*[재료]*' + '\n' + str(second_ingredient).replace("'], ['", '\n').replace("['", '').replace("']", '').replace('[', '').replace(']', '')
				+ '\n\n' + '*[조리법]*' + '\n' + str(second_recipe).replace("['", '').replace("', '", '\n').replace("']", '') + '\n',
		accessory=second_item_image
		)
    third_item_image = ImageElement(
		image_url=attachments_list[2]['image_url'],
		alt_text=text
		)
    third_head_section = SectionBlock(
		text='*<' + attachments_list[2]['href'] + "|" + attachments_list[2]['text'] + '>*'
				+ '\n\n' + '*[재료]*' + '\n' + str(third_ingredient).replace("'], ['", '\n').replace("['", '').replace("']", '').replace('[', '').replace(']', '')
				+ '\n\n' + '*[조리법]*' + '\n' + str(third_recipe).replace("['", '').replace("', '", '\n').replace("']", ''),
		accessory=third_item_image
		)
    accuracy = text2_temp
    order = text2_temp
    reco = text2_temp

    # button = ActionsBlock(
    #             block_id = '#',
    #             elements= [ButtonElement(
    #                             text="정확순",
    #                             action_id="정확순",
    #                             value=accuracy
    #                             ),
    #                         ButtonElement(
    #                             text="최신순",
    #                             action_id="최신순",
    #                             value=order
    #                             ),
    #                         ButtonElement(
    #                             text="추천순",
    #                             action_id="추천순",
    #                             value=reco
    #                             )]
    #             )
    return [first_head_section, divider, second_head_section, divider, third_head_section]




# 챗봇이 멘션을 받았을 경우
@slack_events_adaptor.on("app_mention")
def app_mentioned(event_data):
    global text_temp
    global text2_temp
    channel = event_data["event"]["channel"]
    text = event_data["event"]["text"]
    text_temp = 'www.10000recipe.com/recipe/list.html?q='
    text1 = 'http://www.10000recipe.com/recipe/list.html?q='
    text2 = urllib.parse.quote_plus(text)
    text2_temp = text_temp + text2.replace(((text2.split('+'))[0] + '+'), '')
    text = text1 + text2.replace(((text2.split('+'))[0] + '+'), '')

    message_block = _crawl(text)

    slack_web_client.chat_postMessage(
    	channel=channel, 
    	blocks = extract_json(message_block)
    	)

# @app.route("/click", methods=["GET", "POST"])
# def on_button_click():
#     # 버튼 클릭은 SlackEventsApi에서 처리해주지 않으므로 직접 처리합니다
#     payload = request.values["payload"]
#     click_event = MessageInteractiveEvent(json.loads(payload))

#     text = click_event.block_id
#     # 다른 가격대로 다시 크롤링합니다.
#     message_blocks = _crawl(text)

#     # 메시지를 채널에 올립니다
#     slack_web_client.chat_postMessage(
#         channel=click_event.channel.id,
#         blocks=extract_json(message_blocks)
#     )

#     # Slack에게 클릭 이벤트를 확인했다고 알려줍니다
#     return "OK", 200


# / 로 접속하면 서버가 준비되었다고 알려줍니다.
@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)
