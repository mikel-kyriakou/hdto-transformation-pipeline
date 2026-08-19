from rdflib import Namespace, Graph, URIRef, Literal
from rdflib.namespace import RDF, XSD

from app.models.models import HeritageObjectData

CIDOC = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
RHDTO = Namespace("https://vast-lab.org/rhdto/")
#TODO change this
OUR_NAMESPACE = Namespace("http://aueb.gr/rhdto-transofmration-pipeline/")


class Mapper:

    def __init__(
        self,
        cidoc_crm: Namespace = CIDOC,
        rhdto: Namespace = RHDTO
    ) -> None:
        self.cidoc_crm = cidoc_crm
        self.rhdto = rhdto
        self.our_namespace = OUR_NAMESPACE

    def map(self, heritage_objects: list[HeritageObjectData]) -> Graph:
        graph = Graph()

        graph.bind("crm", self.cidoc_crm)
        graph.bind("rhdto", self.rhdto)

        for i, obj in enumerate(heritage_objects):
            instance_id = str(i)

            object_instance = self._create_object_instance(
                graph,
                instance_id
            )

            self._add_identifier(graph, object_instance, instance_id, obj.id)

            self._add_title(graph, object_instance, instance_id, obj.title)

            self._add_type(graph, object_instance, instance_id, obj.object_type)

            self._add_material(graph, object_instance, instance_id, obj.material)

        return graph

    # =========================================================
    # ADD / MAPPING METHODS
    # =========================================================

    def _add_identifier(self, graph: Graph, object_instance: URIRef, instance_id: str, value: str | None) -> None:

        if value is None:
            return

        identifier_instance = self._create_identifier_instance(graph, instance_id, value)

        graph.add((object_instance, self.cidoc_crm.P48_has_preferred_identifier, identifier_instance))

    def _add_title(self, graph: Graph, object_instance: URIRef, instance_id: str, value: str | None) -> None:

        if value is None:
            return

        title_instance = self._create_title_instance(graph, instance_id, value)

        graph.add((object_instance, self.cidoc_crm.P102_has_title, title_instance))

    def _add_type(self, graph: Graph, object_instance: URIRef, instance_id: str, value: str | None) -> None:

        if value is None:
            return

        type_instance = self._create_type_instance(graph, instance_id, value)

        graph.add((object_instance, self.cidoc_crm.P2_has_type, type_instance))

    def _add_material(self, graph: Graph, object_instance: URIRef, instance_id: str, value: str | None) -> None:

        if value is None:
            return

        material_instance = self._create_material_instance(graph, instance_id, value)

        graph.add((object_instance, self.cidoc_crm.P45_consists_of, material_instance))

    # =========================================================
    # INSTANCE CREATION METHODS
    # =========================================================

    def _create_object_instance(self, graph: Graph, instance_id: str) -> URIRef:
        return self._create_instance(
            graph=graph,
            instance_id=f"tangible-entity-{instance_id}",
            class_type=self.rhdto.HC3_Tangible_Entity
        )

    def _create_identifier_instance(self, graph: Graph, instance_id: str, object_id: str) -> URIRef:
        return self._create_instance_with_literal(
            graph=graph,
            instance_id=f"identifier-{instance_id}",
            class_type=self.cidoc_crm.E42_Identifier,
            literal_value=object_id
        )

    def _create_title_instance(self, graph: Graph, instance_id: str, title: str) -> URIRef:
        return self._create_instance_with_literal(
            graph=graph,
            instance_id=f"title-{instance_id}",
            class_type=self.cidoc_crm.E35_Title,
            literal_value=title
        )

    def _create_type_instance(self, graph: Graph, instance_id: str, object_type: str) -> URIRef:
        return self._create_instance_with_literal(
            graph=graph,
            instance_id=f"type-{instance_id}",
            class_type=self.cidoc_crm.E55_Type,
            literal_value=object_type
        )

    def _create_material_instance(self, graph: Graph, instance_id: str, material: str) -> URIRef:
        return self._create_instance_with_literal(
            graph=graph,
            instance_id=f"material-{instance_id}",
            class_type=self.cidoc_crm.E57_Material,
            literal_value=material
        )

    # ---------------------------------------------------------
    # Generic RDF creation methods
    # ---------------------------------------------------------

    def _create_instance(self, graph: Graph, instance_id: str, class_type: URIRef) -> URIRef:
        instance = self.our_namespace[instance_id]

        graph.add((instance, RDF.type, class_type))

        return instance

    def _create_instance_with_literal(self, graph: Graph, instance_id: str, class_type: URIRef, literal_value: str, property: URIRef = None) -> URIRef:
        instance = self._create_instance(graph, instance_id, class_type)

        if property is None:
            property = self.cidoc_crm.P190_has_symbolic_content

        graph.add((instance, property, Literal(literal_value, datatype=XSD.string)))

        return instance


if __name__ == "__main__":

    mapper = Mapper()

    graph = mapper.map(heritage_objects=[
        HeritageObjectData(
            id="1",
            title="Test Object",
            object_type="Test Type",
            material="Test Material"
        ),
        HeritageObjectData(
            id="2",
            title="Test Object 2",
            object_type="Test Type 2",
            material="Test Material 2"
    )])

    print(graph.serialize(format="turtle"))
