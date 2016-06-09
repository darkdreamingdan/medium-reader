import json

class MediumArticle:
	def __init__ ( self, strJSON ):
		art = json.loads ( strJSON[16:], strict=False )
		self.success = art['success']
		if not self.success:
			return
			
		self.data = art
		self.title = art['payload']['value']['title']
		self.subtitle = art['payload']['value']['content']['subtitle']
		self.id = art['payload']['value']['id']
		self.url = art['payload']['value']['canonicalUrl']
		
		self.authorId = art['payload']['value']['creatorId'].encode('utf-8')
		self.author = art['payload']['references']['User'][self.authorId]['name']
		self.username = art['payload']['references']['User'][self.authorId]['username']
		self.userUrl = "https://medium.com/u/" + self.authorId

	def isResponse ( self ):
		art = self.data
		if art['success'] != True:
			return 500
		
		if art['payload']['value'].has_key('inResponseToPostId'):
			responseID = art['payload']['value']['inResponseToPostId']
			if responseID:
				return True
					
		return False
		
	isComment = isResponse

	def toHTML ( self ):
		art = self.data
		if art['success'] != True:
			return 500
			
		htmlList = []
			
		paragraphs = art['payload']['value']['content']['bodyModel']['paragraphs']
		link = art['payload']['value']['mediumUrl']
		inBulletList = False
		inNumberedList = False
		for data in paragraphs:
			html = data['text']
			
			wasBulletList = inBulletList
			wasNumberedList = inNumberedList
			
			type = data['type']
			
			if data.has_key('markups'):
				html = self.processMarkups ( html, data['markups'] )
			
			if type == 3: # Heading
				html = self.processH1 ( html )
			elif type == 13: # Secondary Heading
				html = self.processH2 ( html )
			elif type == 9: # Bullet list
				html = self.processList ( html, openBullet=(not inBulletList) )
			elif type == 10: # Number list
				html = self.processList ( html, openNumber=(not inNumberedList) )
			elif type == 6: # Block quote with line on the side
				html = self.processBlockQuote ( html, False )
			elif type == 7: # Block quote with big writing
				html = self.processBlockQuote ( html, True )
			elif type == 8: # Code blockquote
				html = self.processCodeblock ( html )
			elif type == 14:
				html = self.processMediumBlock ( html ) 

			
			if data.has_key('hasDropCap') and data['hasDropCap'] == True:
				html = self.processDropCap ( html )
					
			if data.has_key('metadata'):
				if data['metadata'].has_key ( "originalWidth" ) and data['metadata'].has_key ( "originalHeight" ):
					html = self.processImage ( html, data['metadata']['id'], data['metadata']['originalWidth'], data['metadata']['originalHeight'] )
				
			if data.has_key('iframe'):
				html = self.processEmbed ( html, data['iframe']['mediaResourceId'], data['iframe']['iframeWidth'], data['iframe']['iframeHeight'], link )

			inBulletList = True if (type == 9) else False
			inNumberedList = True if (type == 10) else False
			
			if wasBulletList and not inBulletList:
				html = self.processList ( html, closeBullet=True )
			if wasNumberedList and not inNumberedList:
				html = self.processList ( html, closeNumber=True )
				
			htmlList.append ( html )
		
		# Section breaks are handled in a seperate part of the JSON
		sections = art['payload']['value']['content']['bodyModel']['sections']
		for data in reversed(sections): 
			# Skip the first empty section
			if data['startIndex'] == 0:
				continue
			
			htmlList.insert ( data['startIndex'], self.generateSeperator () )
		
		# TO DO: Handle post responses.
		# Handle responses.  First highlighted responses, which are treated as 'Quotes', then general post responses.
		# if art['payload']['value'].has_key('inResponseToPostId'):
			# responseID = art['payload']['value']['inResponseToPostId'].encode("utf8")
			# if responseID:
				# if art['payload']['references'].has_key('Quote'):
					# quote = art['payload']['references']['Quote'][responseID]
					# text = quote['paragraphs'][1]['text']
					# userid = quote['userId'].encode("utf8")
					# username = art['payload']['references']['User'][userid]['name']
					# postId = quote['postId'].encode("utf8")
					# postName = art['payload']['references']['Post'][postId]['title']
					# htmlList.insert(0, generateResponseBlock ( text, postName, username ) )
		
		return "<p>".join(htmlList)
		
	def processH1 ( self, html ):
		return "<h1>" + html + "</h1>"
		
	def processH2 ( self, html ):
		return "<h2>" + html + "</h2>"
		
	def processMarkups ( self, text, markupsList ):
		# 'insertions' is a list of tuples containing ( insertionIndex, htmlTag ) of markups.
		insertions = []
		html = text
		for info in markupsList:
			otag = ""
			ctag = ""
			startpos = info['start']
			endpos = info['end']
			if info['type'] == 1: # Bold
				otag = "<b>"
				ctag = "</b>"
			elif info['type'] == 2: # Italic
				otag = "<i>"
				ctag = "</i>"
			elif info['type'] == 3: # URL
				url = ""; title = ""; rel = ""
				if info.has_key('href'):
					url = info['href']
					title = info['title']
					rel = info['rel']
				elif info.has_key('userId'):
					url = "https://medium.com/u/" + info['userId']
					title = text[startpos:endpos]
				else:
					continue
				otag = '<a href="%s" title="%s" rel="%s">' % ( url, title, rel )
				ctag = "</a>"
			insertions.append ( (startpos, otag) )
			insertions.append ( (endpos, ctag) )
		
		for v in sorted(insertions, key=lambda x: x[0], reverse=True):
			html = html[:v[0]] + v[1] + html[v[0]:]

		return html
		
	def processList ( self, html, openBullet=False, closeBullet=False, openNumber=False, closeNumber=False ):
		if closeBullet:
			return "</ul>" + html
		if closeNumber:
			return "</ol>" + html
			
		html = "<li>" + html + "</li>"
		
		if openBullet:
			html = "<ul>" + html
		if openNumber:
			html = "<ol>" + html
		
		return html	
		
	def processDropCap ( self, html ):
		return '<span style="float: left; font-size: 400%; line-height: 80%">' + html[:1] + '</span>' + html[1:]
		
	def processBlockQuote ( self, html, bBig ):
		if bBig:
			return '<div style="text-align:center; font-size:x-large"><i><blockquote>' + html + '</div></i></blockquote>'
		else:
			return "<i><blockquote>" + html + "</i></blockquote>"
			
	def processCodeblock ( self, html ):
		return "<code>" + html + "</code>"
		
	def processImage ( self, html, name, width, height ):
		url = "https://cdn-images-1.medium.com/max/1080/" + name
		s =		'<div style="text-align:center; font-size:small">'
		s +=	'	<img src="%s" height="%d" width="%d"><p>' % (url,height,width)
		s +=		html
		s +=	'</div>'
		return s
		
	def processEmbed ( self, html, id, width, height, link ):
		url = "http://placehold.it/%sx%s" % (width,height)
		s =		'<div style="text-align:center; font-size:small">'
		s +=	'	<a href="%s"><img src="%s" height="%d" width="%d"></a><p>' % (link,url,height,width)
		s +=		html
		s +=	'</div>'
		return s
		
	def processMediumBlock ( self, quote ):
		s =		'<div style="border: 1px solid grey; font-size:small; display:inline">'
		s +=		quote
		s +=	'</div>'
		return s


	def generateSeperator ( self ):
		bullet = unichr(8226)
		return u'<div style="text-align:center">%s  %s  %s</div>' % (bullet,bullet,bullet)



