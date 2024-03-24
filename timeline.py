#!/usr/bin/python3
# -*- coding: utf-8 -*-
from datetime import datetime
from .channel import Channel

from random import randint, choice
from copy import deepcopy
import json, time, base64, copy, requests, os, random

def loggedIn(func):
    def checkLogin(*args, **kwargs):
        if args[0].isLogin:
            return func(*args, **kwargs)
        else:
            args[0].callback.default('You want to call the function, you must login to LINE')
    return checkLogin
    
class Timeline(Channel):

    def __init__(self):
        if not self.channelId:
            self.channelId = self.server.CHANNEL_ID['LINE_TIMELINE']
        Channel.__init__(self, self.channel, self.channelId, False)
        self.tl = self.getChannelResult()
        self.__loginTimeline()

    def __loginTimeline(self):
        self.server.setTimelineHeadersWithDict({
            'Content-Type': 'application/json; charset=UTF-8',
            'User-Agent': 'androidapp.line/11.5.1 (Linux; U; Android 7.0; en-GB; Redmi Note 4 Build/NRD90M)',
            'X-Line-Mid': self.profile.mid,
            'X-Line-Carrier': self.server.CARRIER,
            'X-LSR': 'ID',
            'X-LPV': '1',
            'X-Line-Application': 'ANDROID 11.5.1 Android OS 7.0',
            'Accept-Encoding': 'gzip',
            'X-Line-ChannelToken': self.tl.channelAccessToken
        })
        self.LineLegyDomain = "https://legy-jp-addr.line.naver.jp"
        self.LineHostDomain = "https://ga2.line.naver.jp"
        self.LineGwzDomain  = "https://gwz.line.naver.jp"
        self.LineObsDomain  = "https://obs-sg.line-apps.com"
        self.LineLiffDomain = "https://api.line.me/message/v3/share"
        self.LinePermission = "https://access.line.me/dialog/api/permissions"
        self.profileDetail = self.getProfileDetail()

    @loggedIn
    def genOBSParamsV2(self, params):
        return base64.b64encode(json.dumps(params).encode('utf-8'))

    @loggedIn
    def genObjectId(self):
        random.seed = (os.urandom(1024))
        return ''.join(random.choice("abcdef1234567890") for i in range(32))

    @loggedIn
    def updateCover(self, picture):
        oid = self.genObjectId()
        print(oid)
        headers = copy.deepcopy(self.server.timelineHeaders)
        headers["X-Line-PostShare"] = "false"
        headers["X-Line-StoryShare"] = "false"
        headers["X-Line-Signup-Region"] = "ID"
        headers["Content-Type"] = "image/png"
        print(headers)
        obs = self.genOBSParamsV2(
            {"name": picture, "oid": oid, "type": "image", "userid": self.profile.mid, "ver": "2.0"})
        headers["x-obs-params"] = obs
        result = requests.post(
            self.LineObsDomain + "/r/myhome/c/" + oid, headers=headers, data=open(picture, 'rb'))
        if result.status_code != 201:
            raise Exception("[ Error ] Fail change cover")
        print(result.text)
        self.updateProfileCoverById(oid)
        return

    @loggedIn
    def getProfileDetail(self, mid=None, styleMediaVersion='v2', storyVersion='v6'):
        if mid is None:
            mid = self.profile.mid
        params = {
            'homeId': mid,
            'styleMediaVersion': styleMediaVersion,
            'storyVersion': storyVersion
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET",
            'x-line-global-config': "discover.enable=true; follow.enable=true",
        })
        url = self.server.urlEncode(self.LineHostDomain+'/hm', '/api/v1/home/profile.json', params)
        r = self.server.postContent(url, headers=hr, data='')

        return r.json()

    @loggedIn
    def getProfileCoverDetail(self, mid=None):
        if mid is None:
            mid = self.profile.mid
        params = {'homeId': mid}
        header = self.server.additionalHeaders(self.server.timelineHeaders, {'x-lhm': "GET",})
        url = self.server.urlEncode(self.LineHostDomain+ '/hm', '/api/v1/home/cover.json', params)
        r = self.server.postContent(url, headers=header)
        return r.json()

    @loggedIn
    def getHomeProfile(self, mid=None, postLimit=10, commentLimit=1, likeLimit=1):
        if mid is None:
            mid = self.profile.mid
        params = {'homeId': mid, 'postLimit': postLimit, 'commentLimit': commentLimit, 'likeLimit': likeLimit, 'sourceType': 'LINE_PROFILE_COVER'}
        url = self.server.urlEncode(self.LineLegyDomain, '/mh/api/v52/post/list.json', params)
        r = self.server.getContent(url, headers=self.server.timelineHeaders)
        return r.json()

    @loggedIn
    def getProfileCoverURLV2(self, mid=None):
        r = self.getProfileCoverDetail(mid)
        print(json.dumps(r,indent=2))

        params = {'userid': mid, 'oid': r['result']['coverObsInfo']['objectId']}
        return self.server.urlEncode(self.server.LINE_OBS_DOMAIN, '/myhome/c/download.nhn', params)


    @loggedIn
    def getHomeProfile(self, mid=None, postLimit=10, commentLimit=1, likeLimit=1):
        if mid is None:
            mid = self.profile.mid
        params = {'homeId': mid, 'postLimit': postLimit, 'commentLimit': commentLimit, 'likeLimit': likeLimit, 'sourceType': 'LINE_PROFILE_COVER'}
        url = self.server.urlEncode(self.LineLegyDomain, '/mh/api/v52/post/list.json', params)
        r = self.server.getContent(url, headers=self.server.timelineHeaders)
        return r.json()

    @loggedIn
    def updateProfileCoverById(self, objid, isVideo=False):
        data = {
            "homeId": self.profile.mid,
            "coverObjectId": objid,
            "storyShare": False,
            "meta": {}
        }
        if isVideo:
            data['videoCoverObjectId'] = objid
        headers = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "POST",
        })
        r = self.server.postContent(self.LineHostDomain+ '/hm/api/v1/home/cover.json', headers=headers, data=json.dumps(data))
        return r.json()

    @loggedIn
    def getProfileCoverURL(self, mid=None):
        if mid is None:
            mid = self.profile.mid
        profileDetail = self.getProfileDetail(mid)
        if 'videoCoverObsInfo' in profileDetail['result']:
            params = {'userid': mid, 'oid': profileDetail['result']['videoCoverObsInfo']['objectId']}
            url = self.server.urlEncode(self.LineObsDomain, '/myhome/vc/download.nhn', params)
            return url
        else:
            params = {'userid': mid, 'oid': profileDetail['result']['coverObsInfo']['objectId']}
            url = self.server.urlEncode(self.LineObsDomain, '/myhome/c/download.nhn', params)
            return url

    @loggedIn
    def sendPostToTalk(self, mid, postId):
        if mid is None:
            mid = self.profile.mid
        params = {'receiveMid': mid, 'postId': postId}
        url = self.server.urlEncode(self.LineLegyDomain, '/mh/api/v52/post/sendPostToTalk.json', params)
        r = self.server.getContent(url, headers=self.server.timelineHeaders)
        return r.json()

    @loggedIn
    def getPost(self, postId, mid=None, commentLimit=1, likeLimit=1):
        if mid is None:
            mid = self.profile.mid
        params = {'homeId': mid, 'postId': postId, 'commentLimit': commentLimit, 'likeLimit': likeLimit, 'sourceType': 'LINE_PROFILE_COVER'}
        url = self.server.urlEncode(self.LineLegyDomain, '/mh/api/v52/post/get.json', params)
        r = self.server.getContent(url, headers=self.server.timelineHeaders)
        return r.json()

    @loggedIn
    def createComment(self, mid, contentId, text, contentMetadata={}):
        if mid is None:
            mid = self.profile.mid
        params = {'homeId': mid, 'sourceType': 'TIMELINE'}
        data = {
            'contentId': contentId,
        }
        if '@!' in text:
            text = text.replace('@!','@')
        if '@' in text:
            data.update({
                'actorId': mid,
                'commentText': str(text),
                'recallInfos':[
                    {
                        'start': text.index('@'),
                        'end': text.index('@')+1,
                        'user':{
                            'actorId': mid
                        }
                    }
                ]
            })
        else:
            data['commentText'] = str(text)
        if contentMetadata != {}:
            data['secret'] = False
            data['contentsList'] = []
            data['contentsList'].append({
                'categoryId' : 'sticker',
                'extData' : {
                    'id' : contentMetadata["STKID"],
                    'packageId' : contentMetadata["STKPKGID"],
                    'packageVersion' : 1
                }
            })
        url = self.server.urlEncode(self.LineGwzDomain, '/mh/api/v52/comment/create.json', params)
        data = json.dumps(data)
        r = self.server.postContent(url, data=data, headers=self.server.timelineHeaders)
        return r.json()

    @loggedIn
    def listComment(self, mid, contentId):
        params = {
            'homeId': mid,
            #'actorId': actorId,
            'contentId': contentId,
            #'limit': 10
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET"
        })
        url = self.server.urlEncode(self.LineLegyDomain, '/mh/api/v52/comment/getList.json', params)
        r = self.server.postContent(url, headers=hr)
        return r.json()

    @loggedIn
    def deleteComment(self, mid, postId, commentId):
        if mid is None:
            mid = self.profile.mid
        params = {'homeId': mid, 'sourceType': 'TIMELINE'}
        url = self.server.urlEncode(self.LineLegyDomain, '/mh/api/v45/comment/delete.json', params)
        data = {'commentId': commentId, 'activityExternalId': postId, 'actorId': mid}
        data = json.dumps(data)
        r = self.server.postContent(url, data=data, headers=self.server.timelineHeaders)
        return r.json()

    @loggedIn
    def likePost(self, mid, postId, likeType=1001):
        if mid is None:
            mid = self.profile.mid
        if likeType not in [1001,1002,1003,1004,1005,1006]:
            raise Exception('Invalid parameter likeType')
        params = {'homeId': mid, 'sourceType': 'TIMELINE'}
        url = self.server.urlEncode(self.LineLegyDomain, '/mh/api/v45/like/create.json', params)
        data = {'likeType': likeType, 'activityExternalId': postId, 'actorId': mid}
        data = json.dumps(data)
        r = self.server.postContent(url, data=data, headers=self.server.timelineHeaders)
        return r.json()

    @loggedIn
    def createLikeV2(self, mid, contentId, likeType=1001):
        if mid is None:
            mid = self.profile.mid
        if likeType not in [1001,1002,1003,1004,1005,1006]:
            raise Exception('Invalid parameter likeType')
        params = {'homeId': mid, 'sourceType': 'TIMELINE'}
        data = {
           "contentId" : contentId,
           "likeType" : str(likeType),
           "sharable" : False,
           "commandId" : 16777265,
           "channelId" : "1341209850",
           "commandType" : 188210
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "POST"
        })
        url = self.server.urlEncode(self.LineLegyDomain, '/mh/api/v41/like/create.json', params)
        r = self.server.postContent(url, json=data, headers=hr)
        print(r)
        return r

    @loggedIn
    def unlikePost(self, mid, postId):
        if mid is None:
            mid = self.profile.mid
        params = {'homeId': mid, 'sourceType': 'TIMELINE'}
        url = self.server.urlEncode(self.LineLegyDomain, '/mh/api/v45/like/cancel.json', params)
        data = {'activityExternalId': postId, 'actorId': mid}
        data = json.dumps(data)
        r = self.server.postContent(url, data=data, headers=self.server.timelineHeaders)
        return r.json()

    def listLike(self, mid, contentId, likeId=None, updatedTime=None):
        params = {
            'homeId': mid,
            'contentId': contentId
        }
        if updatedTime != None:
            params["updatedTime"] = updatedTime
        if likeId != None:
            params["likeId"] = likeId

        header = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': "GET"
        })
        url = self.server.urlEncode(self.LineLegyDomain, '/mh/api/v41/like/getList.json', params)
        r = self.server.postContent(url, headers=header)
        return r.json()

    @loggedIn
    def feedPostLike(self, mid):
        home = self.getHomeProfile(mid)
        likeType = [1001,1002,1003,1004,1005,1006]
        if 'feeds' in home['result']:
            for feed in home['result']['feeds']:
                homeId = feed['post']['postInfo']['homeId']
                postId = feed['post']['postInfo']['postId']
                self.likePost(homeId, postId, likeType=random.choice(likeType))
            return f" 「 Post 」\nType : Liked♪\nName : {self.getContact(mid).displayName}\n • Success liked all post."
        else:
            return f" 「 Post 」\nType : Liked♪\nName : {self.getContact(mid).displayName}\n • Failed, post target not found."
    
    @loggedIn
    def getGroupPost(self, mid, postLimit=10, commentLimit=1, likeLimit=1):
        params = {'homeId': mid, 'commentLimit': commentLimit, 'likeLimit': likeLimit, 'sourceType': 'TALKROOM'}
        url = self.server.urlEncode(self.LineLegyDomain, '/mh/api/54/post/list.json', params)
        r = self.server.getContent(url, headers=self.server.timelineHeaders)
        return r.json()

    """
        Chat Post
    """
 
    @loggedIn
    def createChatPostV2(self, to, text, holdingTime=None, textMeta=[]):
        params = {'homeId': to, 'sourceType': 'GROUPHOME'}
        url = self.server.urlEncode(self.LineLegyDomain, '/mh/api/v39/post/create.json', params)
        payload = {'postInfo': {'readPermission': {'type': 'ALL'}}, 'sourceType': 'GROUPHOME', 'contents': {'text': text,'textMeta':textMeta}}
        if holdingTime != None:
            payload["postInfo"]["holdingTime"] = holdingTime
        data = json.dumps(payload)
        r = self.server.postContent(url, data=data, headers=self.server.timelineHeaders)
        return r.json()
  
    @loggedIn
    def searchNote(self, mid, text):
        data = {
           "query" : text,
           "queryType" : "TEXT",
           "homeId" : mid,
           "postLimit" : 20,
           "commandId" : 16,
           "channelId" : "1341209850",
           "commandType" : 188259
        }
        url = self.server.urlEncode(
            'https://gwz.line.naver.jp/mh',
            '/api/v46/search/note.json',
            {}
        )
        r = self.server.postContent(url, headers=self.server.timelineHeaders, data=json.dumps(data))
        res = r.json()
        return res["result"]["feeds"]
  
    @loggedIn
    def getGroupAlbum(self, mid):
        params = {'homeId': mid, 'type': 'g', 'sourceType': 'TALKROOM'}
        url = self.server.urlEncode('https://ga2.line.naver.jp/mh', '/album/v3/albums.json', params)
        r = self.server.getContent(url, headers=self.server.timelineHeaders)
        return r.json()

    @loggedIn
    def getAlbumImages(self, mid, albumId):
        params = {'homeId': mid}  
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': 'GET',
            'content-type': "application/json",
        })
        url = self.server.urlEncode('https://gwz.line.naver.jp/ext/album', '/api/v3/photos/%s' % albumId, params)
        r = self.server.postContent(url, headers=hr)
        return r.json()   

    @loggedIn
    def genObjectId(self):
        random.seed = (os.urandom(1024))
        return ''.join(random.choice("abcdef1234567890") for i in range(32))

    """
        Story
    """

    @loggedIn
    def getStory(self, mid=None):
        if mid == None:
            mid = self.profile.mid
        params = {"userMid": mid}
        url = self.server.urlEncode('https://ga2.line.naver.jp', '/st/api/v6/story')
        result = self.server.postContent(url, data=json.dumps(params), headers=self.server.timelineHeaders).json()
        return result

    @loggedIn
    def getRecentStoryV2(self):
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'x-lhm': 'POST',
            'content-type': "application/json"
        })
        r = self.server.postContent(self.LineHostDomain + '/st/api/v6/story', data=data, headers=hr)
        return r.json()

    @loggedIn
    def getStoryMedia(self, to, mid):
        story = self.getStory(mid)
        listnya = []
        if story['message'] == 'success':
            if story['result']['contents']:
                for content in story['result']['contents']:
                    if content['media'][0]['mediaType'] == 'IMAGE':
                        path = 'https://obs.line-scdn.net/' + content['media'][0]['hash']
                        listnya.append({"type":"IMAGE", "url":path})
                    if content['media'][0]['mediaType'] == 'VIDEO':
                        path = 'https://obs.line-scdn.net/' + content['media'][0]['hash']
                        listnya.append({"type":"VIDEO", "url":path})
        print(listnya)
        return listnya

    @loggedIn
    def getLikeStory(self, mid):
        story = self.getStory(mid)
        displayName = self.getContact(mid).displayName
        likeType = [1001, 1002, 1003, 1004, 1005, 1006]
        if story['message'] == 'success':
            if story['result']['contents']:
                for content in story['result']['contents']:
                    self.likeStory(content['contentId'], random.choice(likeType))
                return f' 「 Story 」\nType : Liked♪\nName : {displayName}\n • Success liked all story.'
            else:
                return f' 「 Story 」\nType : Comment♪\nName : {displayName}\n • Failed, story does not exist.'

    @loggedIn
    def getCommentStory(self, mid, text=None):
        story = self.getStory(mid)
        displayName = self.getContact(mid).displayName
        if story['message'] == 'success':
            if story['result']['contents']:
                for content in story['result']['contents']:
                    self.commentStory(mid, content['contentId'], text)
                return f' 「 Story 」\nType : Comment♪\nName : {displayName}\n • Success comment story.'
            else:
                return f' 「 Story 」\nType : Comment♪\nName : {displayName}\n • Failed, story does not exist.'

    @loggedIn
    def getContentStory(self, contentId=None):
        if contentId == None:
            raise Exception('contentId is required.')
        params = {"contentId": contentId}
        return self.server.postContent(self.LineHostDomain + '/st/api/v6/story/content', data=json.dumps(params), headers=self.server.timelineHeaders).json()

    @loggedIn
    def readStory(self, mid=None, contentId=None):
        if not isinstance(mid and contentId, str):
            raise Exception('mid and contentId is required.')
        params = {"userMid": mid, "contentId": contentId, "createdTime": int(time.time()), "tsId":"", "friendType":""}
        return self.server.postContent(self.LineHostDomain + '/st/api/v6/story/content/read', data=json.dumps(params), headers=self.server.timelineHeaders).json()

    @loggedIn
    def likeStory(self, contentId, likeType: int):
        liked = [1001, 1002, 1003, 1004, 1005, 1006]
        if likeType not in liked:
            raise Exception ('Whats type like huh?')
        params = {"tsId": "", "contentId": contentId, "like": True, "likeType": str(likeType)}
        return self.server.postContent(self.LineHostDomain + '/st/api/v6/story/content/like', data=json.dumps(params), headers=self.server.timelineHeaders).json()

    @loggedIn
    def commentStory(self, mid=None, contentId=None, text=None):
        if not isinstance(mid and contentId, str):
            raise Exception('mid and contentId is required.')
        if text == None:
            text = 'Auto comment by DeadLine™'
        params = {"to":{"userMid": mid, "friendType": "","tsId": ""}, "contentId": contentId, "message": text}
        return self.server.postContent(self.LineHostDomain + '/st/api/v6/story/message/send', data=json.dumps(params), headers=self.server.timelineHeaders).json()

    @loggedIn
    def getRecentStory(self):
        params = {"lastRequestTime": int(time.time()), "lastTimelineVisitTime": int(time.time())}
        return self.server.postContent(self.LineHostDomain + '/st/api/v6/story/recentstory/list', headers = self.server.timelineHeaders, data = json.dumps(params)).json()

    @loggedIn
    def getViewerStoryList(self, contentId=None):
        if not isinstance(contentId, str):
            raise Exception('contentId is required.')
        params = {"contentId": contentId, "size": 20}
        return self.server.postContent(self.LineHostDomain + '/st/api/v6/story/content/viewer/list', headers = self.server.timelineHeaders, data = json.dumps(params)).json()

    @loggedIn
    def getLikeStoryList(self, contentId = None):
        if not isinstance(contentId, str):
            raise Exception('contentId is required.')
        params = {"userMid": self.profile.mid, "include": "MERGED", "contentId": contentId, "size":20}
        return self.server.postContent(self.LineHostDomain + '/st/api/v6/story/content/like/list', headers = self.server.timelineHeaders, data = json.dumps(params)).json()

    @loggedIn
    def updateStory(self, objId=None, obsHash=None, mediaType='image'):
        if not isinstance(objId and obsHash, str):
            raise Exception('You have to upload and get the x-obs-oid & x-obs-hash')
        params = {"content": {"sourceType": "USER", "contentType": "USER", "media":[{"oid": objId, "service": "story", "sid": "st", "hash": obsHash, "mediaType": mediaType.upper()}]},"shareInfo":{"shareType": "FRIEND"}}
        self.server.timelineHeaders.update({'X-Line-BDBTemplateVersion': 'v1'})
        result = self.server.postContent('https://ga2s.line.naver.jp/st/api/v6/story/content/create', headers = self.server.timelineHeaders, data=json.dumps(params)).json()
        print(result)
        return result
