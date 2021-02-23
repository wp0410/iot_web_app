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
from datetime import date
import wp_repository

class InputProbeStatistics:
    """ Class for statistics records calculated from recorder InputProbe messages (published by input
        hardware devices).

    Attributes:
        probe_date : date
            Day for which the statistics have been calculated.
        probe_hour : int
            Hour of the day for which the statistics have been calculated.
        probe_min : int
            Minute of the hour for which the statistics have been caculated.
        device_id : str
            Unique identifier of the device that published the InputProbe messages.
        channel_no : int
            Number of the input channel of the input device from which the input probe was collected.
        count : int
            Number of messages for the grouping criteria (probe_date, probe_hour, probe_min, device_id, channel_no).
        minimum : Any
            Minimum target value for the group of messages.
        maximum : Any
            Maximum target value for the group of messages.
        average : Any
            Average target value for the group of messages.

    Properties:
        entity_id : str
            Getter for the generic "entity id" attribute. Will be mapped to device_id for this class.
        sub_entity_id : str
            Getter for the generic "sub entity id" attribute. Will be mapped to channel_no for this class.
        sub_entity_printable : str
            Getter for a "printable" representation of the sub entity identifier.

    Methods:
        InputProbeStatistics:
            Constructor.
        trend_overall : wp_repository.SQLStatement, static
            Composes the SQL SELECT statement to calculate the overall daily trend based on InputProbe values.
        trend_entity : wp_repository.SQLStatement, static
            Composes the SQL SELECT statement to calculate the daily trend by device based on InputProbe values.
        trend_sub_entity : wp_repository.SQLStatement, static
            Composes the SQL SELECT statement to calculate the daily trend by device input channel
            based on InputProbe values.
        entity_list : Composes the SQL SELECT statement to retrieve the list of devices that created InputProbe
            messages on the given day.
        load_row : None
            Converts a row read from the SQLite result cursor of one of the created SQL SELECT statements
            into an InputProbeStatistics object.
        _load_row_t01 : None
            Converts a row read from the SQLite result cursor of the "trend_overall" statement into an
            InputProbeStatistics object.
        _load_row_t02 : None
            Converts a row read from the SQLite result cursor of the "trend_entity" statement
            into an InputProbeStatistics object.
        _load_row_t03 : None
            Converts a row read from the SQLite result cursor of the "trend_sub_entity" statement
            into an InputProbeStatistics object.
        _load_row_t09 : None
            Converts a row read from the SQLite result cursor of the "entity_list" statement
            into an InputProbeStatistics object.
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self):
        """ Constructor. """
        self.probe_date = None
        self.probe_hour = None
        self.probe_min = None
        self.device_id = None
        self.channel_no = None
        self.count = None
        self.minimum = None
        self.maximum = None
        self.average = None

    @property
    def entity_id(self) -> str:
        """ Getter for the generic "entity id" attribute. Will be mapped to device_id for this class. """
        return self.device_id

    @property
    def sub_entity_id(self) -> str:
        """ Getter for the generic "sub entity id" attribute. Will be mapped to channel_no for this class. """
        return str(self.channel_no)

    @property
    def sub_entity_printable(self) -> str:
        """ Getter for a "printable" representation of the sub entity identifier. """
        return f"Channel: {self.channel_no:02d}"

    @staticmethod
    def trend_overall(eval_date: date, by_min: int = 0, eval_target: str = 'value') -> wp_repository.SQLStatement:
        """ Composes the SQL SELECT statement to calculate the overall daily trend based on InputProbe values.

        Parameters:
            eval_date : date
                Day for which the statistics shall be calculated.
            by_min : int, optional
                Specifies the number of minutes for further grouping of the calculated values.
                Default: 0 (no grouping by minute).
            eval_target : str, optional
                Specifies the attribute of the InputProbe records to be used for statistics calculation.
                Default: 'value'.

        Returns:
            wp_repository.SQLStatement : The SQL SELECT statement for calculating the statistics.
        """
        query = wp_repository.SQLStatement()
        query.stmt_text = "SELECT 't01' AS res_type, date(probe_time) as eval_date, "
        query.append_text("strftime('%H',datetime(probe_time)) as grp_hour, ")
        if by_min == 0:
            query.append_text("0 as grp_min, ")
        else:
            s_prtm_full = "strftime('%s',datetime(probe_time))"
            s_prtm_hour = "strftime('%s',datetime(strftime('%Y-%m-%d %H:00:00',datetime(probe_time))))"
            query.append_text(f"{by_min}*((({s_prtm_full}-{s_prtm_hour})/60)/{by_min}) as grp_min, ")
        query.append_text("COUNT(1) AS num_res, ")
        query.append_text(f"MIN({eval_target}) AS min_res, MAX({eval_target}) AS max_res, ")
        query.append_text(f"AVG(ALL {eval_target}) AS avg_res ")
        query.append_text("FROM iot_recorder_input_probe ")
        query.append_text("WHERE date(probe_time) = ? ")
        query.append_text("GROUP BY res_type, eval_date, grp_hour, grp_min ")
        query.append_text("ORDER BY res_type, eval_date, grp_hour, grp_min")
        query.stmt_params = [f"{eval_date.strftime('%Y-%m-%d')}"]
        return query

    def _load_row_t01(self, cursor_row: list) -> None:
        """ Converts a row read from the SQLite result cursor of the "trend_overall" statement
            into an InputProbeStatistics object.

        Parameters:
            cursor_row : list
                Row of values read from the SQLite cursor.
        """
        self.probe_date = cursor_row[1]
        self.probe_hour = cursor_row[2]
        self.probe_min = cursor_row[3]
        self.count = cursor_row[4]
        self.minimum = cursor_row[5]
        self.maximum = cursor_row[6]
        self.average = cursor_row[7]

    @staticmethod
    def trend_entity(eval_date: date, entity_id: str = None, by_min: int = 0,
                     eval_target: str = 'value') -> wp_repository.SQLStatement:
        """ Composes the SQL SELECT statement to calculate the daily trend by device based on InputProbe values.

        Parameters:
            eval_date : date
                Day for which the statistics shall be calculated.
            entity_id : str, optional
                Unique identifier of the device for which the statistics shall be calculated. If empty,
                trends for all devices will be created. Default: None.
            by_min : int, optional
                Specifies the number of minutes for further grouping of the calculated values.
                Default: 0 (no grouping by minute).
            eval_target : str, optional
                Specifies the attribute of the InputProbe records to be used for statistics calculation.
                Default: 'value'.

        Returns:
            wp_repository.SQLStatement : The SQL SELECT statement for calculating the statistics.
        """
        query = wp_repository.SQLStatement()
        query.stmt_text = "SELECT 't02' AS res_type, date(probe_time) as eval_date, "
        query.append_text("strftime('%H',datetime(probe_time)) as grp_hour, ")
        if by_min == 0:
            query.append_text("0 as grp_min, ")
        else:
            s_prtm_full = "strftime('%s',datetime(probe_time))"
            s_prtm_hour = "strftime('%s',datetime(strftime('%Y-%m-%d %H:00:00',datetime(probe_time))))"
            query.append_text(f"{by_min}*((({s_prtm_full}-{s_prtm_hour})/60)/{by_min}) as grp_min, ")
        query.append_text("device_id, COUNT(1) AS num_res, ")
        query.append_text(f"MIN({eval_target}) AS min_res, MAX({eval_target}) AS max_res, ")
        query.append_text(f"AVG(ALL {eval_target}) AS avg_res ")
        query.append_text("FROM iot_recorder_input_probe ")
        query.append_text("WHERE date(probe_time) = ? ")
        query.append_text("" if entity_id is None else " AND device_id = ? ")
        query.append_text("GROUP BY res_type, device_id, eval_date, grp_hour, grp_min ")
        query.append_text("ORDER BY res_type, device_id, eval_date, grp_hour, grp_min")

        query.stmt_params = [f"{eval_date.strftime('%Y-%m-%d')}"]
        if entity_id is not None:
            query.append_param(entity_id)
        return query

    def _load_row_t02(self, cursor_row: list) -> None:
        """ Converts a row read from the SQLite result cursor of the "trend_entity" statement
            into an InputProbeStatistics object.

        Parameters:
            cursor_row : list
                Row of values read from the SQLite cursor.
        """
        self.probe_date = cursor_row[1]
        self.probe_hour = cursor_row[2]
        self.probe_min = cursor_row[3]
        self.device_id = cursor_row[4]
        self.count = cursor_row[5]
        self.minimum = cursor_row[6]
        self.maximum = cursor_row[7]
        self.average = cursor_row[8]

    @staticmethod
    def trend_sub_entity(eval_date: date, entity_id: str = None, sub_entity_id: Any = None,
                         by_min: int = 0, eval_target: str = 'value') -> wp_repository.SQLStatement:
        """ Composes the SQL SELECT statement to calculate the daily trend by device input channel
            based on InputProbe values.

        Parameters:
            eval_date : date
                Day for which the statistics shall be calculated.
            entity_id : str, optional
                Unique identifier of the device for which the statistics shall be calculated. If empty,
                trends for all devices will be created. Default: None.
            sub_entity_id : Any
                Number of the input channel for which the statistics shall be calculated. If empty, trends
                for all channels will be created. Default: None.
            by_min : int, optional
                Specifies the number of minutes for further grouping of the calculated values.
                Default: 0 (no grouping by minute).
            eval_target : str, optional
                Specifies the attribute of the InputProbe records to be used for statistics calculation.
                Default: 'value'.

        Returns:
            wp_repository.SQLStatement : The SQL SELECT statement for calculating the statistics.
        """
        query = wp_repository.SQLStatement()
        query.stmt_text = "SELECT 't03' AS res_type, date(probe_time) as eval_date, "
        query.append_text("strftime('%H',datetime(probe_time)) as grp_hour, ")
        if by_min == 0:
            query.append_text("0 as grp_min, ")
        else:
            s_prtm_full = "strftime('%s',datetime(probe_time))"
            s_prtm_hour = "strftime('%s',datetime(strftime('%Y-%m-%d %H:00:00',datetime(probe_time))))"
            query.append_text(f"{by_min}*((({s_prtm_full}-{s_prtm_hour})/60)/{by_min}) as grp_min, ")
        query.append_text("device_id, channel_no, COUNT(1) AS num_res, ")
        query.append_text(f"MIN({eval_target}) AS min_res, MAX({eval_target}) AS max_res, ")
        query.append_text(f"AVG(ALL {eval_target}) AS avg_res ")
        query.append_text("FROM iot_recorder_input_probe ")
        query.append_text("WHERE date(probe_time) = ? ")
        query.append_text("" if entity_id is None else " AND device_id = ? ")
        query.append_text("" if sub_entity_id is None else " AND channel_no = ? ")
        query.append_text("GROUP BY res_type, device_id, channel_no, eval_date, grp_hour, grp_min ")
        query.append_text("ORDER BY res_type, device_id, channel_no, eval_date, grp_hour, grp_min")

        query.stmt_params = [f"{eval_date.strftime('%Y-%m-%d')}"]
        if entity_id is not None:
            query.append_param(entity_id)
        if sub_entity_id is not None:
            query.append_param(sub_entity_id)
        return query

    def _load_row_t03(self, cursor_row: list) -> None:
        """ Converts a row read from the SQLite result cursor of the "trend_sub_entity" statement
            into an InputProbeStatistics object.

        Parameters:
            cursor_row : list
                Row of values read from the SQLite cursor.
        """
        self.probe_date = cursor_row[1]
        self.probe_hour = cursor_row[2]
        self.probe_min = cursor_row[3]
        self.device_id = cursor_row[4]
        self.channel_no = cursor_row[5]
        self.count = cursor_row[6]
        self.minimum = cursor_row[7]
        self.maximum = cursor_row[8]
        self.average = cursor_row[9]

    @staticmethod
    def entity_list(eval_date: date) -> wp_repository.SQLStatement():
        """ Composes the SQL SELECT statement to retrieve the list of devices that created InputProbe
            messages on the given day.

        Parameters:
            eval_date : date
                Day for which the device list shall be calculated.

        Returns:
            wp_repository.SQLStatement : The SQL SELECT statement for calculating the statistics.
        """
        query = wp_repository.SQLStatement()
        query.stmt_text = "SELECT DISTINCT 't09' as res_type, date(probe_time) AS probe_date, "
        query.append_text("device_id FROM iot_recorder_input_probe WHERE date(probe_time) = ? ORDER BY device_id")
        query.stmt_params = [f"{eval_date.strftime('%Y-%m-%d')}"]
        return query

    def load_row(self, cursor_row: list) -> None:
        """ Converts a row read from the SQLite result cursor of one of the created SQL SELECT statements
            into an InputProbeStatistics object.

        Parameters:
            cursor_row : list
                Row of values read from a SQLite cursor.
        """
        res_type = cursor_row[0]
        if res_type == "t01":
            self._load_row_t01(cursor_row)
        elif res_type == "t02":
            self._load_row_t02(cursor_row)
        elif res_type == "t03":
            self._load_row_t03(cursor_row)
        elif res_type == "t09":
            self._load_row_t09(cursor_row)


    def _load_row_t09(self, cursor_row: list) -> None:
        """ Converts a row read from the SQLite result cursor of the "entity_list" statement
            into an InputProbeStatistics object.

        Parameters:
            cursor_row : list
                Row of values read from the SQLite cursor.
        """
        self.probe_date = cursor_row[1]
        self.probe_hour = 0
        self.probe_min = 0
        self.device_id = cursor_row[2]
        self.channel_no = 0
        self.count = 0
        self.minimum = 0
        self.maximum = 0
        self.average = 0
