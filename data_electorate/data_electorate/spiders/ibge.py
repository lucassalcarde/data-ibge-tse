"""Arquivo spider população ibge."""
import scrapy
from ..items import Population
import unidecode
import re
import json
import operator


class IbgeSpider(scrapy.Spider):
    name = 'ibge'

    def __init__(self, city, state):
        """
        Metodo init recebe argumento do script.

        Keyword Arguments:
            city {[str]} -- [cidade]
            state {[str]} -- [estado]
        OBS:
            command scrapy crawl ibge -a city=piracicaba
        """
        self.city = unidecode.unidecode(
            city.lower().replace(' ', '-')
        )
        self.state = state.upper()

    def start_requests(self):
        """Start url da api."""
        return [scrapy.FormRequest(
            url='https://cidades.ibge.gov.br/dist/main-client.js?' +
                'v=Hcl6KcEU2URPgqRm7NOufkc2rYjeYbmHXSMqLs7IR2U',
            method='GET',
            callback=self.parse
        )]

    def parse(self, response):
        """selecionando código do estado."""
        dict_states = re.findall(
            r"exports.ufs = (.+?);", response.text,
            re.MULTILINE | re.DOTALL
        )
        if dict_states:
            states_json = json.loads(
                dict_states[0].replace('\n        ', '\n        "').
                replace(':', '":')
            )
            cod_state = [
                dict_state['codigo'] for dict_state in states_json
                if dict_state['sigla'] == self.state
            ]
        """selecionando código da cidade."""
        dict_cyties = re.findall(
            r"exports.municipios = (.+?);", response.text,
            re.MULTILINE | re.DOTALL
        )
        if dict_cyties:
            data_json = json.loads(dict_cyties[0])
            cod_city = [
                dict_city['codigo'] for dict_city in data_json
                if dict_city['slug'] == self.city
                and dict_city['codigoUf'] == cod_state[0]
            ]
        yield scrapy.FormRequest(
            url='https://servicodados.ibge.gov.br/api/v1/pesquisas/' +
                'indicadores/29171%7C25207/resultados/' +
                str(cod_city[0])[:-1],
            method='GET',
            callback=self.parse_indicators
        )

    def parse_indicators(self, response):
        """Seleciona informação dos indicadores acessados."""
        indicators_json = json.loads(response.text)
        year_value = []
        for dict_indicator in indicators_json:
            # year_censo = list(dict_indicator['res'][0]['res'].keys())
            year_value.append(
                max(
                    dict_indicator['res'][0]['res'].items(),
                    key=operator.itemgetter(1)
                )
            )
        population = Population(
            year_estimed=year_value[1][0], value_estimed=year_value[1][1],
            year_censo=year_value[0][0], value_censo=year_value[0][1]
        )
        yield population
