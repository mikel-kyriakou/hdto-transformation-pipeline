from rdflib import Graph, RDF
from collections import Counter


class MetricsGenerator:

    @staticmethod
    def items_per_class(graph: Graph) -> dict[str, int]:
        result = Counter()

        for subject, predicate, obj in graph.triples((None, RDF.type, None)):
            result[str(obj)] += 1

        return dict(result)