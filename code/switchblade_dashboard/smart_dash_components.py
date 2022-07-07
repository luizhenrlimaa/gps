import json
from abc import abstractmethod
import re
import pandas as pd

COMPONENT_CHART_TYPE = 0
COMPONENT_TABLE_TYPE = 1
COMPONENT_CARD_TYPE = 2
COMPONENT_CUSTOM_HTML_TYPE = 3

COMPONENT_TYPES = (
    (COMPONENT_CHART_TYPE, 'Chart'),
    (COMPONENT_TABLE_TYPE, 'Table'),
    (COMPONENT_CARD_TYPE, 'Card'),
    (COMPONENT_CUSTOM_HTML_TYPE, 'CustomHTML')
)


class ECharts:

    chart_id = ''
    title = ''
    component_type = COMPONENT_CHART_TYPE
    legend = {}
    extra_options = {}
    custom_actions = []
    charts_theme_name = None

    def __init__(self, chart_id, title='', show_legend=True, extra_options={}, charts_theme_name=None):
        self.chart_id = chart_id
        self.title = title
        self.legend = self.format_legend(show_legend)
        self.extra_options = extra_options
        self.charts_theme_name = charts_theme_name

    def get_component_name(self):
        class_name = self.__class__.__name__
        class_name = 'v-' + re.sub(r'(?<!^)(?=[A-Z])', '-', class_name).lower()
        return class_name

    @classmethod
    def format_legend(cls, show_legend):
        if not show_legend:
            legend = {'show': 0}
        else:
            legend = {'show': 1}

        return legend

    @classmethod
    def format_zoom(cls, start=0, end=50, background_color='#2B3B7C', zoom_line_color='#494F69',
                    zoom_area_color='#C2C3CD', zoom_font_size=13, zoom_font_color='#C2C3CD'):
        return [{
            'start': start,
            'end': end,
            'backgroundColor': background_color,
            'dataBackground': {
                'lineStyle': {'color': zoom_line_color},
                'areaStyle': {'color': zoom_area_color}
            },
            'textStyle': {
                'fontSize': zoom_font_size,
                'color': zoom_font_color
            },
            'handleIcon': 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.'
                          '8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-'
                          '0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.'
                          '7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,1'
                          '9.6H6.7v-1.4h6.6V19.6z',
            'handleSize': '80%',
            'handleStyle': {
                'color': '#fff',
                'shadowBlur': 3,
                'shadowColor': 'rgba(0, 0, 0, 0.6)',
                'shadowOffsetX': 2,
                'shadowOffsetY': 2
            }
        }]

    @classmethod
    def format_gradient_colors(cls, x=0, y=0, x2=1, y2=0, colors_defs=[], global_coordinates=False):
        parsed_global_coordinates = 0 if global_coordinates is False else 1

        return {
            'x': x,
            'y': y,
            'x2': x2,
            'y2': y2,
            'colorStops': colors_defs,
            'global': parsed_global_coordinates,
            'type': 'linear'
        }

    @classmethod
    def sort_data(cls, data, series_columns):
        unorderable_columns = list(set(data.columns.tolist()) - set(series_columns))
        return data[unorderable_columns + series_columns] if series_columns else data

    @classmethod
    def format_colors(cls, series=[], legend={}):

        colors = []

        for series_data in series:
            if series_data not in legend:
                continue

            color = legend[series_data].get('color', 'white')
            colors.append(color)

        return {
            'color': colors
        }

    @classmethod
    def format_percentage_mode_series(cls, data, series_columns):
        return {
            'percentage_mode': True,
            'origin_series': data[series_columns].to_dict('records')
        }

    @abstractmethod
    def get_data(self, data, legend):
        pass

    @abstractmethod
    def get_example_data(self):
        return {'df': pd.DataFrame(), 'extra_info': {}, 'legend': {}, 'definitions': {}}


class RingChart(ECharts):

    @classmethod
    def get_example_data(cls):
        df = pd.DataFrame({
            'A': {0: 1},
            'B': {0: 2},
            'C': {0: 3},
            'D': {0: 4}
        })

        total = int(df.sum(axis=1))

        definitions = RingChart.config(series_columns=['A', 'B', 'C', 'D'])

        return {
            'df': df,
            'extra_info': {'graphic': total},
            'legend': {
                'A': {'color': 'red'},
                'B': {'color': 'green'},
                'C': {'color': '#361109'},
                'D': {'color': '#C2C3CD'}
            },
            **definitions
        }

    @classmethod
    def config(cls, series_columns):
        return {
            'definitions': {
                'series_columns': series_columns
            }
        }

    @classmethod
    def _format_graphic(cls, graphic_text=''):
        return {
            'graphic': {
                'style': {'text': graphic_text}
            }
        }

    @classmethod
    def _format_dataset(cls, data):
        dataset_values = []

        if not data.empty:
            dataset_values = [list(x) for x in zip(data.columns.tolist(), data.values.flatten().tolist())]

        return {
            'dataset': {
                'source': dataset_values
            }
        }

    @classmethod
    def get_data(cls, data={}, legend={}):
        df = data.get('df', pd.DataFrame())
        definitions = data.get('definitions', {})
        extra_info = data.get('extra_info', {})
        extra_info_graphic = extra_info.get('graphic', None)

        if definitions:
            series_columns = definitions.get('series_columns', [])
            df = cls.sort_data(df, series_columns) if series_columns else df

        dataset = cls._format_dataset(df)
        graphic = cls._format_graphic(extra_info_graphic) if extra_info_graphic is not None else {}
        colors = cls.format_colors(df.columns.tolist(), legend) if legend else {}

        return {**dataset, **graphic, **colors}


class MultipleRingChart(ECharts):

    @classmethod
    def get_example_data(cls):
        df = pd.DataFrame({
            'A': {0: 1},
            'B': {0: 2},
            'C': {0: 3},
            'D': {0: 4}
        })

        definitions = MultipleRingChart.config(
            series_columns=[
                ['A', 'B'],
                ['C', 'D']
            ],
            rings_defs=[
                {'top': '10%', 'radius': ['10%', '30%']},
                {'top': '10%', 'radius': ['60%', '80%']},
            ],
            series_to_show=['A', 'C']
        )

        return {
            'df': df,
            'legend': {
                'A': {'color': 'blue'},
                'C': {'color': 'orange'}
            },
            **definitions
        }

    @classmethod
    def config(cls, series_columns, rings_defs=[], series_to_show=[]):
        return {
            'definitions': {
                'series_columns': series_columns,
                'rings_defs': rings_defs,
                'series_to_show': series_to_show
            }
        }

    @classmethod
    def _format_series(cls, data, definitions={}, legend={}):
        series_data = [{'data': [{'value': 0, 'name': 'No Info'}]}]

        rings = definitions.get('series_columns', [])
        rings_defs = definitions.get('rings_defs', [])
        series_to_show = definitions.get('series_to_show', [])

        if not data.empty and rings:
            series_data = []

            for i, ring in enumerate(rings):

                series_dict = {
                    'type': 'pie',
                    'data': []
                }

                if rings_defs:
                    series_dict = {**series_dict, **rings_defs[i]}

                for series in ring:

                    if legend:
                        if 'color' not in series_dict:
                            series_dict['color'] = []

                        if series in legend:
                            series_dict['color'].append(legend[series].get('color', '#ACB0BF'))
                        else:
                            series_dict['color'].append('#ACB0BF')

                    display = True if not series_to_show or series in series_to_show else False

                    series_dict_data = {
                        'value': str(data[series].values[0]),
                        'name': series if display else f'{series} ring {i}'
                    }

                    if not display:
                        series_dict_data = {
                            **series_dict_data,
                            **{
                                'label': {'show': False},
                                'labelLine': {'show': False},
                                'emphasis': {'labelLine': {'show': False}}
                            }
                        }

                    series_dict['data'].append(series_dict_data)

                series_data.append(series_dict)

        return {
            'series': series_data
        }

    @classmethod
    def get_data(cls, data={}, legend={}):
        df = data.get('df', pd.DataFrame())
        definitions = data.get('definitions', {})
        series = cls._format_series(df, definitions, legend)

        return {**series}


class BarChart(ECharts):

    BAR_CHART_ORIENTATION_VERTICAL = 0
    BAR_CHART_ORIENTATION_HORIZONTAL = 1

    BAR_CHART_ORIENTATIONS = (
        (BAR_CHART_ORIENTATION_VERTICAL, 'vertical'),
        (BAR_CHART_ORIENTATION_HORIZONTAL, 'horizontal')
    )

    custom_actions = ['insertEvents']

    @classmethod
    def get_example_data(cls, orientation=BAR_CHART_ORIENTATION_VERTICAL, stacked=False, stacked_sum=False,
                         reverse_legend=False):

        df = pd.DataFrame({
            'step': {
                1: 'Step 1',
                2: 'Step 2',
                3: 'Step 3',
                4: 'Step 4'
            },
            'A': {
                1: 10,
                2: 20,
                3: 30,
                4: 40
            },
            'B': {
                1: 10,
                2: 20,
                3: 30,
                4: ''
            },
            'C': {
                1: 10,
                2: 20,
                3: '',
                4: ''
            },
            'D': {
                1: 10,
                2: '',
                3: '',
                4: 40
            }
        })

        orientation = \
            orientation if orientation in dict(cls.BAR_CHART_ORIENTATIONS) else cls.BAR_CHART_ORIENTATION_VERTICAL

        if stacked and not stacked_sum:
            definitions = BarChart.config(
                series_columns=['A', 'B', 'C', 'D'],
                axis_column='step',
                orientation=orientation,
                stacked_series={
                    'stack_1': ['A', 'B'],
                    'stack_2': ['C', 'D']
                },
                reverse_legend=reverse_legend
            )
        elif stacked and stacked_sum:
            definitions = BarChart.config(
                series_columns=['A', 'B', 'C', 'D'],
                axis_column='step',
                orientation=orientation,
                stacked_series={
                    'stack_1': ['A', 'B'],
                    'stack_2': ['C', 'D']
                },
                stacked_sum=True,
                reverse_legend=reverse_legend
            )
        else:
            definitions = BarChart.config(
                series_columns=['A', 'B', 'C', 'D'],
                axis_column='step',
                orientation=orientation,
                reverse_legend=reverse_legend
            )

        return {
            'df': df,
            'legend': {
                'A': {'color': 'red'},
                'B': {'color': 'green'},
                'C': {'color': 'cyan'},
                'D': {'color': '#43A220'}
            },
            **definitions
        }

    @classmethod
    def config(cls, series_columns, axis_column, orientation=BAR_CHART_ORIENTATION_VERTICAL, stacked_series={},
               stacked_sum=False, percentage_mode=False, reverse_legend=False, show_label=True, bar_min_height=20,
               rotate_label=0):
        return {
            'definitions': {
                'series_columns': series_columns,
                'axis_column': axis_column,
                'orientation': orientation,
                'stacked_series': stacked_series,
                'stacked_sum': stacked_sum,
                'percentage_mode': percentage_mode,
                'reverse_legend': reverse_legend,
                'show_label': show_label,
                'bar_min_height': bar_min_height,
                'rotate_label': rotate_label
            }
        }

    @classmethod
    def _format_series(cls, data, definitions={}):

        series_columns = definitions.get('series_columns', [])
        orientation = definitions.get('orientation', cls.BAR_CHART_ORIENTATION_VERTICAL)
        stacked_series = definitions.get('stacked_series', {})
        stacked_sum = definitions.get('stacked_sum', False)
        percentage_mode = definitions.get('percentage_mode', False)
        show_label = definitions.get('show_label', True)
        bar_min_height = definitions.get('bar_min_height', 20)
        rotate_label = definitions.get('rotate_label', 0)

        series_data = [
            {
                'name': 'No info',
                'type': 'bar',
                'label': {
                    'show': True,
                    'position': 'top' if orientation == cls.BAR_CHART_ORIENTATION_VERTICAL else 'right'
                }
            },
        ]

        if stacked_series and percentage_mode:
            data[series_columns] = data[series_columns].apply(pd.to_numeric, downcast='float', errors='coerce')
            data_series_sum = data.sum(axis=1)

            for series_column in series_columns:
                data[series_column] = (data[series_column] / data_series_sum) * 100
                data[series_column].fillna(0, inplace=True)
                data[series_columns] = data[series_columns].astype(float).round(2)

        if not data.empty and definitions:

            if not series_columns:
                return {'series': []}

            if stacked_series and stacked_sum:
                data_as_numeric = data.replace(r'^\s*$', 0, regex=True).fillna(0)
                stacked_sum_data = pd.DataFrame()

                for stack_name, series_to_stack in stacked_series.items():
                    stacked_series_sum = data_as_numeric[series_to_stack].sum(axis=1)
                    stacked_series_df = pd.DataFrame({stack_name: stacked_series_sum})
                    stacked_sum_data = pd.concat([stacked_sum_data, stacked_series_df], axis=1)

                del data_as_numeric
            else:
                stacked_sum_data = pd.DataFrame()

            if orientation == cls.BAR_CHART_ORIENTATION_VERTICAL:
                series_method = getattr(cls, '_format_series_vertical')
            elif orientation == cls.BAR_CHART_ORIENTATION_HORIZONTAL:
                series_method = getattr(cls, '_format_series_horizontal')
            else:
                series_method = None

            if series_method:
                series_data = series_method(data, series_columns, stacked_series, stacked_sum, stacked_sum_data,
                                            bar_min_height, show_label, rotate_label)

            else:
                series_data = []

        return {
            'series': series_data
        }

    @classmethod
    def _format_series_vertical(cls, data, series_columns, stacked_series, stacked_sum, stacked_sum_data,
                                bar_min_height, show_label, rotate_label):

        series_data = []

        for series_column in series_columns:
            series = {
                'name': series_column,
                'data': data[series_column].values.tolist(),
                'type': 'bar',
                'barMinHeight': bar_min_height,
                'seriesLayoutBy': 'row',
                'clip': False
            }

            if show_label:
                series['label'] = {
                    'show': True,
                    'fontSize': 12,
                    'rotate': rotate_label,
                    'color': '#050D2F',
                    'position': 'inside',
                }
            else:
                series['label'] = {'show': False}

            if stacked_series:
                for stack_name, series_to_stack in stacked_series.items():
                    if series_column not in series_to_stack:
                        continue

                    series['stack'] = stack_name
                    break

            series_data.append(series)

        if stacked_series and stacked_sum:
            for stack_name, series_to_stack in stacked_series.items():
                series_values = stacked_sum_data[stack_name].values.tolist()

                for i, series in enumerate(series_values):
                    series = {
                        'name': series_to_stack[-1],
                        'data': [0 if i == j else '' for j, value in enumerate(series_values)],
                        'stack': stack_name,
                        'barMinHeight': 0,
                        'type': 'bar',
                        'seriesLayoutBy': 'row',
                        'clip': False,
                        'label': {
                            'show': True,
                            'fontSize': 12,
                            'color': '#C2C3CD',
                            'position': 'top',
                            'formatter': str(series)
                        }
                    }

                    series_data.append(series)

        return series_data

    @classmethod
    def _format_series_horizontal(cls, data, series_columns, stacked_series, stacked_sum, stacked_sum_data,
                                  bar_min_height, show_label, rotate_label):
        series_data = []

        for series_column in series_columns:
            series = {
                'name': series_column,
                'data': data[series_column].values.tolist(),
                'type': 'bar',
                'barMinHeight': bar_min_height
            }

            if show_label:
                series['label'] = {
                    'show': True,
                    'position': 'right' if not stacked_series else 'inside',
                    'fontSize': 12 if stacked_series and stacked_sum else 18,
                    'rotate': rotate_label
                }
            else:
                series['label'] = {'show': False}

            if stacked_series:
                for stack_name, series_to_stack in stacked_series.items():
                    if series_column not in series_to_stack:
                        continue

                    series['stack'] = stack_name
                    break

            series_data.append(series)

        if stacked_series and stacked_sum:
            for stack_name, series_to_stack in stacked_series.items():
                series_values = stacked_sum_data[stack_name].values.tolist()

                for i, series in enumerate(series_values):
                    series = {
                        'name': series_to_stack[-1],
                        'data': [0 if i == j else '' for j, value in enumerate(series_values)],
                        'stack': stack_name,
                        'barMinHeight': 0,
                        'type': 'bar',
                        'label': {
                            'show': True,
                            'color': '#C2C3CD',
                            'position': 'right',
                            'fontSize': 12,
                            'formatter': str(series)
                        }
                    }

                    series_data.append(series)

        return series_data

    @classmethod
    def _format_axis(cls, data, definitions={}):

        percentage_mode = definitions.get('percentage_mode', False)

        x_axis = {
            'axisLine': {
                'lineStyle': {
                    'color': '#C2C3CD',
                },
            },
            'splitLine': {
                'lineStyle': {
                    'type': 'dashed',
                    'color': 'gray',
                },
            },
        }

        y_axis = {
            'splitLine': {
                'lineStyle': {
                    'type': 'dashed',
                    'color': 'gray',
                },
            },
            'axisLine': {
                'lineStyle': {
                    'color': '#C2C3CD',
                }
            },
        }

        axis_data = []

        orientation = definitions.get('orientation', cls.BAR_CHART_ORIENTATION_VERTICAL)

        if not data.empty and definitions:
            axis_column = definitions.get('axis_column', None)
            axis_data = data[axis_column].drop_duplicates().values.tolist() if axis_column else axis_data

        if orientation == cls.BAR_CHART_ORIENTATION_VERTICAL:
            x_axis['type'] = 'category'
            x_axis['axisLabel'] = {'color': '#C2C3CD', 'fontSize': 13}
            x_axis['data'] = axis_data

            if percentage_mode:
                y_axis['max'] = 100
                y_axis['min'] = 0

        elif orientation == cls.BAR_CHART_ORIENTATION_HORIZONTAL:
            x_axis['type'] = 'value'
            x_axis['position'] = 'top'
            y_axis['type'] = 'category'
            y_axis['data'] = axis_data

            if percentage_mode:
                x_axis['max'] = 100
                x_axis['min'] = 0

        return {
            'xAxis': x_axis,
            'yAxis': y_axis
        }

    @classmethod
    def _format_legend(cls, definitions={}, series=[], reverse_legend=False):
        orientation = definitions.get('orientation', cls.BAR_CHART_ORIENTATION_VERTICAL)

        legend = {
            'type': 'scroll',
            'textStyle': {
                'fontSize': 13,
                'color': '#C2C3CD',
                'fontFamily': "'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif",
            }
        }

        if orientation == cls.BAR_CHART_ORIENTATION_VERTICAL:
            legend['orient'] = 'vertical'
            legend['right'] = 10
            legend['top'] = '10%'
        elif orientation == cls.BAR_CHART_ORIENTATION_HORIZONTAL:
            legend['bottom'] = 10

        if reverse_legend:
            series.reverse()
            legend['data'] = series

        return {'legend': legend}

    @classmethod
    def _format_tooltip(cls, definitions={}):

        orientation = definitions.get('orientation', cls.BAR_CHART_ORIENTATION_VERTICAL)
        stacked_series = definitions.get('stacked_series', {})
        stacked_sum = definitions.get('stacked_sum', False)

        if orientation == cls.BAR_CHART_ORIENTATION_HORIZONTAL:
            if not stacked_series or (stacked_series and not stacked_sum):
                return {
                    'tooltip': {
                        'trigger': 'axis',
                        'axisPointer': {'type': 'shadow'},
                    }
                }

        return {}

    @classmethod
    def _format_grid(cls, definitions={}):

        orientation = definitions.get('orientation', cls.BAR_CHART_ORIENTATION_VERTICAL)

        if orientation == cls.BAR_CHART_ORIENTATION_HORIZONTAL:
            return {
                'grid': {
                    'top': '15%',
                    'left': '5%',
                    'right': '10%',
                    'bottom': '10%',
                    'containLabel': True
                }
            }

        return {}

    @classmethod
    def get_data(cls, data={}, legend={}):
        df = data.get('df', pd.DataFrame())
        definitions = data.get('definitions', {})
        stacked_series = definitions.get('stacked_series', {})
        percentage_mode = definitions.get('percentage_mode', False)
        reverse_legend = definitions.get('reverse_legend', False)
        series_columns = definitions.get('series_columns', [])

        if definitions:
            df = cls.sort_data(df, series_columns) if series_columns else df

        percentage_mode_series = cls.format_percentage_mode_series(df, series_columns) if stacked_series and percentage_mode else {}
        series = cls._format_series(df, definitions)
        axis = cls._format_axis(df, definitions)
        tooltip = cls._format_tooltip(definitions)
        grid = cls._format_grid(definitions)
        legend_configs = cls._format_legend(definitions, df.columns.tolist(), reverse_legend)
        colors = cls.format_colors(df.columns.tolist(), legend) if legend else {}

        return {**series, **axis, **tooltip,  **grid, **legend_configs, **colors, **percentage_mode_series}

    @classmethod
    def get_events_data(cls, data, definitions={}):
        if not data.empty and definitions:
            axis_column = definitions.get('axis_column', None)
            orientation = definitions.get('orientation', cls.BAR_CHART_ORIENTATION_VERTICAL)

            return {
                'insertEvents': {
                    'data': data[axis_column].drop_duplicates().values.tolist() if axis_column else [],
                    'axis': 'xAxis' if orientation == cls.BAR_CHART_ORIENTATION_VERTICAL else 'yAxis'
                }
            }

        else:
            return {}

    @classmethod
    def get_custom_actions_data(cls, data={}):
        df = data.get('df', pd.DataFrame())
        definitions = data.get('definitions', {})

        events_data = cls.get_events_data(df, definitions)

        return {**events_data}


class LineAndBarChart(ECharts):

    custom_actions = ['insertEvents']

    @classmethod
    def get_example_data(cls, multiple_axes=False):
        df = pd.DataFrame({
            'step': {
                1: 'Step 1',
                2: 'Step 2',
                3: 'Step 3',
                4: 'Step 4'
            },
            'A': {
                1: 10,
                2: 20,
                3: 30,
                4: 40
            },
            'B': {
                1: 20,
                2: 25,
                3: 40,
                4: ''
            },
            'C': {
                1: 35,
                2: 15,
                3: 70,
                4: ''
            },
            'D': {
                1: 40,
                2: 35,
                3: '',
                4: 80
            }
        })

        if not multiple_axes:
            definitions = LineAndBarChart.config(
                series_columns=['A', 'B', 'C', 'D'],
                x_axis_column='step'
            )
        else:
            definitions = LineAndBarChart.config(
                series_columns=['A', 'B', 'C', 'D'],
                x_axis_column='step',
                axes=[
                    {
                        'name': 'axis_1',
                        'name_offset': 25,
                        'bar': ['A'],
                        'line': ['B', 'C'],
                    },
                    {
                        'label': 'º',
                        'line': ['D']
                    }
                ]
            )

        return {
            'df': df,
            'legend': {
                'A': {'color': '#149E5F'},
                'B': {'color': '#2DB3D5'},
                'C': {'color': '#E3416A'},
                'D': {'color': '#3C75D3'}
            },
            **definitions
        }

    @classmethod
    def config(cls, series_columns, x_axis_column, axes=[]):
        return {
            'definitions': {
                'series_columns': series_columns,
                'x_axis_column': x_axis_column,
                'axes': axes
            }
        }

    @classmethod
    def _format_series(cls, data, definitions={}):
        series_data = [
            {
                'name': 'No info',
                'type': 'bar',
                'label': {
                    'show': True,
                    'fontSize': 18,
                    'position': 'top',
                },
                'yAxisIndex': 1,
                'data': [],
            },
        ]

        if not data.empty and definitions:
            series_columns = definitions.get('series_columns', [])
            axes = definitions.get('axes', [])

            if series_columns:
                if axes:
                    series_data = cls._format_series_multiple_axes(series_columns, data, axes)
                else:
                    series_data = cls._format_series_single_axis(series_columns, data)

        return {
            'series': series_data
        }

    @classmethod
    def _format_series_single_axis(cls, series_columns, data):

        series_data = []

        for i, series_column in enumerate(series_columns):
            series = {
                'name': series_column,
                'type': 'bar' if i == 0 else 'line',
                'label': {
                    'show': True,
                    'fontSize': 18,
                    'position': 'top'
                },
                'yAxisIndex': 1,
                'data': data[series_column].values.tolist()
            }

            series_data.append(series)

        return series_data

    @classmethod
    def _format_series_multiple_axes(cls, series_columns, data, axes):

        series_data = []

        for series_column in series_columns:
            for i, axis in enumerate(axes):
                axis_bar_series = axis.get('bar', [])
                axis_line_series = axis.get('line', [])

                if series_column not in axis_bar_series and series_column not in axis_line_series:
                    continue

                series = {
                    'name': series_column,
                    'type': 'bar' if series_column in axis_bar_series else 'line',
                    'label': {
                        'show': True,
                        'fontSize': 13,
                        'position': 'top'
                    },
                    'yAxisIndex': i,
                    'data': data[series_column].values.tolist()
                }

                series_data.append(series)
                break

        return series_data

    @classmethod
    def _format_x_axis(cls, data, definitions={}):

        x_axis_data = []

        if not data.empty and definitions:
            x_axis_column = definitions.get('x_axis_column', None)
            x_axis_data = data[x_axis_column].drop_duplicates().values.tolist() if x_axis_column else x_axis_data

        return {
            'xAxis': {'data': x_axis_data}
        }

    @classmethod
    def _format_y_axis(cls, definitions={}):

        if not definitions:
            return {}

        axes = definitions.get('axes', [])

        if not axes:
            return {}

        y_axis = []

        for i, axis in enumerate(axes):
            axis_name = axis.get('name', None)
            axis_name_offset = axis.get('name_offset', None)
            axis_label = axis.get('label', None)

            y_axis_data = {
                'axisLine': {
                    'lineStyle': {
                        'color': 'DFDFDF',
                    }
                },
                'splitLine': {
                    'lineStyle': {
                        'type': 'dashed',
                        'color': 'gray',
                    },
                },
                'type': 'value',
                'position': 'left' if i == 0 else 'right'
            }

            if axis_name:
                y_axis_data['name'] = axis_name
                y_axis_data['nameLocation'] = 'middle'
                y_axis_data['nameGap'] = axis_name_offset if axis_name_offset else 25
                y_axis_data['nameTextStyle'] = {
                    'fontSize': 13
                }

            if axis_label:
                y_axis_data['axisLabel'] = {'formatter': '{value} ' + f'{axis_label}'}

            if i > 1:
                y_axis_data['offset'] = 45 if 'name' in axes[i - 1] else 30

            y_axis.append(y_axis_data)

        return {
            'yAxis': y_axis
        }

    @classmethod
    def _format_tooltip(cls, definitions={}):

        if not definitions:
            return {}

        axes = definitions.get('axes', [])

        if not axes:
            return {}

        return {
            'tooltip': {
                'trigger': 'axis',
                'axisPointer': {'type': 'shadow'}
            }
        }

    @classmethod
    def get_data(cls, data={}, legend={}):
        df = data.get('df', pd.DataFrame())
        definitions = data.get('definitions', {})

        if definitions:
            series_columns = definitions.get('series_columns', [])
            df = cls.sort_data(df, series_columns) if series_columns else df

        series = cls._format_series(df, definitions)
        x_axis = cls._format_x_axis(df, definitions)
        y_axis = cls._format_y_axis(definitions)
        colors = cls.format_colors(df.columns.tolist(), legend) if legend else {}
        tooltip = cls._format_tooltip(definitions)

        return {**series, **x_axis, **y_axis, **colors, **tooltip}

    @classmethod
    def get_events_data(cls, data, definitions={}):
        if not data.empty and definitions:
            x_axis_column = definitions.get('x_axis_column', None)

            return {
                'insertEvents': {
                    'data': data[x_axis_column].drop_duplicates().values.tolist() if x_axis_column else [],
                    'axis': 'xAxis'
                }
            }

        else:
            return {}

    @classmethod
    def get_custom_actions_data(cls, data={}):
        df = data.get('df', pd.DataFrame())
        definitions = data.get('definitions', {})

        events_data = cls.get_events_data(df, definitions)

        return {**events_data}


class LineChart(ECharts):

    custom_actions = ['insertEvents']

    @classmethod
    def get_example_data(cls, stacked=False, multiple_axes=False, smooth_lines=False):
        df = pd.DataFrame({
            'step': {
                1: 'Step 1',
                2: 'Step 2',
                3: 'Step 3',
                4: 'Step 4'
            },
            'A': {
                1: 1278,
                2: 1592,
                3: 1476,
                4: 1176,
            },
            'B': {
                1: 2369,
                2: 2587,
                3: 2289,
                4: 2376
            },
            'C': {
                1: 3756,
                2: 3610,
                3: 3387,
                4: 3416
            },
            'D': {
                1: 4326,
                2: 4078,
                3: 4702,
                4: 4576
            }
        })

        if stacked:
            definitions = LineChart.config(
                series_columns=['A', 'B', 'C', 'D'],
                x_axis_column='step',
                stacked_series={
                    'stack_1': ['A', 'B'],
                    'stack_2': ['C', 'D']
                },
                smooth_lines=smooth_lines,
            )
        elif multiple_axes:
            definitions = LineChart.config(
                series_columns=['A', 'B', 'C', 'D'],
                x_axis_column='step',
                axes=[
                    {
                        'name': 'axis_1',
                        'name_offset': 50,
                        'series': ['A', 'B', 'C'],
                    },
                    {
                        'label': 'º',
                        'series': ['D']
                    }
                ],
                smooth_lines=smooth_lines
            )
        else:
            definitions = LineChart.config(
                series_columns=['A', 'B', 'C', 'D'],
                x_axis_column='step',
                smooth_lines=smooth_lines
            )

        return {
            'df': df,
            'legend': {
                'A': {'color': '#149E5F'},
                'B': {'color': '#2DB3D5'},
                'C': {'color': '#E3416A'},
                'D': {'color': '#3C75D3'}
            },
            **definitions
        }

    @classmethod
    def config(cls, series_columns, x_axis_column, stacked_series={}, axes=[], smooth_lines=False, percentage_mode=False):
        return {
            'definitions': {
                'series_columns': series_columns,
                'x_axis_column': x_axis_column,
                'stacked_series': stacked_series,
                'axes': axes,
                'smooth_lines': smooth_lines,
                'percentage_mode': percentage_mode
            }
        }

    @classmethod
    def _format_dataset(cls, data, definitions={}):
        dataset_values = []

        if not data.empty and definitions:
            series_columns = definitions.get('series_columns', [])
            x_axis_column = definitions.get('x_axis_column', None)
            percentage_mode = definitions.get('percentage_mode', False)

            if series_columns and x_axis_column:

                x_axis_values = data[x_axis_column].drop_duplicates().values.tolist()

                for x_axis_value in x_axis_values:

                    values = data[data[x_axis_column] == x_axis_value][series_columns].values.flatten().tolist()

                    if percentage_mode:
                        values_df = pd.DataFrame(values)
                        values_df = (values_df/values_df.sum()).multiply(100)
                        values_df = values_df.astype(float).round(2)
                        values = values_df.values.flatten().tolist()

                    values.insert(0, x_axis_value)
                    dataset_values.append(values)

                dataset_values.insert(0, [x_axis_column] + series_columns)

        return {
            'dataset': {
                'source': dataset_values
            }
        }

    @classmethod
    def _format_series(cls, data, definitions={}):
        series_data = []

        if not data.empty and definitions:
            series_columns = definitions.get('series_columns', [])
            stacked_series = definitions.get('stacked_series', {})
            axes = definitions.get('axes', [])
            smooth_lines = definitions.get('smooth_lines', False)

            if axes:
                series_data = cls._format_series_multiple_axes(series_columns, axes, smooth_lines)
            else:
                series_data = cls._format_series_single_axis(series_columns, stacked_series, smooth_lines)

        return {
            'series': series_data
        }

    @classmethod
    def _format_series_single_axis(cls, series_columns, stacked_series, smooth_lines=False):

        series_data = []

        for series_name in series_columns:
            series = {
                'name': series_name,
                'type': 'line',
                'smooth': 1 if smooth_lines else 0,
            }

            if stacked_series:
                for stack_name, series_to_stack in stacked_series.items():
                    if series_name not in series_to_stack:
                        continue

                    series['stack'] = stack_name
                    break

            series_data.append(series)

        return series_data

    @classmethod
    def _format_series_multiple_axes(cls, series_columns, axes, smooth_lines=False):

        series_data = []

        for series_name in series_columns:
            for i, axis in enumerate(axes):

                axis_series = axis.get('series', [])

                if series_name not in axis_series:
                    continue

                series = {
                    'name': series_name,
                    'type': 'line',
                    'smooth': 1 if smooth_lines else 0,
                    'yAxisIndex': i
                }

                series_data.append(series)
                break

        return series_data

    @classmethod
    def _format_y_axis(cls, definitions={}):

        if not definitions:
            return {}

        axes = definitions.get('axes', [])

        if not axes:
            return {}

        y_axis = []

        for i, axis in enumerate(axes):
            axis_name = axis.get('name', None)
            axis_name_offset = axis.get('name_offset', None)
            axis_label = axis.get('label', None)

            y_axis_data = {
                'position': 'left' if i == 0 else 'right'
            }

            if axis_name:
                y_axis_data['name'] = axis_name
                y_axis_data['nameLocation'] = 'middle'
                y_axis_data['nameGap'] = axis_name_offset if axis_name_offset else 25
                y_axis_data['nameTextStyle'] = {
                    'fontSize': 13
                }

            if axis_label:
                y_axis_data['axisLabel'] = {'formatter': '{value} ' + f'{axis_label}'}

            if i > 1:
                y_axis_data['offset'] = 45 if 'name' in axes[i - 1] else 30

            y_axis.append(y_axis_data)

        return {
            'yAxis': y_axis
        }

    @classmethod
    def get_data(cls, data={}, legend={}):
        df = data.get('df', pd.DataFrame())
        definitions = data.get('definitions', {})

        if definitions:
            series_columns = definitions.get('series_columns', [])
            df = cls.sort_data(df, series_columns) if series_columns else df

        dataset = cls._format_dataset(df, definitions)
        series = cls._format_series(df, definitions)
        y_axis = cls._format_y_axis(definitions)
        colors = cls.format_colors(df.columns.tolist(), legend) if legend else {}

        return {**dataset, **series, **y_axis, **colors}

    @classmethod
    def get_events_data(cls, data, definitions={}):
        if not data.empty and definitions:
            x_axis_column = definitions.get('x_axis_column', None)

            return {
                'insertEvents': {
                    'data': data[x_axis_column].drop_duplicates().values.tolist() if x_axis_column else [],
                    'axis': 'xAxis'
                }
            }

        else:
            return {}

    @classmethod
    def get_custom_actions_data(cls, data={}):
        df = data.get('df', pd.DataFrame())
        definitions = data.get('definitions', {})

        events_data = cls.get_events_data(df, definitions)

        return {**events_data}


class AreaChart(LineChart):

    @classmethod
    def _format_series_area_style(cls, series={}):

        series_data = series.get('series', [])

        for series in series_data:
            series['areaStyle'] = {}

        return {
            'series': series_data
        }

    @classmethod
    def get_data(cls, data={}, legend={}):
        df = data.get('df', pd.DataFrame())
        definitions = data.get('definitions', {})
        percentage_mode = definitions.get('percentage_mode', False)
        series_columns = definitions.get('series_columns', [])

        if definitions:
            df = cls.sort_data(df, series_columns) if series_columns else df

        percentage_mode_series = cls.format_percentage_mode_series(df, series_columns) if percentage_mode else {}
        dataset = cls._format_dataset(df, definitions)
        series = cls._format_series(df, definitions)
        series = cls._format_series_area_style(series)
        y_axis = cls._format_y_axis(definitions)
        colors = cls.format_colors(df.columns.tolist(), legend) if legend else {}

        return {**dataset, **series, **y_axis, **colors, **percentage_mode_series}


class ScatterChart(ECharts):

    @classmethod
    def get_example_data(cls):
        df = pd.DataFrame({
            'axis_measures': {
                1: '19/08 00:00',
                2: '19/08 00:00',
                3: '19/08 01:00',
                4: '19/08 01:00'
            },
            'axis': {
                1: 'X Axis',
                2: 'Y Axis',
                3: 'X Axis',
                4: 'Y Axis'
            },
            'A': {
                1: 42,
                2: 4592,
                3: 34,
                4: 4236,
            },
            'B': {
                1: 48,
                2: 4058,
                3: 41,
                4: 4912,
            },
            'C': {
                1: 39,
                2: 5025,
                3: 50,
                4: 4369,
            },
        })

        definitions = ScatterChart.config(
            series_columns=['A', 'B', 'C'],
            axis_column='axis',
            axis_measurement_column='axis_measures'
        )

        return {
            'df': df,
            'legend': {
                'A': {'color': 'black'},
                'B': {'color': 'grey'},
                'C': {'color': 'white'}
            },
            **definitions
        }

    @classmethod
    def config(cls, series_columns, axis_column, axis_measurement_column):
        return {
            'definitions': {
                'series_columns': series_columns,
                'axis_column': axis_column,
                'axis_measurement_column': axis_measurement_column
            }
        }

    @classmethod
    def _format_dataset(cls, data, definitions={}):
        dataset = []

        if not data.empty and definitions:
            series_columns = definitions.get('series_columns', [])
            axis_measurement_column = definitions.get('axis_measurement_column', None)

            if series_columns and axis_measurement_column:

                axis_measurement_values = data[axis_measurement_column].drop_duplicates().values.tolist()

                for series in series_columns:
                    dataset_values = {'source': [[series]]}

                    for axis_measurement in axis_measurement_values:
                        dataset_values['source'].append(
                            data[data[axis_measurement_column] == axis_measurement][series].values.flatten().tolist()
                        )

                    dataset.append(dataset_values)

        return {
            'dataset': dataset
        }

    @classmethod
    def _format_series(cls, data, definitions={}):
        series_data = []

        if not data.empty and definitions:

            series_columns = definitions.get('series_columns', [])

            for i, series_name in enumerate(series_columns):
                series_data.append({
                    'name': series_name,
                    'type': 'scatter',
                    'datasetIndex': i
                })

        return {
            'series': series_data
        }

    @classmethod
    def get_data(cls, data={}, legend={}):
        df = data.get('df', pd.DataFrame())
        definitions = data.get('definitions', {})

        if definitions:
            series_columns = definitions.get('series_columns', [])
            df = cls.sort_data(df, series_columns) if series_columns else df

        dataset = cls._format_dataset(df, definitions)
        series = cls._format_series(df, definitions)
        colors = cls.format_colors(df.columns.tolist(), legend) if legend else {}

        return {**dataset, **series, **colors}


class Table:

    table_id = ''
    title = ''
    entries = 25
    extra_options = {}
    component_type = COMPONENT_TABLE_TYPE

    def __init__(self, table_id, title='', entries=None, extra_options={}):
        self.table_id = table_id
        self.title = title
        self.entries = entries if entries is not None else self.entries
        self.extra_options = extra_options

    @abstractmethod
    def get_data(self, data):
        pass

    @abstractmethod
    def get_example_data(self):
        return {'df': pd.DataFrame(), 'pagination': {}}


class SimpleTable(Table):

    @classmethod
    def get_example_data(cls, custom_style=False):

        def color_negative_red(val):
            color = 'red'
            return 'background-color: %s' % color

        df = pd.DataFrame({
            'A': {
                1: 10,
                2: 20,
                3: 30,
                4: 40,
                5: 50,
                6: 60,
                7: 70,
                8: 80,
                9: 90,
                10: 100
            },
            'B': {
                1: 10,
                2: 20,
                3: 30,
                4: 40,
                5: 50,
                6: 60,
                7: 70,
                8: 80,
                9: 90,
                10: 100
            },
            'C': {
                1: 10,
                2: 20,
                3: 30,
                4: 40,
                5: 50,
                6: 60,
                7: 70,
                8: 80,
                9: 90,
                10: 100
            },
            'D': {
                1: 10,
                2: 20,
                3: 30,
                4: 40,
                5: 50,
                6: 60,
                7: 70,
                8: 80,
                9: 90,
                10: 100
            }
        })

        if custom_style:
            df = df.style.applymap(color_negative_red, subset=['A', 'B']).render()

        return {
            'df': df,
            'pagination': {
                'items_count': 10,
                'items_per_page': 5,
                'table_pages_count': 2,
                'pagination_index': 1
            }
        }

    @classmethod
    def config_pagination(
            cls,
            items_count=0,
            items_start_index=1,
            items_end_index=1,
            items_per_page=0,
            table_pages_count=0,
            pagination_index=1):

        return {
            'items_count': items_count,
            'items_start_index': items_start_index,
            'items_end_index': items_end_index,
            'items_per_page': items_per_page,
            'table_pages_count': table_pages_count,
            'pagination_index': pagination_index
        }

    @classmethod
    def format_data(cls, data, pagination):
        if isinstance(data, pd.DataFrame):
            return {'table_html': data.style.render(), 'pagination': pagination}
        elif type(data) == str:
            return {'table_html': data, 'pagination': pagination}
        else:
            return {'table_html': '', 'pagination': pagination}

    @classmethod
    def get_data(cls, data={}):
        df = data.get('df', pd.DataFrame())
        pagination = data.get('pagination', {})
        data = cls.format_data(df, pagination)
        return {**data}


class Card:

    card_id = ''
    title = ''
    export = False
    extra_options = {}
    component_type = COMPONENT_CARD_TYPE

    def __init__(self, card_id, title='', extra_options={}):
        self.card_id = card_id
        self.title = title
        self.extra_options = extra_options

    def get_component_name(self):
        class_name = self.__class__.__name__
        class_name = 'v-' + re.sub(r'(?<!^)(?=[A-Z])', '-', class_name).lower()
        return class_name

    @abstractmethod
    def get_data(self, data):
        pass

    @abstractmethod
    def get_example_data(self):
        return {'value': 0}


class SimpleCard(Card):

    @classmethod
    def get_example_data(cls):
        return {'value': 1000}

    @classmethod
    def get_data(cls, data):
        return {'content': str(data.get('value', 0))}


class PercentageCard(Card):

    @classmethod
    def get_example_data(cls):
        return {
            'value': 1000,
            'percentage': 50
        }

    @classmethod
    def get_data(cls, data):
        return {
            'content': str(data.get('value', 0)),
            'percentage': str(data.get('percentage', 0))
        }


class LinkCard(Card):

    export = True

    @classmethod
    def get_example_data(cls):
        return {'value': 1000}

    @classmethod
    def get_data(cls, data):
        return {'title': str(data.get('value', 0))}


class CustomHTML:

    component_id = ''
    title = ''
    component_type = COMPONENT_CUSTOM_HTML_TYPE

    def __init__(self, component_id, title=''):
        self.component_id = component_id
        self.title = title

    @classmethod
    def get_data(cls, data):
        return {'content': str(data.get('content', ''))}

    @classmethod
    def get_example_data(cls):
        return {'content': str('Content Example')}
