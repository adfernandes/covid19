{%- assign everything = "" | split: "," -%}
{%- for country in site.data.countries -%}
{%- capture country_text -%}{{ country | replace: " ", "&nbsp;" }}{%- endcapture -%}
{%- capture country_html -%}[{{ country_text }}](#0){:onClick="return setPlotSrc('plots/{{ include.model }}/svg/{{ country }}.svg');"}{%- endcapture -%}
{% assign everything = country_html | concat: everything %}
{% endfor %}

{{ everything | array_to_sentence_string | replace: ", ", ",&nbsp;&nbsp; " | replace: " and ", " and&nbsp;&nbsp; " }}

<script>
    function setPlotSrc(location) {
        document.getElementById("plot").src = location;
        return false;
    }
</script>

<img id="plot" style="display: block; width: 100%; height: auto; border: 1pt solid LightGrey; border-left: 0; border-right: 0;" src="plots/empty.svg">
