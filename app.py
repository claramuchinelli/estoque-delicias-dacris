<h2>Estoque - Delícias da Cris</h2>

<form method="POST">
<select name="sabor">
{% for item in itens %}
<option value="{{ item.sabor }}">{{ item.sabor }}</option>
{% endfor %}
</select>

<input type="number" name="quantidade" placeholder="Quantidade" required>

<select name="tipo">
<option value="adicionar">Adicionar</option>
<option value="vender">Vender</option>
</select>

<button type="submit">Atualizar</button>
</form>

<hr>

{% for item in itens %}
<p>{{ item.sabor }}: {{ item.quantidade }} unidades</p>
{% endfor %}
