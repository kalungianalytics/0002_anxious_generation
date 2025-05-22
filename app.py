# === Imports ===
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from highlight_text import ax_text
from matplotlib.patches import FancyArrowPatch

# === Utility Function ===
def add_annotation(ax, x, y, text, highlight_word, dx=0.5, dy=5, color="#e41a1c", curve=0.2,
                   arrow_position="bottom", lw=1, alpha=1.0, show_arrow=True):
    """
    Adds a styled annotation with curved arrow and optional highlighted words.
    """
    text_x = x + dx
    text_y = y + dy

    # Normalize input
    if isinstance(highlight_word, str):
        highlight_word = [highlight_word]
    if isinstance(color, str):
        color = [color] * len(highlight_word)

    highlight_textprops = [{"color": c, "weight": "bold"} for c in color]

    vertical_alignment = "bottom" if arrow_position == "bottom" else "top"
    padding = 0.5 if arrow_position == "top" else -0.5

    ax_text(
        x=text_x,
        y=text_y,
        s=text,
        ax=ax,
        highlight_textprops=highlight_textprops,
        delim=("{", "}"),
        fontsize=9,
        fontname="DejaVu Sans",
        color="#4d4d4d",
        ha="center",
        va=vertical_alignment,
        textalign="center"
    )

    if show_arrow:
        arrow = FancyArrowPatch(
            posA=(text_x, text_y + padding),
            posB=(x, y + 0.5),
            connectionstyle=f"arc3,rad={curve}",
            arrowstyle='->',
            color=color[0],
            lw=lw,
            alpha=alpha,
            mutation_scale=10
        )
        ax.add_patch(arrow)

# === Constants and Styles ===
GREY10 = "#1a1a1a"
GREY30 = "#4d4d4d"
custom_colors = {
    'FEMALE TOTAL': '#984ea3', 'MALE TOTAL': '#377eb8', 'ALL TOTAL': '#2B2B2B',
    'Girls': '#984ea3', 'Boys': '#377eb8', 'All': '#2B2B2B'
}
label_map = {'FEMALE TOTAL': 'Girls', 'MALE TOTAL': 'Boys', 'ALL TOTAL': 'All'}
order = ['No usage', '<1\u202fh', '1 to <3\u202fh', '3 to <5\u202fh', '>5\u202fh']

# === Streamlit Setup ===
st.set_page_config(layout="wide", page_title="Teen Depression Visualization")
st.title("Teen Depression and Social Media Use")
st.markdown("This app displays two linked charts: one showing UK data by social media usage, and another showing trends over time in the US.")

# === Layout Columns ===
col1, col2, col3 = st.columns([0.025, 0.95, 0.025])

# === Radio Button Selector ===
with col2:
    view_option = st.radio(
        "Select view:",
        options=["All Teens", "Split by Gender", "All Categories", "Percent per category by Gender (UK Only)"],
        index=0,
        horizontal=True
    )

# === Category Selection ===
if view_option == "All Teens":
    uk_categories = ["All"]
    us_categories = ["ALL TOTAL"]
elif view_option == "Split by Gender":
    uk_categories = ["Boys", "Girls"]
    us_categories = ["MALE TOTAL", "FEMALE TOTAL"]
elif view_option == "All Categories":
    uk_categories = ["All", "Boys", "Girls"]
    us_categories = ["ALL TOTAL", "MALE TOTAL", "FEMALE TOTAL"]
else:
    uk_categories = ["Girls %", "Boys %"]
    us_categories = []

# === Load and Prepare Data ===
df1 = pd.read_csv("data_social_media_use.csv")
df2 = pd.read_csv("flat_data.csv")

df1_melted = df1.melt(id_vars=['Social media use in hours/weekday'], var_name='Category', value_name='value')
pivot1 = df1_melted.pivot(index='Social media use in hours/weekday', columns='Category', values='value')
pivot1 = pivot1.reindex(order)
x1 = list(range(len(order)))

df_filtered = df2[df2['Category'].isin(us_categories)]
pivot2 = df_filtered.pivot(index='Category', columns='Year', values='Value')

# === Create Figure and Axes ===
fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(12, 6))
fig.patch.set_facecolor('seashell')
for ax in [ax1, ax2]:
    ax.set_facecolor('seashell')
    ax.spines[['right', 'top', 'left', 'bottom']].set_visible(False)

# === Plot UK Data ===
for category in uk_categories:
    if category not in pivot1.columns:
        continue
    y = pivot1[category].values
    color_key = category.replace(" %", "")
    ax1.plot(x1, y, label=category, linestyle='-', color=custom_colors.get(color_key, GREY30))
    ax1.plot(x1[-1], y[-1], 'o', color=custom_colors.get(color_key, GREY30))
    ax1.text(x1[-1] + 0.2, y[-1], category, color=custom_colors.get(color_key, GREY30), fontsize=10, va='center')

ax1.set_xlim(-0.5, len(order))
ax1.set_xticks(x1)
ax1.set_xticklabels(order)

# === Dynamic Annotations for UK ===
if view_option == "All Teens":
    y = pivot1["All"].values
    add_annotation(
    ax=ax1,
    x=x1[3],
    y=y[3],
    text="{Significant increase} in \nteen depression when \n{Social Media} usage \nexceeded 3 hours a day.",
    highlight_word=["Significant increase", "Social Media"],
    dx=-2,
    dy=11,
    color=[ "#2b2b2b", "#2b2b2b"],  # or any two colors you prefer
    arrow_position="bottom",
    alpha=0.8
    )

elif view_option == "Split by Gender":
    girls = pivot1["Girls"].values
    boys = pivot1["Boys"].values
    # Annotation 1: Boys line
    add_annotation(
        ax=ax1,
        x=x1[3],
        y=y[3],
        text="{Sharp increase} for girls \nas usage increases.",
        highlight_word=["Sharp increase"],
        dx=-2,
        dy=8,
        color=["#984ea3"],  # or any two colors you prefer
        arrow_position="bottom",
        alpha=0.8
    )
    
    # Annotation 2: Boys line with inverted curve and arrow from top
    add_annotation(
        ax=ax1,
        x=x1[4],
        y=y[3],
        text="{Gap between} \ngenders c.25% at \nheaviest use point.",
        highlight_word=["Gap Between"],
        dx=-1,
        dy=-5.8,
        color=["#377eb8"],
        arrow_position="top",  # arrow from top of the label
        curve=-0.2,             # <- invert curve direction
        alpha=0.8,
    )


elif view_option == "All Categories":
    all_val = pivot1["All"].values
    girls = pivot1["Girls"].values
    add_annotation(
        ax=ax1,
        x=x1[3],
        y=y[3],
        text="Although a great starting point, \nthe {All line} hides a {significant insight}: \n{the disparity of impact by gender}.",
        highlight_word=["significant insight", "All line", "the disparity of impact by gender"],
        dx=-1.5,
        dy=7,
        color=["#984ea3", "#984ea3", "#2b2b2b"],  # or any two colors you prefer
        arrow_position="bottom",
        show_arrow=False,
        alpha=0.8
    )

elif view_option == "Percent per category by Gender (UK Only)":
    if "Girls %" in pivot1.columns:
        girls_pct = pivot1["Girls %"].values
        add_annotation(
            ax=ax1,
            x=x1[4],
            y=y[1],
            text="{Almost 70%} of the >5 h \ncategory were girls. {c.40%} \nexperienced clinically relevant \nsymptoms of depression.",
            highlight_word=["Almost 70%","c.40%"],
            dx=-0.5,
            dy=-10,
            color=["#984ea3", "#984ea3"], 
            arrow_position="top",
            show_arrow=True,
            alpha=0.8
        )
    if "Boys %" in pivot1.columns:
        boys_pct = pivot1["Boys %"].values

# === Set Axes Labels and Lines for UK ===
if view_option == "Percent per category by Gender (UK Only)":
    ax1.set_yticks([30, 40, 50, 60, 70])
    ax1.set_ylim(20, 75)
    for y in [30, 40, 50, 60, 70]:
        ax1.hlines(y, xmin=0, xmax=len(order) - 1, color='gray', linestyle=':', linewidth=0.7, alpha=0.4)
else:
    ax1.set_yticks([10, 20, 30, 40])
    ax1.set_ylim(0, 45)
    for y in [10, 20, 30, 40]:
        ax1.hlines(y, xmin=0, xmax=len(order) - 1, color='gray', linestyle=':', linewidth=0.7, alpha=0.4)

ax1.set_xlabel('Social media use in hours/weekday', labelpad=15, fontname="DejaVu Sans", color=GREY30)
ax1.set_ylabel(
    'Percent per category by user' if view_option == "Percent per category by Gender (UK Only)" else 'Clinically relevant symptoms (%)',
    labelpad=15, fontname="DejaVu Sans", color=GREY30
)

# === Plot US Data ===
if view_option != "Percent per category by Gender (UK Only)":
    years = pivot2.columns
    for category in us_categories:
        values = pivot2.loc[category]
        ax2.plot(years, values, color=custom_colors[category], label=label_map[category])
        ax2.plot(years[-1], values.iloc[-1], 'o', color=custom_colors[category])
        ax2.text(years[-1] + 0.6, values.iloc[-1], label_map[category], color=custom_colors[category],
                 fontsize=10, va='center', fontname="DejaVu Sans")

    for y in range(5, 35, 5):
        ax2.hlines(y, xmin=years.min(), xmax=years.max() + 1, color='gray', linestyle=':', linewidth=0.7, alpha=0.4)
    ax2.set_xticks(years)
    ax2.set_xticklabels([str(y) if i % 2 == 0 else '' for i, y in enumerate(years)], rotation=45)
    ax2.set_ylabel('Percent of US teens with at least one MDE in the year', labelpad=15, fontname="DejaVu Sans", color=GREY30)
    ax2.axvspan(2010, 2015, color='gray', alpha=0.1)
    ax2.set_xlim(years.min(), years.max() + 1)

# === Add annotations for US (Plot 2) ===
    if view_option == "All Teens":
        all_teens = pivot2.loc["ALL TOTAL"]
        x_val = 2013
        y_val = all_teens.loc[2013]
        add_annotation(
            ax=ax2,
            x=x_val,
            y=y_val,
            text="Noticeable {increase} in\nsymptoms from 2010\nto 2015 as smartphone\nadoption accelerates." ,
            highlight_word=["increase"],
            dx=-3,
            dy=9.5,
            color=["#2B2B2B"],
            arrow_position="bottom",
            alpha=0.8,
        )

    elif view_option == "Split by Gender":
        girls = pivot2.loc["FEMALE TOTAL"]
        x_val = 2013
        y_val = girls.loc[2013]
        add_annotation(
            ax=ax2,
            x=x_val,
            y=y_val,
            text="{Girls} experienced a much sharper rise\nthan boys from 2010 to 2015.",
            highlight_word=["Girls"],
            dx=-2,
            dy=6,
            color=["#984ea3"],
            arrow_position="bottom",
            alpha=0.8,
        )

    elif view_option == "All Categories":
        girls = pivot2.loc["FEMALE TOTAL"]
        boys = pivot2.loc["MALE TOTAL"]
        x_val = 2021
        y_val = girls.loc[2021]
        add_annotation(
            ax=ax2,
            x=x_val,
            y=y_val,
            text="Growing {gap} evident\nbetween boys and girls",
            highlight_word=["gap"],
            dx=-7,
            dy=-5,
            color=["#984ea3"],
            arrow_position="top",
            curve=-0.2,
            alpha=0.3,
        )
        add_annotation(
            ax=ax2,
            x=x_val,
            y=boys.loc[2021],
            text="{ }",
            highlight_word=[" "],
            dx=-7,
            dy=10.75,
            color=["#377eb8"],
            arrow_position="bottom",
            curve=0.2,
            alpha=0.3,
        )

else:
    ax2.axis("off")
    add_annotation(
        ax=ax2,
        x=0.5,
        y=0.5,
        text="{Data not available} for US trends \nin this view.",
        highlight_word=["Data not available"],
        dx=0,
        dy=0,
        color=["#e41a1c"],
        arrow_position=None,
        show_arrow=False
    )

# === Titles and Layout ===
fig.text(0.25, 0.93, "Depression by Level of Social Media Use, U.K.", color=GREY10,
         fontsize=15, fontname="DejaVu Sans", weight="bold", ha="center")
fig.text(0.25, 0.84,
         "Percent of UK teens depressed as a function of hours per weekday on social media.\n"
         "Teens who are heavy users of social media are more depressed than light users and\n"
         "nonusers — especially girls.",
         color=GREY30, fontname="DejaVu Sans", fontsize=9, ha="center")

fig.text(0.75, 0.93, "Major Depression Among Teens, U.S.", color=GREY10,
         fontsize=15, fontname="DejaVu Sans", weight="bold", ha="center")
fig.text(0.75, 0.86,
         "Percent of US teens (ages 12–17) who had at least one major depressive episode\n"
         "in the past year. Source: U.S. National Survey on Drug Use and Health",
         color=GREY30, fontname="DejaVu Sans", fontsize=9, ha="center")

plt.subplots_adjust(left=0.08, right=0.95, top=0.82, bottom=0.15, wspace=0.3)

# === Streamlit Display ===
with col2:
    st.pyplot(fig, clear_figure=True)
    st.subheader("Underlying Data (UK)")
    # Select and format the DataFrame
    columns_to_show = ["Social media use in hours/weekday", "All", "Girls", "Boys", "Girls %", "Boys %"]
    st.dataframe(df1[columns_to_show])
    #st.subheader("Underlying Data (US)")
    #st.dataframe(pivot1)