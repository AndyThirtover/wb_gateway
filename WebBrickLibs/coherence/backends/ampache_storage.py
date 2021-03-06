# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php

# Copyright 2008, Frank Scholz <coherence@beebits.net>

import time

try:
    import hashlib
    def md5(s):
        m =hashlib.md5()
        m.update(s)
        return m.hexdigest()
except ImportError:
    import md5 as oldmd5
    def md5(s):
        m=oldmd5.new()
        m.update(s)
        return m.hexdigest()

from twisted.internet import reactor,defer
from twisted.python import failure

from coherence.upnp.core import DIDLLite
from coherence.upnp.core.soap_service import errorCode
from coherence.upnp.core import utils

import coherence.extern.louie as louie

from coherence.backend import BackendItem, BackendStore


ROOT_CONTAINER_ID = 0
AUDIO_CONTAINER = 100
AUDIO_ALL_CONTAINER_ID = 101
AUDIO_ARTIST_CONTAINER_ID = 102
AUDIO_ALBUM_CONTAINER_ID = 103
AUDIO_PLAYLIST_CONTAINER_ID = 104
AUDIO_GENRE_CONTAINER_ID = 105
AUDIO_TAG_CONTAINER_ID = 106


from urlparse import urlsplit

class ProxySong(utils.ReverseProxyResource):

    def __init__(self, uri):
        self.uri = uri
        _,host_port,path,query,_ = urlsplit(uri)
        if host_port.find(':') != -1:
            host,port = tuple(host_port.split(':'))
            port = int(port)
        else:
            host = host_port
            port = 80

        utils.ReverseProxyResource.__init__(self, host, port, '?'.join((path,query)))


class Container(BackendItem):

    logCategory = 'ampache_store'

    get_path = None

    def __init__(self, id, parent_id, name, store=None, children_callback=None, container_class=DIDLLite.Container):
        self.id = id
        self.parent_id = parent_id
        self.name = name
        self.mimetype = 'directory'
        self.item = container_class(id, parent_id,self.name)
        self.update_id = 0
        if children_callback != None:
            self.children = children_callback
        else:
            self.children = []
        self.item.childCount = None #self.get_child_count()

        if store!=None:
            self.get_url = lambda: store.urlbase + str(self.id)

    def add_child(self, child):
        self.children.append(child)
        if self.item.childCount != None:
            self.item.childCount += 1

    def get_children(self,start=0,end=0):
        self.info("container.get_children %r %r", start, end)
        if(end - start > 250 or
           end - start == 0):
            end = start+250

        if callable(self.children):
            return self.children(start,end-start)
        else:
            children = self.children
        if end == 0:
            return children[start:]
        else:
            return children[start:end]

    def get_child_count(self):
        if self.item.childCount != None:
            return self.item.childCount

        if callable(self.children):
            return len(self.children())
        else:
            return len(self.children)

    def get_item(self):
        return self.item

    def get_name(self):
        return self.name

    def get_id(self):
        return self.id


class Playlist(BackendItem):

    logCategory = 'ampache_store'

    get_path = None

    def __init__(self, store, element):
        self.store = store
        self.ampache_id = element.get('id')
        self.id = 'playlist.%d' % int(element.get('id'))
        self.title = element.find('name').text
        self.creator = element.find('owner').text
        self.tracks = int(element.find('items').text)
        try:
            self.cover = element.find('art').text
        except:
            self.cover = None

    def get_children(self,start=0,end=0):
        return self.store.ampache_query('playlist_songs', start, end-start, filter=self.ampache_id)

    def get_child_count(self):
        return self.tracks

    def get_item(self, parent_id = AUDIO_PLAYLIST_CONTAINER_ID):
        item = DIDLLite.PlaylistItem(self.id, parent_id, self.title)
        item.childCount = self.get_child_count()
        item.artist = self.artist
        item.albumArtURI = self.cover
        return item

    def get_id(self):
        return self.id

    def get_name(self):
        return self.title

    def get_cover(self):
        return self.cover


class Album(BackendItem):

    logCategory = 'ampache_store'

    get_path = None

    def __init__(self, store, element):
        self.store = store
        self.ampache_id = element.get('id')
        self.id = 'album.%d' % int(element.get('id'))
        self.title = element.find('name').text
        self.artist = element.find('artist').text
        self.tracks = int(element.find('tracks').text)
        try:
            self.cover = element.find('art').text
        except:
            self.cover = None

    def get_children(self,start=0,end=0):
        return self.store.ampache_query('album_songs', start, end-start, filter=self.ampache_id)

    def get_child_count(self):
        return self.tracks

    def get_item(self, parent_id = AUDIO_ALBUM_CONTAINER_ID):
        item = DIDLLite.MusicAlbum(self.id, parent_id, self.title)
        item.childCount = self.get_child_count()
        item.artist = self.artist
        item.albumArtURI = self.cover
        return item

    def get_id(self):
        return self.id

    def get_name(self):
        return self.title

    def get_cover(self):
        return self.cover


class Artist(BackendItem):

    logCategory = 'ampache_store'

    get_path = None

    def __init__(self, store, element):
        self.store = store
        self.ampache_id = element.get('id')
        self.id = 'artist.%d' % int(element.get('id'))

        try:
            self.count_albums = int(element.find('albums').text)
        except:
            self.count_albums = None
        try:
            self.count_songs = int(element.find('songs').text)
        except:
            self.count_songs = None
        self.name = element.find('name').text

    def get_children(self,start=0,end=0):
        return self.store.ampache_query('artist_albums', start, end-start, filter=self.ampache_id)

    def get_child_count(self):
        if self.count_albums != None:
            return self.count_albums

        def got_childs(result):
            self.count_albums = len(result)
            return self.count_albums

        d = self.get_children()
        d.addCallback(got_childs)
        return d

    def get_item(self, parent_id = AUDIO_ARTIST_CONTAINER_ID):
        item = DIDLLite.MusicArtist(self.id, parent_id, self.name)
        return item

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

class Genre(BackendItem):

    logCategory = 'ampache_store'

    get_path = None

    def __init__(self, store, element):
        self.store = store
        self.ampache_id = element.get('id')
        self.id = 'genre.%d' % int(element.get('id'))

        try:
            self.count_albums = int(element.find('albums').text)
        except:
            self.count_albums = None
        try:
            self.count_artists = int(element.find('artists').text)
        except:
            self.count_artists = None
        try:
            self.count_songs = int(element.find('songs').text)
        except:
            self.count_songs = None
        self.name = element.find('name').text

    def get_children(self,start=0,end=0):
        return self.store.ampache_query('genre_songs', start, end-start, filter=self.ampache_id)

    def get_child_count(self):
        if self.count_songs != None:
            return self.count_songs

        def got_childs(result):
            self.count_songs = len(result)
            return self.count_songs

        d = self.get_children()
        d.addCallback(got_childs)
        return d

    def get_item(self, parent_id = AUDIO_GENRE_CONTAINER_ID):
        item = DIDLLite.Genre(self.id, parent_id, self.name)
        return item

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

class Tag(BackendItem):

    logCategory = 'ampache_store'

    get_path = None

    def __init__(self, store, element):
        self.store = store
        self.ampache_id = element.get('id')
        self.id = 'tag.%d' % int(element.get('id'))

        try:
            self.count_albums = int(element.find('albums').text)
        except:
            self.count_albums = None
        try:
            self.count_artists = int(element.find('artists').text)
        except:
            self.count_artists = None
        try:
            self.count_songs = int(element.find('songs').text)
        except:
            self.count_songs = None
        self.name = element.find('name').text

    def get_children(self,start=0,end=0):
        return self.store.ampache_query('tag_songs', start, end-start, filter=self.ampache_id)

    def get_child_count(self):
        if self.count_songs != None:
            return self.count_songs

        def got_childs(result):
            self.count_songs = len(result)
            return self.count_songs

        d = self.get_children()
        d.addCallback(got_childs)
        return d

    def get_item(self, parent_id = AUDIO_TAG_CONTAINER_ID):
        item = DIDLLite.Genre(self.id, parent_id, self.name)
        return item

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name


class Track(BackendItem):

    logCategory = 'ampache_store'

    def __init__(self,store,element):
        self.store = store
        self.id = 'song.%d' % int(element.get('id'))
        self.parent_id = 'album.%d' % int(element.find('album').get('id'))

        self.url = element.find('url').text

        seconds = int(element.find('time').text)
        hours = seconds / 3600
        seconds = seconds - hours * 3600
        minutes = seconds / 60
        seconds = seconds - minutes * 60
        self.duration = ("%d:%02d:%02d") % (hours, minutes, seconds)

        self.bitrate = 0

        self.title = element.find('title').text
        self.artist = element.find('artist').text
        self.album = element.find('album').text
        self.genre = element.find('genre').text
        self.track_nr = element.find('track').text

        try:
            self.cover = element.find('art').text
        except:
            self.cover = None
        try:
            self.mimetype = element.find('mimetype').text
        except:
            self.mimetype = "audio/mpeg"
        try:
            self.size = int(element.find('size').text)
        except:
            self.size = 0

        if self.store.proxy == True:
            self.location = ProxySong(self.url)

    def get_children(self, start=0, request_count=0):
        return []

    def get_child_count(self):
        return 0

    def get_item(self, parent_id=None):

        self.debug("Track get_item %r @ %r" %(self.id,self.parent_id))

        # create item
        item = DIDLLite.MusicTrack(self.id,self.parent_id)
        item.album = self.album

        item.artist = self.artist
        #item.date =
        item.genre = self.genre
        item.originalTrackNumber = self.track_nr
        item.title = self.title

        item.albumArtURI = self.cover

        # add http resource
        res = DIDLLite.Resource(self.get_url(), 'http-get:*:%s:*' % self.mimetype)
        if self.size > 0:
            res.size = self.size
        if self.duration > 0:
            res.duration = str(self.duration)
        if self.bitrate > 0:
            res.bitrate = str(bitrate)
        item.res.append(res)

        return item

    def get_id(self):
        return self.id

    def get_name(self):
        return self.title

    def get_url(self):
        if self.store.proxy == True:
            return self.store.urlbase + str(self.id)
        else:
            return self.url

    def get_path(self):
        return None


class AmpacheStore(BackendStore):

    """ this is a backend to the Ampache Media DB

    """

    implements = ['MediaServer']
    logCategory = 'ampache_store'

    def __init__(self, server, **kwargs):
        self.config = kwargs
        self.name = kwargs.get('name','Ampache')
        self.key = kwargs.get('key','')
        self.user = kwargs.get('user',None)
        self.url = kwargs.get('url','http://localhost/ampache/server/xml.server.php')

        if kwargs.get('proxy','no') in [1,'Yes','yes','True','true']:
            self.proxy = True
        else:
            self.proxy = False

        self.urlbase = kwargs.get('urlbase','')
        if self.urlbase[len(self.urlbase)-1] != '/':
            self.urlbase += '/'


        self.server = server
        self.update_id = 0
        self.token = None

        self.songs = 0
        self.albums = 0
        self.artists = 0

        self.get_token(api_version=350001)

    def __repr__(self):
        return "Ampache storage"


    def get_by_id(self,id):
        self.info("looking for id %r", id)
        if isinstance(id, basestring):
            id = id.split('@',1)
            id = id[0]
        if isinstance(id, basestring) and id.startswith('artist_all_tracks_'):
            try:
                return self.containers[id]
            except:
                return None
        item = None
        try:
            id = int(id)
            item = self.containers[id]
        except ValueError:
            try:
                type,id = id.split('.')
                if type in ['song','artist','album','playlist','genre','tag']:
                    item = self.ampache_query(type, filter=str(id))
            except ValueError:
                return None
        return item

    def got_auth_response( self, response):
        self.info( "got_auth_response %r", response)
        try:
            response = utils.parse_xml(response, encoding='utf-8')
        except SyntaxError, msg:
            self.warning('error parsing ampache answer %r', msg)
            raise SyntaxError, 'error parsing ampache answer %r' % msg
        try:
            error = response.find('error').text
            #if error == 'Error Invalid Handshake, attempt logged':
            #    """ maybe we've send out the wrong version number,
            #        let's try it again
            #    """
            #    return self.get_token(api_version=350001)
            self.warning('error on token request %r', error)
            raise ValueError, error
        except AttributeError:
            try:
                self.token = response.find('auth').text
                self.songs = int(response.find('songs').text)
                self.albums = int(response.find('albums').text)
                self.artists = int(response.find('artists').text)
                try:
                    self.playlists = int(response.find('playlists').text)
                except:
                    self.playlists = 0
                try:
                    self.genres = int(response.find('genres').text)
                except:
                    self.genres = 0
                try:
                    self.tags = int(response.find('tags').text)
                except:
                    self.tags = 0
                self.info('ampache returned auth token %r', self.token)
                self.info('Songs: %d, Artists: %d, Albums: %d, Playlists %d, Genres %d, Tags %d' % (self.songs, self.artists,self.albums,self.playlists,self.genres,self.tags))

                self.containers = {}
                self.containers[ROOT_CONTAINER_ID] = \
                            Container( ROOT_CONTAINER_ID,-1, self.name, store=self)

                self.wmc_mapping.update({'4': lambda : self.get_by_id(AUDIO_ALL_CONTAINER_ID),       # all tracks
                                         '5': lambda : self.get_by_id(AUDIO_GENRE_CONTAINER_ID),     # all genres
                                         '6': lambda : self.get_by_id(AUDIO_ARTIST_CONTAINER_ID),    # all artists
                                         '7': lambda : self.get_by_id(AUDIO_ALBUM_CONTAINER_ID),     # all albums
                                         '13': lambda : self.get_by_id(AUDIO_PLAYLIST_CONTAINER_ID), # all playlists
                                        })

                louie.send('Coherence.UPnP.Backend.init_completed', None, backend=self)
            except AttributeError:
                raise ValueError, 'no authorization token returned'

    def got_auth_error(self, e):
        self.warning('error calling ampache %r', e)
        louie.send('Coherence.UPnP.Backend.init_failed', None, backend=self, msg=e)

    def get_token( self,api_version=None):
        """ ask Ampache for the authorization token """
        timestamp = int(time.time())
        passphrase = md5('%d%s' % (timestamp, self.key))
        request = ''.join((self.url, '?action=handshake&auth=%s&timestamp=%d' % (passphrase, timestamp)))
        if self.user != None:
            request = ''.join((request, '&user=%s' % self.user))
        if api_version != None:
            request = ''.join((request, '&version=%s' % str(api_version)))
        self.info("auth_request %r", request)
        d = utils.getPage(request)
        d.addCallback(self.got_auth_response)
        d.addErrback(self.got_auth_error)

    def got_error(self, e):
        self.warning('error calling ampache %r', e)

    def got_response(self, response, query_item):
        self.info("got a response for %r", query_item)
        response = utils.parse_xml(response, encoding='utf-8')
        items = []
        try:
            self.warning('error on token request %r', response.find('error').text)
            raise ValueError, response.find('error').text
        except AttributeError:
            if query_item in ('song','artist','album','playlist','genre'):
                q = response.find(query_item)
                if q == None:
                    return None
                else:
                    if q.tag in ['song']:
                        return Track(self,q)
                    if q.tag == 'artist':
                        return Artist(self,q)
                    if q.tag in ['album']:
                        return Album(self,q)
                    if q.tag in ['playlist']:
                        return Playlist(self,q)
                    if q.tag in ['genre']:
                        return Genre(self,q)
                    if q.tag in ['tag']:
                        return Tag(self,q)
            else:
                if query_item in ('songs','artists','albums','playlists','genres','tag'):
                    query_item = query_item[:-1]
                if query_item in ('playlist_songs','album_songs','genre_songs','tag_songs'):
                    query_item = 'song'
                if query_item in ('artist_albums',):
                    query_item = 'album'
                for q in response.findall(query_item):
                    if query_item in ('song',):
                        items.append(Track(self,q))
                    if query_item in ('artist',):
                        items.append(Artist(self,q))
                    if query_item in ('album',):
                        items.append(Album(self,q))
                    if query_item in ('playlist',):
                        items.append(Playlist(self,q))
                    if query_item in ('genre',):
                        items.append(Genre(self,q))
                    if query_item in ('tag',):
                        items.append(Tag(self,q))
        return items

    def ampache_query(self, item, start=0, request_count=0, filter=None):
        request = ''.join((self.url, '?action=%s&auth=%s&offset=%d' % (item,self.token, start)))
        if request_count > 0:
            request = ''.join((request, '&limit=%d' % request_count))
        if filter != None:
            request = ''.join((request, '&filter=%s' % filter))
        self.info("ampache_query %r", request)
        d = utils.getPage(request)
        d.addCallback(self.got_response, item)
        d.addErrback(self.got_error)
        return d

    def ampache_query_songs(self, start=0, request_count=0):
        return self.ampache_query('songs', start, request_count)

    def ampache_query_albums(self, start=0, request_count=0):
        return self.ampache_query('albums', start, request_count)

    def ampache_query_artists(self, start=0, request_count=0):
        return self.ampache_query('artists', start, request_count)

    def ampache_query_playlists(self, start=0, request_count=0):
        return self.ampache_query('playlists', start, request_count)

    def ampache_query_genres(self, start=0, request_count=0):
        return self.ampache_query('genres', start, request_count)

    def ampache_query_tags(self, start=0, request_count=0):
        return self.ampache_query('tags', start, request_count)

    def upnp_init(self):
        if self.server:
            self.server.connection_manager_server.set_variable(0, 'SourceProtocolInfo',
                            ['http-get:*:audio/mpeg:*',
                             'http-get:*:application/ogg:*',])

        self.containers[AUDIO_ALL_CONTAINER_ID] = \
                Container( AUDIO_ALL_CONTAINER_ID,ROOT_CONTAINER_ID, 'All tracks',
                          store=self,
                          children_callback=self.ampache_query_songs)
        self.containers[AUDIO_ALL_CONTAINER_ID].item.childCount = self.songs
        self.containers[ROOT_CONTAINER_ID].add_child(self.containers[AUDIO_ALL_CONTAINER_ID])

        self.containers[AUDIO_ALBUM_CONTAINER_ID] = \
                Container( AUDIO_ALBUM_CONTAINER_ID,ROOT_CONTAINER_ID, 'Albums',
                          store=self,
                          children_callback=self.ampache_query_albums)
        self.containers[AUDIO_ALBUM_CONTAINER_ID].item.childCount = self.albums
        self.containers[ROOT_CONTAINER_ID].add_child(self.containers[AUDIO_ALBUM_CONTAINER_ID])

        self.containers[AUDIO_ARTIST_CONTAINER_ID] = \
                Container( AUDIO_ARTIST_CONTAINER_ID,ROOT_CONTAINER_ID, 'Artists',
                          store=self,
                          children_callback=self.ampache_query_artists)
        self.containers[AUDIO_ARTIST_CONTAINER_ID].item.childCount = self.artists
        self.containers[ROOT_CONTAINER_ID].add_child(self.containers[AUDIO_ARTIST_CONTAINER_ID])

        self.containers[AUDIO_PLAYLIST_CONTAINER_ID] = \
                Container( AUDIO_PLAYLIST_CONTAINER_ID,ROOT_CONTAINER_ID, 'Playlists',
                          store=self,
                          children_callback=self.ampache_query_playlists,
                          container_class=DIDLLite.PlaylistContainer)
        self.containers[AUDIO_PLAYLIST_CONTAINER_ID].item.childCount = self.playlists
        self.containers[ROOT_CONTAINER_ID].add_child(self.containers[AUDIO_PLAYLIST_CONTAINER_ID])

        self.containers[AUDIO_GENRE_CONTAINER_ID] = \
                Container( AUDIO_GENRE_CONTAINER_ID,ROOT_CONTAINER_ID, 'Genres',
                          store=self,
                          children_callback=self.ampache_query_genres)
        self.containers[AUDIO_GENRE_CONTAINER_ID].item.childCount = self.genres
        self.containers[ROOT_CONTAINER_ID].add_child(self.containers[AUDIO_GENRE_CONTAINER_ID])

        self.containers[AUDIO_TAG_CONTAINER_ID] = \
                Container( AUDIO_TAG_CONTAINER_ID,ROOT_CONTAINER_ID, 'Tags',
                          store=self,
                          children_callback=self.ampache_query_tags)
        self.containers[AUDIO_TAG_CONTAINER_ID].item.childCount = self.tags
        self.containers[ROOT_CONTAINER_ID].add_child(self.containers[AUDIO_TAG_CONTAINER_ID])

    def upnp_XBrowse(self, *args, **kwargs):
        try:
            ObjectID = kwargs['ObjectID']
        except:
            self.debug("hmm, a Browse action and no ObjectID argument? An XBox maybe?")
            try:
                ObjectID = kwargs['ContainerID']
            except:
                ObjectID = 0
        BrowseFlag = kwargs['BrowseFlag']
        Filter = kwargs['Filter']
        StartingIndex = int(kwargs['StartingIndex'])
        RequestedCount = int(kwargs['RequestedCount'])
        SortCriteria = kwargs['SortCriteria']
        parent_container = None
        requested_id = None

        if BrowseFlag == 'BrowseDirectChildren':
            parent_container = str(ObjectID)
        else:
            requested_id = str(ObjectID)

        self.info("upnp_Browse request %r %r %r %r", ObjectID, BrowseFlag, StartingIndex, RequestedCount)

        didl = DIDLLite.DIDLElement(upnp_client=kwargs.get('X_UPnPClient', ''),
                           requested_id=requested_id,
                           parent_container=parent_container)

        def build_response(tm):
            num_ret = didl.numItems()
            #if int(kwargs['RequestedCount']) != 0 and num_ret != int(kwargs['RequestedCount']):
            #    num_ret = 0
            #if RequestedCount == 0 and tm-StartingIndex != num_ret:
            #    num_ret = 0
            r = {'Result': didl.toString(), 'TotalMatches': tm,
                 'NumberReturned': num_ret}

            self.info("upnp_Browse response %r %r", num_ret, tm)

            if hasattr(item, 'update_id'):
                r['UpdateID'] = item.update_id
            elif hasattr(self, 'update_id'):
                r['UpdateID'] = self.update_id # FIXME
            else:
                r['UpdateID'] = 0

            return r

        total = 0
        items = []

        wmc_mapping = getattr(self, "wmc_mapping", None)
        if(kwargs.get('X_UPnPClient', '') == 'XBox' and
            wmc_mapping != None and
            wmc_mapping.has_key(ObjectID)):
            """ fake a Windows Media Connect Server
            """
            root_id = wmc_mapping[ObjectID]
            if callable(root_id):
                item = root_id()
                if item  is not None:
                    if isinstance(item, list):
                        total = len(item)
                        if int(RequestedCount) == 0:
                            items = item[StartingIndex:]
                        else:
                            items = item[StartingIndex:StartingIndex+RequestedCount]
                    else:
                        d = defer.maybeDeferred( item.get_children, StartingIndex, StartingIndex + RequestedCount)
                        d.addCallback( process_result)
                        d.addErrback(got_error)
                        return d

            for i in items:
                didl.addItem(i.get_item())

            return build_response(total)

        root_id = ObjectID

        item = self.get_by_id(root_id)
        if item == None:
            return failure.Failure(errorCode(701))
        def got_error(r):
            return r

        def process_result(result, found_item):
            if result == None:
                result = []
            if BrowseFlag == 'BrowseDirectChildren':
                l = []

                def process_items(result, tm):
                    if result == None:
                        result = []
                    for i in result:
                        if i[0] == True:
                            didl.addItem(i[1])

                    return build_response(tm)

                for i in result:
                    d = defer.maybeDeferred(i.get_item)
                    l.append(d)

                def got_child_count(count):
                    dl = defer.DeferredList(l)
                    dl.addCallback(process_items, count)
                    return dl

                d = defer.maybeDeferred(found_item.get_child_count)
                d.addCallback(got_child_count)

                return d

            else:
                didl.addItem(result)
                total = 1

            return build_response(total)

        def proceed(result):
            if BrowseFlag == 'BrowseDirectChildren':
                d = defer.maybeDeferred( result.get_children, StartingIndex, StartingIndex + RequestedCount)
            else:
                d = defer.maybeDeferred( result.get_item)

            d.addCallback( process_result, result)
            d.addErrback(got_error)
            return d

        if isinstance(item,defer.Deferred):
            item.addCallback(proceed)
            return item
        else:
            return proceed(item)


if __name__ == '__main__':

    from coherence.base import Coherence

    def main():
        def got_result(result):
            print "got_result"

        def call_browse(ObjectID=0,StartingIndex=0,RequestedCount=0):
            r = f.backend.upnp_Browse(BrowseFlag='BrowseDirectChildren',
                            RequestedCount=RequestedCount,
                            StartingIndex=StartingIndex,
                            ObjectID=ObjectID,
                            SortCriteria='*',
                            Filter='')
            r.addCallback(got_result)
            r.addErrback(got_result)

        def call_test(start,count):
            r = f.backend.ampache_query_artists(start,count)
            r.addCallback(got_result)
            r.addErrback(got_result)


        config = {}
        config['logmode'] = 'warning'
        c = Coherence(config)
        f = c.add_plugin('AmpacheStore',
                        url='http://localhost/ampache/server/xml.server.php',
                        key='password',
                        user=None)
        reactor.callLater(3, call_browse, 0, 0, 0)

        #reactor.callLater(3, call_browse, AUDIO_ALL_CONTAINER_ID, 0, 0)
        #reactor.callLater(3, call_browse, AUDIO_ARTIST_CONTAINER_ID, 0, 10)
        #reactor.callLater(3, call_browse, AUDIO_ALBUM_CONTAINER_ID, 0, 10)
        #reactor.callLater(3, call_test, 0, 10)

    reactor.callWhenRunning(main)
    reactor.run()
