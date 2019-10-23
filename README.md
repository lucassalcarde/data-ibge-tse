# Data-ibge-tse

Com nome da cidade e sigla do estado. 

Do ibge tem o retorno do ultimo ano do censo feito e população, também o ultimo calculo de estimativa de população e o ano dessa estimativa.
Do tse  tem o retorno do mais recente quantitativo do eleitorado, mês e ano.

# Install

- python 3

$ git clone git://github.com/lucassalcarde/data-ibge-tse.git

$ pip install -r requirements.txt

# Usage

>>> data_ibge_tse = ScrapingData(city='São Pedro', state='SP')

>>> data_ibge_tse.results

{'year_estimed': '2019', 'value_estimed': '35653', 'year_censo': '2010', 'value_censo': '31662', 'city': 'SÃO PEDRO', 'electorate': '25.443', 'year_electorate': '2019', 'month_electorate': '201909'}
