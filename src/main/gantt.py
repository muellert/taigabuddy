"""Create a Gantt chart with Plotly.

The chart generated will be put into a variable, which can then be
interpolated into a web page.
"""

from plotly.offline import plot
# import plotly.graph_objs as go
import plotly.figure_factory as ff
from datetime import date, timedelta

pl_config = {
    'showLink': False,
    'editable': False,
    'scrollZoom': False,
    'showTips': False,
    'displayModeBar': False,
}


def issues_gantt(il):
    """create a Plotly Gantt chart and return it as a string"""
    today = date.today()
    # soon = within 3 days:
    soon = today + timedelta(3)
    df = [dict(Task=str(il[x].ref),
               Start=str(il[x].created_date).split("T")[0],
               Finish=str(il[x].eta))
               for x in il]
    fig = ff.create_gantt(df)
    result = plot(fig, output_type="div", config=pl_config)
    # print("issues_gantt(): figure = ", fig)
    return result
