import streamlit as st
import random
import json
from datetime import datetime

# ---------------------- 菜品数据库 陕科大食堂 ----------------------
food_list = [
    {"id":1,"name":"兰州拉面","price":10,"taste":["面食","清淡"],"place":"食堂一楼","desc":"分量足，可加辣"},
    {"id":2,"name":"麻辣香锅","price":16,"taste":["麻辣","米饭"],"place":"食堂二楼","desc":"自选荤素"},
    {"id":3,"name":"杂粮煎饼","price":6,"taste":["小吃"],"place":"食堂三楼","desc":"脆饼款，早餐优选"},
    {"id":4,"name":"番茄鸡蛋面","price":11,"taste":["酸甜","面食"],"place":"食堂一楼","desc":"汤汁浓郁"},
    {"id":5,"name":"黄焖鸡米饭","price":14,"taste":["麻辣","米饭"],"place":"食堂二楼","desc":"配米饭"},
    {"id":6,"name":"粥+包子套餐","price":7,"taste":["清淡","小吃"],"place":"食堂一楼","desc":"适合早餐"},
    {"id":7,"name":"馄饨","price":9,"taste":["清淡"],"place":"食堂三楼","desc":"鲜骨汤"},
    {"id":8,"name":"奥尔良烤肉饭","price":13,"taste":["酸甜","米饭"],"place":"食堂二楼","desc":"配菜丰富"},
    {"id":9,"name":"麻辣烫","price":15,"taste":["麻辣"],"place":"食堂二楼","desc":"自选菜"},
    {"id":10,"name":"肉夹馍+凉皮","price":12,"taste":["小吃"],"place":"食堂一楼","desc":"经典搭配"}
]

# ---------------------- 本地持久化存储（收藏、历史） ----------------------
def load_data():
    try:
        with open("data.json","r",encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"collect": [], "history": []}

def save_data(data):
    with open("data.json","w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

data = load_data()

# ---------------------- 筛选函数 ----------------------
def filter_food(budget, taste_select, people):
    res = []
    for food in food_list:
        if food["price"] > budget:
            continue
        if taste_select != "不限制" and taste_select not in food["taste"]:
            continue
        res.append(food)
    return res

# 随机挑选1~3个
def random_pick(foods):
    if not foods:
        return []
    cnt = random.randint(1,3)
    return random.sample(foods, k=min(cnt, len(foods)))

# ---------------------- 页面UI ----------------------
st.set_page_config(page_title="今天吃什么｜陕科大干饭助手", layout="wide")
st.title("🍚 今天吃什么？决策助手")
st.subheader("陕科大校园版｜选择困难终结者")

tab1, tab2, tab3 = st.tabs(["🎲 推荐", "❤️ 我的收藏", "🕒 历史记录"])

with tab1:
    col1,col2,col3 = st.columns(3)
    with col1:
        budget = st.number_input("单人预算上限（元）", min_value=1, value=15, step=1)
    with col2:
        taste_opt = ["不限制","清淡","麻辣","酸甜","面食","米饭","小吃"]
        taste_select = st.selectbox("口味偏好", taste_opt)
    with col3:
        people_opt = ["1人","2人","3人及以上"]
        people = st.selectbox("就餐人数", people_opt)

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        run = st.button("✨ 帮我选", type="primary")
    with btn_col2:
        refresh = st.button("🔄 换一批")

    if run or refresh:
        match_food = filter_food(budget, taste_select, people)
        result = random_pick(match_food)
        st.session_state["last_result"] = result

        # 写入历史记录
        if result:
            record = {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "foods": result
            }
            data["history"].insert(0, record)
            if len(data["history"]) > 10:
                data["history"].pop()
            save_data(data)

    show_result = st.session_state.get("last_result", [])
    st.divider()
    st.markdown("### 🎯 推荐结果")
    if not show_result:
        st.info("点击【帮我选】获取推荐！")
    else:
        for food in show_result:
            c1,c2 = st.columns([4,1])
            with c1:
                tags = " ".join(food["taste"])
                st.markdown(f"""
                **{food['name']}**
                💰 {food['price']}元｜📍{food['place']}
                标签：{tags}
                > {food['desc']}
                """)
            with c2:
                if st.button("收藏", key=f"col_{food['id']}"):
                    ids = [x["id"] for x in data["collect"]]
                    if food["id"] not in ids:
                        data["collect"].append(food)
                        save_data(data)
                        st.rerun()
            st.divider()

with tab2:
    st.markdown("### ❤️ 收藏列表")
    if not data["collect"]:
        st.info("还没有收藏菜品")
    else:
        for food in data["collect"]:
            st.markdown(f"""
            **{food['name']}**
            💰 {food['price']}元｜📍{food['place']}
            > {food['desc']}
            """)
            if st.button("取消收藏", key=f"del_{food['id']}"):
                data["collect"] = [x for x in data["collect"] if x["id"] != food["id"]]
                save_data(data)
                st.rerun()
            st.divider()

with tab3:
    st.markdown("### 🕒 推荐历史（最多保存10条）")
    if not data["history"]:
        st.info("暂无历史")
    else:
        for item in data["history"]:
            st.markdown(f"⏰ {item['time']}")
            for f in item["foods"]:
                st.markdown(f"- {f['name']}｜{f['price']}元｜{f['place']}")
            st.divider()
