---
usemathjax: true
layout: default
---

{% comment %}
Warning! Some of the 'space' characters below are really unicode 'non-breaking-space' characters!
{%- endcomment -%}
{% assign everything = "" | split: "," %}
{%- for country in site.data.countries -%}
{%- capture country_text -%}{{ country | replace: " ", " " }}{%- endcapture -%}
{%- capture country_html -%}[{{ country_text }}](plots/svg/{{ country }}.svg){:target="plot"}{%- endcapture -%}
{% assign everything = country_html | concat: everything %}
{% endfor %}
{{ everything | array_to_sentence_string | replace: ", ", ",   " | replace: " and ", " and   " }}

<div style="display: flex; flex-direction: column; border: 1pt solid LightGrey; border-left: 0; border-right: 0;">
<iframe name="plot" style="border: none; flex-grow: 1;"></iframe>
</div>

# What is this, and Why should I care?

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

Special thanks to [Johns Hopkins University](https://www.jhu.edu/) and the [ESRI Living Atlas Team](https://livingatlas.arcgis.com/en/) for providing the world with such a valuable resource. Like almost every analysis online, this work was based on the [JHU CSSE Data](https://github.com/CSSEGISandData/COVID-19).

This site is auto-generated [via GitHub repository]({{ site.github.repository_url }}) and workflow Actions.

You can reach me at $$\small\text{Andrew Fernandes}\ \email{andrew}{fernandes.org}$$.
