"""
1. This script is a web crawler that scrapes a single novel from the Fanqie website.
- Website: https://fanqienovel.com/reader/7070069849975849506?enter_from=page
"""
import requests
import parsel
import re
from tqdm import tqdm
import time
import random

from io import BytesIO
import ddddocr
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont


def smart_delay(min_seconds=1, max_seconds=3):
    time.sleep(random.uniform(min_seconds, max_seconds))


def sanitize_filename(title):
    return re.sub(r'[\/:*?"<>|]+', '_', title)


def font_to_img(_code, font_path):
    """
    This function is used to convert the font code to an image.
    """
    img_size = 1024
    img = Image.new('1', (img_size, img_size), 255)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, int(img_size * 0.7))
    txt = chr(_code)

    bbox = draw.textbbox((0, 0), txt, font=font)
    x = bbox[2] - bbox[0]
    y = bbox[3] - bbox[1]

    draw.text(((img_size - x) // 2, (img_size - y) // 7), txt, font=font, fill=0)
    return img


def identify_word(font_path):
    """
    Identify the font code and convert it to a word.
    """
    font = TTFont(font_path)
    ocr = ddddocr.DdddOcr(beta=True)

    font_mapping = {}

    for cmap_code, glyph_name in font.getBestCmap().items():
        bytes_io = BytesIO()
        pil = font_to_img(cmap_code, font_path)
        pil.save(bytes_io, format="PNG")
        word = ocr.classification(bytes_io.getvalue())
        print(f"数字Unicode: [{cmap_code}] - 16进制Unicode: [{glyph_name}] - 识别结果: {word}")

        # Mapping Model
        font_mapping[cmap_code] = word

        # Save the font image
        # with open(f"font_img\\{cmap_code}_{glyph_name}.png", "wb") as f:
        #     f.write(bytes_io.getvalue())

    del_key = []  # 收集要删除的键
    for key, value in font_mapping.items():
        if not value:
            del_key.append(key)

    for i in del_key:
        font_mapping.pop(i)

    return font_mapping


def single_novel(headers, url, decoder):
    """
    This function is used to scrape a single novel from the Fanqie website.
    :return:
    """
    smart_delay()
    response = requests.get(url = url, headers = headers)

    # Get text
    html = response.text

    # Get the novel title
    selector = parsel.Selector(html)
    title = selector.css('.muye-reader-title::text').get()

    # Get the novel content
    content_list = selector.css('.muye-reader-content p::text').getall()
    content = '\n\n'.join(content_list)

    new_content = ''
    for i in content:
        # print(i, ord(i))
        try:
            # decode the content
            new_word = decoder[ord(i)]
            new_content += new_word
        except:
            new_word = i
            new_content += new_word

    # Save the content
    with open("./主角长辈/" + sanitize_filename(title) + ".txt", "w", encoding="utf-8") as f:
        f.write(new_content)


def patch_novel(headers, link, mapping):
    """
    First: https://fanqienovel.com/reader/7070069849975849506?enter_from=page
    Second: https://fanqienovel.com/reader/7070070463103402504?enter_from=search
    Third: https://fanqienovel.com/reader/7070070663809073671?enter_from=search
    """
    link_data = requests.get(url = link, headers = headers).text

    # Get the novel ID
    id_list = re.findall('"itemId":"(\d+)"', link_data)

    # Get the novel title
    name = re.findall('<div class="info-name"><h1>(.*?)</h1>', link_data)[0]

    print("Collecting: ", name)
    n = 0
    for i in tqdm(id_list):
        if n == 73: # 73
            single_novel(headers, f"https://fanqienovel.com/reader/{i}?enter_from=page", mapping)
            break
        n += 1


if __name__ == "__main__":
    headers = {
        # User Information
        'cookie':'x-web-secsdk-uid=9c8a9626-d979-4644-a5e5-fdd03907d508; Hm_lvt_2667d29c8e792e6fa9182c20a3013175=1745953872; HMACCOUNT=B8E51C9762411323; csrf_session_id=902a6c705e879baabff55b645f91cc79; s_v_web_id=verify_ma2vuudk_qIaJLENX_utDK_4XCy_ApoR_HMC71whXqbpB; gfkadpd=2503,36144; serial_uuid=7498814688156321307; serial_webid=7498814688156321307; passport_csrf_token=11a2bd60b94ebdaf28d4dbb15804edc0; passport_csrf_token_default=11a2bd60b94ebdaf28d4dbb15804edc0; odin_tt=7d3734b9e1db7b5ce2d57b11985e04d5ec7e54a2b8240ed625dc9c7c129b8adfc3b111cde9a90e1028f12d5a19fe3a0f80be83cb3036683ee791b1eee63d8bfc; n_mh=fv0PjgTuuKi867YyQhvA5l8x7FoPLYaLnvMSUafbRDc; sid_guard=512f87a7c34b3b9eab7b788e240af088%7C1745953893%7C5184000%7CSat%2C+28-Jun-2025+19%3A11%3A33+GMT; uid_tt=db870fc3f9dbaba7ab2f828cb6a243ae; uid_tt_ss=db870fc3f9dbaba7ab2f828cb6a243ae; sid_tt=512f87a7c34b3b9eab7b788e240af088; sessionid=512f87a7c34b3b9eab7b788e240af088; sessionid_ss=512f87a7c34b3b9eab7b788e240af088; is_staff_user=false; sid_ucp_v1=1.0.0-KDg2OTgxMGVhMGQ4M2YxMWYwMTk2YjUyZTdmZjk5OGRjMDU4ZTdmZTYKHwiEqfDNzc3CBxDlyMTABhjHEyAMMMu2tq4GOAdA9AcaAmhsIiA1MTJmODdhN2MzNGIzYjllYWI3Yjc4OGUyNDBhZjA4OA; ssid_ucp_v1=1.0.0-KDg2OTgxMGVhMGQ4M2YxMWYwMTk2YjUyZTdmZjk5OGRjMDU4ZTdmZTYKHwiEqfDNzc3CBxDlyMTABhjHEyAMMMu2tq4GOAdA9AcaAmhsIiA1MTJmODdhN2MzNGIzYjllYWI3Yjc4OGUyNDBhZjA4OA; novel_web_id=7498814688156321307; Hm_lpvt_2667d29c8e792e6fa9182c20a3013175=1746039621; ttwid=1%7CuGjWpxnOkFjmLID61hNpbD2hfk9PhUUOE1M7egWCU7A%7C1746039622%7C4eda76f6ff65300d62bb85c8edd7336e8f85b74dfc55aa8e425b669e2d6a47e3',        # User Agent: Chrome Information
        'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
    }

    # 你是这样的学姐 Content URL
    link = 'https://fanqienovel.com/page/7254393795939142695?enter_from=search'

    # 你是这样的学姐 URL
    # url = 'https://fanqienovel.com/reader/7070069849975849506?enter_from=page'

    # mapping = identify_word('dc027189e0ba4cd-700.woff2')
    # print("Font Mapping: ", mapping)

    word_mapping = {58344: 'd', 58345: '在', 58346: '主', 58347: '特', 58348: '家', 58349: '军', 58350: '然', 58351: '表',
              58352: '场', 58353: '4', 58354: '要', 58355: '只', 58356: 'v', 58357: '和', 58359: '6', 58360: '别',
              58361: '还', 58362: 'g', 58363: '现', 58364: '儿', 58365: '岁', 58368: '此', 58369: '象', 58370: '月',
              58371: '3', 58372: '出', 58373: '战', 58374: '工', 58375: '相', 58376: 'o', 58377: '男', 58378: '直',
              58379: '失', 58380: '世', 58381: 'f', 58382: '都', 58383: '平', 58384: '文', 58385: '什', 58386: 'v',
              58387: 'o', 58388: '将', 58389: '真', 58390: 't', 58391: '那', 58392: '当', 58394: '会', 58395: '立',
              58396: '些', 58397: 'u', 58398: '是', 58399: '十', 58400: '张', 58401: '学', 58402: '气', 58403: '大',
              58404: '爱', 58405: '两', 58406: '命', 58407: '全', 58408: '后', 58409: '东', 58410: '性', 58411: '通',
              58412: '被', 58413: '1', 58414: '它', 58415: '乐', 58416: '接', 58417: '而', 58418: '感', 58419: '车',
              58420: 'l', 58421: '公', 58422: '了', 58423: '常', 58424: '以', 58425: '何', 58426: '可j', 58427: '话',
              58428: '先', 58429: 'p', 58430: 'i', 58431: '4', 58432: '轻', 58433: 'm', 58434: '士', 58435: 'w',
              58436: '着', 58437: '变', 58438: '尔', 58439: '快', 58440: 'l', 58441: '个', 58442: '说', 58443: '少',
              58444: '色', 58445: '里', 58446: '安', 58447: '花', 58448: '远', 58449: '7', 58450: '难', 58451: '师',
              58452: '放', 58453: 't', 58454: '报', 58455: '认', 58456: '面', 58457: '道', 58458: 's', 58460: '克',
              58461: '地', 58462: '度', 58463: 'l', 58464: '好', 58465: '机', 58466: 'u', 58467: '民', 58468: '写',
              58469: '把', 58470: '万', 58471: '同', 58472: '水', 58473: '新', 58474: '没', 58475: '书', 58476: '电',
              58477: '吃', 58478: '像', 58479: '斯', 58480: '5', 58481: '为', 58482: 'y', 58483: '白', 58485: '日',
              58486: '教', 58487: '看', 58488: '但', 58489: '第', 58490: '加', 58491: '候', 58492: '作', 58493: '上',
              58494: '拉', 58495: '住', 58496: '有', 58497: '法', 58498: 'r', 58499: '事', 58500: '应', 58501: '位',
              58502: '利', 58503: '你', 58504: '声', 58505: '身', 58506: '国', 58507: '问', 58508: '马', 58509: '女',
              58510: '他', 58511: 'y', 58512: '比', 58513: '父', 58514: 'x', 58515: 'a', 58516: 'h', 58517: 'n',
              58518: 's', 58519: 'x', 58520: '边', 58521: '美', 58522: '对', 58523: 'f所', 58524: '金', 58525: '活',
              58526: '回', 58527: '意', 58528: '到', 58529: 'z', 58530: '从', 58531: 'j', 58532: '知', 58533: '又',
              58534: '内', 58535: '因', 58536: '点', 58537: 'q', 58538: '三', 58539: '定', 58540: '8', 58541: 'R',
              58542: 'b', 58543: '正', 58544: '或', 58545: '夫', 58546: '向', 58547: '德', 58548: '听', 58549: '更',
              58551: '得', 58552: '告', 58553: '并', 58554: '本', 58555: 'q', 58556: '过', 58557: '记', 58558: 'l',
              58559: '让', 58560: '打', 58561: 'f', 58562: '人', 58563: '就', 58564: '者', 58565: '去', 58566: '原',
              58567: '满', 58568: '体', 58569: '做', 58570: '经', 58571: 'K', 58572: '走', 58573: '如', 58574: '孩',
              58575: 'c', 58576: 'g', 58577: '给', 58578: '使', 58579: '物', 58581: '最', 58582: '笑', 58583: '部',
              58484: '几',
              58585: '员', 58586: '等', 58587: '受', 58588: 'k', 58589: '行', 58590: '一', 58591: '条', 58592: '果',
              58593: '动', 58594: '光', 58595: '门', 58596: '头', 58597: '见', 58598: '往', 58599: '自', 58600: '解',
              58601: '成', 58602: '处', 58603: '天', 58604: '能', 58605: '于', 58606: '名', 58607: '其', 58608: '发',
              58609: '总', 58610: '母', 58611: '的', 58612: '死', 58613: '手', 58614: '入', 58615: '路', 58616: '进',
              58617: '心', 58618: '来', 58619: 'h', 58620: '时', 58621: '力', 58622: '多', 58623: '开', 58624: '已',
              58625: '许', 58626: 'd', 58627: '至', 58628: '由', 58629: '很', 58630: '界', 58631: 'n', 58632: '小',
              58633: '与', 58634: 'z', 58635: '想', 58636: '代', 58637: '么', 58638: '分', 58639: '生', 58640: '口',
              58641: '再', 58642: '妈', 58643: '望', 58644: '次', 58645: '西', 58646: '风', 58647: '种', 58648: '带',
              58649: 'j', 58651: '实', 58652: '情', 58653: '才', 58654: '这', 58656: 'e', 58657: '我', 58658: '神',
              58659: '格', 58660: '长', 58661: '觉', 58662: '间', 58663: '年', 58664: '眼', 58665: '无', 58666: '不',
              58667: '亲', 58668: '关', 58669: '结', 58670: '0', 58671: '友', 58672: '信', 58673: '下', 58674: '却',
              58675: '重', 58676: '己', 58677: '老', 58678: '2', 58679: '音', 58680: '字', 58681: 'm', 58682: '呢',
              58683: '明', 58684: '之', 58685: '前', 58686: '高', 58687: 'p', 58688: 'b', 58689: '目', 58690: '太',
              58691: 'e', 58692: '9', 58693: '起', 58694: '棱', 58695: '她', 58696: '也', 58697: 'w', 58698: '用',
              58699: '方', 58700: '子', 58701: '英', 58702: '每', 58703: '理', 58704: '便', 58705: '四', 58706: '数',
              58707: '期', 58708: '中', 58709: 'c', 58710: '外', 58711: '样', 58712: 'a', 58713: '海', 58714: '们',
              58715: '任'}

    # single_novel(headers, url, word_mapping)

    patch_novel(headers, link, word_mapping)

    exit()