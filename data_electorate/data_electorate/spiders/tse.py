"""Arquivo spider eleitorado tse."""
# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.exceptions import CloseSpider
from ..items import Electorate


class TseSpider(scrapy.Spider):
    name = 'tse'
    allowed_domains = ['inter04.tse.jus.br']
    start_urls = [
        'http://www.tse.jus.br/eleitor/estatisticas-de-eleitorado/' +
        'consulta-quantitativo/'
    ]

    def __init__(self, city, state):
        """
        Metodo init recebe argumento do script.

        Keyword Arguments:
            city {[str]} -- [cidade] (default: {None})
        OBS:
            command scrapy crawl ibge -a city=piracicaba
        """
        self.city = city.upper()
        self.state = state.upper()

    def parse(self, response):
        """Seleciona iframe com formulario."""
        self.min_row = 31
        iframe = response.css("#texto-conteudo div iframe::attr(src)").get()
        yield scrapy.Request(iframe, callback=self.parse_contents)

    def parse_contents(self, response):
        """
        Armazena algumas informações deixadas na pagina.
        E faz requesição com maior ano
        """
        self.page_instance = response.css("#pInstance::attr(value)").get()
        self.page_id = response.css("#pPageSubmissionId::attr(value)").get()

        page_protected = response.css(
            "#pPageItemsProtected::attr(value)"
        ).get()
        page_ck = response.css(
            "input[data-for*=P0_LV_ABRANGENCIA]::attr(value)"
        ).get()

        year = response.css("select.selectlist option::text").get()
        month = response.css("#P0_SLS_MES_ELEQ option::attr(value)").get()

        form_data = {
            'p_flow_id': '2001',
            'p_flow_step_id': '109',
            'p_instance': str(self.page_instance),
            'p_page_submission_id': str(self.page_id),
            'p_request': 'P0_SLS_ANO_ELEQ',
            'p_reload_on_submit': 'A',
            'p_json': json.dumps({
                'salt': str(self.page_id),
                'pageItems': {
                    'itemsToSubmit': [
                        {'n': 'P0_SLS_ANO_ELEQ', 'v': str(year)},
                        {'n': 'P0_SLS_MES_ELEQ', 'v': str(month)},
                        {'n': 'P0_SLS_ABRANGENCIA_ELEQ', 'v': '%null%'},
                        {'n': 'P0_LV_ABRANGENCIA', 'v': 'BRUMZ',
                         'ck': str(page_ck)}
                    ],
                    'protected': str(page_protected),
                    'rowVersion': ''
                }
            })}

        yield scrapy.FormRequest(
                        url='http://inter04.tse.jus.br/ords/dwtse/' +
                            'wwv_flow.accept',
                        method='POST',
                        formdata=form_data,
                        callback=self.parse_contents_month,
                    )


    def parse_contents_month(self, response):
        """
        Armazena algumas informações deixadas na pagina.

        E Faz requesição com maior mes e estado
        """
        self.page_instance = response.css("#pInstance::attr(value)").get()
        self.page_id = response.css("#pPageSubmissionId::attr(value)").get()

        page_protected = response.css(
            "#pPageItemsProtected::attr(value)"
        ).get()
        page_ck = response.css(
            "input[data-for*=P0_LV_ABRANGENCIA]::attr(value)"
        ).get()

        self.year = response.css("select.selectlist option::text").get()
        self.month = response.css("#P0_SLS_MES_ELEQ option::attr(value)").get()

        form_data = {
            'p_flow_id': '2001',
            'p_flow_step_id': '109',
            'p_instance': str(self.page_instance),
            'p_page_submission_id': str(self.page_id),
            'p_request': 'P0_SLS_UF_MUN_ELEQ',
            'p_reload_on_submit': 'A',
            'p_json': json.dumps({
                'salt': str(self.page_id),
                'pageItems': {
                    'itemsToSubmit': [
                        {'n': 'P0_SLS_ANO_ELEQ', 'v': str(self.year)},
                        {'n': 'P0_SLS_MES_ELEQ', 'v': str(self.month)},
                        {'n': 'P0_SLS_ABRANGENCIA_ELEQ', 'v': 'M'},
                        {'n': 'P0_SLS_UF_MUN_ELEQ', 'v': self.state},
                        {'n': 'P0_LV_ABRANGENCIA', 'v': 'BRUMZ',
                         'ck': str(page_ck)}
                    ],
                    'protected': str(page_protected),
                    'rowVersion': ''
                }
            })}
        yield scrapy.FormRequest(
                        url='http://inter04.tse.jus.br/ords/dwtse/' +
                            'wwv_flow.accept',
                        method='POST',
                        formdata=form_data,
                        callback=self.parse_results,
                        dont_filter=True,
                    )


    def parse_results(self, response):
        """
        Procura na lista de cidades.
        Se não encontrado requisita proxima pagina
        Até encontrar ou retorna Cidade Não encontrada
        """
        cities = response.css('td[headers*=COL03_000]::text').extract()
        cont = 0
        for city_tse in cities:
            if city_tse == self.city:
                value = response.css(
                    'td[headers*=COL04_000]::text'
                ).extract()[cont]
                electorate = Electorate(
                    city=city_tse, electorate=value,
                    year_electorate=self.year, month_electorate=self.month
                )
                yield electorate
                raise CloseSpider('Cidade Encontrada')
            else:
                cont += 1

        form_data = {
            'p_flow_id': '2001',
            'p_flow_step_id': '109',
            'p_instance': str(self.page_instance),
            'p_debug': '',
            'p_request': 'APXWGT',
            'p_widget_action': 'paginate',
            'p_pg_min_row': str(self.min_row),
            'p_pg_max_rows': '30',
            'p_pg_rows_fetched': '30',
            'x01': '31212748418837964',
            'p_widget_name': 'classic_report',
            'p_json': json.dumps({'salt': str(self.page_id)})
        }
        self.min_row += 30
        if cities:
            yield scrapy.FormRequest(
                        url='http://inter04.tse.jus.br/ords/dwtse/wwv_flow.ajax',
                        method='POST',
                        formdata=form_data,
                        callback=self.parse_results
                    )
        else:
            raise CloseSpider('Cidade Não encontrada')
