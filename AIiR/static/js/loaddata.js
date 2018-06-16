var values = {
	dupa:"aaasds"
};
{% for dat in data %}
values.push("{{dat.task}}");
{% endfor %}
