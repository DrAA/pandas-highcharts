# -*- coding: utf-8 -*-

import copy

import pandas

_pd2hc_kind = {
    "bar": "column",
    "barh": "bar",
    "area": "area",
    "line": "line",
    "pie": "pie",
    "scatter": "scatter",
}


def pd2hc_kind(kind):
    if kind not in _pd2hc_kind:
        raise ValueError("%(kind)s plots are not yet supported" % locals())
    return _pd2hc_kind[kind]

_pd2hc_linestyle = {
    "-": "Solid",
    "--": "Dash",
    "-.": "DashDot",
    ":": "Dot"
}


def pd2hc_linestyle(linestyle):
    if linestyle not in _pd2hc_linestyle:
        raise ValueError("%(linestyle)s linestyles are not yet supported" % locals())
    return _pd2hc_linestyle[linestyle]


def json_encode(obj):
    return pandas.io.json.dumps(obj)


def serialize(df, output_type="javascript", chart_type="default", *args, **kwargs):
    def serialize_chart(df, output, *args, **kwargs):
        output["chart"] = {}
        if 'render_to' in kwargs:
            output['chart']['renderTo'] = kwargs['render_to']
        if "figsize" in kwargs:
            output["chart"]["width"] = kwargs["figsize"][0]
            output["chart"]["height"] = kwargs["figsize"][1]
        if "kind" in kwargs:
            output["chart"]["type"] = pd2hc_kind(kwargs["kind"])
        if kwargs.get('polar'):
            output['chart']['polar'] = True

    def serialize_colors(df, output, *args, **kwargs):
        pass

    def serialize_credits(df, output, *args, **kwargs):
        pass

    def serialize_data(df, output, *args, **kwargs):
        pass

    def serialize_drilldown(df, output, *args, **kwargs):
        pass

    def serialize_exporting(df, output, *args, **kwargs):
        pass

    def serialize_labels(df, output, *args, **kwargs):
        pass

    def serialize_legend(df, output, *args, **kwargs):
        pass

    def serialize_loading(df, output, *args, **kwargs):
        pass

    def serialize_navigation(df, output, *args, **kwargs):
        pass

    def serialize_noData(df, output, *args, **kwargs):
        pass

    def serialize_pane(df, output, *args, **kwargs):
        pass

    def serialize_plotOptions(df, output, *args, **kwargs):
        if kwargs.get("kind") == 'area':
            output['plotOptions'] = {
                'area': {
                    'stacking': 'normal',
                }
            }
        elif kwargs.get("kind") == 'scatter':
            output['plotOptions'] = {
                'scatter': {
                    'marker': {
                        'radius': 4,
                    }
                }
            }

    def serialize_series(df, output, *args, **kwargs):
        def is_secondary(c, **kwargs):
            return c in kwargs.get("secondary_y", [])
        if kwargs.get('sort_columns'):
            df = df.sort_index()
        series = df.to_dict('series')
        output["series"] = []
        for name, data in series.items():
            if df[name].dtype.kind in "biufc":
                sec = is_secondary(name, **kwargs)
                d = dict(name=name)
                if sec:
                    d['yAxis'] = int(sec)
                    if kwargs.get("mark_right", True):
                        d['name'] += " (right)"
                if kwargs.get("kind") == "area":
                    d["data"] = data.values.tolist()
                else:
                    d["data"] = list(zip(df.index, data.values.tolist()))
                if kwargs.get('color'):
                    if kwargs['color'].get(d['name']):
                        d['color'] = kwargs['color'][d['name']]
                if kwargs.get('polar'):
                    d['data'] = [v for k, v in d['data']]
                if kwargs.get("linewidth"):
                    d["lineWidth"] = kwargs["linewidth"].get(name, 2)
                if kwargs.get("style"):
                    d["dashStyle"] = pd2hc_linestyle(kwargs["style"].get(name, "-"))
                output["series"].append(d)
        output['series'].sort(key=lambda s: s['name'])

    def serialize_subtitle(df, output, *args, **kwargs):
        pass

    def serialize_title(df, output, *args, **kwargs):
        output["title"] = {"text": kwargs.get("title", "")}

    def serialize_tooltip(df, output, *args, **kwargs):
        if 'tooltip' in kwargs:
            output['tooltip'] = kwargs['tooltip']

    def serialize_xAxis(df, output, *args, **kwargs):
        output["xAxis"] = {}
        if df.index.name:
            output["xAxis"]["title"] = {"text": df.index.name}
        if df.index.dtype.kind in "M":
            output["xAxis"]["type"] = "datetime"
        if df.index.dtype.kind == 'O' or kwargs.get("kind") == 'area':
            output['xAxis']['categories'] = sorted(list(df.index)) if kwargs.get('sort_columns') else list(df.index)
        if kwargs.get("grid"):
            output["xAxis"]["gridLineWidth"] = 1
            output["xAxis"]["gridLineDashStyle"] = "Dot"
        if kwargs.get("loglog") or kwargs.get("logx"):
            output["xAxis"]["type"] = 'logarithmic'
        if "xlim" in kwargs:
            output["xAxis"]["min"] = kwargs["xlim"][0]
            output["xAxis"]["max"] = kwargs["xlim"][1]
        if "rot" in kwargs:
            output["xAxis"]["labels"] = {"rotation": kwargs["rot"]}
        if "fontsize" in kwargs:
            output["xAxis"].setdefault("labels", {})["style"] = {"fontSize": kwargs["fontsize"]}
        if "xticks" in kwargs:
            output["xAxis"]["tickPositions"] = kwargs["xticks"]

    def serialize_yAxis(df, output, *args, **kwargs):

        def config_axis(*args, **kwargs):
            yAxis = {}
            if kwargs.get("grid"):
                yAxis["gridLineWidth"] = 1
                yAxis["gridLineDashStyle"] = "Dot"
            if kwargs.get("loglog") or kwargs.get("logy"):
                yAxis["type"] = 'logarithmic'
            if "ylim" in kwargs:
                yAxis["min"] = kwargs["ylim"][0]
                yAxis["max"] = kwargs["ylim"][1]
            if "rot" in kwargs:
                yAxis["labels"] = {"rotation": kwargs["rot"]}
            if "fontsize" in kwargs:
                yAxis.setdefault("labels", {})["style"] = {"fontSize": kwargs["fontsize"]}
            if "yticks" in kwargs:
                yAxis["tickPositions"] = kwargs["yticks"]
            yAxis["title"] = {"text": kwargs.get("ylabel", "")}
            return yAxis

        output["yAxis"] = [config_axis(*args, **kwargs)]
        if kwargs.get("secondary_y"):
            kwargs2 = copy.deepcopy(kwargs)
            for arg in ['ylim', 'rot', 'yticks', 'ylabel', 'loglog', 'logy']:
                if arg in kwargs2:
                    del kwargs2[arg]
                if arg + '2' in kwargs:
                    kwargs2[arg] = kwargs[arg + '2']
            yAxis2 = config_axis(*args, **kwargs2)
            yAxis2["opposite"] = True
            output["yAxis"].append(yAxis2)

    def serialize_zoom(df, output, *args, **kwargs):
        if "zoom" in kwargs:
            if kwargs["zoom"] not in ("x", "y", "xy"):
                raise ValueError("zoom must be in ('x', 'y', 'xy')")
            output["chart"]["zoomType"] = kwargs["zoom"]

    output = {}
    df_copy = copy.deepcopy(df)
    if "x" in kwargs:
        df_copy.index = df_copy.pop(kwargs["x"])
    if kwargs.get("use_index", True) is False:
        df_copy = df_copy.reset_index()
    if "y" in kwargs:
        df_copy = pandas.DataFrame(df_copy, columns=kwargs["y"])
    serialize_chart(df_copy, output, *args, **kwargs)
    serialize_colors(df_copy, output, *args, **kwargs)
    serialize_credits(df_copy, output, *args, **kwargs)
    serialize_data(df_copy, output, *args, **kwargs)
    serialize_drilldown(df_copy, output, *args, **kwargs)
    serialize_exporting(df_copy, output, *args, **kwargs)
    serialize_labels(df_copy, output, *args, **kwargs)
    serialize_legend(df_copy, output, *args, **kwargs)
    serialize_loading(df_copy, output, *args, **kwargs)
    serialize_navigation(df_copy, output, *args, **kwargs)
    serialize_noData(df_copy, output, *args, **kwargs)
    serialize_pane(df_copy, output, *args, **kwargs)
    serialize_plotOptions(df_copy, output, *args, **kwargs)
    serialize_series(df_copy, output, *args, **kwargs)
    serialize_subtitle(df_copy, output, *args, **kwargs)
    serialize_title(df_copy, output, *args, **kwargs)
    serialize_tooltip(df_copy, output, *args, **kwargs)
    serialize_xAxis(df_copy, output, *args, **kwargs)
    serialize_yAxis(df_copy, output, *args, **kwargs)
    serialize_zoom(df_copy, output, *args, **kwargs)

    if kwargs.get("output_fun"):
        output = kwargs['output_fun'](output)

    if kwargs.get("debug"):
        from IPython.display import display  ## AA debug
        output_clean = output.copy()
        series_clean = []
        for s in output_clean['series']:
            s_clean = s.copy()
            s_clean.pop('data')
            series_clean.append(s_clean)
        output_clean['series'] = series_clean
        display(output_clean)

    if output_type == "dict":
        return output
    if output_type == "json":
        return json_encode(output)
    if chart_type == "stock":
        return "new Highcharts.StockChart(%s);" % json_encode(output)
    return "new Highcharts.Chart(%s);" % json_encode(output)
