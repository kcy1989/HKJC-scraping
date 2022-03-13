import json
import pandas as pd
import time
import requests

# for counting run time
st = time.time()

# settings
start_date = "2022-01-01"  # input start date in YYYY-MM-DD format
end_date = "2022-02-28"  # input end date in YYYY-MM-DD format
get_all = True  # input False if do not want all league data
league = ["意大利甲組聯賽", "墨西哥超級聯賽", "美國職業聯賽", "英格蘭超級聯賽"]  # input Chinese league name, this can be anything if get_all = True


def gen_date_list(start_date, end_date):
    day_list = [i.strftime("%Y%m%d") for i in pd.date_range(start=start_date, end=end_date, freq='D')]
    return day_list


def get_total_page(day):
    url = f"https://bet.hkjc.com/football/getJSON.aspx?jsontype=search_result.aspx&startdate={day}&enddate={day}&teamid=default"
    response = requests.post(url)
    try:
        js = response.json()[0]
        match_count = js["matchescount"]
        total_page = -(-int(match_count) // 20)
    except:
        total_page = 0
    return total_page


def go_url(day, page):
    url = f"https://bet.hkjc.com/football/getJSON.aspx?jsontype=search_result.aspx&startdate={day}&enddate={day}&teamid=default&pageno={page}"
    try:
        response = requests.post(url)
        js = response.json()[0]
    except:
        try:
            response = requests.post(url)
            js = response.json()[0]
        except:
            try:
                response = requests.post(url)
                js = response.json()[0]
            except:
                pass
    return js


def get_odd_json(id):
    url = f"https://bet.hkjc.com/football/getJSON.aspx?jsontype=last_odds.aspx&matchid={id}"
    try:
        response = requests.post(url)
        js = response.json()
    except:
        js = None
    return js


def get_data_in_page(pages):
    id = []
    match_id = []
    match_date = []
    league_name = []
    home_team = []
    away_team = []
    first_half_home_score = []
    first_half_away_score = []
    second_half_home_score = []
    second_half_away_score = []

    for page in range(pages):
        page_num = page + 1
        js = go_url(day, page_num)

        id = id + get_id(js)
        match_id = match_id + get_match_id(js)
        match_date = match_date + get_match_date(js)
        league_name = league_name + get_league_name(js)
        home_team = home_team + get_home_team(js)
        away_team = away_team + get_away_team(js)
        first_half_home_score = first_half_home_score + get_first_half_home_score(js)
        first_half_away_score = first_half_away_score + get_first_half_away_score(js)
        second_half_home_score = second_half_home_score + get_second_half_home_score(js)
        second_half_away_score = second_half_away_score + get_second_half_away_score(js)

    page_dict = {"ID": id, "match_id": match_id, "比賽日期": match_date, "聯賽": league_name,
                 "主隊": home_team, "客隊": away_team,
                 "上半場主隊得分": first_half_home_score, "上半場客隊得分": first_half_away_score,
                 "全場主隊得分": second_half_home_score, "全場客隊得分": second_half_away_score}

    if not get_all:
        df = pd.DataFrame(page_dict)
        page_dict = df.loc[df['聯賽'].isin(league)]
    else:
        pass
    return page_dict


def get_odd_data(js, id):
    handicap_HG = get_odds_handicap_HG(js)
    handicap_home = get_odds_handicap_home(js)
    handicap_draw = get_odds_handicap_draw(js)
    handicap_away = get_odds_handicap_away(js)
    handicap2_HG = get_odds_handicap2_HG(js)
    handicap2_home = get_odds_handicap2_home(js)
    handicap2_away = get_odds_handicap2_away(js)

    odd_dict = {"ID": id, "讓球主客和主隊讓球": handicap_HG, "讓球主客和主勝": handicap_home, "讓球主客和打和": handicap_draw, "讓球主客和客勝": handicap_away,
                "讓球主隊讓球": handicap2_HG, "讓球主勝": handicap2_home, "讓球客勝": handicap2_away}

    score_hl_dict = get_score_hl(js)
    odds_had = get_odds_had(js)
    odds_full_other = get_odds_full_other(js)
    odds_half_other = get_odds_half_other(js)
    odds_halffull = get_odds_hf(js)

    dict = {**odds_had, **odd_dict, **score_hl_dict, **odds_full_other, **odds_half_other, **odds_halffull}
    return dict


def get_id(js):
    temp = []
    for match in js["matches"]:
        try:
            temp.append(match["matchID"])
        except:
            temp.append(None)
    return temp


def get_match_id(js):
    temp = []
    for match in js["matches"]:
        try:
            temp.append(match["matchIDinofficial"])
        except:
            temp.append(None)
    return temp


def get_match_date(js):
    temp = []
    for match in js["matches"]:
        try:
            temp.append(match["matchDate"])
        except:
            temp.append(None)
    return temp


def get_league_name(js):
    temp = []
    for match in js["matches"]:
        try:
            temp.append(match["league"]["leagueNameCH"])
        except:
            temp.append(None)
    return temp


def get_home_team(js):
    temp = []
    for match in js["matches"]:
        try:
            temp.append(match["homeTeam"]["teamNameCH"])
        except:
            temp.append(None)
    return temp


def get_away_team(js):
    temp = []
    for match in js["matches"]:
        try:
            temp.append(match["awayTeam"]["teamNameCH"])
        except:
            temp.append(None)
    return temp


def get_first_half_home_score(js):
    temp = []
    for match in js["matches"]:
        try:
            temp.append(match["accumulatedscore"][0]["home"])
        except:
            temp.append(None)
    return temp


def get_first_half_away_score(js):
    temp = []
    for match in js["matches"]:
        try:
            temp.append(match["accumulatedscore"][0]["away"])
        except:
            temp.append(None)
    return temp


def get_second_half_home_score(js):
    temp = []
    for match in js["matches"]:
        try:
            temp.append(match["accumulatedscore"][1]["home"])
        except:
            temp.append(None)
    return temp


def get_second_half_away_score(js):
    temp = []
    for match in js["matches"]:
        try:
            temp.append(match["accumulatedscore"][1]["away"])
        except:
            temp.append(None)
    return temp


def get_odds_had(js):
    try:
        temp_h = js["hadodds"]["H"].partition("@")[2]
        temp_d = js["hadodds"]["D"].partition("@")[2]
        temp_a = js["hadodds"]["A"].partition("@")[2]
    except:
        temp_h, temp_d, temp_a = None, None, None
    dict = {"主客和主": temp_h, "主客和和": temp_d, "主客和客": temp_a}
    return dict


def get_odds_handicap_HG(js):
    try:
        temp = js["hhaodds"]["HG"]
    except:
        temp = None
    return temp


def get_odds_handicap_home(js):
    try:
        temp = js["hhaodds"]["H"]
        temp = temp.partition("@")[2]
    except:
        temp = None
    return temp


def get_odds_handicap_draw(js):
    try:
        temp = js["hhaodds"]["D"]
        temp = temp.partition("@")[2]
    except:
        temp = None
    return temp


def get_odds_handicap_away(js):
    try:
        temp = js["hhaodds"]["A"]
        temp = temp.partition("@")[2]
    except:
        temp = None
    return temp


def get_odds_handicap2_HG(js):
    try:
        temp = js["hdcodds"]["HG"]
    except:
        temp = None
    return temp


def get_odds_handicap2_home(js):
    try:
        temp = js["hdcodds"]["H"]
        temp = temp.partition("@")[2]
    except:
        temp = None
    return temp


def get_odds_handicap2_away(js):
    try:
        temp = js["hdcodds"]["A"]
        temp = temp.partition("@")[2]
    except:
        temp = None
    return temp


def get_score_hl(js):
    dict = {}
    for i in range(3):
        try:
            temp_line = js["hilodds"]["LINELIST"][i]["LINE"]
            temp_high = js["hilodds"]["LINELIST"][i]["H"].partition("@")[2]
            temp_low = js["hilodds"]["LINELIST"][i]["L"].partition("@")[2]
        except:
            temp_line, temp_high, temp_low = None, None, None
        dict[f"大細分界{i+1}"] = temp_line
        dict[f"大{i+1}"] = temp_high
        dict[f"細{i+1}"] = temp_low
    return dict


def get_odds_full_other(js):
    try:
        temp_home = js["crsodds"]["SM1MH"].partition("@")[2]
        temp_draw = js["crsodds"]["SM1MD"].partition("@")[2]
        temp_away = js["crsodds"]["SM1MA"].partition("@")[2]
    except:
        temp_home, temp_draw, temp_away = None, None, None
    dict = {"全場-主其他": temp_home, "全場-和其他": temp_draw, "全場-客其他": temp_away}
    return dict


def get_odds_half_other(js):
    try:
        temp_home = js["fcsodds"]["SM1MH"].partition("@")[2]
        temp_draw = js["fcsodds"]["SM1MD"].partition("@")[2]
        temp_away = js["fcsodds"]["SM1MA"].partition("@")[2]
    except:
        temp_home, temp_draw, temp_away = None, None, None
    dict = {"半場-主其他": temp_home, "半場-和其他": temp_draw, "半場-客其他": temp_away}
    return dict


def get_odds_hf(js):
    try:
        temp_hh = js["hftodds"]["HH"].partition("@")[2]
        temp_hd = js["hftodds"]["HD"].partition("@")[2]
        temp_ha = js["hftodds"]["HA"].partition("@")[2]
        temp_dh = js["hftodds"]["DH"].partition("@")[2]
        temp_dd = js["hftodds"]["DD"].partition("@")[2]
        temp_da = js["hftodds"]["DA"].partition("@")[2]
        temp_ah = js["hftodds"]["AH"].partition("@")[2]
        temp_ad = js["hftodds"]["AD"].partition("@")[2]
        temp_aa = js["hftodds"]["AA"].partition("@")[2]
    except:
        temp_hh, temp_hd, temp_ha = None, None, None
        temp_dh, temp_dd, temp_da = None, None, None
        temp_ah, temp_ad, temp_aa = None, None, None
    dict = {"半全場主主": temp_hh, "半全場主和": temp_hd, "半全場主客": temp_ha,
            "半全場和主": temp_dh, "半全場和和": temp_dd, "半全場和客": temp_da,
            "半全場客主": temp_ah, "半全場客和": temp_ad, "半全場客客": temp_aa}
    return dict


def make_value(df):
    df["全場主隊得分"] = df["全場主隊得分"].astype(float)
    df["全場客隊得分"] = df["全場客隊得分"].astype(float)
    df["上半場主隊得分"] = df["上半場主隊得分"].astype(float)
    df["上半場客隊得分"] = df["上半場客隊得分"].astype(float)
    df["讓球主客和主隊讓球"] = df["讓球主客和主隊讓球"].astype(float)
    return df


def combine(df, df2):
    df = pd.merge(df, df2, on="ID", how="left")
    df.set_index("ID", inplace=True)
    df.sort_values(by=["match_id"], inplace=True)
    df.drop_duplicates(inplace=True)
    return df


def highlight_hda_home(x):
    c1 = 'background-color: yellow'
    c2 = ''
    mask = x['全場主隊得分'] > x["全場客隊得分"]
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    df1.loc[mask, '主客和主'] = c1
    return df1


def highlight_hda_draw(x):
    c1 = 'background-color: yellow'
    c2 = ''
    mask = x['全場主隊得分'] == x["全場客隊得分"]
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    df1.loc[mask, '主客和和'] = c1
    return df1


def highlight_hda_away(x):
    c1 = 'background-color: yellow'
    c2 = ''
    mask = x['全場主隊得分'] < x["全場客隊得分"]
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    df1.loc[mask, '主客和客'] = c1
    return df1


def highlight_handicap_home(x):
    c1 = 'background-color: yellow'
    c2 = ''
    mask = x['全場主隊得分'] + x['讓球主客和主隊讓球'] > x["全場客隊得分"]
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    df1.loc[mask, '讓球主客和主勝'] = c1
    return df1


def highlight_handicap_draw(x):
    c1 = 'background-color: yellow'
    c2 = ''
    mask = x['全場主隊得分'] + x['讓球主客和主隊讓球'] == x["全場客隊得分"]
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    df1.loc[mask, '讓球主客和打和'] = c1
    return df1


def highlight_handicap_away(x):
    c1 = 'background-color: yellow'
    c2 = ''
    mask = x['全場主隊得分'] + x['讓球主客和主隊讓球'] < x["全場客隊得分"]
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    df1.loc[mask, '讓球主客和客勝'] = c1
    return df1


def make2_handicap(df):
    try:
        df[["讓球主隊讓球1", "讓球主隊讓球2"]] = df['讓球主隊讓球'].str.split('/', 1, expand=True).astype(float)
    except:
        df["讓球主隊讓球1"] = None
        df["讓球主隊讓球2"] = None
    df["讓球主勝1"] = df["讓球主勝"].astype(float)
    df["讓球客勝1"] = df["讓球客勝"].astype(float)
    df["讓球主勝2"] = df["讓球主勝"].astype(float)
    df["讓球客勝2"] = df["讓球客勝"].astype(float)
    df.drop(["讓球主隊讓球", "讓球主勝", "讓球客勝"], axis=1, inplace=True)
    return df


def make_hl_all(df):
    try:
        df[["大細分界1-1", "大細分界1-2"]] = df['大細分界1'].str.split('/', 1, expand=True).astype(float)
    except:
        df["大細分界1-1"] = None
        df["大細分界1-2"] = None
    df["大1-1"] = df["大1"].astype(float)
    df["細1-1"] = df["細1"].astype(float)
    df["大1-2"] = df["大1"].astype(float)
    df["細1-2"] = df["細1"].astype(float)
    df.drop(["大細分界1", "大1", "細1"], axis=1, inplace=True)

    try:
        df[["大細分界2-1", "大細分界2-2"]] = df['大細分界2'].str.split('/', 1, expand=True).astype(float)
    except:
        df["大細分界2-1"] = None
        df["大細分界2-2"] = None
    df["大2-1"] = df["大2"].astype(float)
    df["細2-1"] = df["細2"].astype(float)
    df["大2-2"] = df["大2"].astype(float)
    df["細2-2"] = df["細2"].astype(float)
    df.drop(["大細分界2", "大2", "細2"], axis=1, inplace=True)

    try:
        df[["大細分界3-1", "大細分界3-2"]] = df['大細分界3'].str.split('/', 1, expand=True).astype(float)
    except:
        df["大細分界3-1"] = None
        df["大細分界3-2"] = None
    df["大3-1"] = df["大3"].astype(float)
    df["細3-1"] = df["細3"].astype(float)
    df["大3-2"] = df["大3"].astype(float)
    df["細3-2"] = df["細3"].astype(float)
    df.drop(["大細分界3", "大3", "細3"], axis=1, inplace=True)
    return df


def highlight_handicap2_home1(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = x['全場主隊得分'] + x['讓球主隊讓球1'] >= x["全場客隊得分"]
        df1.loc[mask, '讓球主勝1'] = c1
    except:
        pass
    return df1


def highlight_handicap2_away1(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = x['全場主隊得分'] + x['讓球主隊讓球1'] <= x["全場客隊得分"]
        df1.loc[mask, '讓球客勝1'] = c1
    except:
        pass
    return df1


def highlight_handicap2_home2(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = x['全場主隊得分'] + x['讓球主隊讓球2'] >= x["全場客隊得分"]
        df1.loc[mask, '讓球主勝2'] = c1
    except:
        pass
    return df1


def highlight_handicap2_away2(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = x['全場主隊得分'] + x['讓球主隊讓球2'] <= x["全場客隊得分"]
        df1.loc[mask, '讓球客勝2'] = c1
    except:
        pass
    return df1


def highlight_hl_high11(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = x['全場主隊得分'] + x['全場客隊得分'] >= x["大細分界1-1"]
        df1.loc[mask, '大1-1'] = c1
    except:
        pass
    return df1


def highlight_hl_low11(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = x['全場主隊得分'] + x['全場客隊得分'] <= x["大細分界1-1"]
        df1.loc[mask, '細1-1'] = c1
    except:
        pass
    return df1


def highlight_hl_high12(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = x['全場主隊得分'] + x['全場客隊得分'] >= x["大細分界1-2"]
        df1.loc[mask, '大1-2'] = c1
    except:
        pass
    return df1


def highlight_hl_low12(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = x['全場主隊得分'] + x['全場客隊得分'] <= x["大細分界1-2"]
        df1.loc[mask, '細1-2'] = c1
    except:
        pass
    return df1


def highlight_hl_high21(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = x['全場主隊得分'] + x['全場客隊得分'] >= x["大細分界2-1"]
        df1.loc[mask, '大2-1'] = c1
    except:
        pass
    return df1


def highlight_hl_low21(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = x['全場主隊得分'] + x['全場客隊得分'] <= x["大細分界2-1"]
        df1.loc[mask, '細2-1'] = c1
    except:
        pass
    return df1


def highlight_hl_high22(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = x['全場主隊得分'] + x['全場客隊得分'] >= x["大細分界2-2"]
        df1.loc[mask, '大2-1'] = c1
    except:
        pass
    return df1


def highlight_hl_low22(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = x['全場主隊得分'] + x['全場客隊得分'] <= x["大細分界2-2"]
        df1.loc[mask, '細2-2'] = c1
    except:
        pass
    return df1


def highlight_hl_high31(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = x['全場主隊得分'] + x['全場客隊得分'] >= x["大細分界3-1"]
        df1.loc[mask, '大3-1'] = c1
    except:
        pass
    return df1


def highlight_hl_low31(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = x['全場主隊得分'] + x['全場客隊得分'] <= x["大細分界3-1"]
        df1.loc[mask, '細3-1'] = c1
    except:
        pass
    return df1


def highlight_hl_high32(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = x['全場主隊得分'] + x['全場客隊得分'] >= x["大細分界3-2"]
        df1.loc[mask, '大3-2'] = c1
    except:
        pass
    return df1


def highlight_hl_low32(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = x['全場主隊得分'] + x['全場客隊得分'] <= x["大細分界3-2"]
        df1.loc[mask, '細3-2'] = c1
    except:
        pass
    return df1


def highlight_full_home_other(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = (x['全場主隊得分'] > x['全場客隊得分']) & ((x['全場主隊得分'] > 5) | (x["全場客隊得分"] > 2))
        df1.loc[mask, '全場-主其他'] = c1
    except:
        pass
    return df1


def highlight_full_draw_other(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = (x['全場主隊得分'] == x['全場客隊得分']) & (x['全場主隊得分'] > 3)
        df1.loc[mask, '全場-和其他'] = c1
    except:
        pass
    return df1


def highlight_full_away_other(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = (x['全場主隊得分'] < x['全場客隊得分']) & ((x['全場主隊得分'] > 2) | (x["全場客隊得分"] > 5))
        df1.loc[mask, '全場-客其他'] = c1
    except:
        pass
    return df1


def highlight_half_home_other(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = (x['上半場主隊得分'] > x['上半場客隊得分']) & ((x['上半場主隊得分'] > 5) | (x["上半場客隊得分"] > 2))
        df1.loc[mask, '全場-主其他'] = c1
    except:
        pass
    return df1


def highlight_half_draw_other(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = (x['上半場主隊得分'] == x['上半場客隊得分']) & (x['上半場主隊得分'] > 3)
        df1.loc[mask, '全場-和其他'] = c1
    except:
        pass
    return df1


def highlight_half_away_other(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = (x['上半場主隊得分'] < x['上半場客隊得分']) & ((x['上半場主隊得分'] > 2) | (x["上半場客隊得分"] > 5))
        df1.loc[mask, '全場-客其他'] = c1
    except:
        pass
    return df1


def highlist_hf_hh(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = (x['上半場主隊得分'] > x['上半場客隊得分']) & (x['全場主隊得分'] > x['全場客隊得分'])
        df1.loc[mask, '半全場主主'] = c1
    except:
        pass
    return df1


def highlist_hf_hd(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = (x['上半場主隊得分'] > x['上半場客隊得分']) & (x['全場主隊得分'] == x['全場客隊得分'])
        df1.loc[mask, '半全場主和'] = c1
    except:
        pass
    return df1


def highlist_hf_ha(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = (x['上半場主隊得分'] > x['上半場客隊得分']) & (x['全場主隊得分'] < x['全場客隊得分'])
        df1.loc[mask, '半全場主客'] = c1
    except:
        pass
    return df1


def highlist_hf_dh(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = (x['上半場主隊得分'] == x['上半場客隊得分']) & (x['全場主隊得分'] > x['全場客隊得分'])
        df1.loc[mask, '半全場和主'] = c1
    except:
        pass
    return df1


def highlist_hf_dd(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = (x['上半場主隊得分'] == x['上半場客隊得分']) & (x['全場主隊得分'] == x['全場客隊得分'])
        df1.loc[mask, '半全場和和'] = c1
    except:
        pass
    return df1


def highlist_hf_da(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = (x['上半場主隊得分'] == x['上半場客隊得分']) & (x['全場主隊得分'] < x['全場客隊得分'])
        df1.loc[mask, '半全場和客'] = c1
    except:
        pass
    return df1


def highlist_hf_ah(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = (x['上半場主隊得分'] < x['上半場客隊得分']) & (x['全場主隊得分'] > x['全場客隊得分'])
        df1.loc[mask, '半全場客主'] = c1
    except:
        pass
    return df1


def highlist_hf_ad(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = (x['上半場主隊得分'] < x['上半場客隊得分']) & (x['全場主隊得分'] == x['全場客隊得分'])
        df1.loc[mask, '半全場客和'] = c1
    except:
        pass
    return df1


def highlist_hf_aa(x):
    c1 = 'background-color: yellow'
    c2 = ''
    df1 = pd.DataFrame(c2, index=df.index, columns=df.columns)
    try:
        mask = (x['上半場主隊得分'] < x['上半場客隊得分']) & (x['全場主隊得分'] < x['全場客隊得分'])
        df1.loc[mask, '半全場客客'] = c1
    except:
        pass
    return df1


def apply_color(df):
    df = df.style.apply(highlight_hda_home, axis=None) \
    .apply(highlight_hda_draw, axis=None) \
    .apply(highlight_hda_away, axis=None) \
    .apply(highlight_handicap_home, axis=None) \
    .apply(highlight_handicap_draw, axis=None) \
    .apply(highlight_handicap_away, axis=None) \
    .apply(highlight_handicap2_home1, axis=None) \
    .apply(highlight_handicap2_away1, axis=None) \
    .apply(highlight_handicap2_home2, axis=None) \
    .apply(highlight_handicap2_away2, axis=None) \
    .apply(highlight_hl_high11, axis=None) \
    .apply(highlight_hl_low11, axis=None) \
    .apply(highlight_hl_high12, axis=None) \
    .apply(highlight_hl_low12, axis=None) \
    .apply(highlight_hl_high21, axis=None) \
    .apply(highlight_hl_low21, axis=None) \
    .apply(highlight_hl_high22, axis=None) \
    .apply(highlight_hl_low22, axis=None) \
    .apply(highlight_hl_high31, axis=None) \
    .apply(highlight_hl_low31, axis=None) \
    .apply(highlight_hl_high32, axis=None) \
    .apply(highlight_hl_low32, axis=None) \
    .apply(highlight_full_home_other, axis=None) \
    .apply(highlight_full_draw_other, axis=None) \
    .apply(highlight_full_away_other, axis=None) \
    .apply(highlight_half_home_other, axis=None) \
    .apply(highlight_half_draw_other, axis=None) \
    .apply(highlight_half_away_other, axis=None) \
    .apply(highlist_hf_hh, axis=None) \
    .apply(highlist_hf_hd, axis=None) \
    .apply(highlist_hf_ha, axis=None) \
    .apply(highlist_hf_dh, axis=None) \
    .apply(highlist_hf_dd, axis=None) \
    .apply(highlist_hf_da, axis=None) \
    .apply(highlist_hf_ah, axis=None) \
    .apply(highlist_hf_ad, axis=None) \
    .apply(highlist_hf_aa, axis=None)
    return df


def order(df):
    df = df[['match_id', "比賽日期", "聯賽", "主隊", "客隊", "上半場主隊得分", "上半場客隊得分", "全場主隊得分", "全場客隊得分",
             "主客和主", "主客和和", "主客和客",
             "半場-主其他", "半場-和其他", "半場-客其他",
             "全場-主其他", "全場-和其他", "全場-客其他",
             "讓球主客和主隊讓球", "讓球主客和主勝", "讓球主客和打和", "讓球主客和客勝",
             "讓球主隊讓球1", "讓球主勝1", "讓球客勝1",
             "讓球主隊讓球2", "讓球主勝2", "讓球客勝2",
             "大細分界1-1", "大1-1", "細1-1",
             "大細分界1-2", "大1-2", "細1-2",
             "大細分界2-1", "大2-1", "細2-1",
             "大細分界2-2", "大2-2", "細2-2",
             "大細分界3-1", "大3-1", "細3-1",
             "大細分界3-2", "大3-2", "細3-2",
             "半全場主主", "半全場主和", "半全場主客", "半全場和主", "半全場和和", "半全場和客", "半全場客主", "半全場客和", "半全場客客"]]
    return df


def save_df(df):
    s = ''.join(letter for letter in start_date if letter.isalnum())
    e = ''.join(letter for letter in end_date if letter.isalnum())
    if get_all:
        df.to_excel(f"Excel/result_{s}_{e}_full.xlsx")
    else:
        num = len(league)
        df.to_excel(f"Excel/result_{s}_{e}_{num}.xlsx")


if __name__ == '__main__':
    print("Start downloading...")
    date_list = gen_date_list(start_date, end_date)

    df = pd.DataFrame({})
    df_odds = pd.DataFrame({})
    for day in date_list:
        percent = round(100 * date_list.index(day) / len(date_list), 2)
        pages = get_total_page(day)
        df_day = pd.DataFrame(get_data_in_page(pages))
        df = pd.concat([df, df_day])
        print(f"Downloaded data of {day}.  {percent}% finished.")

        for id in df_day["ID"]:
            js_odd = get_odd_json(id)
            tempdata = get_odd_data(js_odd, id)
            df_match_odd = pd.DataFrame(tempdata, index=[0])
            df_odds = pd.concat([df_odds, df_match_odd])

    print("Processing...")
    df = df.drop_duplicates()
    df = combine(df, df_odds)
    df = make_value(df)
    print("Still Processing...")
    df = make2_handicap(df)
    df = make_hl_all(df)
    df = order(df).reset_index()
    print("Applying Color...")
    df = apply_color(df)
    save_df(df)
    print("File saved.")

    used_time = time.time() - st
    used_min = int(used_time / 60)
    used_sec = round(used_time % 60, 3)
    print(f"Used {used_min} minutes {used_sec} seconds to run this script.")
