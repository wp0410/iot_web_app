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
from datetime import date
import wp_repository

class IotStatisticsGenerator:
    """ Software component for generating time based statistics from an IOT message recorder repository.

    Attributes:
        _stat_db_path : str
            Full path name of the IOT message recorder database.
        _contents_type : type
            Type of the generated statistics records.

    Methods:
        IotStatisticsGenerator:
            Constructor
        entities : list
            Retrieves a list of all entities that published IOT message recorder messages of the given
            type (self._contents_type).
        overall_trend : list
            Calculates trends (minima, maxima, averages) from IOT message recorder messages published on the
            given day, grouped by the given grouping criteria.
        sub_entity_values : list
            Calculates trends (minima, maxima, averages) for sub-entities from IOT message recorder messages
            published on the given day by the given entity.
    """
    def __init__(self, stat_db_path: str, contents_type: type):
        """ Constructor.

        Parameters:
            stat_db_path : str
                Full path name of the IOT message recorder statistics database (SQLite 3).
            contents_type : type
                Specifies the resulting statistics type.
        """
        self._stat_db_path = stat_db_path
        self._contents_type = contents_type

    def entities(self, eval_date: date = date.today()) -> list:
        """ Retrieves a list of all entities that published IOT message recorder messages of the given
            type (self._contents_type).

        Parameters:
            eval_date : date
                Day for which the entity list shall be calculated.

        Returns:
            list : List of entities that published messages on the given day.
        """
        stat_template = self._contents_type()
        sql_stmt = stat_template.entity_list(eval_date)
        with wp_repository.SQLiteRepository(self._contents_type, self._stat_db_path) as stat_repo:
            result = stat_repo.query(sql_stmt)
        return result

    def overall_trend(self, eval_target: str = 'value',
                      eval_date: date = date.today(),
                      by_min: int = 0,
                      by_entity: bool = False, by_sub_entity: bool = False) -> list:
        """ Calculates trends (minima, maxima, averages) from IOT message recorder messages published on the
            given day, grouped by the given grouping criteria.

        Parameters:
            eval_target : str, optional
                Attribute of the contents type that shall be used for trend calcuation. Default: 'value'.
            eval_date : date, optional
                Day for which the trends shall be calculated. Default: date.today().
            by_min : int, optional
                Number of minutes for further grouping the calculated trend values. Default: 0 (grouping of
                values by hour only).
            by_entity : bool, optional
                Specifies whether or not the trend values shall be grouped by identification of the entities
                that published the messages. Default: False.
            by_sub_entity : bool, optional
                Specifies whether or not the trend values shall be further grouped by identification of the
                sub-entities of the entities that published the messages. Default: False.

        Returns:
            list : Array of statistics records, depending on the given contents type.
        """
        stat_template = self._contents_type()
        if not by_entity:
            sql_stmt = stat_template.trend_overall(
                eval_date = eval_date, eval_target = eval_target, by_min = by_min)
        elif not by_sub_entity:
            sql_stmt = stat_template.trend_entity(eval_date = eval_date, eval_target = eval_target, by_min = by_min)
        else:
            sql_stmt = stat_template.trend_sub_entity(eval_date = eval_date, eval_target = eval_target, by_min = by_min)
        with wp_repository.SQLiteRepository(self._contents_type, self._stat_db_path) as stat_repo:
            result = stat_repo.query(sql_stmt)
        return result

    def sub_entity_values(self, entity_id: str, eval_target: str = 'value', eval_date: date = date.today(),
                          by_min: int = 0) -> list:
        """ Calculates trends (minima, maxima, averages) for sub-entities from IOT message recorder messages published
            on the given day by the given entity.

        Parameters:
            entity_id : str
                Unique identifier of the entity that published the messages to be used for trend calculation.
            eval_target : str, optional
                Attribute of the contents type that shall be used for trend calcuation. Default: 'value'.
            eval_date : date, optional
                Day for which the trends shall be calculated. Default: date.today().
            by_min : int, optional
                Number of minutes for further grouping the calculated trend values. Default: 0 (grouping of
                values by hour only).

        Returns:
            list : Array of statistics records, depending on the given contents type.
        """
        stat_template = self._contents_type()
        sql_stmt = stat_template.trend_sub_entity(
            entity_id = entity_id, eval_date = eval_date, eval_target = eval_target, by_min = by_min)
        with wp_repository.SQLiteRepository(self._contents_type, self._stat_db_path) as stat_repo:
            result = stat_repo.query(sql_stmt)
        return result

