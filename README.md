MediumReader
===================

MediumReader is Python API for reading a Medium article. It piggy backs the JSON article output, and provides some basic functions.  The main functionality is converting this JSON into a basic HTML.

To get the JSON of a Medium article, get your URL and add ?format=json.  For example:
https://danny.fyi/i-love-my-pebble-time-steel-smartwatch-and-not-for-why-youd-think-72eb1d03adfe?format=json

Using the library is pretty straightforward:

    from medium_reader import MediumArticle
    
    # Pass your JSON string to the MediumArticle Class
    article = MediumArticle ( strJSON ) 
    print ( "Title: " + article.title )
    print ( "Author: " + article.author )
    print ( "URL: " + article.url )
	if article.isResponse():
		print ( "This post is a response to another article" )

The main use is to produce some basic HTML that could go into an app, email etc.  This is exposed by the toHTML function:

    html = article.toHTML () 
    
    # Write it to an HTML file...
    text_file = open("output.html", "w")
	text_file.write(html)
	text_file.close()

Using this function, it does some basic markup, and produces a fairly representative output of the article:

![Sample article from MediumReader](http://i.imgur.com/u5ddMnP.png?1)


It's representative, whilst also basic enough for additional CSS to be added for customisation. It supports the majority of formatting within a Medium article, though a few things (e.g. embeds) are currently unsupported.