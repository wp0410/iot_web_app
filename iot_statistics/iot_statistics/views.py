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

    Routes and views for the flask application.
"""
from datetime import datetime, date, timedelta
from flask import render_template, redirect, url_for, request
import wp_configfile
from iot_statistics import app
import iot_statistics.model.stat_input_probe as stat_input_probe
import iot_statistics.model.stat_generator as stat_generator
import iot_statistics.view.stat_view as stat_view

@app.route('/')
@app.route('/home')
def home():
    """ Renders the home page. """
    return redirect(url_for('dashboard'))

@app.route('/dashboard', methods=['GET'])
@app.route('/dashboard/<eval_day_str>', methods=['GET'])
def dashboard(eval_day_str: str = None):
    """  Renders the overall dashboard.

    Parameters:
        eval_day_str : str, optional
            Selected evaluation day date (Format "%Y%m%d"). Default: None.
    """
    if eval_day_str is None:
        ev_day = request.args.get('ev_day', None, str)
        if ev_day is None:
            target_date = datetime.today()
        else:
            target_date = datetime.strptime(ev_day, "%d.%m.%Y")
            ev_offs = request.args.get('ev_offset', 0, int)
            if ev_offs != 0:
                target_date = target_date + timedelta(days=ev_offs)
        target_date = date(target_date.year, target_date.month, target_date.day)
        return redirect(url_for('dashboard', eval_day_str = target_date.strftime("%Y%m%d")))
    eval_day = datetime.strptime(eval_day_str, "%Y%m%d")
    eval_day = date(eval_day.year, eval_day.month, eval_day.day)
    conf = wp_configfile.ConfigFile(app_name = "iot_statistics")
    stat_gen = stat_generator.IotStatisticsGenerator(conf['sqlite_stat_db'], stat_input_probe.InputProbeStatistics)
    input_probe_stat = stat_gen.overall_trend(eval_date = eval_day)
    device_list = stat_gen.entities(eval_date = eval_day)
    return render_template(
        'dashboard.html',
        eval_day = eval_day.strftime("%d.%m.%Y"),
        device_list = device_list,
        input_probe_stat = stat_view.InputProbeStatisticsView(input_probe_stat))

@app.route('/dashb_dev', methods=['GET'])
@app.route('/dashb_dev/<eval_day_str>', methods=['GET'])
def dashb_dev(eval_day_str: str = None):
    """  Renders the device overview dashboard.

    Parameters:
        eval_day_str : str, optional
            Selected evaluation day date (Format "%Y%m%d"). Default: None.
    """
    if eval_day_str is None:
        ev_day = request.args.get('ev_day', None, str)
        if ev_day is None:
            target_date = datetime.today()
        else:
            target_date = datetime.strptime(ev_day, "%d.%m.%Y")
            ev_offs = request.args.get('ev_offset', 0, int)
            if ev_offs != 0:
                target_date = target_date + timedelta(days=ev_offs)
        target_date = date(target_date.year, target_date.month, target_date.day)
        return redirect(url_for('dashb_dev', eval_day_str = target_date.strftime("%Y%m%d")))
    eval_day = datetime.strptime(eval_day_str, "%Y%m%d")
    eval_day = date(eval_day.year, eval_day.month, eval_day.day)
    conf = wp_configfile.ConfigFile(app_name = "iot_statistics")
    stat_gen = stat_generator.IotStatisticsGenerator(conf['sqlite_stat_db'], stat_input_probe.InputProbeStatistics)
    input_probe_stat = stat_gen.overall_trend(eval_date = eval_day, by_entity = True)
    dev_stat_view = stat_view.InputProbeStatisticsView(input_probe_stat)
    input_probe_stat = stat_gen.overall_trend(eval_date = eval_day, by_entity = True, by_sub_entity = True)
    chan_stat_view = stat_view.InputProbeStatisticsView(input_probe_stat)
    device_list = stat_gen.entities(eval_date = eval_day)
    return render_template(
        'dashboard_device.html',
        eval_day = eval_day.strftime("%d.%m.%Y"),
        device_list = device_list,
        device_stat = dev_stat_view,
        channel_stat = chan_stat_view )

@app.route('/dashb_dev_detail', methods=['GET'])
@app.route('/dashb_dev_detail/<eval_day_str>', methods=['GET'])
def dashb_dev_detail(eval_day_str: str = None):
    """  Renders the device detail dashboard.

    Parameters:
        eval_day_str : str, optional
            Selected evaluation day date (Format "%Y%m%d"). Default: None.
    """
    device_id = request.args.get('device')
    if eval_day_str is None:
        ev_day = request.args.get('ev_day', None, str)
        if ev_day is None:
            target_date = datetime.today()
        else:
            target_date = datetime.strptime(ev_day, "%d.%m.%Y")
            ev_offs = request.args.get('ev_offset', 0, int)
            if ev_offs != 0:
                target_date = target_date + timedelta(days=ev_offs)
        target_date = date(target_date.year, target_date.month, target_date.day)
        return redirect(url_for('dashb_dev_detail', eval_day_str = target_date.strftime("%Y%m%d"), device = device_id))
    eval_day = datetime.strptime(eval_day_str, "%Y%m%d")
    eval_day = date(eval_day.year, eval_day.month, eval_day.day)
    conf = wp_configfile.ConfigFile(app_name = "iot_statistics")
    stat_gen = stat_generator.IotStatisticsGenerator(conf['sqlite_stat_db'], stat_input_probe.InputProbeStatistics)
    dev_stat = stat_gen.sub_entity_values(eval_date = eval_day, entity_id = device_id, by_min = 5)
    device_stat = stat_view.InputProbeStatisticsView(dev_stat)
    device_list = stat_gen.entities(eval_date = eval_day)
    return render_template(
        'dashboard_device_detail.html',
        eval_day = eval_day.strftime("%d.%m.%Y"),
        device_list = device_list,
        device = device_id,
        device_stat = device_stat)

@app.route('/dashb_sensor', methods=['GET'])
def dashb_sensor(eval_day_str: str = None):
    """  Renders the sensor overview dashboard.

    Parameters:
        eval_day_str : str, optional
            Selected evaluation day date (Format "%Y%m%d"). Default: None.
    """
    return redirect(url_for('home', eval_day_str=eval_day_str))
