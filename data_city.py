"""Arquivo scraping dados da cidade."""
from dataclasses import dataclass
# from layout_pdf.layout_pdf_func
from data_electorate.data_electorate.spiders import tse, ibge
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from twisted.internet import reactor
from scrapy.signalmanager import dispatcher
from scrapy import signals
import locale


locale.setlocale(locale.LC_ALL, '')

@dataclass
class ScrapingData:
    """
    Atributos da classe.

    city {[str]} -- [cidade]
    site {[list]} -- [define spiders a serem usadas]
    """

    city: str
    state: str

    def __post_init__(self):
        """
        Novos attributos da classe.

        results {[dict]} -- [dicionario de dados com resultados]
        """
        self.results = {}

        def crawler_results(signal, sender, item, response, spider):
            self.results.update(item)
        dispatcher.connect(crawler_results, signal=signals.item_passed)
        configure_logging()  # imprime no terminal
        process = CrawlerRunner(get_project_settings())
        process.crawl(tse.TseSpider, city=self.city, state=self.state)
        process.crawl(ibge.IbgeSpider, city=self.city, state=self.state)

        p = process.join()
        p.addBoth(lambda _: reactor.stop())
        reactor.run()

"""
while True:
    city = input('\nQual cidade gostaria de pesquisar?\n')
    if city:
        break
while True:
    state = input('\nDigite a sigla do estado:\n')
    if len(state) == 2:
        break
data_city = ScrapingData(city=city, state=state)
if data_city.results:
    print(f'\n\t\t\t{city.title()}')
    print(
        f'Censo {data_city.results["year_censo"]} \t\t--> ' +
        f'\t{int(data_city.results["value_censo"]):n} pessoas'
    )
    print(
        f'Estimativa {data_city.results["year_estimed"]} \t--> ' +
        f'\t{int(data_city.results["value_estimed"]):n} pessoas'
    )
    print(
        f'Eleitores {data_city.results["month_electorate"][-2:]}/' +
        f'{data_city.results["year_electorate"]} \t--> \t{data_city.results["electorate"]} eleitores'
    )
else:
    print(f'\nCidade ou Estado Não encontrado, verifique digitação')
"""