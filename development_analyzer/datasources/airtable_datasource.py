import pandas as pd
from development_analyzer.datasources.datasource import DataSource

import os


class AirtableDataSource(DataSource):

    def import_dataset(self, file_path: str):
        super().import_dataset(file_path)
        # TODO import using airtable API
        from pyairtable import Api

        api = Api(os.environ['AIRTABLE_API_KEY'])
        base = os.environ['AIRTABLE_BASE']
        table = os.environ['AIRTABLE_TABLE']

        table = api.table(base, table)
        records = table.all()
        # parse records:
        records = [record['fields'] for record in records]

        df = pd.DataFrame(records)
        df.to_csv(file_path, index=False)
