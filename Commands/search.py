import mapping
import bot
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from justwatch import JustWatch
import tmdbsimple as tmdb
tmdb.API_KEY = bot.tmdb_apikey
tmdb.REQUESTS_TIMEOUT = bot.tmdb_timeout


def getMaxResults(num):
    max_results = 10
    if num < max_results:
        max_results = num
    return max_results


def onSearch(query):
    text = f'πδ½ ζη΄’ηζ―οΌ*{query}*'
    text = f'{text}\nπθ―·ιζ©ιθ¦ζη΄’ηη±»επ'
    tv = mapping.onType('tv')
    movie = mapping.onType('movie')
    keybaord = [[InlineKeyboardButton(f'{tv}', callback_data=f'search_tv_{query}'), InlineKeyboardButton(
        f'{movie}', callback_data=f'search_movie_{query}')]]
    reply_markup = InlineKeyboardMarkup(keybaord)
    return text, reply_markup


def onSearchResult(object_type, query):
    search = tmdb.Search()
    text = f'β*ζ²‘ζζΎε°η»ζ*β'
    object_switch = mapping.onType(object_type)
    keyboard = []
    keyboard.append([InlineKeyboardButton(
                    f'πδΈζ»‘ζζη΄’η»ζοΌεζ₯δΈζ¬‘ε§β³', callback_data=f'again_{query}')])
    match object_type:
        case 'tv':
            response = search.tv(query={query}, language='zh-CN')
        case 'movie':
            response = search.movie(query={query}, language='zh-CN')
    total_results = response['total_results']
    if total_results > 0:
        max_results = getMaxResults(total_results)
        text = f'*ε±ζΎε° {object_switch} η {total_results} δΈͺη»ζ*\nπδΈΊδ½ εεΊε {max_results} δΈͺη»ζπ\n'
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
                            release_year = f'{release_date[0]}εΉ΄'
                case 'movie':
                    title = results[i]['title']
                    if 'release_date' in results[i]:
                        if results[i]['release_date'] != '':
                            release_date = results[i]['release_date'].split(
                                '-')
                            release_year = f'{release_date[0]}εΉ΄'
            tmdbid = results[i]['id']
            callback = f'info_{object_type}_{tmdbid}_{query}'
            keyboard.append([InlineKeyboardButton(
                f'γ{title}γ {release_year}', callback_data=callback)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return text, reply_markup


def onInfomation(object_type, tmdbid, query):
    object_switch = mapping.onType(object_type)
    text = ''
    match object_type:
        case 'tv':
            content_type = 'show'

            response = tmdb.TV(tmdbid).info(language='zh-CN')
            title = response['name']
            original_title = response['original_name']
            text = f'*{object_switch}*οΌ*{title}* ο½ {original_title}\n\n'

            time_seasons = response['number_of_seasons']
            time_episodes = response['number_of_episodes']
            if time_seasons > 0 or time_episodes > 0:
                text = f'{text}\nβ° *ζΆιΏ*οΌε± {time_seasons} ε­£ {time_episodes} ι'

            release_date = response['first_air_date']
            if release_date is not None:
                text = f'{text}\nπ *εΉ΄δ»½*οΌ{release_date}'

        case 'movie':
            content_type = 'movie'

            response = tmdb.Movies(tmdbid).info(language='zh-CN')

            title = response['title']
            original_title = response['original_title']
            text = f'*{object_switch}*οΌ*{title}* ο½ {original_title}\n\n'

            time = response['runtime']
            if time > 0:
                text = f'{text}\nβ° *ζΆιΏ*οΌ{time} ει'

            release_date = response['release_date']
            if release_date is not None:
                text = f'{text}\nπ *εΉ΄δ»½*οΌ{release_date}'

    genre = ''
    if len(response['genres']) > 0:
        for i in response['genres']:
            name = i['name']
            genre = f'{genre}{name} '
        text = f'{text}\nπ *η±»ε*οΌ{genre}'

    with open("./json/country.json", 'r') as j_3166:
        d_3166 = json.load(j_3166)
        iso_3166 = ''
        for code in response['production_countries']:
            for i in d_3166:
                if code['iso_3166_1'] == i:
                    iso_3166 = f'{iso_3166}{d_3166[i]} '
        text = f'{text}\nπ *ε°εΊ*οΌ{iso_3166}'
    with open("./json/language.json", 'r') as j_639:
        d_639 = json.load(j_639)
        iso_639 = ''
        for code in response['spoken_languages']:
            for i in d_639:
                if code['iso_639_1'] == i:
                    iso_639 = f'{iso_639}{d_639[i]} '
        text = f'{text}\nπ *θ―­θ¨*οΌ{iso_639}'

    vote_average = response['vote_average']
    if vote_average != 0:
        text = f'{text}\nπ *θ―ε*οΌ{vote_average}'

    url = f'https://www.themoviedb.org/{object_type}/{tmdbid}?language=zh-CN'
    text = f'{text}\nπ *ε°ε*οΌ{url}'
    keyboard = []
    keyboard.append([InlineKeyboardButton(
                    f'πδΈζ»‘ζζη΄’η»ζοΌεζ₯δΈζ¬‘ε§β³', callback_data=f'again_{query}')])
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
                                    f'πζθ½ε¨εͺιε¨ηΊΏθ§ηζθ΄­δΉ°οΌπ₯', callback_data=f'watch_{content_type}_{jwdbid}')])
            break

    reply_markup = InlineKeyboardMarkup(keyboard)
    return text, reply_markup


def onSelectCountry(content_type, jwdbid):
    list = mapping.getCountry()
    keyboard = []
    text = 'π«ζζͺζΎε°ε―η¨ηεΉ³ε°π«'
    for i in list:
        just_watch = JustWatch(country=i[1])
        results = just_watch.get_title(
            title_id=jwdbid, content_type=content_type)
        if 'offers' in results:
            text = 'πθ―·ιζ©ιθ¦ζη΄’ηε½ε?Άζε°εΊπ'
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
        name = mapping.onProviders(providers, i['provider_id'])
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
    keytype = mapping.onOfferType(key)
    text = f'*ζΎε°δΊθΏδΊε¨{mapping.onCountry(country)}η{keytype}*'
    extra = ''
    for i in dictlist:
        name = dictlist[i]['name']
        url = dictlist[i]['url']
        if key == 'buy' or key == 'rent':
            price = dictlist[i]['price']
            currency = dictlist[i]['currency']
            extra = f' - π°{price}{currency}'
        keyboard.append([InlineKeyboardButton(f'{name}{extra}', url=url)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return text, reply_markup
