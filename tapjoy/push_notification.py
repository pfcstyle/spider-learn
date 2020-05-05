import re
class push_notification():
    name: str
    platform: str # iOS or Android

    country: str #Japan Korea China Taiwan
    isExcludeCountry: bool

    language: str #Japanese ...
    isExcludeLanguage: bool

    date: str
    hour: str
    minute: str

    messageTitle: str
    messageContent: str

    def __init__(self):
        name = 'test'
        platform = 'iOS'
        country = 'Japan'
        isExcludeCountry = False
        language = 'Japanese'
        isExcludeLanguage = False
        date = '2020/06/01'
        hour = '23'
        minute = '50'
        messageTitle = 'test title'
        messageContent = 'test content'


def filter_tags(htmlstr):
    dr = re.compile(r'<[^>]+>', re.S)
    dd = dr.sub('', htmlstr)
    return dd


def createiOSPushByAndroid(push_android: push_notification):
    push_iOS = push_notification()
    push_iOS.name = push_android.name.replace('AOS', 'iOS')
    push_iOS.platform = 'iOS'
    push_iOS.country = push_android.country
    push_iOS.isExcludeCountry = push_android.isExcludeCountry
    push_iOS.language = push_android.language
    push_iOS.isExcludeLanguage = push_android.isExcludeLanguage
    push_iOS.date = push_android.date
    push_iOS.hour = push_android.hour
    push_iOS.minute = push_android.minute
    push_iOS.messageTitle = filter_tags(push_android.messageTitle)
    push_iOS.messageContent = filter_tags(push_android.messageContent)
    return push_iOS
