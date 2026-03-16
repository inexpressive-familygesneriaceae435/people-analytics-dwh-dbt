{% macro turnover_rate(terminations, headcount) %}
    case
        when {{ headcount }} > 0
        then round({{ terminations }} * 100.0 / {{ headcount }}, 2)
        else 0
    end
{% endmacro %}


{% macro absence_rate(absence_hours, headcount, standard_monthly_hours=176) %}
    case
        when {{ headcount }} > 0
        then round({{ absence_hours }} / ({{ headcount }} * {{ standard_monthly_hours }}) * 100, 2)
        else 0
    end
{% endmacro %}


{% macro completion_rate(completed, total) %}
    round(
        {{ completed }} * 1.0 / nullif({{ total }}, 0),
        3
    )
{% endmacro %}


{% macro safe_divide(numerator, denominator, default_value=0) %}
    case
        when {{ denominator }} is not null and {{ denominator }} != 0
        then {{ numerator }} * 1.0 / {{ denominator }}
        else {{ default_value }}
    end
{% endmacro %}
