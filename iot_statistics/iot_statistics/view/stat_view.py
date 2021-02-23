"""
    Copyright 2021 Walter Pachlinger (walter.pachlinger@gmail.com)

    Licensed under the EUPL, Version 1.2 or - as soon they will be approved by the European
    Commission - subsequent versions of the EUPL (the LICENSE). You may not use this work except
    in compliance with the LICENSE. You may obtain a copy of the LICENSE at:

        https://joinup.ec.europa.eu/software/page/eupl

    Unless required by applicable law or agreed to in writing, software distributed under the
    LICENSE is distributed on an "AS IS" basis, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
    either express or implied. See the LICENSE for the specific language governing permissions
    and limitations under the LICENSE.
"""
from typing import Any

class InputProbeStatisticsView:
    """ Wrapper for a list of InputProbe statistics values. Extracts the values as needed for displaying
        them on the web page.

    Attributes:
        _data : list
            List of InputProbe statistics values.

    Properties:
        labels : list
            Getter for the list of x-axis labels for the line chart on the web page.
        entities : list
            Getter for the list of unique entity identifiers within the data set.
        minima : str
            Getter for the concatenated minimum values, separated by commas.
        maxima : str
            Getter for the concatenated maximum values, separated by commas.
        averages : str
            Getter for the concatenated average values, separated by commas.
        averages_by_entity : list
            Getter for the concatenated average values by entity, separated by commas.
        minima_by_entity : list
            Getter for the concatenated minimum values by entity, separated by commas.
        maxima_by_entity : list
            Getter for the concatenated maximum values by entity, separated by commas.
        trends_by_entity : dict
            Converts a "trend by entity" statistics into a dictionary that can be used on the web page
            to create ChartJs line charts.
        trends_by_sub_entity : dict
            Converts a "trend by sub-entity" statistics into a dictionary that can be used on the web page
            to create ChartJs line charts. Dictionary keys are the sub-entity identifiers.
        subs_by_entity : dict
            Converts a "trend by sub-entity" statistics into a dictionary that can be used on the web page
            to create ChartJs line charts. Dictionary keys are the entity identifiers. A "data set" will be
            created for every sub-entity.

    Methods:
        _entity_list : list
            Extracts the list of entries from the data associated with the current instance.
        _aggregate_by_entity : list
            Groups all data elements by unique entity identifier and extracts an aggregate function value for
            the group.
        _str_value : str
            Converts the given value into a string.
    """
    def __init__(self, input_probe_stat: list):
        self._data = input_probe_stat
        self._line_colors = ['#ff0000', '#00ff00', '#0000ff',
                             '#ffff00', '#ff00ff', '#00ffff',
                             '#ff007f', '#7f00ff', '#00ff7f',
                             '#ff7f00', '#7fff00', '#007fff']
        self._color_names = {'Minimum': '#99ff99', 'Maximum': '#ff9999', 'Average': '#99ccff'}
        self._entities = None
        self._trends_by_entity = None
        self._subs_by_entity = None
        self._values_per_sub = None

    @property
    def labels(self) -> list:
        """ Getter for the list of x-axis labels for the line chart on the web page. """
        lb_list = []
        for input_probe in self._data:
            lbl = f"{int(input_probe.probe_hour):02}:{int(input_probe.probe_min):02}"
            if lbl not in lb_list:
                lb_list.append(lbl)
        labels = []
        sep = ""
        for lbl in lb_list:
            labels.append(
                {'separator': sep, 'label': lbl})
            sep = ","
        return labels

    @property
    def entities(self) -> list:
        """ Getter for the list of unique entity identifiers within the data set. """
        if self._entities is None:
            self._entities = self._entity_list()
        return self._entities

    @property
    def minima(self) -> str:
        """ Getter for the concatenated minimum values, separated by commas. """
        min_list = []
        for input_probe in self._data:
            min_list.append(self._str_value(input_probe.minimum))
        return ','.join(min_list)

    @property
    def maxima(self) -> str:
        """ Getter for the concatenated maximum values, separated by commas. """
        max_list = []
        for input_probe in self._data:
            max_list.append(self._str_value(input_probe.maximum))
        return ','.join(max_list)

    @property
    def averages(self) -> str:
        """ Getter for the concatenated average values, separated by commas. """
        avg_list = []
        for input_probe in self._data:
            avg_list.append(self._str_value(input_probe.average))
        return ','.join(avg_list)

    @property
    def averages_by_entity(self) -> list:
        """ Getter for the concatenated average values by entity, separated by commas. """
        return self._aggregate_by_entity('average')

    @property
    def minima_by_entity(self) -> list:
        """ Getter for the concatenated minimum values by entity, separated by commas. """
        return self._aggregate_by_entity('minimum')

    @property
    def maxima_by_entity(self) -> list:
        """ Getter for the concatenated maximum values by entity, separated by commas. """
        return self._aggregate_by_entity('maximum')

    @property
    def trends_by_entity(self) -> dict:
        """ Converts a "trend by entity" statistics into a dictionary that can be used on the web page
            to create ChartJs line charts. """
        if self._trends_by_entity is not None:
            return self._trends_by_entity

        self._trends_by_entity = dict()
        entity_id = ''
        e_min_list = []
        e_avg_list = []
        e_max_list = []
        chart_no = 1
        for data_elem in self._data:
            if data_elem.entity_id != entity_id:
                if len(entity_id) > 0:
                    self._trends_by_entity[entity_id] = {
                        'chartId': chart_no,
                        'dataSets': [{'label': "Minimum", 'data': ','.join(e_min_list),
                                      'borderColor': self._color_names['Minimum']},
                                     {'label': "Average", 'data': ','.join(e_avg_list),
                                      'borderColor': self._color_names['Average']},
                                     {'label': "Maximum", 'data': ','.join(e_max_list),
                                      'borderColor': self._color_names['Maximum']}]
                    }
                    chart_no += 1
                entity_id = data_elem.entity_id
                e_min_list = [self._str_value(data_elem.minimum)]
                e_avg_list = [self._str_value(data_elem.average)]
                e_max_list = [self._str_value(data_elem.maximum)]
            else:
                e_min_list.append(self._str_value(data_elem.minimum))
                e_avg_list.append(self._str_value(data_elem.average))
                e_max_list.append(self._str_value(data_elem.maximum))
        if len(entity_id) > 0:
            self._trends_by_entity[entity_id] = {
                'chartId': chart_no,
                'dataSets': [{'label': "Minimum", 'data': ','.join(e_min_list),
                              'borderColor': self._color_names['Minimum']},
                             {'label': "Average", 'data': ','.join(e_avg_list),
                              'borderColor': self._color_names['Average']},
                             {'label': "Maximum", 'data': ','.join(e_max_list),
                              'borderColor': self._color_names['Maximum']}]
            }
        return self._trends_by_entity

    @property
    def trends_by_sub_entity(self) -> dict:
        """ Converts a "trend by sub-entity" statistics into a dictionary that can be used on the web page
            to create ChartJs line charts. Dictionary keys are the sub-entity identifiers."""
        if self._values_per_sub is not None:
            return self._values_per_sub

        self._values_per_sub = dict()
        sub_entity_prn_id = ''
        s_min_list = []
        s_avg_list = []
        s_max_list = []
        chart_no = 1
        for data_elem in self._data:
            if data_elem.sub_entity_printable != sub_entity_prn_id:
                if len(sub_entity_prn_id) > 0:
                    self._values_per_sub[sub_entity_prn_id] = {
                        'chartId': chart_no,
                        'dataSets': [{'label': "Minimum", 'data': ','.join(s_min_list),
                                      'borderColor': self._color_names['Minimum']},
                                     {'label': "Average", 'data': ','.join(s_avg_list),
                                      'borderColor': self._color_names['Average']},
                                     {'label': "Maximum", 'data': ','.join(s_max_list),
                                      'borderColor': self._color_names['Maximum']}]
                    }
                    chart_no += 1
                sub_entity_prn_id = data_elem.sub_entity_printable
                s_min_list = [self._str_value(data_elem.minimum)]
                s_avg_list = [self._str_value(data_elem.average)]
                s_max_list = [self._str_value(data_elem.maximum)]
            else:
                s_min_list.append(self._str_value(data_elem.minimum))
                s_avg_list.append(self._str_value(data_elem.average))
                s_max_list.append(self._str_value(data_elem.maximum))
        if len(sub_entity_prn_id) > 0:
            self._values_per_sub[sub_entity_prn_id] = {
                'chartId': chart_no,
                'dataSets': [{'label': "Minimum", 'data': ','.join(s_min_list),
                              'borderColor': self._color_names['Minimum']},
                             {'label': "Average", 'data': ','.join(s_avg_list),
                              'borderColor': self._color_names['Average']},
                             {'label': "Maximum", 'data': ','.join(s_max_list),
                              'borderColor': self._color_names['Maximum']}]
            }
        return self._values_per_sub

    @property
    def subs_by_entity(self) -> dict:
        # pylint: disable=too-many-branches
        """ Converts a "trend by sub-entity" statistics into a dictionary that can be used on the web page
            to create ChartJs line charts. Dictionary keys are the entity identifiers. A "data set" will be
            created for every sub-entity. """
        if self._subs_by_entity is not None:
            return self._subs_by_entity

        self._subs_by_entity = dict()
        entity_id = ''
        sub_entity_prn_id = ''
        e_data_sets = []
        sub_avg_list = []
        chart_no = 1
        sub_no = 0
        for data_elem in self._data:
            if data_elem.entity_id != entity_id:
                if data_elem.sub_entity_printable != sub_entity_prn_id:
                    if len(sub_entity_prn_id) > 0:
                        e_data_sets.append({'label': sub_entity_prn_id, 'data': ','.join(sub_avg_list),
                                            'borderColor': self._line_colors[sub_no]})
                        sub_no = (sub_no + 1) % len(self._line_colors)
                    sub_entity_prn_id = data_elem.sub_entity_printable
                    sub_avg_list = [self._str_value(data_elem.average)]
                else:
                    sub_avg_list.append(self._str_value(data_elem.average))

                if len(entity_id) > 0:
                    if len(sub_entity_prn_id) > 0:
                        e_data_sets.append({'label': sub_entity_prn_id, 'data': ','.join(sub_avg_list),
                                            'borderColor': self._line_colors[sub_no]})
                    self._subs_by_entity[entity_id] = {
                        'chartId': chart_no,
                        'dataSets': e_data_sets
                    }
                    e_data_sets = []
                    sub_no = 0
                    chart_no += 1
                entity_id = data_elem.entity_id
            else:
                if data_elem.sub_entity_printable != sub_entity_prn_id:
                    if len(sub_entity_prn_id) > 0:
                        e_data_sets.append({'label': sub_entity_prn_id, 'data': ','.join(sub_avg_list),
                                            'borderColor': self._line_colors[sub_no]})
                        sub_no = (sub_no + 1) % len(self._line_colors)
                    sub_entity_prn_id = data_elem.sub_entity_printable
                    sub_avg_list = [f"{data_elem.average:.5f}"]
                else:
                    sub_avg_list.append(self._str_value(data_elem.average))
        if len(entity_id) > 0:
            if len(sub_entity_prn_id) > 0:
                e_data_sets.append({'label': sub_entity_prn_id, 'data': ','.join(sub_avg_list),
                                    'borderColor': self._line_colors[sub_no]})
            self._subs_by_entity[entity_id] = {
                'chartId': chart_no,
                'dataSets': e_data_sets
            }
        return self._subs_by_entity

    def _entity_list(self) -> list:
        """ Extracts the list of entries from the data associated with the current instance.

        Returns:
            list : List of entries from the associated data.
        """
        entities = []
        for data_elem in self._data:
            if data_elem.entity_id not in entities:
                entities.append(data_elem.entity_id)
        return entities
    def _aggregate_by_entity(self, aggregate: str) -> list:
        """ Groups all data elements by unique entity identifier and extracts an aggregate function value for
            the group.

        Returns:
            list : List of aggregate function values per entity.
        """
        data_sets = []
        self._entities = []
        entity_id = ''
        e_data_list = []
        ds_no = 0
        for data_elem in self._data:
            if data_elem.entity_id != entity_id:
                if len(entity_id) > 0:
                    e_data = ','.join(e_data_list)
                    data_sets.append({'label': entity_id, 'data': e_data, 'borderColor': self._line_colors[ds_no]})
                    self._entities.append(entity_id)
                    ds_no += 1
                entity_id = data_elem.entity_id
                e_data_list = [self._str_value(getattr(data_elem, aggregate))]
            else:
                e_data_list.append(self._str_value(getattr(data_elem, aggregate)))
        if len(entity_id) > 0:
            e_data = ','.join(e_data_list)
            data_sets.append({'label': entity_id, 'data': e_data, 'borderColor': self._line_colors[ds_no]})
            self._entities.append(entity_id)
        return data_sets

    @staticmethod
    def _str_value(value: Any) -> str:
        """ Converts the given value into a string.

        Parameters:
            value : Any
                Value to be converted.

        Returns:
            Value as string.
        """
        if isinstance(value, int):
            return f"{value}"
        if isinstance(value, float):
            return f"{value:.5f}"
        return value
