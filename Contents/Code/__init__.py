# Debug
DEBUG           = True
DEBUG_STRUCTURE = False

# General
TITLE      = 'The Filipino Channel'
PREFIX     = '/video/tfctv'
USER_AGENT = 'Mozilla/4,0'


# Resources
ART      = 'art-default.jpg'
ICON     = 'icon-default.png'
LOGO     = 'TFC-logo.jpg'
MORE     = 'more.png'


# GitHub latest version
CHECK_VERSION = False
VERSION_URL = 'https://raw.githubusercontent.com/magnuslsjoberg/The-Filipino-Channel.bundle/master/Contents/Version.txt'

# TFC main website URLs
BASE_URL             = 'http://tfc.tv'
URL_LOGIN            = 'https://tfc.tv/user/login'

RE_SUB_CAT_ID = Regex(r"/category/list/(?P<sub_cat_id>\d+)/")
RE_SHOW_ID    = Regex(r"/show/details/(?P<show_id>\d+)/")
RE_EPISODE_ID = Regex(r"/episode/details/(?P<episode_id>\d+)/")
RE_MOVIE_ID   = Regex(r"/episode/details/(?P<movie_id>\d+)/")
RE_LIVE_ID    = Regex(r"/live/details/(?P<live_id>\d+)/")

# For some extremely strange and annoying reason data-src can't be extracted with XPath!!!
# <div class="show-cover" data-src="https://timg.tfc.tv/xcms/episodeimages/129284/20170614-ikaw-487-1.jpg">
RE_EPISODE_IMAGE_PATH = Regex(r'^<div class="show-cover" data-src="(?P<image_path>[^"]+)">')

# style="background-image:url(https://timg.tfc.tv/xcms/categoryimages/4046/I-AMERICA-HERO-WEB.jpg);">
RE_MOVIE_BANNER_PATH = Regex(r'background-image:url\((?P<banner_path>[^"]+)\);')

# Constructed URLs for URL service
URL_PLEX_MOVIE   = 'tfctv://{MOVIE_ID}'
URL_PLEX_EPISODE = 'tfctv://{SHOW_ID}/{EPISODE_ID}'

# Max umber of items to show in one listing
NUM_SHOWS_ON_PAGE = 12
MAX_NUM_EPISODES  = 50

# Set default cache to 3 hours
CACHE_TIME = 3 * CACHE_1HOUR



####################################################################################################
def Start( **kwargs ):

    InputDirectoryObject.thumb = R('Search.png')
    DirectoryObject.art  = R(ART)

    ObjectContainer.title1 = TITLE

    HTTP.CacheTime = CACHE_TIME

    HTTP.Headers['User-Agent']      = USER_AGENT
    HTTP.Headers['Accept']          = '*/*'
    HTTP.Headers['Accept-Encoding'] = 'deflate, gzip'
    

####################################################################################################
@handler(PREFIX, TITLE, art=ART, thumb=LOGO)
def MainMenu( **kwargs ):

    try:
    
        oc = ObjectContainer()

        if CHECK_VERSION:
        
            # Check latest version in GitHub
            try:
                html = HTML.ElementFromURL( VERSION_URL, cacheTime = 0 ) #### 24*CACHE_1HOUR )
                Log.Debug(str(html))
                
                version = html.content
                Log.Debug(version)
                
                oc.header  = "UPGRADE AVAILABLE!"
                oc.message = "Latest version %s found." % str(version)
        
                return oc

            except:
                oc.header  = "ALL OK"
                oc.message = "NO version found."

                return oc

                pass
            
        html = HTML.ElementFromURL( BASE_URL )

        categories = html.xpath('//div[@id="main_nav_desk"]/ul/li/a')

        for category in categories:
            category_name = category.xpath('./text()')[0]
            category_name = String.DecodeHTMLEntities( category_name ).strip()

            category_id = int(category.xpath('./@data-id')[0])

            #Log.Debug("%s:%d" % (category_name,category_id) )

            oc.add( DirectoryObject( key = Callback( Category, title = TITLE, name = category_name, cat_id = category_id ), title = category_name ) )

        #oc.add( DirectoryObject( key = Callback( MostLovedShows, title = TITLE, name = 'Most Loved Shows' ), title = 'Most Loved Shows' ) )
        #oc.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search The Filipino Channel', prompt='Search for...'))
        #oc.add(SearchDirectoryObject(identifier='com.plexapp.plugins.tfctv', title='Search', summary='Search The Filipno Channel', prompt='Search:', thumb=R('search.png')))

        return oc
        
    except:

        return NothingFound(TITLE, name, 'content')


####################################################################################################
@route(PREFIX + '/category', cat_id=int )
def Category( title, name, cat_id, **kwargs ):

    try:
    
        oc = ObjectContainer( title1 = title, title2 = name )


        html = HTML.ElementFromURL( BASE_URL )

        sub_categories = html.xpath( '//div[@id="main_nav_desk"]/ul/li/a[@data-id="%d"]/following::ul[1]//a' % int(cat_id) )


        #Log.Debug("sub_categories: '%s'" % (HTML.StringFromElement(sub_categories)) )

        for sub_category in sub_categories:
            sub_category_name = sub_category.xpath('./text()')[0]
            sub_category_name = String.DecodeHTMLEntities( sub_category_name ).strip()

            sub_category_url = sub_category.xpath('./@href')[0]
            if sub_category_url.startswith('/'):
                sub_category_url = BASE_URL + sub_category_url

            #Log.Debug("    %s:%s" % (sub_category_name,sub_category_url) )

            oc.add( DirectoryObject( key = Callback( SubCategory, title = name, name = sub_category_name, url = sub_category_url ), title = sub_category_name ) )


        if len(oc) < 1:
            return NothingFound(title, name, 'items')

        return oc    
        
    except:
    
        return NothingFound(title, name, 'content')



####################################################################################################
'''
@route(PREFIX + '/search', first=int )
def Search( query, first=0, **kwargs ):

    Log.Debug('#### IN SEARCH ####')
    oc = ObjectContainer( title2 = 'Search Results' )
   
    try:
        result = JSON.ObjectFromURL( URL_SEARCH.replace('{QUERY}',String.Quote(query)) )

        Log.Debug("RESULT: %s", result )

        shows = result[first:first+MAX_NUM_SHOWS]  
        
        for show in shows:
        
            Log.Debug(" show: %s", show )
            
            show_id     = show['id']
            show_name   = ExtractHtmlText( show, 'title' )
            show_blurb  = ExtractHtmlText( show, 'blurb' )
            show_image  = ExtractImageUrl( show, 'image' , fallback=R(ICON) )
            show_banner = ExtractImageUrl( show, 'banner', fallback=R(ART)  )
            
            #Log.Debug( "#### show_name  : %s ####" % (show_name)   )
            #Log.Debug( "#### show_blurb : %s ####" % (show_blurb)  )
            #Log.Debug( "#### show_image : %s ####" % (show_image)  )
            #Log.Debug( "#### show_banner: %s ####" % (show_banner) )

            #oc.add( DirectoryObject( key = Callback( Show, title = 'Search Results', name = show_name, show_id = show_id ), title = show_name, thumb = show_image, art = show_banner, summary = show_blurb ) )

        if len(shows) == MAX_NUM_SHOWS:
            oc.add( NextPageObject(key = Callback( Search, query, first = first + MAX_NUM_SHOWS ) ) )

        if len(oc) < 1:
            return NothingFound('Search Results', query, 'items')
                
        return oc 
    
    except:
    
        return NothingFound('Search Results', query, 'content') 


####################################################################################################
@route(PREFIX + '/mostlovedshows', first=int )
def MostLovedShows( title, name, first=0, **kwargs ):

    try:

        oc = ObjectContainer( title1 = title, title2 = name )

        lovedShows = JSON.ObjectFromURL( URL_GET_MOST_LOVED_SHOWS )

        shows = lovedShows[first:first+MAX_NUM_SHOWS]

        #Log.Debug(" * loved shows: %s" % (lovedShows) )

        for show in shows:

            show_id    = show['categoryId']
            show_name  = ExtractHtmlText( show, 'categoryName' )
            show_blurb = ExtractHtmlText( show, 'blurb' )
            show_image = ExtractImageUrl( show, 'image', fallback=R(ICON) )

            #Log.Debug("Add loved show: %s" % (show_name) )

            #oc.add( DirectoryObject( key = Callback( Show, title = name, name = show_name, show_id = show_id ), title = show_name, thumb = show_image, summary = show_blurb ) )

        if len(shows) == MAX_NUM_SHOWS:
            oc.add( NextPageObject(key = Callback( MostLovedShows, title = title, name = name, first = first + MAX_NUM_SHOWS ) ) )

        if len(oc) < 1:
            return NothingFound(title, name, 'shows')
                
        return oc

    except:

        return NothingFound(title, name, 'content')

'''

####################################################################################################
@route(PREFIX + '/subcategory', page=int )
def SubCategory( title, name, url, page=1, **kwargs ):
 
    try:
    
        oc = ObjectContainer( title1 = title, title2 = name )

        page_url = "%s/%d" % (url,page)
        html = HTML.ElementFromURL( page_url )

        shows = html.xpath('//section[contains(@class,"category-list")]//li[contains(@class,"og-grid-item-o")]')

        for show in shows:

            show_name = show.xpath('./@data-title')[0]
            show_name = String.DecodeHTMLEntities( show_name ).strip()
            #Log.Debug( "#### show_name  : %s" % (show_name) )

            show_url = show.xpath('./a/@href')[0]
            if show_url.startswith('/'):
                show_url = BASE_URL + show_url
            #Log.Debug( "#### show_url   : %s" % (show_url) )

            show_image = show.xpath('./a/img/@src')[0]
            #Log.Debug( "#### show_image : %s ####" % (show_image)  )

            show_banner = show_image
            #Log.Debug( "#### show_banner: %s ####" % (show_banner) )

            show_blurb = show.xpath('./a/h3[@class="show-cover-thumb-aired-mobile"]/text()')[0]
            show_blurb = String.DecodeHTMLEntities( show_blurb ).strip()
            #Log.Debug( "#### show_blurb : %s ####" % (show_blurb)  )

            oc.add( DirectoryObject( key = Callback( Show, title = name, name = show_name, url = show_url ), title = show_name, thumb = show_image, art = show_banner, summary = show_blurb ) )

        # Add more button if more pages
        last_page = int(html.xpath('//ul[@id="pagination"]/li/a/text()')[-1])
        #Log.Debug("#### Page %d (%d) ####", page, last_page)
        if page < last_page:
            oc.add( NextPageObject(key = Callback( SubCategory, title = title, name = name, url = url, page = page + 1 ) ) )

        if len(oc) < 1:
            return NothingFound(title, name, 'shows')

        #Log.Debug( "#### Added %d DirectoryObject! ####" % int(len(oc))  )

        return oc 
    
    except:
        pass
    
    return NothingFound(title, name, 'content')


####################################################################################################
@route(PREFIX + '/show', page=int )
def Show( title, name, url, page=1, **kwargs ):
 
    try:

        page_url = "%s/%d" % (url,page)

        Log.Debug( "#### Show: %s : %s ####" % (name,page_url)  )


        cookies = Login()

        Log.Debug( '##### Show::cookies: "%s" #####' % (cookies) )

        HTTP.Headers['Cookie'] = cookies
        
        
        html = HTML.ElementFromURL( page_url )

        oc = ObjectContainer( title1 = title, title2 = name )

        canonical_url = html.xpath('//link[@rel="canonical"]/@href')[0]
        #Log.Debug( "#### canonical_url : %s ####" % (canonical_url)  )

        try:
            live_id = RE_LIVE_ID.search(canonical_url).group('live_id')
        except:
            live_id = None
        #Log.Debug( "#### live_id : %s ####" % (live_id) )

        if live_id:

            # Live stream
            live_name  = html.xpath('//meta[@property="og:title"]/@content')[0]
            live_name = String.DecodeHTMLEntities( live_name ).strip()
            #Log.Debug( "#### live_name : %s ####" % (live_name)  )

            live_blurb = html.xpath('//meta[@property="og:description"]/@content')[0]
            live_blurb = String.DecodeHTMLEntities( live_blurb ).strip()
            #Log.Debug( "#### live_blurb : %s ####" % (live_blurb)  )

            live_image = html.xpath('//meta[@property="og:image"]/@content')[0]
            #Log.Debug( "#### live_image : %s ####" % (live_image)  )

            live_banner = live_image
            #Log.Debug( "#### live_banner : %s ####", live_banner )

            # Extract live_id from url
            live_id = RE_LIVE_ID.search(canonical_url).group('live_id')
            #Log.Debug( "#### live_id : %s ####" % (live_id) )

            oc.add( VideoClipObject(
                     url                     = URL_PLEX_MOVIE.replace('{MOVIE_ID}',str(live_id)),
                     title                   = live_name,
                     thumb                   = live_image,
                     source_title            = 'TFC.tv',
                     summary                 = live_blurb,
                     #duration                = duration,
                     #originally_available_at = originally_available_at,
                     #art                     = live_banner
                 ))

            return oc

        # it is either a movie or a tv show
        try:
            show_banner = html.xpath('//link[@rel="image_src"]/@href')[0]
        except:
            show_banner = None
        #Log.Debug( "#### show_banner : %s ####", show_banner )

        try:
            episodes = html.xpath('//section[@class="sub-category-page"]//li[contains(@class,"og-grid-item")]')
        except:
            episodes = []
        #Log.Debug( "#### Found %d episodes! ####" % int(len(episodes)) )

        if len(episodes) == 0:

            # Assume it is a movie

            movie_name  = html.xpath('//meta[@property="og:title"]/@content')[0]
            movie_name = String.DecodeHTMLEntities( movie_name ).strip()
            #Log.Debug( "#### movie_name : %s ####" % (movie_name)  )

            movie_blurb = html.xpath('//meta[@property="og:description"]/@content')[0]
            movie_blurb = String.DecodeHTMLEntities( movie_blurb ).strip()

            movie_image = html.xpath('//meta[@property="og:image"]/@content')[0]
            #Log.Debug( "#### movie_image : %s ####" % (movie_image)  )

            try:
                banner_path = html.xpath('//div[contains(@class,"header-hero-image")]/@style')[0]
                movie_banner = RE_MOVIE_BANNER_PATH.search( banner_path ).group('banner_path')
            except:
                movie_banner = None
            #Log.Debug( "#### movie_banner : %s ####", movie_banner )

            # Extract movie_id from url
            movie_url = html.xpath('//div[contains(@class,"header-hero-image")]//a/@href')[0]
            movie_id  = RE_MOVIE_ID.search(movie_url).group('movie_id')
            #Log.Debug( "#### movie_id : %s ####" % (movie_id) )

            oc.add( MovieObject(
                     url                     = URL_PLEX_MOVIE.replace('{MOVIE_ID}',str(movie_id)),
                     title                   = movie_name,
                     thumb                   = movie_image,
                     source_title            = 'TFC.tv',
                     summary                 = movie_blurb,
                     #duration                = duration,
                     #originally_available_at = originally_available_at,
                     #art                     = movie_banner
                 ))

            return oc

        else:

            # Extract show id from url
            show_id = RE_SHOW_ID.search(page_url).group('show_id')
            #Log.Debug( "#### show_id : %s ####" % (show_id) )

            for episode in episodes:

                episode_name = episode.xpath('./a/div[@class="show-date"]/text()')[0]
                episode_name = String.DecodeHTMLEntities( episode_name ).strip()
                #Log.Debug( "#### episode_name : %s ####" % (episode_name)  )

                episode_id_href = episode.xpath('./a/@href')[0]
                # Impossible to get the regex to work so we just split on the / for now...
                episode_id = int(episode_id_href.split('/')[3])
                #Log.Debug( "#### episode_id : %d ####" % (episode_id)  )

                #originally_available_at = Datetime.ParseDate(episode.xpath('./@data-aired'))

                # For some extremely strange and annoying reason data-src can't be extracted with XPath!!!
                # <div class="show-cover" data-src="https://timg.tfc.tv/xcms/episodeimages/129284/20170614-ikaw-487-1.jpg">
                image_path = HTML.StringFromElement( episode.xpath('./a//div[@class="show-cover"]')[0] )
                # Log.Debug( "#### image_path : %s ####", image_path )

                m = RE_EPISODE_IMAGE_PATH.search( image_path )
                if m:
                    episode_image = m.group('image_path')
                else:
                    episode_image = None
                #Log.Debug( "#### episode_image : %s ####", episode_image )

                episode_blurb = episode.xpath('./@data-show-description')[0]
                episode_blurb = String.DecodeHTMLEntities( episode_blurb ).strip()
                #Log.Debug( "#### episode_blurb : %s ####" % (episode_blurb)  )
                #Log.Debug( "#### episode_banner: %s ####" % (episode_banner) )

                oc.add( EpisodeObject(
                         url                     = URL_PLEX_EPISODE.replace('{SHOW_ID}',str(show_id)).replace('{EPISODE_ID}',str(episode_id)),
                         title                   = episode_name,
                         thumb                   = episode_image,
                         source_title            = 'TFC.tv',
                         summary                 = episode_blurb,
                         show                    = name,
                         #season                  = season,
                         #absolute_index           = index,
                         #duration                = duration,
                         #originally_available_at = originally_available_at,
                         art                     = show_banner
                     ))

            # Add more button if more pages
            last_page = int(html.xpath('//ul[@id="pagination"]/li/a/text()')[-1])
            #Log.Debug("#### Page %d (%d) ####", page, last_page)
            if page < last_page:
                oc.add( NextPageObject(key = Callback( Show, title = title, name = name, url = url, page = page + 1 ) ) )

            if len(oc) < 1:
                return NothingFound(title, name, 'episodes')

            return oc 

    except:
        pass

        return NothingFound(title, name, 'content')



####################################################################################################
def ExtractHtmlText(dict, key, fallback=''):
    try:
        text = String.DecodeHTMLEntities( dict[key] ).strip()
    except: 
        text = fallback
        Log.Debug("# Using fallback text: '%s' instead of json['%s'] #" % (fallback,key) )
    #Log.Debug("# ExtractHtmlText: json['%s'] = '%s' #" % (key,text) )
    return text


####################################################################################################
def ExtractImageUrl(dict, key, fallback):
    try:
        url = str(dict[key])
        url = url.replace(r"http://","")
        url = "http://" + String.Quote(url)
        url = Resource.ContentsOfURLWithFallback( url, fallback=fallback )
    except: 
        url = fallback
        Log.Debug("# Using fallback image: '%s' instead of json['%s'] #" % (fallback,key) )
    #Log.Debug("# ExtractImageUrl: json['%s'] = '%s'#" % (key,url) )
    return url


####################################################################################################
def NothingFound(title, name, items):

    oc = ObjectContainer( title1 = title, title2 = name )

    oc.header  = name
    oc.message = "No %s found." % str(items)
    
    return oc

   
####################################################################################################
def Login():

    global COOKIES

    #try:
    #    if Prefs['preview']:
    #        COOKIES = ''
    #        return COOKIES
    #except:
    #    pass

    try:

        html = HTML.ElementFromURL( URL_LOGIN, cacheTime = 0 )

        try:
            url = html.xpath('//meta[@property="og:url"]/@content')[0]
        except:
            url = ''

        if url == BASE_URL + '/' and COOKIES:
            # No need to login
            DebugLog( 2, '# Already logged in! # ' )
            return COOKIES

        # Need to login
        Log.Debug( '# Need to login... #' )

        COOKIES = ''

        token = html.xpath('//input[@name="__RequestVerificationToken"]/@value')[0]
        #Log.Debug( '## __RequestVerificationToken: %s ##' % str(token) )
        values = {
                    '__RequestVerificationToken': token,
                    'EMail'                     : Prefs['email'],
                    'Password'                  : Prefs['password']
                 }

        HTTP.Headers['Referer'] = URL_LOGIN
        html = HTML.ElementFromURL( URL_LOGIN, values = values, cacheTime=0 )

        url = html.xpath('//meta[@property="og:url"]/@content')[0]
        if url == BASE_URL + '/':
            Log.Debug( '# Login successful #' )

            COOKIES = HTTP.CookiesForURL( URL_LOGIN )

            # From https://github.com/benaranguren/nuodtayo.tv/blob/master/plugin.video.tfctv/default.py
            cc_fingerprintid = Hash.MD5( Prefs['email'] )
            COOKIES = '%s; cc_fingerprintid=%s;' % (COOKIES, cc_fingerprintid)

            Log.Debug( '## COOKIES: %s ##' % str(COOKIES) )

            return COOKIES
        
    except:
        Log.Error( '## Failed to login!: #' )
        
    raise Ex.MediaNotAvailable


## EOF ##
    
