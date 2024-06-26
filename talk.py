# -*- coding: utf-8 -*-
from akad.ttypes import *
from random import randint
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date
import json, ntpath, humanize, traceback, os, subprocess
import time,random,sys,json,requests,os,subprocess,re,ast,traceback,humanize,threading,base64
#ifrom tmp.MySplit import MySplit
#from MySplit import MySplit

def loggedIn(func):
    def checkLogin(*args, **kwargs):
        if args[0].isLogin:
            return func(*args, **kwargs)
        else:
            args[0].callback.other('You want to call the function, you must login to LINE')
    return checkLogin

class Talk(object):
    isLogin = False
    _messageReq = {}
    _unsendMessageReq = 0


    def __init__(self):
        self.isLogin = True

    """Liff"""
        
    @loggedIn
    def issueLiffView(self, request):
        return self.liff.issueLiffView(request)
        
    @loggedIn
    def revokeToken(self, request):
        return self.liff.revokeToken(request)

    @loggedIn
    def allowLiff(self, token, app_name, ch_id):
        # Copyright by https://github.com/RynKings
        data = {'on': ['P', 'CM'], 'off': []}
        headers = {
            'X-Line-Access': token,
            'X-Line-Application': app_name,
            'X-Line-ChannelId': ch_id,
            'Content-Type': 'application/json'
        }
        r = requests.post("https://access.line.me/dialog/api/permissions", headers=headers, data=json.dumps(data))
        return r.json()

    """User"""

    @loggedIn
    def acquireEncryptedAccessToken(self, featureType=2):
        return self.talk.acquireEncryptedAccessToken(featureType)

    @loggedIn
    def getProfile(self, syncReason=3):
        return self.talk.getProfile(syncReason)

    @loggedIn
    def getSettings(self, syncReason=3):
        return self.talk.getSettings(syncReason)

    @loggedIn
    def getSettingsAttributes2(self, attributesToRetrieve):
        return self.talk.getSettingsAttributes2(attributesToRetrieve)

    @loggedIn
    def updateSettingsAttributes2(self, settings, attributesToUpdate):
        return self.talk.updateSettingsAttributes2(0, settings, attributesToUpdate)

    @loggedIn
    def updateSettingsE2EE(self):
        clientSettings = self.getSettings()
        if clientSettings.e2eeEnable == True:
            clientSettings.e2eeEnable = False
            self.updateSettingsAttributes2(clientSettings, {33})

    @loggedIn
    def notificationMute(self, typeVar=True):
        clientSettings = self.getSettings()
        clientSettings.notificationDisabledWithSub = typeVar
        self.updateSettingsAttributes2(clientSettings, {16})
        return typeVar

    @loggedIn
    def notificationMuteExpiration(self):
        clientSettings = self.getSettings()
        clientSettings.notificationMuteExpiration = 0
        self.updateSettingsAttributes2(clientSettings, {1})
        clientSettings.notificationDisabledWithSub = False
        self.updateSettingsAttributes2(clientSettings, {16})

    @loggedIn
    def privacyReceiveMessages(self, type):
        if type == 'on':
            clientSettings = self.getSettings()
            clientSettings.privacyReceiveMessagesFromNotFriend = False
            self.updateSettingsAttributes2(clientSettings, {25})
        if type == 'off':
            clientSettings = self.getSettings()
            clientSettings.privacyReceiveMessagesFromNotFriend = True
            self.updateSettingsAttributes2(clientSettings, {25})

    @loggedIn
    def setNotificationsEnabled(self, type, target, enablement):
        return self.talk.setNotificationsEnabled(0, type, target, enablement)

    @loggedIn
    def getUserTicket(self):
        return self.talk.getUserTicket()

    @loggedIn
    def updateProfile(self, profileObject):
        return self.talk.updateProfile(0, profileObject)

    @loggedIn
    def updateSettings2(self, settingObject):
        return self.talk.updateSettings2(0, settingObject)

    @loggedIn
    def updateProfileAttribute(self, attrId, value):
        return self.talk.updateProfileAttribute(0, attrId, value)

    """Operation"""

    @loggedIn
    def fetchOps(self):
        return self.poll.fetchOps(self.localRev,15,self.globalRev,self.individualRev)


    @loggedIn
    def fetchOperation(self, revision, count):
        return self.talk.fetchOperations(revision, count)

    @loggedIn
    def getLastOpRevision(self):
        return self.talk.getLastOpRevision()

    @loggedIn
    def registerUserid(self, line_id):
       return self.talk.registerUserid(0,line_id)

    """Message"""

    @loggedIn
    def sendLocation(self, to, location, contentMetadata={}, contentType=15):
        msg = Message()
        msg.to = to
        msg.location = location
        msg.contentType, msg.contentMetadata = contentType, contentMetadata
        if to not in self._messageReq:
            self._messageReq[to] = -1
        self._messageReq[to] += 1
        return self.talk.sendMessage(self._messageReq[to], msg)

    @loggedIn
    def sendMusic(self, to, text, purl, aurl, stxt, name):
        contentMetadata = {'previewUrl': purl, 'i-installUrl': aurl, 'type': 'mt', 'subText': stxt, 'a-installUrl': aurl, 'a-installUrl': aurl, 'a-packageName': 'com.spotify.music', 'countryCode': 'ID', 'a-linkUri': aurl, 'i-linkUri': aurl, 'id': 'mt000000000a6b79f9', 'text': name, 'linkUri': aurl}
        contentType = 19
        return self.sendMessage(to, text, contentMetadata, contentType)

    @loggedIn
    def sendMessageMusic(self, to, title=None, subText=None, url=None, iconurl=None, contentMetadata={}):
        """
        a : Android
        i : Ios
        """
        self.profile = self.getProfile()
        self.userTicket = self.generateUserTicket()
        title = title if title else 'LINE MUSIC'
        subText = subText if subText else self.profile.displayName
        url = url if url else 'line://ti/p/' + self.userTicket
        iconurl = iconurl if iconurl else 'https://obs.line-apps.com/os/p/%s' % self.profile.mid
        msg = Message()
        msg.to, msg._from = to, self.profile.mid
        msg.text = title
        msg.contentType = 19
        msg.contentMetadata = {
            'text': title,
            'subText': subText,
            'a-installUrl': url,
            'i-installUrl': url,
            'a-linkUri': url,
            'i-linkUri': url,
            'linkUri': url,
            'previewUrl': iconurl,
            'type': 'mt',
            'a-packageName': 'com.spotify.music',
            'countryCode': 'JP',
            'id': 'mt000000000a6b79f9'
        }
        if contentMetadata:
            msg.contentMetadata.update(contentMetadata)
        if to not in self._messageReq:
            self._messageReq[to] = -1
        self._messageReq[to] += 1
        return self.talk.sendMessage(self._messageReq[to], msg)        

    @loggedIn
    #loggedIn
    def sendMessageCustom(to, text, name , icon):
        annda = {'MSG_SENDER_ICON': icon,
            'MSG_SENDER_NAME':  name,
            'text': ''
       }
        #text = ""
        client.sendMessage(to, text, contentMetadata=annda)
    @loggedIn
    def generateReplyMessage(self, relatedMessageId):
        msg = Message()
        msg.relatedMessageServiceCode = 1
        msg.messageRelationType = 3
        msg.relatedMessageId = str(relatedMessageId)
        return msg

    @loggedIn
    def sendMentionWithReply(self, msg_id, to, text="", mids=[], isUnicode=False):
        arrData = ""
        arr = []
        mention = "@zeroxyuuki "
        if mids == []:
            raise Exception("Invalid mids")
        if "@!" in text:
            if text.count("@!") != len(mids):
                raise Exception("Invalid mids")
            texts = text.split("@!")
            textx = ""
            unicode = ""
            if isUnicode:
                for mid in mids:
                    unicode += str(texts[mids.index(mid)].encode('unicode-escape'))
                    textx += str(texts[mids.index(mid)])
                    slen = len(textx) if unicode == textx else len(textx) + unicode.count('U0')
                    elen = len(textx) + 15
                    arrData = {'S':str(slen), 'E':str(elen - 4), 'M':mid}
                    arr.append(arrData)
                    textx += mention
            else:
                for mid in mids:
                    textx += str(texts[mids.index(mid)])
                    slen = len(textx)
                    elen = len(textx) + 15
                    arrData = {'S':str(slen), 'E':str(elen - 4), 'M':mid}
                    arr.append(arrData)
                    textx += mention
            textx += str(texts[len(mids)])
        else:
            raise Exception("Invalid mention position")
        self.sendReplyMessage(msg_id, to, textx, {'MENTION': str('{"MENTIONEES":' + json.dumps(arr) + '}')}, 0)


    @loggedIn
    def sendMentionV2(self, to, text="", mids=[], isUnicode=False):
        arrData = ""
        arr = []
        mention = "@zeroxyuuki "
        if mids == []:
            raise Exception("Invalid mids")
        if "@!" in text:
            if text.count("@!") != len(mids):
                raise Exception("Invalid mids")
            texts = text.split("@!")
            textx = ""
            unicode = ""
            if isUnicode:
                for mid in mids:
                    unicode += str(texts[mids.index(mid)].encode('unicode-escape'))
                    textx += str(texts[mids.index(mid)])
                    slen = len(textx) if unicode == textx else len(textx) + unicode.count('U0')
                    elen = len(textx) + 15
                    arrData = {'S':str(slen), 'E':str(elen - 4), 'M':mid}
                    arr.append(arrData)
                    textx += mention
            else:
                for mid in mids:
                    textx += str(texts[mids.index(mid)])
                    slen = len(textx)
                    elen = len(textx) + 15
                    arrData = {'S':str(slen), 'E':str(elen - 4), 'M':mid}
                    arr.append(arrData)
                    textx += mention
            textx += str(texts[len(mids)])
        else:
            raise Exception("Invalid mention position")
        self.sendMessage(to, textx, {'MENTION': str('{"MENTIONEES":' + json.dumps(arr) + '}')}, 0)
    @loggedIn
    def sendReplyMessage(self, relatedMessageId, to, text, contentMetadata={}, contentType=0):
        msg = self.generateReplyMessage(relatedMessageId)
        msg.to = to
        msg.text = text
        msg.contentType = contentType
        msg.contentMetadata = contentMetadata
        if to not in self._messageReq:
            self._messageReq[to] = -1
        self._messageReq[to] += 1
        return self.talk.sendMessage(self._messageReq[to], msg)

    @loggedIn
    def sendReplyImage(self, matId, to, path):
        objectId = self.sendReplyMessage(matId, to=to, text=None, contentType = 1).id
        return self.uploadObjTalk(path=path, type='image', returnAs='objId', objId=objectId)
    
    @loggedIn
    def sendReplyVideo(self, matId, to, path):
        objectId = self.sendReplyMessage(matId, to=to, text=None, contentMetadata={'VIDLEN': '60000','DURATION': '60000'}, contentType = 2).id
        return self.uploadObjTalk(path=path, type='video', returnAs='bool', objId=objectId)

    @loggedIn
    def sendReplyVideoWithURL(self,matId, to, url):
        path = self.downloadFileURL(url, 'path')
        self.sendReplyVideo(matId, to, path)
        return self.deleteFile(path)

    @loggedIn
    def sendReplyImageWithURL(self,matId, to, url):
        path = self.downloadFileURL(url, 'path')
        self.sendReplyImage(matId, to, path)
        return self.deleteFile(path)
        
    @loggedIn
    def sendMessage2(self, to, text, contentMetadata={}, contentType=0):
        msg = Message()
        msg.to, msg._from = to, self.profile.mid
        msg.text = text
        msg.contentType, msg.contentMetadata = contentType, contentMetadata
        if to not in self._messageReq:
            self._messageReq[to] = -1
        self._messageReq[to] += 1
        return self.talk.sendMessage(self._messageReq[to], msg)

    @loggedIn
    def sendMessageaaaa(self, to, text, contentMetadata={}, contentType=0):
        msg = Message()
        msg.to, msg._from = to, self.profile.mid
        msg.text = text
        msg.contentType, msg.contentMetadata = contentType, contentMetadata
        if to not in self._messageReq:
            self._messageReq[to] = -1
        self._messageReq[to] += 1
        return self.talk.sendMessage(self._messageReq[to], msg)
    def sendMessage(self, to, text, contentMetadata={}, contentType=0,msgid=None):
        #msg = self.generateReplyMessage(relatedMessageId)
        msg = Message()
        if 'MENTION' in contentMetadata.keys()!=None:
            try:
                msg.relatedMessageId = str(self.talk.getRecentMessagesV2(to, 10)[0].id)
                msg.relatedMessageServiceCode = 1
                msg.messageRelationType = 3
            except:
                pass
        if msgid != None:
            msg.relatedMessageId = str(msgid)
            msg.relatedMessageServiceCode = 1
            msg.messageRelationType = 3
        msg.to, msg._from = to, self.profile.mid
        if msg._from in ["u5da1a2cc7a64a21997eb846cbd7767a1"]:
            jeda = random.choice([0.3,0.4,0.5,0.6,0.7,0.8])
            time.sleep(jeda)
        msg.text = text
        msg.contentType, msg.contentMetadata = contentType, contentMetadata
        if to not in self._messageReq:
            self._messageReq[to] = -1
        self._messageReq[to] += 1
        return self.talk.sendMessage(self._messageReq[to], msg)

    """ Usage:
        @to Integer
        @text String
        @dataMid List of user Mid
    """
    @loggedIn
    def sendMessages(self, messageObject):
        return self.talk.sendMessage(0, messageObject)

    def giftmessage(self,to):
        a = ("5","7","6","8")
        b = random.choice(a)
        return self.sendMessage(to, text=None, contentMetadata={'PRDTYPE': 'STICKER','STKVER': '1','MSGTPL': b,'STKPKGID': '1380280'}, contentType=9)
    
    def adityarequestweb(self,url):
        r = requests.get("{}".format(url))
        data = r.text
        data = json.loads(data)
        return data
    
    def templatefoot(self,link,AI,AN):
        a={'AGENT_LINK': link,
        'AGENT_ICON': AI,
        'AGENT_NAME': AN}
        return a
    
    def blekedok(self,t:int=None,tt:str=None):
        r = requests.get('https://www.webtoons.com/id/genre')
        soup = BeautifulSoup(r.text,'html5lib')
        data = soup.find_all(class_='card_lst')
        datea = data[t].find_all(class_='info')
        if tt == 'data':
            return datea
        else:
            return data[t].find_all('a')
    
    def getalbum(self, to, wait):
        #to = msg.to
        ha = self.getGroupAlbum(to)
        #msg.text = self.mycmd(msg.text,wait)
        a = [a['title'] for a in ha['result']['items']];c=[a['photoCount'] for a in ha['result']['items']]
        b = '╭「 Album Group 」'
        no=0
        for i in range(len(a)):
            no+=1
            if no == len(a):b+= '\n╰{}. {} | {}'.format(no,a[i],c[i])
            else:b+= '\n│{}. {} | {}'.format(no,a[i],c[i])
        self.sendMessage(to,"{}".format(b))
    
    def adityaarchi(self,wait,sd,dd,ss,split,msg,tex,nama=[]):
        selection = MySplit(split,range(1,len(nama)+1))
        k = len(nama)//20
        for a in range(k+1):
            if a == 0:eto='╭「 '+sd+' 」─'+tex
            else:eto='├「 '+sd+' 」─'+tex
            text = ''
            mids = []
            no = a
            for i in selection.parse()[a*20 : (a+1)*20]:
                mids.append(nama[i-1])
                if dd == 'kick':self.kickoutFromGroup(ss,[nama[i-1]]);hh = ''
                if dd == 'delfriend':
                    try:self.AdityadeleteContact(nama[i-1]);hh = 'Del Friend'
                    except:hh = 'Not Friend User'
                if dd == 'delbl':
                    try:wait['blacklist'].remove(nama[i-1]);hh = 'Del BL'
                    except:hh = 'Not BL User'
                if dd == 'delwl':
                    try:wait['bots'].remove(nama[i-1]);hh = 'Del WL'
                    except:hh = 'Not WL User'
                if dd == 'delml':
                    try:wait['target'].remove(nama[i-1]);hh = 'Del ML'
                    except:hh = 'Not ML User'
                if dd == 'delblock':
                    try:self.unblockContact(nama[i-1]);hh = 'Del Block'
                    except:hh = 'Not Block User'
                if dd == '':hh = ''
                if dd == 'tag':hh = ''
                no+= 1
                if no == len(selection.parse()):text+= "\n╰{}. @! {}".format(i,hh)
                else:text+= "\n│{}. @! {}".format(i,hh)
            if dd == 'tag':self.sendMention(ss,eto+text,sd,mids)
            else:self.sendMention(msg.to,eto+text,sd,mids)
        if dd == 'tag':self.sendMessage(msg.to,'╭「 Mention 」{}\n╰Status: Success tag {} mem'.format(tex,len(nama)-(len(nama)-len(selection.parse()))))
    
    def adityasuperdata(self,to,wait,text='',text1='',data=[]):
        to = to
        key = wait["setkey"].title()
        if data == []:return self.sendMessage(to, "╭───「 {} 」─\n│{}: None\n│    | Command |  \n│Add {}\n│  Key:{} add{} [@]\n│Del {}\n│  Key:{} del{} [@]\n╰──────".format(text,text,text,key,text1,text,key,text1,key,text1))
        self.datamention(to,'{}'.format(text),data)

    def deletefriendnum(self, to, wait, cmd):
        asd = self.refreshContacts()
        selection = MySplit(self.adityasplittext(cmd,'s'),range(1,len(asd)+1))
        k = len(asd)//20
        d = []
        for c in selection.parse():
            d.append(asd[int(c)-1])
        self.sendMessage(to,' 「 Friendlist 」\nWaiting.....')
        for a in range(k+1):
            if a == 0:self.mentionmention(to=to,wait=wait,text='',dataMid=d[:20],pl=-0,ps='╭「 Friendlist 」─\n├ Type: Delete Friendlist',pg='DELFL',pt=d)
            else:self.mentionmention(to=to,wait=wait,text='',dataMid=d[a*20 : (a+1)*20],pl=a*20,ps='├「 Friendlist 」─\n├ Type: Delete Friendlist',pg='DELFL',pt=d)
    def getalbum2(self, to, text, wait):
        #to = msg.to
        ha = self.getGroupAlbum(to)
        a = [a['title'] for a in ha['result']['items']];c=[a['photoCount'] for a in ha['result']['items']]
        a = text.split(' ')
        selection = MySplit(a[3],range(1,len(ha['result']['items'])+1))
        for i in selection.parse():
            try:
                b = random.randint(0,999)
                self.getImageGroupAlbum(to,ha['result']['items'][int(a[2])-1]['id'], ha['result']['items'][int(a[2])-1]['recentPhotos'][i-1]['oid'], returnAs='path', saveAs='{}.png'.format(b))
                self.sendImage(to,'{}.png'.format(b))
                os.remove('{}.png'.format(b))
            except:continue
    def getinformation(self,to,mid,data):
        try:
            if mid in data["bots"]:a = "Whitelisted: Yes"
            else:a = "Whitelisted: No"
            if mid in data["blacklist"]:b = "Blacklisted: Yes"
            else:b = "Blacklisted: No"
            h = self.getContact(mid).statusMessage
            if h == '':hh = '\n'
            else:hh = "Status:\n" + h + "\n\n"
            zxc = " 「 ID 」\nName: @!\n" + hh + "User ID:\n" + mid + "\n"+a+" "+b
            self.sendMention(to, zxc, '',[mid])
            self.sendContact(to,mid)
        except:
            ginfo = self.getCompactGroup(mid)
            try:
                gCreators = ginfo.creator.mid;gtime = ginfo.createdTime
            except:
                gCreators = ginfo.members[0].mid;gtime = ginfo.createdTime
            if ginfo.invitee is None:
                sinvitee = "0"
            else:
                sinvitee = str(len(ginfo.invitee))
            if ginfo.preventedJoinByTicket == True:u = "Disable"
            else:u = "line://ti/g/" + self.reissueGroupTicket(mid)
            zxc = " 「 ID 」\nGroup Name:\n{}\n\nGroup ID:\n{}\n\nAnggota: {}\nInvitation: {}\nTicket:{}\n\nCreated at:\n{}\nby @!".format(ginfo.name,mid,len(ginfo.members),sinvitee,u,humanize.naturaltime(datetime.fromtimestamp(gtime/1000)))
            self.sendMention(to,zxc,'',[gCreators])
            self.sendContact(to,gCreators)
        
    def sendMention(self,to, text="",ps='', mids=[]):
        arrData = ""
        arr = []
        mention = "@MinzTeamBot "
        if mids == []:
            raise Exception("Invalid mids")
        if "@!" in text:
            if text.count("@!") != len(mids):
                raise Exception("Invalid mids")
            texts = text.split("@!")
            textx = ''
            h = ''
            for mid in range(len(mids)):
                h+= str(texts[mid].encode('unicode-escape'))
                textx += str(texts[mid])
                if h != textx:slen = len(textx)+h.count('U0');elen = len(textx)+h.count('U0') + 13
                else:slen = len(textx);elen = len(textx) + 13
                arrData = {'S':str(slen), 'E':str(elen), 'M':mids[mid]}
                arr.append(arrData)
                textx += mention
            textx += str(texts[len(mids)])
        else:
            textx = ''
            slen = len(textx)
            elen = len(textx) + 18
            arrData = {'S':str(slen), 'E':str(elen - 4), 'M':mids[0]}
            arr.append(arrData)
            textx += mention + str(text)
        try:
            try:
                if 'kolori' in ps:contact = self.getContact(ps.split('##')[1])
                else:contact = self.getContact(to)
                cu = "http://profile.line-cdn.net/" + contact.pictureStatus
                cc = str(contact.displayName)
            except Exception as e:
                cdb = self.getContact(self.profile.mid)
                cc = str(cdb.displayName)
                cu = "http://profile.line-cdn.net/" + cdb.pictureStatus
            self.sendMessage(to, textx, {'AGENT_LINK': "line://app/1602687308-DgedGk9A?type=fotext&text=I'm%20RhyN",'AGENT_ICON': "http://dl.profile.line-cdn.net/" + self.getProfile().picturePath,'AGENT_NAME':ps,'MSG_SENDER_ICON':cu,'MSG_SENDER_NAME':cc,'MENTION': str('{"MENTIONEES":' + json.dumps(arr) + '}')}, 0)
        except:
            try:
                self.sendMessage(to, textx, {'AGENT_LINK': "line://app/1602687308-DgedGk9A?type=fotext&text=I'm%20RhyN",'AGENT_ICON': "http://dl.profile.line-cdn.net/" + self.getProfile().picturePath,'MSG_SENDER_NAME': self.getContact(to).displayName,'MSG_SENDER_ICON': 'http://dl.profile.line-cdn.net/' + self.getContact(to).pictureStatus,'MENTION': str('{"MENTIONEES":' + json.dumps(arr) + '}')}, 0)
            except:
                try:
                    self.sendMessage(to, textx, {'AGENT_LINK': "line://app/1602687308-DgedGk9A?type=fotext&text=I'm%20RhyN",'AGENT_ICON': "http://dl.profile.line-cdn.net/" + self.getProfile().picturePath,'MSG_SENDER_NAME': self.getContact("u085311ecd9e3e3d74ae4c9f5437cbcb5").displayName,'MSG_SENDER_ICON': 'http://dl.profile.line-cdn.net/' + self.getContact("u085311ecd9e3e3d74ae4c9f5437cbcb5").pictureStatus,'MENTION': str('{"MENTIONEES":' + json.dumps(arr) + '}')}, 0)
                except:
                    self.sendMessage(to, textx, {'AGENT_LINK': "line://app/1602687308-DgedGk9A?type=fotext&text=I'm%20RhyN",'AGENT_ICON': "http://dl.profile.line-cdn.net/" + self.getProfile().picturePath,'AGENT_NAME':ps,'MENTION': str('{"MENTIONEES":' + json.dumps(arr) + '}')}, 0)

    def sendMention2(self,to, text="",ps='', mids=[]):
        arrData = ""
        arr = []
        mention = "@MinzTeamBot "
        if mids == []:
            raise Exception("Invalid mids")
        if "@!" in text:
            if text.count("@!") != len(mids):
                raise Exception("Invalid mids")
            texts = text.split("@!")
            textx = ''
            h = ''
            for mid in range(len(mids)):
                h+= str(texts[mid].encode('unicode-escape'))
                textx += str(texts[mid])
                if h != textx:slen = len(textx)+h.count('U0');elen = len(textx)+h.count('U0') + 13
                else:slen = len(textx);elen = len(textx) + 13
                arrData = {'S':str(slen), 'E':str(elen), 'M':mids[mid]}
                arr.append(arrData)
                textx += mention
            textx += str(texts[len(mids)])
        else:
            textx = ''
            slen = len(textx)
            elen = len(textx) + 18
            arrData = {'S':str(slen), 'E':str(elen - 4), 'M':mids[0]}
            arr.append(arrData)
            textx += mention + str(text)
        self.sendMessage(to, textx, {'AGENT_LINK': 'line://ti/p/~{}'.format(self.profile.userid),'AGENT_ICON': "http://dl.profile.line-cdn.net/" + self.getProfile().picturePath,'AGENT_NAME': ps,'MENTION': str('{"MENTIONEES":' + json.dumps(arr) + '}')}, 0)
    
    def image_search(self, query):
        query = query.replace(' ', "%20")
        url = "https://www.google.com/search?hl=en&site=imghp&tbm=isch&tbs=isz:l&q=" + query
        mozhdr = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36"}
        req = requests.get(url, headers = mozhdr)
        soupeddata = BeautifulSoup(req.content , "lxml")
        images = soupeddata.find_all("div", {"class": "rg_meta notranslate"})
        aa = random.randint(0,len(images))
        try:
            images = json.loads(images[aa].text)
            return images
        except Exception as e:return e
    
    def forward(self, to):
        if msg.toType == 2:to = msg.to
        else:to = msg._from
        if msg.contentType == 1:
            try:
                if msg.contentMetadata != {}:
                    path = self.downloadObjectMsg(msg.id,'path','dataSeen/m.gif',True)
                    a = threading.Thread(target=self.sendGIF, args=(to,path,)).start()
            except:self.sendImageWithURL(to,'https://obs-sg.line-apps.com/talk/m/download.nhn?oid='+msg.id)
        if msg.contentType == 2:self.sendVideoWithURL(to,'https://obs-sg.line-apps.com/talk/m/download.nhn?oid='+msg.id)
        if msg.contentType == 3:self.sendAudioWithURL(to,'https://obs-sg.line-apps.com/talk/m/download.nhn?oid='+msg.id)
    
    def limitlimit(self,to,wait):
        try:
            if to in wait['talkblacklist']['tos']:
                if wait['talkblacklist']['tos'][to]["expire"] == True:
                    return
                elif time.time() - wait['talkblacklist']['tos'][to]["time"] <= 5:
                    wait['talkblacklist']['tos'][to]["flood"] += 1
                    if wait['talkblacklist']['tos'][to]["flood"] >= 15:
                        wait['talkblacklist']['tos'][to]["flood"] = 0
                        wait['talkblacklist']['tos'][to]["expire"] = True
                        self.sendMessage(to, " 「 FLOOD 」\nFLOOD DETECT, I will mute on 30second in this room")
                else:
                    wait['talkblacklist']['tos'][to]["flood"] = 0
                    wait['talkblacklist']['tos'][to]["time"] = time.time()
            else:
                wait['talkblacklist']['tos'][to] = {"time": time.time(),"flood": 0,"expire": False}
        except:wait['talkblacklist']['tos'] = {}
    
    def templatefoot(self,link,AI,AN):
        a={'AGENT_LINK': link,
        'AGENT_ICON': AI,
        'AGENT_NAME': AN}
        return a
    
    def datamention(self, to, text, data, ps=''):
        if(data == [] or data == {}):return self.sendMention(to," 「 {} 」\nSorry @! I can't found maybe empty".format(text),text,[msg._from])
        k = len(data)//20
        for aa in range(k+1):
            if aa == 0:dd = '╭「 {} 」─{}'.format(text,ps);no=aa
            else:dd = '├「 {} 」─{}'.format(text,ps);no=aa*20
            msgas = dd
            for i in data[aa*20 : (aa+1)*20]:
                no+=1
                if no == len(data):msgas+='\n╰{}. @!'.format(no)
                else:msgas+='\n│{}. @!'.format(no)
            self.sendMention(to, msgas,' 「 {} 」'.format(text), data[aa*20 : (aa+1)*20])
    
    def datamentions(self, to, text, data, date, wait, ps=''):
        if(data == [] or data == {}):return self.sendMention(to," 「 {} 」\nSorry @! I can't found maybe empty".format(text),text,[msg._from])
        k = len(data)//20
        for aa in range(k+1):
            if aa == 0:dd = '╭「 {} 」─{}'.format(text,ps);no=aa
            else:dd = '├「 {} 」─{}'.format(text,ps);no=aa*20
            msgas = dd
            for i in data[aa*20 : (aa+1)*20]:
                no+=1
                if date == 'ADDWL':
                    if i in wait["bots"]:a = 'WL User'
                    else:
                        if i not in wait["blacklist"]:a = 'Add WL';wait["bots"].append(i)
                        else:a = 'BL User'
                if date == 'DELWL':
                    try:wait["bots"].remove(i);a = 'Del WL'
                    except:a = 'Not WL User'
                if date == 'ADDBL':
                    if i in wait["bots"]:a = 'WL User'
                    else:
                        if i not in wait["blacklist"]:a = 'Add BL';wait["blacklist"].append(i)
                        else:a = 'BL User'
                if date == 'DELBL':
                    try:wait["blacklist"].remove(i);a = 'Del BL'
                    except:a = 'Not BL User'
                if date == 'DELFL':
                    try:self.AdityadeleteContact(i);a = 'Del Friend'
                    except:a = 'Not Friend User'
                if no == len(data):msgas+='\n╰{}. @!{}'.format(no,a)
                else:msgas+='\n│{}. @!{}'.format(no,a)
            self.sendMention(to, msgas,' 「 {} 」'.format(text), data[aa*20 : (aa+1)*20])

    def waktunjir(self):
        sd = ''
        if datetime.now().hour > 1 and datetime.now().hour <10:sd+= 'Good Morning'
        if datetime.now().hour > 10 and datetime.now().hour <15:sd+= 'Good Afternoon'
        if datetime.now().hour > 15 and datetime.now().hour <18:sd+= 'Good Evening'
        if datetime.now().hour >= 18:sd+= 'Good Night'
        return sd
    def unsend2(self, to, wait):
        try:
            if msg.to not in wait['Unsend']:
                wait['Unsend'][msg.to] = {'B':[]}
            if msg._from not in [self.profile.mid]:
                return
            wait['Unsend'][msg.to]['B'].append(msg.id)
        except:pass
    
    def adityasplittext(self,text,lp=''):
        separate = text.split(" ")
        if lp == '':adalah = text.replace(separate[0]+" ","")
        elif lp == 's':adalah = text.replace(separate[0]+" "+separate[1]+" ","")
        else:adalah = text.replace(separate[0]+" "+separate[1]+" "+separate[2]+" ","")
        return adalah
    
    def mycmd(self,text,wait):
        cmd = ''
        pesan = text.lower()
        if wait['setkey'] != '':
            if pesan.startswith(wait['setkey']):
                cmd = pesan.replace(wait['setkey']+' ','').replace(wait['setkey'],'')
        else:
            cmd = text
        return cmd
    
    def mentionmention(self, to, wait, text, dataMid=[], pl='', ps='', pg='', pt=[]):
        arr = []
        list_text=ps
        i=0
        no=pl
        if pg == 'MENTIONALLUNSED':
            for l in dataMid:
                no+=1
                if no == len(pt):list_text+='\n╰'+str(no)+'. @[RhyN-'+str(i)+'] '
                else:list_text+='\n│'+str(no)+'. @[RhyN-'+str(i)+'] '
                i=i+1
            text=list_text+text
        if pg == 'SIDERMES':
            for l in dataMid:
                chiya = []
            for rom in wait["lurkt"][to][dataMid[0]].items():
                chiya.append(rom[1])
            for b in chiya:
                a = '{}'.format(humanize.naturaltime(datetime.fromtimestamp(b/1000)))
                no+=1
                if no == len(pt):list_text+='\n│'+str(no)+'. @[RhyN-'+str(i)+']\n╰    「 '+a+" 」"
                else:list_text+='\n│'+str(no)+'. @[RhyN-'+str(i)+']\n│    「 '+a+" 」"
                i=i+1
            text=list_text+text
        if pg == 'DELFL':
            for l in dataMid:
                try:
                    self.deleteContact(l)
                    a = 'Del Friend'
                except:
                    a = 'Not Friend User'
                no+=1
                if no == len(pt):list_text+='\n╰'+str(no)+'. @[RhyN-'+str(i)+'] '+a
                else:list_text+='\n│'+str(no)+'. @[RhyN-'+str(i)+'] '+a
                i=i+1
            text=text+list_text
        if pg == 'DELML':
            for l in dataMid:
                if l not in settings["mimic"]["target"]:
                    a = 'Not ML User'
                else:
                    a = 'DEL ML'
                    settings["mimic"]["target"].remove(l)
                no+=1
                if no == len(pt):list_text+='\n╰'+str(no)+'. @[RhyN-'+str(i)+'] '+a
                else:list_text+='\n│'+str(no)+'. @[RhyN-'+str(i)+'] '+a
                i=i+1
            text=list_text
        i=0
        for l in dataMid:
            mid=l
            name='@[RhyN-'+str(i)+']'
            ln_text=text.replace('\n',' ')
            if ln_text.find(name):
                line_s=int( ln_text.index(name) )
                line_e=(int(line_s)+int( len(name) ))
            arrData={'S': str(line_s), 'E': str(line_e), 'M': mid}
            arr.append(arrData)
            i=i+1
        contentMetadata={'MENTION':str('{"MENTIONEES":' + json.dumps(arr).replace(' ','') + '}')}
        if pg == 'MENTIONALLUNSED':self.unsendMessage(self.sendMessage(to, text, contentMetadata).id)
        else:self.sendMessage(to, text, contentMetadata)
    
    @loggedIn
    def sendSticker(self, to, packageId, stickerId):
        contentMetadata = {
            'STKVER': '100',
            'STKPKGID': packageId,
            'STKID': stickerId
        }
        return self.sendMessage(to, '', contentMetadata, 7)
        
    @loggedIn
    def sendContact(self, to, mid):
        contentMetadata = {'mid': mid}
        return self.sendMessage(to, '', contentMetadata, 13)

    @loggedIn
    def sendGift(self, to, productId, productType):
        if productType not in ['theme','sticker']:
            raise Exception('Invalid productType value')
        contentMetadata = {
            'MSGTPL': str(randint(0, 12)),
            'PRDTYPE': productType.upper(),
            'STKPKGID' if productType == 'sticker' else 'PRDID': productId
        }
        return self.sendMessage(to, '', contentMetadata, 9)

    @loggedIn
    def zalgofy(self, tomid, text):
        M = Message()
        M.to = tomid
        t1 = "\xf4\x80\xb0\x82\xf4\x80\xb0\x82\xf4\x80\xb0\x82\xf4\x80\xb0\x82\xf4\x80\xa0\x81\xf4\x80\xa0\x81\xf4\x80\xa0\x81"
        t2 = "\xf4\x80\x82\xb3\xf4\x8f\xbf\xbf"
        rst = t1 + text + t2
        M.text = rst.replace("\n", " ")
        return self.talk.sendMessage(0, M)

    @loggedIn
    def mainsplit(self,text,lp=''):
        separate = text.split(" ")
        if lp == '':adalah = text.replace(separate[0]+" ","")
        elif lp == 's':adalah = text.replace(separate[0]+" "+separate[1]+" ","")
        else:adalah = text.replace(separate[0]+" "+separate[1]+" "+separate[2]+" ","")
        return adalah
        
    @loggedIn
    def sendMessageAwaitCommit(self, to, text, contentMetadata={}, contentType=0):
        msg = Message()
        msg.to, msg._from = to, self.profile.mid
        msg.text = text
        msg.contentType, msg.contentMetadata = contentType, contentMetadata
        if to not in self._messageReq:
            self._messageReq[to] = -1
        self._messageReq[to] += 1
        return self.talk.sendMessageAwaitCommit(self._messageReq[to], msg)

    @loggedIn
    def unsendMessage(self, messageId):
        self._unsendMessageReq += 1
        return self.talk.unsendMessage(self._unsendMessageReq, messageId)

    @loggedIn
    def requestResendMessage(self, senderMid, messageId):
        return self.talk.requestResendMessage(0, senderMid, messageId)

    @loggedIn
    def respondResendMessage(self, receiverMid, originalMessageId, resendMessage, errorCode):
        return self.talk.respondResendMessage(0, receiverMid, originalMessageId, resendMessage, errorCode)

    @loggedIn
    def removeMessage(self, messageId):
        return self.talk.removeMessage(messageId)
    
    @loggedIn
    def removeAllMessages(self, lastMessageId):
        return self.talk.removeAllMessages(0, lastMessageId)

    @loggedIn
    def removeMessageFromMyHome(self, messageId):
        return self.talk.removeMessageFromMyHome(messageId)

    @loggedIn
    def destroyMessage(self, chatId, messageId):
        return self.talk.destroyMessage(0, chatId, messageId, sessionId)
    
    @loggedIn
    def sendChatChecked(self, consumer, messageId):
        return self.talk.sendChatChecked(0, consumer, messageId)

    @loggedIn
    def sendEvent(self, messageObject):
        return self.talk.sendEvent(0, messageObject)

    @loggedIn
    def getLastReadMessageIds(self, chatId):
        return self.talk.getLastReadMessageIds(0, chatId)

    @loggedIn
    def getPreviousMessagesV2WithReadCount(self, messageBoxId, endMessageId, messagesCount=50):
        return self.talk.getPreviousMessagesV2WithReadCount(messageBoxId, endMessageId, messagesCount)

    @loggedIn
    def getRecentMessagesV2(self, messageBoxId, messagesCount):
        return self.talk.getRecentMessagesV2(messageBoxId, messagesCount)

    """Object"""

    @loggedIn
    def sendImage(self, to, path):
        objectId = self.sendMessage(to=to, text=None, contentType = 1).id
        return self.uploadObjTalk(path=path, type='image', returnAs='bool', objId=objectId)

    @loggedIn
    def sendImageWithURL(self, to, url):
        path = self.downloadFileURL(url, 'path')
        return self.sendImage(to, path)

    @loggedIn
    def sendGIF(self, to, path):
        return self.uploadObjTalk(path=path, type='gif', returnAs='bool', to=to)

    @loggedIn
    def sendGIFWithURL(self, to, url):
        path = self.downloadFileURL(url, 'path')
        return self.sendGIF(to, path)

    @loggedIn
    def sendVideo(self, to, path):
        objectId = self.sendMessage(to=to, text=None, contentMetadata={'VIDLEN': '60000','DURATION': '60000'}, contentType = 2).id
        return self.uploadObjTalk(path=path, type='video', returnAs='bool', objId=objectId)

    @loggedIn
    def sendVideoWithURL(self, to, url):
        path = self.downloadFileURL(url, 'path')
        return self.sendVideo(to, path)

    @loggedIn
    def sendAudio(self, to, path):
        objectId = self.sendMessage(to=to, text=None, contentType = 3).id
        return self.uploadObjTalk(path=path, type='audio', returnAs='bool', objId=objectId)

    @loggedIn
    def sendAudioWithURL(self, to, url):
        path = self.downloadFileURL(url, 'path')
        return self.sendAudio(to, path)

    @loggedIn
    def sendFile(self, to, path, file_name=''):
        if file_name == '':
            file_name = ntpath.basename(path)
        file_size = len(open(path, 'rb').read())
        objectId = self.sendMessage(to=to, text=None, contentMetadata={'FILE_NAME': str(file_name),'FILE_SIZE': str(file_size)}, contentType = 14).id
        return self.uploadObjTalk(path=path, type='file', returnAs='bool', objId=objectId, name=file_name)

    @loggedIn
    def sendFileWithURL(self, to, url, fileName=''):
        path = self.downloadFileURL(url, 'path')
        return self.sendFile(to, path, fileName)

    """Contact"""
        
    @loggedIn
    def blockContact(self, mid):
        return self.talk.blockContact(0, mid)

    @loggedIn
    def unblockContact(self, mid):
        return self.talk.unblockContact(0, mid)

    @loggedIn
    def findAndAddContactByMetaTag(self, userid, reference):
        return self.talk.findAndAddContactByMetaTag(0, userid, reference)

    @loggedIn
    def findAndAddContactsByMid(self, mid):
        return self.talk.findAndAddContactsByMid(0, mid, 0, '')

    @loggedIn
    def findAndAddContactsByEmail(self, emails=[]):
        return self.talk.findAndAddContactsByEmail(0, emails)

    @loggedIn
    def findAndAddContactsByUserid(self, userid):
        return self.talk.findAndAddContactsByUserid(0, userid)

    @loggedIn
    def findContactsByUserid(self, userid):
        return self.talk.findContactByUserid(userid)

    @loggedIn
    def findContactByTicket(self, ticketId):
        return self.talk.findContactByUserTicket(ticketId)

    @loggedIn
    def getAllContactIds(self, syncReason=3):
        return self.talk.getAllContactIds(syncReason)

    @loggedIn
    def getBlockedContactIds(self):
        return self.talk.getBlockedContactIds()

    @loggedIn
    def getContact(self, mid):
        return self.talk.getContact(mid)

    @loggedIn
    def getContacts(self, midlist):
        return self.talk.getContacts(midlist)

    @loggedIn
    def getFavoriteMids(self):
        return self.talk.getFavoriteMids()

    @loggedIn
    def getHiddenContactMids(self):
        return self.talk.getHiddenContactMids()

    @loggedIn
    def tryFriendRequest(self, midOrEMid, friendRequestParams, method=1):
        return self.talk.tryFriendRequest(midOrEMid, method, friendRequestParams)

    @loggedIn
    def makeUserAddMyselfAsContact(self, contactOwnerMid):
        return self.talk.makeUserAddMyselfAsContact(contactOwnerMid)

    @loggedIn
    def getContactWithFriendRequestStatus(self, id):
        return self.talk.getContactWithFriendRequestStatus(id)

    @loggedIn
    def reissueUserTicket(self, expirationTime=100, maxUseCount=100):
        return self.talk.reissueUserTicket(expirationTime, maxUseCount)
    
    def deleteContact(self,contact):
        try:
            self.talk.updateContactSetting(0,contact,ContactSetting.CONTACT_SETTING_DELETE,'True')
        except:
            traceback.print_exc()
        pass
    
    def clearContacts(self):
        t = self.getContacts(self.getAllContactIds())
        for n in t:
            try:
                self.deleteContact(n.mid)
            except:
                pass
        pass
    def refreshContacts(self):
        contact_ids = self.getAllContactIds()
        contacts    = self.getContacts(contact_ids)
        
        contacts = [contact.displayName+',./;'+contact.mid for contact in contacts]
        contacts.sort()
        contacts = [a.split(',./;')[1] for a in contacts]
        return contacts
    
    @loggedIn
    def cloneContactProfile(self, mid):
        contact = self.getContact(mid)
        profile = self.profile
        profile.displayName = contact.displayName
        profile.statusMessage = contact.statusMessage
        profile.pictureStatus = self.downloadFileURL('http://dl.profile.line-cdn.net/' + contact.pictureStatus, 'path')
        if self.getProfileCoverId(mid) is not None:
            self.updateProfileCoverById(self.getProfileCoverId(mid))
        if profile.videoProfile is not None:
            self.updateProfilePicture(profile.pictureStatus)
        return self.updateProfile(profile)

    """Group"""
    @loggedIn
    def getChatRoomAnnouncementsBulk(self, chatRoomMids):
        return self.talk.getChatRoomAnnouncementsBulk(chatRoomMids)

    @loggedIn
    def getChatRoomAnnouncements(self, chatRoomMid):
        return self.talk.getChatRoomAnnouncements(chatRoomMid)

    @loggedIn
    def createChatRoomAnnouncement(self, chatRoomMid, type, contents):
        return self.talk.createChatRoomAnnouncement(0, chatRoomMid, type, contents)

    @loggedIn
    def removeChatRoomAnnouncement(self, chatRoomMid, announcementSeq):
        return self.talk.removeChatRoomAnnouncement(0, chatRoomMid, announcementSeq)

    @loggedIn
    def getGroupWithoutMembers(self, groupId):
        return self.talk.getGroupWithoutMembers(groupId)
    
    @loggedIn
    def findGroupByTicket(self, ticketId):
        group_data = {"class":""}
        split_appname = self.appName.split("\t")
        app_name, app_ver = split_appname[0], split_appname[1]
        if app_name in ["DEPRECATED"]:
            G = self.talk.findGroupByTicket(ticketId)
            pending = G.invitee
            if pending != None:
                pending = [{"mid":x.mid} for x in G.invitee]
            group_data.update({
                "class":G,
                "id": G.id,
                "createdTime":G.createdTime,
                "name": G.name,
                "pictureStatus": G.pictureStatus,
                "preventedJoinByTicket": G.preventedJoinByTicket,
                "groupPreference": {"invitationTicket": G.groupPreference.invitationTicket},
                "creator": {"mid":G.creator.mid},
                "members": [{"mid":x.mid} for x in G.members],
                "invitee": pending
            })

        else:
            G = self.talk.findChatByTicket(FindChatByTicketRequest(ticketId)).chat
            gcExtra = G.extra.groupExtra
            pending = gcExtra.inviteeMids
            if pending != {}:
                pending = [{"mid":x} for x in gcExtra.inviteeMids]
            group_data.update({
                "class":G,
                "id":G.chatMid,
                "createdTime": G.createdTime,
                "name": G.chatName,
                "pictureStatus": G.picturePath.replace("/", "", 1),
                "preventedJoinByTicket": gcExtra.preventedJoinByTicket,
                "groupPreference": {"invitationTicket": gcExtra.invitationTicket},
                "creator": {"mid":gcExtra.creator},
                "members": [{"mid":x} for x in gcExtra.memberMids],
                "invitee": pending
            })

        return group_data

    @loggedIn
    def acceptGroupInvitation(self, groupId):
        split_appname = self.appName.split("\t")
        app_name, app_ver = split_appname[0], split_appname[1]
        if app_name in ["DEPRECATED"]:
            return self.talk.acceptGroupInvitation(0, groupId)
        else:
            return self.talk.acceptChatInvitation(AcceptChatInvitationRequest(0,groupId))

    @loggedIn
    def acceptGroupInvitationByTicket(self, groupId, ticketId):
        split_appname = self.appName.split("\t")
        app_name, app_ver = split_appname[0], split_appname[1]
        if app_name in ["DEPRECATED"]:
            return self.talk.acceptGroupInvitationByTicket(0, groupId, ticketId)
        else:
            return self.talk.acceptChatInvitationByTicket(AcceptChatInvitationByTicketRequest(0,groupId,ticketId))

    @loggedIn
    def cancelGroupInvitation(self, groupId, contactIds):
        split_appname = self.appName.split("\t")
        app_name, app_ver = split_appname[0], split_appname[1]
        if app_name in ["DEPRECATED"]:
            return self.talk.cancelGroupInvitation(0, groupId, contactIds)
        else:
            return self.talk.cancelChatInvitation(CancelChatInvitationRequest(0,groupId,contactIds))

    @loggedIn
    def createGroup(self, name, midlist):
        split_appname = self.appName.split("\t")
        app_name, app_ver = split_appname[0], split_appname[1]
        if app_name in ["DEPRECATED"]:
            return self.talk.createGroup(0, name, midlist)
        else:
            return self.talk.createChat(CreateChatRequest(0,0,name,midlist,"")).chat

    @loggedIn
    def getGroup(self, groupId):
        group_data = {"class":""}
        split_appname = self.appName.split("\t")
        app_name, app_ver = split_appname[0], split_appname[1]
        if app_name in ["DEPRECATED"]:
            G = self.talk.getCompactGroup(groupId)
            pending = G.invitee
            if pending != None:
                pending = [{"mid":x.mid} for x in G.invitee]
            group_data.update({
                "class":G,
                "id": G.id,
                "createdTime":G.createdTime,
                "name": G.name,
                "pictureStatus": G.pictureStatus,
                "preventedJoinByTicket": G.preventedJoinByTicket,
                "groupPreference": {"invitationTicket": G.groupPreference.invitationTicket},
                "creator": {"mid":G.creator.mid},
                "members": [{"mid":x.mid} for x in G.members],
                "invitee": pending
            })

        else:
            G = self.talk.getChats(GetChatsRequest([groupId],True,True)).chats[0]
            gcExtra = G.extra.groupExtra
            pending = gcExtra.inviteeMids
            if pending != {}:
                pending = [{"mid":x} for x in gcExtra.inviteeMids]
            group_data.update({
                "class":G,
                "id":G.chatMid,
                "createdTime": G.createdTime,
                "name": G.chatName,
                "pictureStatus": G.picturePath.replace("/", "", 1),
                "preventedJoinByTicket": gcExtra.preventedJoinByTicket,
                "groupPreference": {"invitationTicket": gcExtra.invitationTicket},
                "creator": {"mid":gcExtra.creator},
                "members": [{"mid":x} for x in gcExtra.memberMids],
                "invitee": pending
            })

        return group_data



    @loggedIn
    def getGroups(self, groupIds):
        return self.talk.getGroups(groupIds)

    @loggedIn
    def getGroupsV2(self, groupIds):
        return self.talk.getGroupsV2(groupIds)

    @loggedIn
    def getCompactGroup(self, groupId):
        return self.talk.getCompactGroup(groupId)

    @loggedIn
    def getCompactRoom(self, roomId):
        return self.talk.getCompactRoom(roomId)

    @loggedIn
    def getGroupIdsByName(self, groupName):
        gIds = []
        for gId in self.getGroupIdsJoined():
            g = self.getCompactGroup(gId)
            if groupName in g.name:
                gIds.append(gId)
        return gIds

    @loggedIn
    def getGroupIdsInvited(self):
        split_appname = self.appName.split("\t")
        app_name, app_ver = split_appname[0], split_appname[1]
        if app_name in ["DEPRECATED"]:
            return self.talk.getGroupIdsInvited()
        else:
            return list(self.getAllChatMids().invitedChatMids)

    @loggedIn
    def getGroupIdsJoined(self):
        split_appname = self.appName.split("\t")
        app_name, app_ver = split_appname[0], split_appname[1]
        if app_name in ["DEPRECATED"]:
            return self.talk.getGroupIdsJoined()
        else:
            return list(self.getAllChatMids().memberChatMids)

    @loggedIn
    def updateGroupPreferenceAttribute(self, groupMid, updatedAttrs):
        return self.talk.updateGroupPreferenceAttribute(0, groupMid, updatedAttrs)

    @loggedIn
    def inviteIntoGroup(self, groupId, midlist):
        split_appname = self.appName.split("\t")
        app_name, app_ver = split_appname[0], split_appname[1]
        if app_name in ["DEPRECATED"]:
            return self.talk.inviteIntoGroup(0, groupId, midlist)
        else:
            return self.talk.inviteIntoChat(InviteIntoChatRequest(0,groupId,midlist))

    @loggedIn
    def kickoutFromGroup(self, groupId, midlist):
        split_appname = self.appName.split("\t")
        app_name, app_ver = split_appname[0], split_appname[1]
        if app_name in ["DEPRECATED"]:
            return self.talk.kickoutFromGroup(0, groupId, midlist)
        else:
            return self.talk.deleteOtherFromChat(DeleteOtherFromChatRequest(0,groupId,midlist))

    @loggedIn
    def leaveGroup(self, groupId):
        split_appname = self.appName.split("\t")
        app_name, app_ver = split_appname[0], split_appname[1]
        if app_name in ["DEPRECATED"]:
            return self.talk.leaveGroup(0, groupId)
        else:
            req = DeleteSelfFromChatRequest()
            req.reqSeq = 0
            req.chatMid = groupId
            return self.talk.deleteSelfFromChat(req)

    @loggedIn
    def rejectGroupInvitation(self, groupId):
        split_appname = self.appName.split("\t")
        app_name, app_ver = split_appname[0], split_appname[1]
        if app_name in ["DEPRECATED"]:
            return self.talk.rejectGroupInvitation(0, groupId)
        else:
            return self.talk.rejectChatInvitation(RejectChatInvitationRequest(0,groupId))

    @loggedIn
    def reissueGroupTicket(self, groupId):
        split_appname = self.appName.split("\t")
        app_name, app_ver = split_appname[0], split_appname[1]
        if app_name in ["DEPRECATED"]:
            return self.talk.reissueGroupTicket(groupId)
        else:
            return self.talk.reissueChatTicket(ReissueChatTicketRequest(0,groupId)).ticketId

    @loggedIn
    def updateGroup(self, groupObject):
        split_appname = self.appName.split("\t")
        app_name, app_ver = split_appname[0], split_appname[1]
        if app_name in ["DEPRECATED"]:
            groupObject["class"].preventedJoinByTicket = groupObject["preventedJoinByTicket"]
            groupObject["class"].name = groupObject["name"]
            return self.talk.updateGroup(0, groupObject["class"])
        else:
            G = groupObject["class"]
            gcExtra = G.extra.groupExtra
            if groupObject["class"].extra.groupExtra.preventedJoinByTicket != groupObject["preventedJoinByTicket"]:
                groupObject["class"].extra.groupExtra.preventedJoinByTicket = groupObject["preventedJoinByTicket"]
                return self.talk.updateChat(UpdateChatRequest(0,groupObject["class"],4))

            if groupObject["class"].chatName != groupObject["name"]:
                groupObject["class"].chatName = groupObject["name"]
                return self.talk.updateChat(UpdateChatRequest(0,groupObject["class"],1))

    """Room"""

    @loggedIn
    def createRoom(self, midlist):
        return self.talk.createRoom(0, midlist)

    @loggedIn
    def getRoom(self, roomId):
        return self.talk.getRoom(roomId)

    @loggedIn
    def inviteIntoRoom(self, roomId, midlist):
        return self.talk.inviteIntoRoom(0, roomId, midlist)

    @loggedIn
    def leaveRoom(self, roomId):
        return self.talk.leaveRoom(0, roomId)

    """Call"""
        
    @loggedIn
    def acquireCallTalkRoute(self, to):
        return self.talk.acquireCallRoute(to)
    
    """Report"""

    @loggedIn
    def reportSpam(self, chatMid, memberMids=[], spammerReasons=[], senderMids=[], spamMessageIds=[], spamMessages=[]):
        return self.talk.reportSpam(chatMid, memberMids, spammerReasons, senderMids, spamMessageIds, spamMessages)
        
    @loggedIn
    def reportSpammer(self, spammerMid, spammerReasons=[], spamMessageIds=[]):
        return self.talk.reportSpammer(spammerMid, spammerReasons, spamMessageIds)


    """GROUP (NEW VERSION)"""

    @loggedIn
    def inviteIntoChat(self, chatMid, targetUserMids=[]):
        return self.talk.inviteIntoChat(InviteIntoChatRequest(0,chatMid,targetUserMids))

    @loggedIn
    def cancelChatInvitation(self, chatMid, targetUserMids=[]):
        return self.talk.cancelChatInvitation(CancelChatInvitationRequest(0,chatMid,targetUserMids))

    @loggedIn
    def acceptChatInvitation(self, chatMid):
        return self.talk.acceptChatInvitation(AcceptChatInvitationRequest(0,chatMid))
    @loggedIn
    def acceptChatInvitationByTicket(self, chatMid, ticketId):
        return self.talk.acceptChatInvitationByTicket(AcceptChatInvitationByTicketRequest(0,chatMid,ticketId))

    @loggedIn
    def deleteOtherFromChat(self, chatMid, targetUserMids=[]):
        return self.talk.deleteOtherFromChat(DeleteOtherFromChatRequest(0,chatMid,targetUserMids))

    @loggedIn
    def reissueChatTicket(self, chatMid):
        return self.talk.reissueChatTicket(ReissueChatTicketRequest(0,chatMid))

    @loggedIn
    def findChatByTicket(self, ticketId):
        return self.talk.findChatByTicket(FindChatByTicketRequest(ticketId))

    @loggedIn
    def getInvitationTicketUrl(self, mid):
        return self.talk.getInvitationTicketUrl(GetInvitationTicketUrlRequest(mid))

    @loggedIn
    def getChats(self, chatMids=[], withMembers=True, withInvitees=True):
        return self.talk.getChats(GetChatsRequest(chatMids,withMembers,withInvitees))

    @loggedIn
    def updateChat(self, chat, updatedAttribute):
        return self.talk.updateChat(UpdateChatRequest(0,chat,updatedAttribute))

    @loggedIn
    def createChat(self, name, targetUserMids=[]):
        return self.talk.createChat(CreateChatRequest(0,0,name,targetUserMids,""))

    @loggedIn
    def rejectChatInvitation(self, chatMid):
        return self.talk.rejectChatInvitation(RejectChatInvitationRequest(0,chatMid))

    @loggedIn
    def deleteSelfFromChat(self,chatMid):
        req = DeleteSelfFromChatRequest()
        req.reqSeq = 0
        req.chatMid = chatMid
        return self.talk.deleteSelfFromChat(req)

    @loggedIn
    def getAllChatMids(self, withMemberChats=True, withInvitedChats=True):
        return self.talk.getAllChatMids(GetAllChatMidsRequest(withMemberChats,withInvitedChats), 0)
