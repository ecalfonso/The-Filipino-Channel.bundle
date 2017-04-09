# Debug
DEBUG           = True
DEBUG_STRUCTURE = False

# General
TITLE      = 'The Filipino Channel'
PREFIX     = '/video/tfctv'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/600.3.18 (KHTML, like Gecko) Version/8.0.3 Safari/600.3.18'

# Resources
ART      = 'art-default.jpg'
ICON     = 'icon-default.png'
LOGO     = 'TFC-logo.jpg'
MORE     = 'more.png'

# TFC URLs
BASE_URL   = 'http://tfc.tv/Synapse'

URL_GET_SITE_MENU        = BASE_URL + '/GetSiteMenu'
URL_GET_MOST_LOVED_SHOWS = BASE_URL + '/GetMostLovedShows'
URL_GET_SHOWS            = BASE_URL + '/GetShows/{SUB_CAT_ID}'
URL_GET_SHOW_DETAILS     = BASE_URL + '/GetShowDetails/{SHOW_ID}'
URL_SEARCH               = BASE_URL + '/ContentSearch?q={QUERY}'

# Constructed URLs for URL service
URL_PLEX_MOVIE   = 'tfctv://{SHOW_ID}'
URL_PLEX_EPISODE = 'tfctv://{SHOW_ID}/{EPISODE_ID}'

# Max umber of items to show in one listing
MAX_NUM_SHOWS    = 20
MAX_NUM_EPISODES =  5

# Set default cache to 3 hours
CACHE_TIME = 3 * CACHE_1HOUR # seconds

# URLs for testing TFC.tv
#http://tfc.tv/Synapse/GetSiteMenu
#http://tfc.tv/Synapse/GetShowDetails/384
#http://tfc.tv/Synapse/GetEpisodeDetails/121696
#http://tfc.tv/Synapse/GetVideo/121696
#http://tfc.tv/Synapse/GetMostLovedShows
#http://tfc.tv/Synapse/MyContent
#http://tfc.tv/Synapse/MyVideos
#http://tfc.tv/Synapse/ContentSearch?q=mother&c=50
#http://tfc.tv/Synapse/GetCelebrityDetails/37
#http://tfc.tv/Synapse/GetComments?categoryId=Shows&streamid=Show_3484&limit=0&depth=3&sort=dateDesc



####################################################################################################
def Start( **kwargs ):

    InputDirectoryObject.thumb = R('Search.png')
    DirectoryObject.art  = R(ART)

    ObjectContainer.title1 = TITLE

    HTTP.CacheTime = 3 * CACHE_TIME

    HTTP.Headers['User-Agent'] = USER_AGENT
    

####################################################################################################
@handler(PREFIX, TITLE, art=ART, thumb=LOGO)
def MainMenu( **kwargs ):

    try:
    
        oc = ObjectContainer()

        site_menu = JSON.ObjectFromURL( URL_GET_SITE_MENU )
            
        #Log.Debug('@#$ JSON:  %s ', siteMenu )
        
        for category in site_menu:
            category_name = ExtractHtmlText( category, 'name' )
            #Log.Debug('%s', category_name )
            oc.add( DirectoryObject( key = Callback( Category, title = TITLE, name = category_name, cat_id = category['id'] ), title = category_name ) )

        oc.add( DirectoryObject( key = Callback( MostLovedShows, title = TITLE, name = 'Most Loved Shows' ), title = 'Most Loved Shows' ) )

        oc.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search The Filipino Channel', prompt='Search for...'))
        #oc.add(SearchDirectoryObject(identifier='com.plexapp.plugins.tfctv', title='Search', summary='Search The Filipno Channel', prompt='Search:', thumb=R('search.png')))

        return oc
        
    except:

        return NothingFound(title, name, 'content')


####################################################################################################
@route(PREFIX + '/category', cat_id=int )
def Category( title, name, cat_id, **kwargs ):

    try:
    
        oc = ObjectContainer( title1 = title, title2 = name )

        siteMenu = JSON.ObjectFromURL( URL_GET_SITE_MENU )

        for category in siteMenu:
            #Log.Debug("%d", category['id'] )
            if category['id'] == cat_id:
                #Log.Debug('cat found')
                for sub_category in category['menu']:
                    sub_category_name = ExtractHtmlText( sub_category, 'name' )
                    #Log.Debug("    %s" % (sub_category_name) )
                    oc.add( DirectoryObject( key = Callback( SubCategory, title = name, name = sub_category_name, sub_id = sub_category['id'] ), title = sub_category_name ) )

        if len(oc) < 1:
            return NothingFound(title, name, 'items')

        return oc    
        
    except:
    
        return NothingFound(title, name, 'content')
                                                                                                                                        

####################################################################################################
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

            oc.add( DirectoryObject( key = Callback( Show, title = 'Search Results', name = show_name, show_id = show_id ), title = show_name, thumb = show_image, art = show_banner, summary = show_blurb ) )

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

            oc.add( DirectoryObject( key = Callback( Show, title = name, name = show_name, show_id = show_id ), title = show_name, thumb = show_image, summary = show_blurb ) )

        if len(shows) == MAX_NUM_SHOWS:
            oc.add( NextPageObject(key = Callback( MostLovedShows, title = title, name = name, first = first + MAX_NUM_SHOWS ) ) )

        if len(oc) < 1:
            return NothingFound(title, name, 'shows')
                
        return oc

    except:

        return NothingFound(title, name, 'content')


####################################################################################################
@route(PREFIX + '/subcategory', sub_id=int, first=int )
def SubCategory( title, name, sub_id, first=0, **kwargs ):
 
    try:
    
        oc = ObjectContainer( title1 = title, title2 = name )

        show_info = JSON.ObjectFromURL( URL_GET_SHOWS.replace('{SUB_CAT_ID}',str(sub_id)) )

        #Log.Debug(" shows: %s", show_info )
        
        try:
            shows = show_info['shows'][first:first+MAX_NUM_SHOWS]  
        except:
            shows = []
        
        for show in shows:
        
            #Log.Debug(" show: %s", show )
            
            show_id     = show['id']
            show_name   = ExtractHtmlText( show, 'name' )
            show_blurb  = ExtractHtmlText( show, 'blurb' )
            show_image  = ExtractImageUrl( show, 'image' , fallback=R(ICON) )
            show_banner = ExtractImageUrl( show, 'banner', fallback=R(ART)  )
            
            #Log.Debug( "#### show_name  : %s ####" % (show_name)   )
            #Log.Debug( "#### show_blurb : %s ####" % (show_blurb)  )
            #Log.Debug( "#### show_image : %s ####" % (show_image)  )
            #Log.Debug( "#### show_banner: %s ####" % (show_banner) )

            oc.add( DirectoryObject( key = Callback( Show, title = name, name = show_name, show_id = show_id ), title = show_name, thumb = show_image, art = show_banner, summary = show_blurb ) )

        if len(shows) == MAX_NUM_SHOWS:
            oc.add( NextPageObject(key = Callback( SubCategory, title = title, name = name, sub_id = sub_id, first = first + MAX_NUM_SHOWS ) ) )

        if len(oc) < 1:
            return NothingFound(title, name, 'shows')
                
        return oc 
    
    except:
    
        return NothingFound(title, name, 'content') 


####################################################################################################
@route(PREFIX + '/show', show_id=int, first=int )
def Show( title, name, show_id, first=0, **kwargs ):
 
    try:
    
        oc = ObjectContainer( title1 = title, title2 = name )

        show_details = JSON.ObjectFromURL( URL_GET_SHOW_DETAILS.replace('{SHOW_ID}',str(show_id)) )

        #Log.Debug( "#### show_details: %s ####" % (show_details) )

        show_name   = ExtractHtmlText( show_details, 'name'  )
        show_blurb  = ExtractHtmlText( show_details, 'blurb' )
        show_image  = ExtractImageUrl( show_details, 'image' , fallback=R(ICON) )
        show_banner = ExtractImageUrl( show_details, 'banner', fallback=R(ART)  )

        oc.art = show_banner

        #Log.Debug( "#### show_name  : %s ####" % (show_name)   )
        #Log.Debug( "#### show_blurb : %s ####" % (show_blurb)  )
        #Log.Debug( "#### show_image : %s ####" % (show_image)  )
        #Log.Debug( "#### show_banner: %s ####" % (show_banner) )
        
        try:
            show_type = show_details['type']
        except:
            show_type = 'Unknown'
        #Log.Debug('#### show_type: %s ####', show_type )

        try:
            episodes = show_details['episodes'][first:first+MAX_NUM_EPISODES]
        except:
            episodes = []
        #Log.Debug('#### #episodes: %d ####', len(episodes) )

        #Log.Debug('#### before show: %s ####', show_name )

        if show_type == 'show' or len(episodes) > 0:
        
            #Log.Debug('#### show: %s ####', show_name )

            for episode in episodes:

                #Log.Debug('#### episode: %s ####', str(episode) )

                episode_name = ExtractHtmlText( episode, 'name' )
                
                #Log.Debug('#### episode_name: %s ####', episode_name )

                episode_id              = episode['id']
                image                   = ExtractImageUrl( episode, 'image', fallback=R(ICON) )
                summary                 = ExtractHtmlText( episode, 'synopsis' )
                index                   = episode['episodenumber']
                duration                = Datetime.MillisecondsFromString(episode['episodelength'])
                originally_available_at = Datetime.ParseDate(episode['dateaired'])

                oc.add( EpisodeObject(
                         url                     = URL_PLEX_EPISODE.replace('{SHOW_ID}',str(show_id)).replace('{EPISODE_ID}',str(episode_id)),
                         title                   = episode_name,
                         thumb                   = image,
                         source_title            = 'TFC.tv',
                         summary                 = summary,
                         show                    = show_name,
                         #season                  = season,
                         absolute_index           = index,
                         duration                = duration,
                         originally_available_at = originally_available_at,
                         art                     = show_banner 
                     ))


            if len(episodes) == MAX_NUM_EPISODES:
                oc.add( NextPageObject(key = Callback( Show, title = title, name = name, show_id = show_id, first = first + MAX_NUM_EPISODES ) ) )

        elif show_type == 'movie':

            Log.Debug('#### movie: %s ####', show_name )
            
            try:
                originally_available_at = Datetime.ParseDate(show_details['dateairedstr'])
            except:
                originally_available_at = ''
            try:
                url = URL_PLEX_MOVIE.replace('{SHOW_ID}',str(show_id))
            except:
                url = 'illegal url'
                
            Log.Debug('#### URL: %s ####', url )

            oc.add( MovieObject(
                         url                     = url,
                         title                   = show_name,
                         thumb                   = show_image,
                         summary                 = show_blurb,
                         #tagline                 = name,   
                         #duration                = duration,
                         year                    = originally_available_at,
                         originally_available_at = originally_available_at,
                         art                     = show_banner
                     )) 

        else:
        
            Log.Debug('#### Unknown type!!: %s ####', show_name )

        if len(oc) < 1:
            return NothingFound(title, name, 'episodes')

        return oc 
    
    except:
    
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

    
## EOF ##
    
