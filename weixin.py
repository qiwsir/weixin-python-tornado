#!/usr/bin/env python3

import logging
import tornado.ioloop
import tornado.web
import hashlib
import xml.etree.ElementTree
import time
import argparse

token = 'python_tornado_token'
logging.basicConfig(level=logging.DEBUG)
reply_text = '''<xml>
	<ToUserName><![CDATA[{toUserName}]]></ToUserName>
	<FromUserName><![CDATA[{fromUserName}]]></FromUserName>
	<CreateTime><![CDATA[{createTime}]]></CreateTime>
	<MsgType><![CDATA[{msgType}]]></MsgType>
	<Content><![CDATA[{content}]]></Content>
	<FuncFlag><![CDATA[{funcFlag}]]></FuncFlag>
</xml>'''

class WeixinMessage:
	def __init__(self, xmlString):
		root = xml.etree.ElementTree.fromstring(text=xmlString)
		self.ToUserName = root.find('ToUserName').text
		self.FromUserName = root.find('FromUserName').text
		self.CreateTime = root.find('CreateTime').text
		self.MsgType = root.find('MsgType').text
		MsgId = root.find('MsgId').text
		if self.MsgType == 'text':
			self.Content = root.find('Content').text
		elif self.MsgType == "image":
			self.PicUrl = root.find('PicUrl').text
		elif self.MsgType == 'location':
			self.Location_X = root.find('Location_X').text
			self.Location_Y = root.find('Location_Y').text
			self.Scale = root.find('Scale').text
			self.Label = root.find('Label').text
		elif self.MsgType == 'link':
			self.Title = root.find('Title').text
			self.Description = root.find('Description').text
			self.Url = root.find('Url').text
		
class IndexHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		checkSignatureResult = self.check_signature()
		if isinstance(checkSignature, str):
			self.write(echostr)
			logging.info("成功接入微信开发平台")			
		else:
			logging.info("接入微信平台失败")
			raise tornado.web.HTTPError(status_code=500,log_message="接入微信平台失败" )
		self.finish()
	
	def post(self):
		checkSignatureResult = self.check_signature()
		if checkSignatureResult == True:
			pass
		else:
			raise tornado.web.HTTPError(status_code=500,log_message='微信校验码失败，该消息可能不是来自微信服务器')
		body = self.request.body
		bodyString = body.decode()
		weixinMessage = WeixinMessage(bodyString)
		reply = '啦啦啦德玛西亚'
		if weixinMessage.MsgType == 'text':
			reply = reply_text.format(
														toUserName = weixinMessage.FromUserName,
														fromUserName = weixinMessage.ToUserName,
														createTime = str(int(time.time())),
														msgType = 'text',
														content = weixinMessage.Content,
														funcFlag = 1
														)
		else:
			reply = reply_text.format(
														toUserName = weixinMessage.FromUserName,
														fromUserName = weixinMessage.ToUserName,
														createTime = str(int(time.time())),
														msgType = 'text',
														content = '你输入的不是文字， 老子现在处理不了',
														funcFlag = 1
														)
		self.set_status(200)
		self.write(reply)
		self.finish()
		
	def check_signature(self):
		signature = self.get_query_argument(name="signature")
		timestamp = self.get_query_argument(name="timestamp")
		nonce = self.get_query_argument(name="nonce")
		echostr = self.get_query_argument(name="echostr",default=False)
		stringList = [ timestamp, nonce, token ]
		stringList.sort(key=None, reverse=False)
		concatenatedString = ''
		for str in stringList:
			concatenatedString += str
		sha1Object = hashlib.sha1()
		encodedConcatenatedString = concatenatedString.encode()
		sha1Object.update(encodedConcatenatedString)
		generated_signature = sha1Object.hexdigest()
		if generated_signature == signature:
			if echostr :
				return echostr
			else:
				return True
		else:
			return False
						
if __name__ == "__main__":
	application = tornado.web.Application([
																				(r"/index.py", IndexHandler)
																				], 
																			debug=True)
	application.listen(80)
	tornado.ioloop.IOLoop.instance().start()
