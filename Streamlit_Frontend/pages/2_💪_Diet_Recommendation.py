import json
import time

import requests
import streamlit as st
import pandas as pd
from Generate_Recommendations import Generator
from random import uniform as rnd
from ImageFinder.ImageFinder import get_images_links as find_image
from streamlit_echarts import st_echarts

st.set_page_config(page_title="自动饮食推荐", page_icon="💪", layout="wide")

nutritions_values = ['Calories', 'FatContent', 'SaturatedFatContent', 'CholesterolContent', 'SodiumContent', 'CarbohydrateContent', 'FiberContent', 'SugarContent', 'ProteinContent']
nutrition_mapping = {
            'Calories': '卡路里',
            'FatContent': '脂肪含量',
            'SaturatedFatContent': '饱和脂肪含量',
            'CholesterolContent': '胆固醇含量',
            'SodiumContent': '钠含量',
            'CarbohydrateContent': '碳水化合物含量',
            'FiberContent': '纤维含量',
            'SugarContent': '糖分含量',
            'ProteinContent': '蛋白质含量'
        }
# Streamlit states initialization
if 'person' not in st.session_state:
    st.session_state.generated = False
    st.session_state.recommendations = None
    st.session_state.person = None
    st.session_state.weight_loss_option = None


class Person:

    def __init__(self, age, height, weight, gender, activity, meals_calories_perc, weight_loss):
        self.age = age
        self.height = height
        self.weight = weight
        self.gender = gender
        self.activity = activity
        self.meals_calories_perc = meals_calories_perc
        self.weight_loss = weight_loss

    def calculate_bmi(self, ):
        bmi = round(self.weight / ((self.height / 100) ** 2), 2)
        return bmi

    def display_result(self, ):
        bmi = self.calculate_bmi()
        bmi_string = f'{bmi} kg/m²'
        if bmi < 18.5:
            category = '体重过轻'
            color = 'Red'
        elif 18.5 <= bmi < 25:
            category = '正常'
            color = 'Green'
        elif 25 <= bmi < 30:
            category = '超重'
            color = 'Yellow'
        else:
            category = '肥胖'
            color = 'Red'
        return bmi_string, category, color

    def calculate_bmr(self):
        if self.gender == '男':
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161
        return bmr

    def calories_calculator(self):
        activites = ['很少/几乎不运动', '轻度运动', '适度运动(3-5天/周)', '经常运动 (6-7天/周)', '高强度活动(从事高强度的体力工作)']
        weights = [1.2, 1.375, 1.55, 1.725, 1.9]
        weight = weights[activites.index(self.activity)]
        maintain_calories = self.calculate_bmr() * weight
        return maintain_calories

    def generate_recommendations(self, ):
        total_calories = self.weight_loss * self.calories_calculator()
        recommendations = []
        for meal in self.meals_calories_perc:
            meal_calories = self.meals_calories_perc[meal] * total_calories
            if meal == '早餐':
                recommended_nutrition = [meal_calories, rnd(10, 30), rnd(0, 4), rnd(0, 30), rnd(0, 400), rnd(40, 75),
                                         rnd(4, 10), rnd(0, 10), rnd(30, 100)]
            elif meal == '午餐':
                recommended_nutrition = [meal_calories, rnd(20, 40), rnd(0, 4), rnd(0, 30), rnd(0, 400), rnd(40, 75),
                                         rnd(4, 20), rnd(0, 10), rnd(50, 175)]
            elif meal == '晚餐':
                recommended_nutrition = [meal_calories, rnd(20, 40), rnd(0, 4), rnd(0, 30), rnd(0, 400), rnd(40, 75),
                                         rnd(4, 20), rnd(0, 10), rnd(50, 175)]
            else:
                recommended_nutrition = [meal_calories, rnd(10, 30), rnd(0, 4), rnd(0, 30), rnd(0, 400), rnd(40, 75),
                                         rnd(4, 10), rnd(0, 10), rnd(30, 100)]
            generator = Generator(recommended_nutrition)
            response = generator.generate()
            recommended_recipes = response.json()['output']
            recommendations.append(recommended_recipes)
        for recommendation in recommendations:
            for recipe in recommendation:
                recipe['image_link'] = find_image(recipe['Name'])
        return recommendations


class Display:
    def __init__(self):
        self.plans = ["保持当前体重", "轻度减重", "减重", "高强度减重"]
        self.weights = [1, 0.9, 0.8, 0.6]
        self.losses = ['-0 kg/周', '-0.25 kg/周', '-0.5 kg/周', '-1 kg/周']
        pass

    def display_bmi(self, person):
        st.header('BMI计算器')
        bmi_string, category, color = person.display_result()
        st.metric(label="身体质量指数-Body Mass Index (BMI)", value=bmi_string)
        new_title = f'<p style="font-family:sans-serif; color:{color}; font-size: 25px;">{category}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        st.markdown(
            """
            健康的BMI范围: 18.5 kg/m² - 25 kg/m².
            """)

    def display_calories(self, person):
        st.header('卡路里计算器')
        maintain_calories = person.calories_calculator()
        st.write(
            '该结果显示了一些每日卡路里估计值，这些估计值可以作为每天消耗多少卡路里以保持、减轻或增加体重的指导方针。')
        for plan, weight, loss, col in zip(self.plans, self.weights, self.losses, st.columns(4)):
            with col:
                st.metric(label=plan, value=f'{round(maintain_calories * weight)} 卡路里/天', delta=loss,
                          delta_color="inverse")

    def display_recommendation(self, person, recommendations):
        st.header('饮食推荐')
        with st.spinner('正在生成饮食推荐...'):
            meals = person.meals_calories_perc
            st.subheader('推荐食谱:')
            for meal_name, column, recommendation in zip(meals, st.columns(len(meals)), recommendations):
                with column:
                    # st.markdown(f'<div style="text-align: center;">{meal_name.upper()}</div>', unsafe_allow_html=True)
                    st.markdown(f'##### {meal_name.upper()}')
                    for recipe in recommendation:
                        recipe_name = recipe['Name']
                        expander = st.expander(recipe_name)
                        recipe_link = recipe['image_link']
                        recipe_img = f'<div><center><img src={recipe_link} alt={recipe_name}></center></div>'
                        nutritions_df = pd.DataFrame({nutrition_mapping[value]: [recipe[value]] for value in nutritions_values})

                        expander.markdown(recipe_img, unsafe_allow_html=True)
                        expander.markdown(
                            f'<h5 style="text-align: center;font-family:sans-serif;">营养价值 (g):</h5>',
                            unsafe_allow_html=True)
                        expander.dataframe(nutritions_df, hide_index=True)
                        expander.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">配料表:</h5>',
                                          unsafe_allow_html=True)
                        for ingredient in recipe['RecipeIngredientParts']:
                            expander.markdown(f"""
                                        - {ingredient}
                            """)
                        expander.markdown(
                            f'<h5 style="text-align: center;font-family:sans-serif;">制作步骤:</h5>',
                            unsafe_allow_html=True)
                        for instruction in recipe['RecipeInstructions']:
                            expander.markdown(f"""
                                        - {instruction}
                            """)
                        expander.markdown(
                            f'<h5 style="text-align: center;font-family:sans-serif;">制作和准备时长:</h5>',
                            unsafe_allow_html=True)
                        expander.markdown(f"""
                                - 制作时长       : {recipe['CookTime']}min
                                - 准备时长       : {recipe['PrepTime']}min
                                - 总时长         : {recipe['TotalTime']}min
                            """)

    def display_meal_choices(self, person, recommendations):
        st.subheader('选择您心仪的食品:')
        # Display meal compositions choices
        if len(recommendations) == 3:
            breakfast_column, launch_column, dinner_column = st.columns(3)
            with breakfast_column:
                breakfast_choice = st.selectbox(f'选择您的早餐:',
                                                [recipe['Name'] for recipe in recommendations[0]])
            with launch_column:
                launch_choice = st.selectbox(f'选择您的午餐:', [recipe['Name'] for recipe in recommendations[1]])
            with dinner_column:
                dinner_choice = st.selectbox(f'选择您的晚餐:', [recipe['Name'] for recipe in recommendations[2]])
            choices = [breakfast_choice, launch_choice, dinner_choice]
        elif len(recommendations) == 4:
            breakfast_column, morning_snack, launch_column, dinner_column = st.columns(4)
            with breakfast_column:
                breakfast_choice = st.selectbox(f'选择您的早餐:',
                                                [recipe['Name'] for recipe in recommendations[0]])
            with morning_snack:
                morning_snack = st.selectbox(f'选择您的早餐点心:',
                                             [recipe['Name'] for recipe in recommendations[1]])
            with launch_column:
                launch_choice = st.selectbox(f'选择您的午餐:', [recipe['Name'] for recipe in recommendations[2]])
            with dinner_column:
                dinner_choice = st.selectbox(f'选择您的晚餐:', [recipe['Name'] for recipe in recommendations[3]])
            choices = [breakfast_choice, morning_snack, launch_choice, dinner_choice]
        else:
            breakfast_column, morning_snack, launch_column, afternoon_snack, dinner_column = st.columns(5)
            with breakfast_column:
                breakfast_choice = st.selectbox(f'请选择您的早餐:',
                                                [recipe['Name'] for recipe in recommendations[0]])
            with morning_snack:
                morning_snack = st.selectbox(f'请选择您的早餐点心:',
                                             [recipe['Name'] for recipe in recommendations[1]])
            with launch_column:
                launch_choice = st.selectbox(f'请选择您的午餐:', [recipe['Name'] for recipe in recommendations[2]])
            with afternoon_snack:
                afternoon_snack = st.selectbox(f'选择您的下午茶:',
                                               [recipe['Name'] for recipe in recommendations[3]])
            with dinner_column:
                dinner_choice = st.selectbox(f'选择您的晚餐:', [recipe['Name'] for recipe in recommendations[4]])
            choices = [breakfast_choice, morning_snack, launch_choice, afternoon_snack, dinner_choice]

            # Calculating the sum of nutritional values of the choosen recipes
        total_nutrition_values = {nutrition_value: 0 for nutrition_value in nutritions_values}
        for choice, meals_ in zip(choices, recommendations):
            for meal in meals_:
                if meal['Name'] == choice:
                    for nutrition_value in nutritions_values:
                        total_nutrition_values[nutrition_value] += meal[nutrition_value]

        total_calories_chose = total_nutrition_values['Calories']
        loss_calories_chose = round(person.calories_calculator() * person.weight_loss)

        # Display corresponding graphs
        st.markdown(
            f'<h5 style="text-align: center;font-family:sans-serif;">食品中的总热量 vs {st.session_state.weight_loss_option}的总热量:</h5>',
            unsafe_allow_html=True)
        total_calories_graph_options = {
            "xAxis": {
                "type": "category",
                "data": ['你选择的卡路里总量', f"{st.session_state.weight_loss_option}的卡路里总量"],
            },
            "yAxis": {"type": "value"},
            "series": [
                {
                    "data": [
                        {"value": total_calories_chose,
                         "itemStyle": {"color": ["#33FF8D", "#FF3333"][total_calories_chose > loss_calories_chose]}},
                        {"value": loss_calories_chose, "itemStyle": {"color": "#3339FF"}},
                    ],
                    "type": "bar",
                }
            ],
        }
        st_echarts(options=total_calories_graph_options, height="400px", )
        st.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">营养价值:</h5>',
                    unsafe_allow_html=True)

        nutritions_graph_options = {
            "tooltip": {"trigger": "item"},
            "legend": {"top": "5%", "left": "center"},
            "series": [
                {
                    "name": "营养含量",
                    "type": "pie",
                    "radius": ["40%", "70%"],
                    "avoidLabelOverlap": False,
                    "itemStyle": {
                        "borderRadius": 10,
                        "borderColor": "#fff",
                        "borderWidth": 2,
                    },
                    "label": {"show": False, "position": "center"},
                    "emphasis": {
                        "label": {"show": True, "fontSize": "40", "fontWeight": "bold"}
                    },
                    "labelLine": {"show": False},
                    "data": [
                        {"value": round(total_nutrition_values[total_nutrition_value]), "name": nutrition_mapping[total_nutrition_value]}
                        for total_nutrition_value in total_nutrition_values],
                }
            ],
        }
        st_echarts(options=nutritions_graph_options, height="500px", )


display = Display()
title = "<h1 style='text-align: center;'>自动饮食推荐</h1>"
st.markdown(title, unsafe_allow_html=True)
with st.form("推荐表"):
    st.write("请选择您的身体参数并单击生成按钮以生成专属于您的个人食谱")
    age = st.number_input('年龄', min_value=2, max_value=120, step=1, value=24)
    height = st.number_input('身高(cm)', min_value=50, max_value=300, step=1, value=185)
    weight = st.number_input('体重(kg)', min_value=10, max_value=300, step=1, value=75)
    gender = st.radio('性别', ('男', '女'))
    activity = st.select_slider('运动强度',
                                options=['很少/几乎不运动', '轻度运动', '适度运动(3-5天/周)',
                                         '经常运动 (6-7天/周)',
                                         '高强度活动(从事高强度的体力工作)'])
    option = st.selectbox('选择您的减肥计划', display.plans)
    st.session_state.weight_loss_option = option
    weight_loss = display.weights[display.plans.index(option)]
    number_of_meals = st.slider('一日几餐？', min_value=3, max_value=5, step=1, value=3)
    if number_of_meals == 3:
        meals_calories_perc = {'早餐': 0.35, '午餐': 0.40, '晚餐': 0.25}
    elif number_of_meals == 4:
        meals_calories_perc = {'早餐': 0.30, '早餐点心': 0.05, '午餐': 0.40, '晚餐': 0.25}
    else:
        meals_calories_perc = {'早餐': 0.30, '早餐点心': 0.05, '午餐': 0.40, '下午茶': 0.05,
                               '晚餐': 0.20}
    generated = st.form_submit_button("生成您的食谱！")
if generated:
    st.session_state.generated = True
    person = Person(age, height, weight, gender, activity, meals_calories_perc, weight_loss)
    with st.container():
        display.display_bmi(person)
    with st.container():
        display.display_calories(person)
    with st.spinner('请稍等，正在生成推荐菜品...'):
        recommendations = person.generate_recommendations()
        st.session_state.recommendations = recommendations
        st.session_state.person = person

if st.session_state.generated:
    with st.container():
        display.display_recommendation(st.session_state.person, st.session_state.recommendations)
        st.success('推荐菜品生成成功!', icon="✅")
    with st.container():
        display.display_meal_choices(st.session_state.person, st.session_state.recommendations)
