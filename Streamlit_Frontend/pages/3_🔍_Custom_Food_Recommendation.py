import streamlit as st
from Generate_Recommendations import Generator
from ImageFinder.ImageFinder import get_images_links as find_image
import pandas as pd
from streamlit_echarts import st_echarts

st.set_page_config(page_title="定制食谱推荐", page_icon="🔍", layout="wide")
nutrition_values = ['Calories', 'FatContent', 'SaturatedFatContent', 'CholesterolContent', 'SodiumContent',
                    'CarbohydrateContent', 'FiberContent', 'SugarContent', 'ProteinContent']
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
if 'generated' not in st.session_state:
    st.session_state.generated = False
    st.session_state.recommendations = None


class Recommendation:
    def __init__(self, nutrition_list, nb_recommendations, ingredient_txt):
        self.nutrition_list = nutrition_list
        self.nb_recommendations = nb_recommendations
        self.ingredient_txt = ingredient_txt
        pass

    def generate(self, ):
        params = {'n_neighbors': self.nb_recommendations, 'return_distance': False}
        ingredients = self.ingredient_txt.split(';')
        generator = Generator(self.nutrition_list, ingredients, params)
        recommendations = generator.generate()
        recommendations = recommendations.json()['output']
        if recommendations != None:
            for recipe in recommendations:
                recipe['image_link'] = find_image(recipe['Name'])
        return recommendations


class Display:
    def __init__(self):
        self.nutrition_values = nutrition_values

    def display_recommendation(self, recommendations):
        st.subheader('推荐食谱如下:')
        if recommendations is not None:
            if len(recommendations) < 3:
                cols = st.columns(len(recommendations))
            else:
                cols = st.columns(3)

            rows = (len(recommendations) + 2) // 3
            for i, recipe in enumerate(recommendations):
                column = cols[i % 3]
                with column:
                    # for recipe in recommendations[rows * row:rows * (row + 1)]:
                    recipe_name = recipe['Name']
                    expander = st.expander(recipe_name)
                    recipe_link = recipe['image_link']
                    recipe_img = f'<div><center><img src={recipe_link} alt={recipe_name}></center></div>'
                    nutritions_df = pd.DataFrame({nutrition_mapping[value]: [recipe[value]] for value in nutrition_values})

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
                    expander.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">制作步骤:</h5>',
                                      unsafe_allow_html=True)
                    for instruction in recipe['RecipeInstructions']:
                        expander.markdown(f"""
                                        - {instruction}
                            """)
                    expander.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">烹饪制作时间:</h5>',
                                      unsafe_allow_html=True)
                    expander.markdown(f"""
                                - 制作时长       : {recipe['CookTime']}min
                                - 准备时长       : {recipe['PrepTime']}min
                                - 总时长         : {recipe['TotalTime']}min
                            """)
        else:
            st.info('Couldn\'t find any recipes with the specified ingredients', icon="🙁")

    def display_overview(self, recommendations):
        if recommendations != None:
            st.subheader('营养成分含量:')
            col1, col2, col3 = st.columns(3)
            with col2:
                selected_recipe_name = st.selectbox('选择一个食物以查看其营养价值分布',
                                                    [recipe['Name'] for recipe in recommendations])
            st.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">营养价值:</h5>',
                        unsafe_allow_html=True)

            for recipe in recommendations:
                if recipe['Name'] == selected_recipe_name:
                    selected_recipe = recipe
            options = {
                "title": {"text": "营养价值", "subtext": f"{selected_recipe_name}", "left": "center"},
                "tooltip": {"trigger": "item"},
                "legend": {"orient": "vertical", "left": "left", },
                "series": [
                    {
                        "name": "营养价值",
                        "type": "pie",
                        "radius": "50%",
                        "data": [{"value": selected_recipe[nutrition_value], "name": nutrition_mapping[nutrition_value]} for
                                 nutrition_value in self.nutrition_values],
                        "emphasis": {
                            "itemStyle": {
                                "shadowBlur": 10,
                                "shadowOffsetX": 0,
                                "shadowColor": "rgba(0, 0, 0, 0.5)",
                            }
                        },
                    }
                ],
            }
            st_echarts(options=options, height="600px", )
            st.caption('您可以从图例中选择/取消选择项目(营养值)。')


title = "<h1 style='text-align: center;'>定制食谱推荐</h1>"
st.markdown(title, unsafe_allow_html=True)

display = Display()

with st.form("recommendation_form"):
    st.header('营养价值:')
    Calories = st.slider('卡路里Calories', 0, 2000, 500)
    FatContent = st.slider('脂肪含量FatContent', 0, 100, 50)
    SaturatedFatContent = st.slider('饱和脂肪含量SaturatedFatContent', 0, 13, 0)
    CholesterolContent = st.slider('胆固醇含量CholesterolContent', 0, 300, 0)
    SodiumContent = st.slider('钠含量SodiumContent', 0, 2300, 400)
    CarbohydrateContent = st.slider('碳水化合物含量CarbohydrateContent', 0, 325, 100)
    FiberContent = st.slider('纤维含量FiberContent', 0, 50, 10)
    SugarContent = st.slider('含糖量SugarContent', 0, 40, 10)
    ProteinContent = st.slider('蛋白质含量ProteinContent', 0, 40, 10)
    nutritions_values_list = [Calories, FatContent, SaturatedFatContent, CholesterolContent, SodiumContent,
                              CarbohydrateContent, FiberContent, SugarContent, ProteinContent]
    st.header('个性化推荐选项(请选择您的偏好):')
    nb_recommendations = st.slider('推荐数量', 5, 20, step=5)
    ingredient_txt = st.text_input('指定建议中包含的成分，以“;”分隔(英文):',
                                   placeholder='成分1;成分2;...')
    st.caption('例: Milk;eggs;butter;chicken...')
    generated = st.form_submit_button("生成推荐食谱!")
if generated:
    with st.spinner('推荐食谱生成中...'):
        recommendation = Recommendation(nutritions_values_list, nb_recommendations, ingredient_txt)
        recommendations = recommendation.generate()
        st.session_state.recommendations = recommendations
    st.session_state.generated = True

if st.session_state.generated:
    with st.container():
        display.display_recommendation(st.session_state.recommendations)
    with st.container():
        display.display_overview(st.session_state.recommendations)
