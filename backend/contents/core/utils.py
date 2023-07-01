def get_measure_form(count: str):
    """Возвращает верную форму слова 'раз' в зависимости от количества."""
    out_of_rule = [12, 13, 14]
    multiple_form = [2, 3, 4]
    measure = 'раз'
    if int(count[-1]) in multiple_form:
        if len(count) > 1:
            if int(count[-2:]) not in out_of_rule:
                measure = 'раза'
        else:
            measure = 'раза'
    return measure
