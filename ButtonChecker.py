import json
from lib2to3.pytree import convert
import requests
import TypeSwtich
import bot
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from justwatch import JustWatch
import tmdbsimple as tmdb
tmdb.API_KEY = bot.tmdb_apikey
tmdb.REQUESTS_TIMEOUT = bot.tmdb_timeout


def getCountry():
    list = [['香港🇭🇰', 'HK'], ["台湾🇹🇼", 'TW'], ["美国🇺🇸", 'US'], ["新加坡🇸🇬", 'SG'], [
        "韩国🇰🇷", 'KR'], ["日本🇯🇵", 'JP'], ["英国🇬🇧", 'GB'], ["土耳其🇹🇷", 'TR']]
    return list


def getMaxResults(num):
    max_results = 10
    if num < max_results:
        max_results = num
    return max_results


def onSearch(query):
    text = f'📝你搜索的是：*{query}*'
    text = f'{text}\n👇请选择需要搜索的类型👇'
    tv = TypeSwtich.onType('tv')
    movie = TypeSwtich.onType('movie')
    keybaord = [[InlineKeyboardButton(f'{tv}', callback_data=f'search_tv_{query}'), InlineKeyboardButton(
        f'{movie}', callback_data=f'search_movie_{query}')]]
    reply_markup = InlineKeyboardMarkup(keybaord)
    return text, reply_markup


def onSearchResult(object_type, query):
    search = tmdb.Search()
    text = f'❌*没有找到结果*❌'
    object_switch = TypeSwtich.onType(object_type)
    keyboard = []
    keyboard.append([InlineKeyboardButton(
                    f'👉不满意搜索结果？再来一次吧⏳', callback_data=f'again_{query}')])
    match object_type:
        case 'tv':
            response = search.tv(query={query}, language='zh-CN')
        case 'movie':
            response = search.movie(query={query}, language='zh-CN')
    total_results = response['total_results']
    if total_results > 0:
        max_results = getMaxResults(total_results)
        text = f'*共找到 {object_switch} 的 {total_results} 个结果*\n👇为你列出前 {max_results} 个结果👇\n'
        results = response['results']
        release_year = ''
        for i in range(max_results):
            match object_type:
                case 'tv':
                    title = results[i]['name']
                    if 'first_air_date' in results[i]:
                        if results[i]['first_air_date'] != '':
                            release_date = results[i]['first_air_date'].split(
                                '-')
                            release_year = f'{release_date[0]}年'
                case 'movie':
                    title = results[i]['title']
                    if 'release_date' in results[i]:
                        if results[i]['release_date'] != '':
                            release_date = results[i]['release_date'].split(
                                '-')
                            release_year = f'{release_date[0]}年'
            tmdbid = results[i]['id']
            callback = f'info_{object_type}_{tmdbid}_{query}'
            keyboard.append([InlineKeyboardButton(
                f'《{title}》 {release_year}', callback_data=callback)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return text, reply_markup


def onInfomation(object_type, tmdbid, query):
    object_switch = TypeSwtich.onType(object_type)
    text = '1'
    match object_type:
        case 'tv':
            content_type = 'show'

            response = tmdb.TV(tmdbid).info(language='zh-CN')
            title = response['name']
            original_title = response['original_name']
            text = f'*{object_switch}*：*{title}* ｜ {original_title}\n\n'

            genre = ''
            if len(response['genres']) > 0:
                for i in response['genres']:
                    name = i['name']
                    genre = f'{genre}{name} '
                text = f'{text}🗂 *类型*：{genre}\n'

            time_seasons = response['number_of_seasons']
            time_episodes = response['number_of_episodes']
            if time_seasons > 0 or time_episodes > 0:
                text = f'{text}⏰ *时长*：共 {time_seasons} 季 {time_episodes} 集\n'

            release_date = response['first_air_date']
            if release_date is not None:
                text = f'{text}📆 *年份*：{release_date}\n'

        case 'movie':
            content_type = 'movie'

            response = tmdb.Movies(tmdbid).info(language='zh-CN')

            title = response['title']
            original_title = response['original_title']
            text = f'*{object_switch}*：*{title}* ｜ {original_title}\n\n'

            genre = ''
            if len(response['genres']) > 0:
                for i in response['genres']:
                    name = i['name']
                    genre = f'{genre}{name} '
                text = f'{text}🗂 *类型*：{genre}\n'

            time = response['runtime']
            if time > 0:
                text = f'{text}⏰ *时长*：{time} 分钟\n'

            release_date = response['release_date']
            if release_date is not None:
                text = f'{text}📆 *年份*：{release_date}\n'

    vote_average = response['vote_average']
    if vote_average != 0:
        text = f'{text}📓 *评分*：{vote_average}\n'

    url = f'https://www.themoviedb.org/{object_type}/{tmdbid}?language=zh-CN'
    text = f'{text}🌐 *地址*：{url}'
    keyboard = []
    keyboard.append([InlineKeyboardButton(
                    f'👉不满意搜索结果？再来一次吧⏳', callback_data=f'again_{query}')])
    justwatch = JustWatch('US')
    results = justwatch.search_for_item(
        query=original_title, content_types=[content_type])
    if len(results['items']) > 0:
        max = 5
        if len(results['items']) < max:
            max = len(results['items'])
        for i in range(max):
            detail = justwatch.get_title(
                title_id=results['items'][i]['id'], content_type=content_type)
            for ii in detail:
                if ii == 'external_ids':
                    for iii in detail[ii]:
                        if iii['provider'] == 'tmdb':
                            if iii['external_id'] == f'{tmdbid}':
                                jwdbid = detail['id']
                                keyboard.append([InlineKeyboardButton(
                                    f'👉我能在哪里在线观看或购买？🖥', callback_data=f'watch_{content_type}_{jwdbid}')])
            break

    reply_markup = InlineKeyboardMarkup(keyboard)
    return text, reply_markup


def onSelectCountry(content_type, jwdbid):
    list = getCountry()
    text = '👇请选择需要搜索的国家或地区👇'
    keyboard = []
    for i in list:
        just_watch = JustWatch(country=i[1])
        results = just_watch.get_title(
            title_id=jwdbid, content_type=content_type)
        if 'offers' in results:
            button = InlineKeyboardButton(
                i[0], callback_data=f'country_{i[1]}_{content_type}_{jwdbid}')
            if len(keyboard) == 0:
                keyboard.append([button])
            else:
                inline = len(keyboard)-1
                if len(keyboard[inline]) < 3:
                    keyboard[inline].append(button)
                else:
                    keyboard.append([button])

    reply_markup = InlineKeyboardMarkup(keyboard)
    return text, reply_markup


def onOffer(country, content_type, jwdbid):
    just_watch = JustWatch(country=country)
    results = just_watch.get_title(title_id=jwdbid, content_type=content_type)
    providers = just_watch.get_providers()
    return results['offers'], providers


def onOfferConvert(offer, providers):
    dictlist = {}
    for i in offer:
        name = TypeSwtich.onProviders(providers, i['provider_id'])
        url = i['urls']['standard_web']
        match i['monetization_type']:
            case 'flatrate':
                if 'flatrate' not in dictlist:
                    dictlist['flatrate'] = {}
                dictlist['flatrate'][name] = {}
                dictlist['flatrate'][name]['name'] = name
                dictlist['flatrate'][name]['url'] = url
            case 'free':
                if 'free' not in dictlist:
                    dictlist['free'] = {}
                dictlist['free'][name] = {}
                dictlist['free'][name]['name'] = name
                dictlist['free'][name]['url'] = url
            case 'ads':
                if 'ads' not in dictlist:
                    dictlist['ads'] = {}
                dictlist['ads'][name] = {}
                dictlist['ads'][name]['name'] = name
                dictlist['ads'][name]['url'] = url
            case 'buy':
                if 'buy' not in dictlist:
                    dictlist['buy'] = {}
                dictlist['buy'][name] = {}
                dictlist['buy'][name]['name'] = name
                dictlist['buy'][name]['url'] = url
                dictlist['buy'][name]['price'] = i['retail_price']
                dictlist['buy'][name]['currency'] = i['currency']
            case 'rent':
                if 'rent' not in dictlist:
                    dictlist['rent'] = {}
                dictlist['rent'][name] = {}
                dictlist['rent'][name]['name'] = name
                dictlist['rent'][name]['url'] = url
                dictlist['rent'][name]['price'] = i['retail_price']
                dictlist['rent'][name]['currency'] = i['currency']
    return dictlist


def onOfferSender(dictlist, key, country):
    keyboard = []
    keytype = TypeSwtich.onOfferType(key)
    text = f'*找到了这些在{TypeSwtich.onCountry(country)}的{keytype}*'
    extra = ''
    for i in dictlist:
        name = dictlist[i]['name']
        url = dictlist[i]['url']
        if key == 'buy' or key == 'rent':
            price = dictlist[i]['price']
            currency = dictlist[i]['currency']
            extra = f' - 💰{price}{currency}'
        keyboard.append([InlineKeyboardButton(f'{name}{extra}', url=url)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return text, reply_markup


def onTrending(datatype):
    match datatype:
        case 'today':
            key = bot.tmdb_apikey
            language = 'zh-CN'
            url = f'https://api.themoviedb.org/3/trending/all/day?api_key={key}&language={language}'
            response = json.loads(requests.get(url).text)
            text = f'👇为你送上本日特别推荐：👇'
            keyboard = []
            results = response['results']
            for i in range(len(results)):
                recommend = results[i]
                id = recommend['id']
                object_type = 'movie'
                title = 'title'
                if recommend['media_type'] == 'tv':
                    object_type = 'tv'
                    title = 'name'
                query = recommend[title]
                object_switch = TypeSwtich.onType(object_type)
                content = f'#{i+1} -《{query}》{object_switch}'
                button = InlineKeyboardButton(
                    content, callback_data=f'info_{object_type}_{id}_{query}')
                if len(keyboard) == 0:
                    keyboard.append([button])
                else:
                    inline = len(keyboard)-1
                    if len(keyboard[inline]) < 2:
                        keyboard[inline].append(button)
                    else:
                        keyboard.append([button])
            reply_markup = InlineKeyboardMarkup(keyboard)
            return text, reply_markup
