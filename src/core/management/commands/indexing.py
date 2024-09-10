from django_elasticsearch_dsl.management.commands.search_index import (
    Command as SearchIndexCommand,
)


class Command(SearchIndexCommand):
    def handle(self, *args, **options):
        models = self._get_models(["infrastructure"])

        # We need to know if and which aliases exist to mitigate naming
        # conflicts with indices, therefore this is needed regardless
        # of using the '--use-alias' arg.
        aliases = []
        for index in self.es_conn.indices.get_alias().values():
            aliases += index["aliases"].keys()

        self._rebuild(models, aliases, options)
